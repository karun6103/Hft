import asyncio
import aiohttp
from typing import Dict, Optional
from loguru import logger
from config import config

class NotificationManager:
    def __init__(self):
        self.telegram_bot_token = config.telegram_bot_token
        self.telegram_chat_id = config.telegram_chat_id
        self.enable_notifications = config.enable_notifications
    
    async def send_trade_notification(self, trade_info: Dict):
        """Send notification about a completed trade"""
        if not self.enable_notifications:
            return
        
        message = self._format_trade_message(trade_info)
        
        # Send to all configured channels
        await asyncio.gather(
            self._send_telegram_message(message),
            self._send_console_message(message),
            return_exceptions=True
        )
    
    async def send_opportunity_notification(self, opportunity: Dict):
        """Send notification about a new arbitrage opportunity"""
        if not self.enable_notifications:
            return
        
        message = self._format_opportunity_message(opportunity)
        
        await asyncio.gather(
            self._send_telegram_message(message),
            self._send_console_message(message),
            return_exceptions=True
        )
    
    async def send_error_notification(self, error: str, context: str = ""):
        """Send notification about an error"""
        if not self.enable_notifications:
            return
        
        message = f"🚨 ERROR: {error}\nContext: {context}"
        
        await asyncio.gather(
            self._send_telegram_message(message),
            self._send_console_message(message),
            return_exceptions=True
        )
    
    async def send_daily_summary(self, summary: Dict):
        """Send daily performance summary"""
        if not self.enable_notifications:
            return
        
        message = self._format_daily_summary(summary)
        
        await asyncio.gather(
            self._send_telegram_message(message),
            self._send_console_message(message),
            return_exceptions=True
        )
    
    def _format_trade_message(self, trade_info: Dict) -> str:
        """Format trade information into a message"""
        profit = trade_info.get('profit', 0)
        profit_percentage = trade_info.get('profit_percentage', 0)
        
        emoji = "✅" if profit > 0 else "❌"
        
        message = f"{emoji} ARBITRAGE TRADE COMPLETED\n\n"
        message += f"Symbol: {trade_info.get('symbol', 'N/A')}\n"
        message += f"Buy Exchange: {trade_info.get('buy_exchange', 'N/A')}\n"
        message += f"Sell Exchange: {trade_info.get('sell_exchange', 'N/A')}\n"
        message += f"Profit: ${profit:.2f}\n"
        message += f"Profit %: {profit_percentage:.2f}%\n"
        message += f"Trade ID: {trade_info.get('trade_id', 'N/A')}"
        
        return message
    
    def _format_opportunity_message(self, opportunity: Dict) -> str:
        """Format arbitrage opportunity into a message"""
        message = "🔍 NEW ARBITRAGE OPPORTUNITY\n\n"
        message += f"Symbol: {opportunity.get('symbol', 'N/A')}\n"
        message += f"Buy Exchange: {opportunity.get('buy_exchange', 'N/A')}\n"
        message += f"Sell Exchange: {opportunity.get('sell_exchange', 'N/A')}\n"
        message += f"Buy Price: ${opportunity.get('buy_price', 0):.4f}\n"
        message += f"Sell Price: ${opportunity.get('sell_price', 0):.4f}\n"
        message += f"Profit %: {opportunity.get('profit_percentage', 0):.2f}%\n"
        message += f"Volume: {opportunity.get('volume', 0):.2f}"
        
        return message
    
    def _format_daily_summary(self, summary: Dict) -> str:
        """Format daily summary into a message"""
        daily_stats = summary.get('daily_stats', {})
        
        message = "📊 DAILY PERFORMANCE SUMMARY\n\n"
        message += f"Total Trades: {daily_stats.get('total_trades', 0)}\n"
        message += f"Successful Trades: {daily_stats.get('successful_trades', 0)}\n"
        message += f"Failed Trades: {daily_stats.get('failed_trades', 0)}\n"
        message += f"Win Rate: {daily_stats.get('win_rate', 0):.1f}%\n"
        message += f"Total Profit: ${daily_stats.get('total_profit', 0):.2f}\n"
        message += f"Total Loss: ${daily_stats.get('total_loss', 0):.2f}\n"
        message += f"Net Profit: ${daily_stats.get('net_profit', 0):.2f}\n"
        message += f"Average Profit: ${daily_stats.get('average_profit', 0):.2f}\n"
        message += f"Active Trades: {summary.get('active_trades', 0)}"
        
        return message
    
    async def _send_telegram_message(self, message: str) -> bool:
        """Send message via Telegram"""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        logger.info("Telegram notification sent successfully")
                        return True
                    else:
                        logger.error(f"Failed to send Telegram notification: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return False
    
    async def _send_console_message(self, message: str) -> bool:
        """Send message to console/log"""
        try:
            logger.info(f"NOTIFICATION: {message}")
            return True
        except Exception as e:
            logger.error(f"Error sending console notification: {e}")
            return False
    
    async def send_startup_notification(self):
        """Send notification when bot starts"""
        message = "🚀 FOREX ARBITRAGE BOT STARTED\n\n"
        message += "Bot is now monitoring for arbitrage opportunities.\n"
        message += f"Monitoring {len(config.trading_pairs)} trading pairs.\n"
        message += f"Connected to {len(config.exchanges)} exchanges."
        
        await asyncio.gather(
            self._send_telegram_message(message),
            self._send_console_message(message),
            return_exceptions=True
        )
    
    async def send_shutdown_notification(self, final_stats: Dict):
        """Send notification when bot shuts down"""
        message = "🛑 FOREX ARBITRAGE BOT STOPPED\n\n"
        message += "Final Statistics:\n"
        message += f"Total Trades: {final_stats.get('total_trades', 0)}\n"
        message += f"Net Profit: ${final_stats.get('net_profit', 0):.2f}\n"
        message += f"Win Rate: {final_stats.get('win_rate', 0):.1f}%"
        
        await asyncio.gather(
            self._send_telegram_message(message),
            self._send_console_message(message),
            return_exceptions=True
        )
    
    async def send_risk_alert(self, risk_metrics: Dict):
        """Send alert when risk thresholds are exceeded"""
        message = "⚠️ RISK ALERT\n\n"
        message += f"Daily Loss: ${risk_metrics.get('daily_loss', 0):.2f}\n"
        message += f"Max Drawdown: {risk_metrics.get('max_drawdown', 0):.2%}\n"
        message += f"Active Trades: {risk_metrics.get('active_trades', 0)}\n"
        message += f"Current Balance: ${risk_metrics.get('current_balance', 0):.2f}"
        
        await asyncio.gather(
            self._send_telegram_message(message),
            self._send_console_message(message),
            return_exceptions=True
        )
    
    def test_notifications(self):
        """Test notification channels"""
        test_message = "🧪 TEST NOTIFICATION\n\nThis is a test message from the Forex Arbitrage Bot."
        
        asyncio.create_task(
            asyncio.gather(
                self._send_telegram_message(test_message),
                self._send_console_message(test_message),
                return_exceptions=True
            )
        )