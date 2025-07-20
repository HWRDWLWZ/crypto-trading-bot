from flask import render_template, jsonify, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app import app, db
from models import Trade, Position, MarketAnalysis, TradingConfig
from sqlalchemy import desc, func
import json
import os
from datetime import datetime, timedelta
from spreadsheet_manager import SpreadsheetManager

@app.route('/')
def dashboard():
    """Main dashboard"""
    # Show login page if not authenticated
    if not current_user.is_authenticated:
        return render_template('login.html')
    return render_template('dashboard.html')

@app.route('/api/dashboard_data')
@login_required
def dashboard_data():
    """API endpoint for dashboard data"""
    try:
        # Get active positions
        positions = Position.query.all()
        positions_data = []
        total_pnl = 0
        
        for pos in positions:
            pos_data = {
                'id': pos.id,
                'symbol': pos.symbol,
                'side': pos.side,
                'quantity': pos.quantity,
                'entry_price': pos.entry_price,
                'current_price': pos.current_price,
                'unrealized_pnl': pos.unrealized_pnl,
                'stop_loss': pos.stop_loss,
                'take_profit': pos.take_profit,
                'opened_at': pos.opened_at.isoformat()
            }
            positions_data.append(pos_data)
            total_pnl += pos.unrealized_pnl
        
        # Get recent trades
        recent_trades = Trade.query.order_by(desc(Trade.timestamp)).limit(10).all()
        trades_data = []
        
        for trade in recent_trades:
            trade_data = {
                'id': trade.id,
                'symbol': trade.symbol,
                'side': trade.side,
                'quantity': trade.quantity,
                'price': trade.price,
                'timestamp': trade.timestamp.isoformat(),
                'pnl': trade.pnl
            }
            trades_data.append(trade_data)
        
        # Get market analysis summary
        latest_analysis = db.session.query(
            MarketAnalysis.symbol,
            func.max(MarketAnalysis.timestamp).label('latest_time')
        ).group_by(MarketAnalysis.symbol).subquery()
        
        analysis_summary = db.session.query(MarketAnalysis).join(
            latest_analysis,
            (MarketAnalysis.symbol == latest_analysis.c.symbol) &
            (MarketAnalysis.timestamp == latest_analysis.c.latest_time)
        ).all()
        
        analysis_data = []
        for analysis in analysis_summary:
            analysis_data.append({
                'symbol': analysis.symbol,
                'timeframe': analysis.timeframe,
                'overall_score': analysis.overall_score,
                'signal': analysis.signal,
                'timestamp': analysis.timestamp.isoformat()
            })
        
        # Calculate performance metrics
        total_trades = Trade.query.count()
        winning_trades = Trade.query.filter(Trade.pnl > 0).count()
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return jsonify({
            'positions': positions_data,
            'recent_trades': trades_data,
            'analysis_summary': analysis_data,
            'metrics': {
                'total_pnl': round(total_pnl, 2),
                'active_positions': len(positions_data),
                'total_trades': total_trades,
                'win_rate': round(win_rate, 1)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trades')
@login_required
def trades():
    """Trades history page"""
    page = request.args.get('page', 1, type=int)
    trades = Trade.query.order_by(desc(Trade.timestamp)).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template('trades.html', trades=trades)

@app.route('/api/trades')
@login_required
def api_trades():
    """API endpoint for trades data"""
    try:
        trades = Trade.query.order_by(desc(Trade.timestamp)).limit(100).all()
        trades_data = []
        
        for trade in trades:
            trades_data.append({
                'id': trade.id,
                'symbol': trade.symbol,
                'side': trade.side,
                'quantity': trade.quantity,
                'price': trade.price,
                'timestamp': trade.timestamp.isoformat(),
                'pnl': trade.pnl,
                'status': trade.status
            })
        
        return jsonify(trades_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analysis/<symbol>')
@login_required
def symbol_analysis(symbol):
    """Detailed analysis for a specific symbol"""
    try:
        # Get latest analysis for all timeframes
        analyses = MarketAnalysis.query.filter_by(symbol=symbol).order_by(
            desc(MarketAnalysis.timestamp)
        ).limit(10).all()
        
        analysis_data = []
        for analysis in analyses:
            analysis_data.append({
                'timeframe': analysis.timeframe,
                'timestamp': analysis.timestamp.isoformat(),
                'rsi': analysis.rsi,
                'macd': analysis.macd,
                'overall_score': analysis.overall_score,
                'signal': analysis.signal,
                'trend_score': analysis.trend_score,
                'momentum_score': analysis.momentum_score,
                'volume_score': analysis.volume_score
            })
        
        return jsonify(analysis_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/config')
@login_required
def config():
    """Configuration page"""
    return render_template('config.html')

@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def api_config():
    """API endpoint for configuration"""
    if request.method == 'GET':
        try:
            # Load configuration from file
            with open('bot_config.json', 'r') as f:
                config_data = json.load(f)
            return jsonify(config_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            config_data = request.json
            
            # Save configuration to file
            with open('bot_config.json', 'w') as f:
                json.dump(config_data, f, indent=4)
            
            flash('設定が保存されました', 'success')
            return jsonify({'success': True})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/performance')
@login_required
def api_performance():
    """API endpoint for performance metrics"""
    try:
        # Calculate daily performance
        today = datetime.utcnow().date()
        days_back = 30
        
        performance_data = []
        for i in range(days_back):
            date = today - timedelta(days=i)
            
            # Get trades for this date
            day_trades = Trade.query.filter(
                func.date(Trade.timestamp) == date
            ).all()
            
            daily_pnl = sum(trade.pnl for trade in day_trades)
            trade_count = len(day_trades)
            
            performance_data.append({
                'date': date.isoformat(),
                'pnl': round(daily_pnl, 2),
                'trade_count': trade_count
            })
        
        performance_data.reverse()  # Chronological order
        
        return jsonify(performance_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/close_position/<int:position_id>', methods=['POST'])
@login_required
def close_position(position_id):
    """Manually close a position"""
    try:
        position = Position.query.get_or_404(position_id)
        
        # In a real implementation, this would place a market order
        # For now, just remove the position
        db.session.delete(position)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'ポジションが決済されました'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# スプレッドシート管理
spreadsheet_manager = SpreadsheetManager()

@app.route('/spreadsheet')
@login_required
def spreadsheet():
    """スプレッドシート管理ページ"""
    return render_template('spreadsheet.html')

@app.route('/pair_selector')
@login_required
def pair_selector():
    """通貨ペア選択ページ"""
    return render_template('pair_selector.html')

@app.route('/reports')
@login_required
def reports():
    """分析レポートページ"""
    return render_template('reports.html')

@app.route('/api/reports')
@login_required
def api_reports():
    """レポート一覧API"""
    try:
        import glob
        import json
        
        # レポートファイル一覧取得
        report_files = glob.glob('daily_report_*.json')
        report_files.sort(reverse=True)  # 新しい順
        
        reports = []
        for file_path in report_files[:10]:  # 最新10件
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                    reports.append(report_data)
            except Exception as e:
                print(f"レポート読み込みエラー: {file_path}, {e}")
                continue
        
        return jsonify({
            'reports': reports,
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': f'レポート取得エラー: {str(e)}'}), 500

@app.route('/api/generate_report', methods=['POST'])
@login_required
def api_generate_report():
    """新しいレポート生成API"""
    try:
        from analysis_report import AnalysisReportGenerator
        
        generator = AnalysisReportGenerator()
        report = generator.generate_daily_report()
        
        # レポートを保存
        filename = f"daily_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'レポートが生成されました',
            'filename': filename,
            'report': report
        })
        
    except Exception as e:
        return jsonify({'error': f'レポート生成エラー: {str(e)}'}), 500

@app.route('/api/run_optimization', methods=['POST'])
@login_required
def api_run_optimization():
    """改善エージェント実行API"""
    try:
        from improvement_agent import ImprovementAgent
        
        agent = ImprovementAgent()
        result = agent.run_optimization_cycle()
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'message': '最適化が完了しました',
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': f'最適化エラー: {str(e)}'}), 500

@app.route('/api/export_data', methods=['POST'])
@login_required
def export_data():
    """データをスプレッドシートにエクスポート"""
    try:
        data = request.json
        export_type = data.get('type', 'trades')  # trades, positions, analysis, summary
        file_type = data.get('file_type', 'excel')  # excel, google_sheets
        spreadsheet_id = data.get('spreadsheet_id', '')
        
        success = False
        message = ""
        
        if export_type == 'trades':
            success = spreadsheet_manager.export_trades_to_spreadsheet(file_type, spreadsheet_id)
            message = "取引データをエクスポートしました" if success else "取引データのエクスポートに失敗しました"
        
        elif export_type == 'positions':
            success = spreadsheet_manager.export_positions_to_spreadsheet(file_type, spreadsheet_id)
            message = "ポジションデータをエクスポートしました" if success else "ポジションデータのエクスポートに失敗しました"
        
        elif export_type == 'analysis':
            success = spreadsheet_manager.export_analysis_to_spreadsheet(file_type, spreadsheet_id)
            message = "分析データをエクスポートしました" if success else "分析データのエクスポートに失敗しました"
        
        elif export_type == 'summary':
            success = spreadsheet_manager.create_trading_summary_spreadsheet(file_type, spreadsheet_id)
            message = "取引サマリーを作成しました" if success else "取引サマリーの作成に失敗しました"
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': f'エクスポートエラー: {str(e)}'}), 500

@app.route('/api/import_config', methods=['POST'])
def import_config():
    """スプレッドシートから設定をインポート"""
    try:
        data = request.json
        file_type = data.get('file_type', 'excel')
        spreadsheet_id = data.get('spreadsheet_id', '')
        sheet_name = data.get('sheet_name', 'Config')
        
        success = spreadsheet_manager.import_config_from_spreadsheet(file_type, spreadsheet_id, sheet_name)
        
        if success:
            return jsonify({'success': True, 'message': '設定をインポートしました'})
        else:
            return jsonify({'error': '設定のインポートに失敗しました'}), 400
            
    except Exception as e:
        return jsonify({'error': f'インポートエラー: {str(e)}'}), 500

@app.route('/api/download_excel')
def download_excel():
    """Excelファイルをダウンロード"""
    try:
        file_path = spreadsheet_manager.get_file_path()
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=f'trading_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        else:
            return jsonify({'error': 'Excelファイルが見つかりません'}), 404
            
    except Exception as e:
        return jsonify({'error': f'ダウンロードエラー: {str(e)}'}), 500

@app.route('/api/get_binance_pairs')
def get_binance_pairs():
    """Binanceの利用可能通貨ペアを取得"""
    try:
        from binance_pairs import BinancePairManager
        manager = BinancePairManager()
        pairs = manager.get_available_pairs()
        current_pairs = manager.get_current_config()
        
        return jsonify({
            'available_pairs': pairs[:30],  # 上位30ペア
            'current_pairs': current_pairs,
            'success': True
        })
    except Exception as e:
        return jsonify({'error': f'通貨ペア取得エラー: {str(e)}'}), 500

@app.route('/api/update_trading_pairs', methods=['POST'])
def update_trading_pairs():
    """通貨ペア設定を更新"""
    try:
        data = request.json
        selected_pairs = data.get('pairs', [])
        
        if not selected_pairs:
            return jsonify({'error': '通貨ペアを選択してください'}), 400
        
        from binance_pairs import BinancePairManager
        manager = BinancePairManager()
        success = manager.update_trading_pairs(selected_pairs)
        
        if success:
            return jsonify({
                'success': True, 
                'message': f'{len(selected_pairs)}ペアの設定を更新しました',
                'pairs': selected_pairs
            })
        else:
            return jsonify({'error': '設定の更新に失敗しました'}), 500
            
    except Exception as e:
        return jsonify({'error': f'設定更新エラー: {str(e)}'}), 500

@app.route('/api/create_sample_config_sheet')
def create_sample_config_sheet():
    """設定用のサンプルスプレッドシートを作成"""
    try:
        # サンプル設定データ
        import pandas as pd
        
        config_data = [
            {'Section': 'risk_management', 'Key': 'max_positions', 'Value': '5', 'Description': '最大同時ポジション数'},
            {'Section': 'risk_management', 'Key': 'risk_per_trade', 'Value': '0.02', 'Description': '1取引あたりのリスク'},
            {'Section': 'risk_management', 'Key': 'stop_loss_pct', 'Value': '0.02', 'Description': 'ストップロス（%）'},
            {'Section': 'risk_management', 'Key': 'take_profit_pct', 'Value': '0.06', 'Description': 'テイクプロフィット（%）'},
            {'Section': 'analysis', 'Key': 'min_score_buy', 'Value': '75', 'Description': '買いシグナル最小スコア'},
            {'Section': 'analysis', 'Key': 'min_score_sell', 'Value': '25', 'Description': '売りシグナル最大スコア'},
            {'Section': 'notifications', 'Key': 'enable_trade_alerts', 'Value': 'true', 'Description': '取引アラート有効'},
            {'Section': 'notifications', 'Key': 'webhook_url', 'Value': '', 'Description': 'Webhook URL'},
        ]
        
        df = pd.DataFrame(config_data)
        
        # Excelファイルに保存（新規作成または既存ファイルに追加）
        try:
            if os.path.exists(spreadsheet_manager.excel_file_path):
                with pd.ExcelWriter(spreadsheet_manager.excel_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name='Config', index=False)
            else:
                with pd.ExcelWriter(spreadsheet_manager.excel_file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Config', index=False)
        except Exception:
            # 新規作成
            with pd.ExcelWriter(spreadsheet_manager.excel_file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Config', index=False)
        
        return jsonify({'success': True, 'message': 'サンプル設定シートを作成しました'})
        
    except Exception as e:
        return jsonify({'error': f'設定シート作成エラー: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
