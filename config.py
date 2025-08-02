import os
from typing import Dict, List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class ExchangeConfig(BaseModel):
    name: str
    api_key: str
    secret_key: str
    sandbox: bool = True
    rate_limit: int = 1000

class ArbitrageConfig(BaseModel):
    min_profit_threshold: float = 0.001  # 0.1% minimum profit
    max_position_size: float = 1000.0    # Maximum position size in USD
    max_slippage: float = 0.0005         # 0.05% maximum slippage
    execution_delay: float = 0.1          # 100ms execution delay
    risk_per_trade: float = 0.02         # 2% risk per trade

class DatabaseConfig(BaseModel):
    url: str = "sqlite:///arbitrage_bot.db"
    echo: bool = False

class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    file: str = "arbitrage_bot.log"

class Config:
    # Exchange configurations
    exchanges: Dict[str, ExchangeConfig] = {
        "binance": ExchangeConfig(
            name="binance",
            api_key=os.getenv("BINANCE_API_KEY", ""),
            secret_key=os.getenv("BINANCE_SECRET_KEY", ""),
            sandbox=True
        ),
        "coinbase": ExchangeConfig(
            name="coinbase",
            api_key=os.getenv("COINBASE_API_KEY", ""),
            secret_key=os.getenv("COINBASE_SECRET_KEY", ""),
            sandbox=True
        ),
        "kraken": ExchangeConfig(
            name="kraken",
            api_key=os.getenv("KRAKEN_API_KEY", ""),
            secret_key=os.getenv("KRAKEN_SECRET_KEY", ""),
            sandbox=True
        )
    }
    
    # Trading pairs to monitor
    trading_pairs: List[str] = [
        "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
        "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP",
        "EUR/JPY", "GBP/JPY", "CHF/JPY", "EUR/CHF"
    ]
    
    # Arbitrage settings
    arbitrage: ArbitrageConfig = ArbitrageConfig()
    
    # Database settings
    database: DatabaseConfig = DatabaseConfig()
    
    # Logging settings
    logging: LoggingConfig = LoggingConfig()
    
    # Monitoring settings
    price_update_interval: float = 1.0  # seconds
    arbitrage_check_interval: float = 5.0  # seconds
    
    # Risk management
    max_daily_loss: float = 100.0  # USD
    max_concurrent_trades: int = 5
    stop_loss_percentage: float = 0.02  # 2%
    
    # Notification settings
    enable_notifications: bool = True
    telegram_bot_token: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")

# Global config instance
config = Config()