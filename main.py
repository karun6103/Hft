#!/usr/bin/env python3
"""
Forex Arbitrage Bot
A high-frequency trading bot that identifies and executes arbitrage opportunities
across multiple cryptocurrency exchanges.
"""

import asyncio
import signal
import sys
from loguru import logger
from config import config
from arbitrage_engine import ArbitrageEngine
from notification_manager import NotificationManager

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format=config.logging.format,
    level=config.logging.level,
    colorize=True
)
logger.add(
    config.logging.file,
    format=config.logging.format,
    level=config.logging.level,
    rotation="1 day",
    retention="30 days"
)

class ForexArbitrageBot:
    def __init__(self):
        self.engine = ArbitrageEngine()
        self.notification_manager = NotificationManager()
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    async def start(self):
        """Start the forex arbitrage bot"""
        try:
            logger.info("=" * 50)
            logger.info("FOREX ARBITRAGE BOT STARTING")
            logger.info("=" * 50)
            
            # Send startup notification
            await self.notification_manager.send_startup_notification()
            
            # Start the arbitrage engine
            self.running = True
            await self.engine.start()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Fatal error in arbitrage bot: {e}")
            await self.notification_manager.send_error_notification(
                str(e), "Main bot loop"
            )
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the forex arbitrage bot"""
        if not self.running:
            return
        
        logger.info("Stopping Forex Arbitrage Bot...")
        self.running = False
        
        # Stop the arbitrage engine
        self.engine.stop()
        
        # Get final statistics
        final_stats = self.engine.get_performance_summary()
        
        # Send shutdown notification
        await self.notification_manager.send_shutdown_notification(final_stats)
        
        logger.info("=" * 50)
        logger.info("FOREX ARBITRAGE BOT STOPPED")
        logger.info("=" * 50)
        
        # Log final statistics
        logger.info("Final Performance Summary:")
        logger.info(f"  Total Trades: {final_stats['daily_stats']['total_trades']}")
        logger.info(f"  Successful Trades: {final_stats['daily_stats']['successful_trades']}")
        logger.info(f"  Failed Trades: {final_stats['daily_stats']['failed_trades']}")
        logger.info(f"  Win Rate: {final_stats['daily_stats'].get('win_rate', 0):.1f}%")
        logger.info(f"  Net Profit: ${final_stats['daily_stats'].get('net_profit', 0):.2f}")
        logger.info(f"  Active Trades: {final_stats['active_trades']}")

async def main():
    """Main entry point"""
    bot = ForexArbitrageBot()
    await bot.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)