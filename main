import os
import logging
import threading
import time
from app import app
from trading_bot import TradingBot

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def start_trading_bot():
    """Start the trading bot in a separate thread"""
    try:
        bot = TradingBot()
        while True:
            try:
                bot.run_analysis_cycle()
                logger.info("取引分析サイクル完了 - 2分待機中...")
                time.sleep(120)  # Wait 2 minutes for higher frequency trading
            except Exception as e:
                logger.error(f"取引ボットエラー: {e}")
                time.sleep(60)  # Wait 1 minute before retry
    except Exception as e:
        logger.error(f"取引ボット初期化エラー: {e}")

if __name__ == "__main__":
    # Start trading bot in background thread
    bot_thread = threading.Thread(target=start_trading_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask app
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
