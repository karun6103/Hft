# Forex Arbitrage Bot

A high-frequency trading bot that identifies and executes arbitrage opportunities across multiple cryptocurrency exchanges. The bot monitors price differences between exchanges and automatically executes trades when profitable opportunities are detected.

## 🚀 Features

- **Multi-Exchange Support**: Connect to multiple exchanges (Binance, Coinbase, Kraken)
- **Real-Time Monitoring**: Continuous price monitoring with configurable intervals
- **Risk Management**: Advanced risk controls including position sizing, stop losses, and drawdown limits
- **Performance Tracking**: Comprehensive logging and performance metrics
- **Web Dashboard**: Real-time monitoring dashboard with charts and statistics
- **Notifications**: Telegram notifications for trades and alerts
- **Database Storage**: SQLite database for trade history and performance tracking
- **Configurable**: Easy configuration through environment variables

## 📋 Requirements

- Python 3.8+
- Exchange API keys
- Internet connection for real-time data

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd forex-arbitrage-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your API keys and configuration:
   ```env
   BINANCE_API_KEY=your_binance_api_key
   BINANCE_SECRET_KEY=your_binance_secret_key
   COINBASE_API_KEY=your_coinbase_api_key
   COINBASE_SECRET_KEY=your_coinbase_secret_key
   KRAKEN_API_KEY=your_kraken_api_key
   KRAKEN_SECRET_KEY=your_kraken_secret_key
   ```

4. **Get Exchange API Keys**:
   - [Binance API](https://www.binance.com/en/my/settings/api-management)
   - [Coinbase API](https://docs.cloud.coinbase.com/)
   - [Kraken API](https://www.kraken.com/u/settings/api)

## 🚀 Usage

### Starting the Bot

```bash
python main.py
```

### Starting the Web Dashboard

```bash
python web_dashboard.py
```

Then visit `http://localhost:8000` in your browser.

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BINANCE_API_KEY` | Binance API key | Required |
| `BINANCE_SECRET_KEY` | Binance secret key | Required |
| `COINBASE_API_KEY` | Coinbase API key | Required |
| `COINBASE_SECRET_KEY` | Coinbase secret key | Required |
| `KRAKEN_API_KEY` | Kraken API key | Required |
| `KRAKEN_SECRET_KEY` | Kraken secret key | Required |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (optional) | None |
| `TELEGRAM_CHAT_ID` | Telegram chat ID (optional) | None |

### Trading Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| `MIN_PROFIT_THRESHOLD` | Minimum profit percentage to execute trade | 0.1% |
| `MAX_POSITION_SIZE` | Maximum position size in USD | $1,000 |
| `MAX_DAILY_LOSS` | Maximum daily loss limit | $100 |
| `MAX_CONCURRENT_TRADES` | Maximum number of concurrent trades | 5 |
| `STOP_LOSS_PERCENTAGE` | Stop loss percentage | 2% |

## 📊 Monitoring

### Web Dashboard

The web dashboard provides real-time monitoring of:
- Performance metrics
- Recent trades
- Risk management status
- Arbitrage opportunities
- Configuration summary

### Logs

Logs are stored in `arbitrage_bot.log` with rotation:
- Daily log rotation
- 30-day retention
- Different log levels (DEBUG, INFO, WARNING, ERROR)

### Database

SQLite database (`arbitrage_bot.db`) stores:
- Trade history
- Arbitrage opportunities
- Performance metrics
- Exchange prices

## 🔒 Risk Management

The bot includes comprehensive risk management:

1. **Position Sizing**: Automatic calculation based on account balance and risk per trade
2. **Daily Loss Limits**: Stops trading when daily loss limit is reached
3. **Drawdown Protection**: Monitors maximum drawdown and stops if exceeded
4. **Concurrent Trade Limits**: Limits number of simultaneous trades
5. **Stop Loss**: Automatic stop loss on losing trades
6. **Slippage Protection**: Prevents execution if prices move unfavorably

## 📈 Performance Tracking

The bot tracks various performance metrics:
- Total trades and win rate
- Profit/loss tracking
- Average profit per trade
- Maximum drawdown
- Risk-adjusted returns

## 🔔 Notifications

### Telegram Notifications

Set up Telegram notifications:
1. Create a bot with [@BotFather](https://t.me/botfather)
2. Get your bot token and chat ID
3. Add to `.env` file:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

Notifications include:
- Trade executions
- Arbitrage opportunities
- Error alerts
- Daily summaries
- Risk alerts

## 🏗️ Architecture

```
├── main.py                 # Main entry point
├── config.py              # Configuration management
├── arbitrage_engine.py    # Core arbitrage logic
├── exchange_manager.py    # Exchange connections
├── risk_manager.py        # Risk management
├── notification_manager.py # Notifications
├── models.py              # Database models
├── web_dashboard.py       # Web dashboard
└── requirements.txt       # Dependencies
```

## 🔧 Development

### Project Structure

```
forex-arbitrage-bot/
├── main.py
├── config.py
├── arbitrage_engine.py
├── exchange_manager.py
├── risk_manager.py
├── notification_manager.py
├── models.py
├── web_dashboard.py
├── requirements.txt
├── .env.example
├── README.md
└── arbitrage_bot.db (created automatically)
```

### Adding New Exchanges

1. Add exchange configuration to `config.py`
2. Implement exchange-specific methods in `exchange_manager.py`
3. Test with sandbox mode first

### Customizing Risk Management

Modify `risk_manager.py` to adjust:
- Position sizing algorithms
- Risk thresholds
- Stop loss strategies

## ⚠️ Disclaimer

This software is for educational purposes only. Trading cryptocurrencies involves substantial risk of loss. The authors are not responsible for any financial losses incurred through the use of this software.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the logs for error details
- Review the configuration settings

## 🔄 Updates

Stay updated with the latest features and security patches by regularly pulling from the repository.

---

**Happy Trading! 🚀**