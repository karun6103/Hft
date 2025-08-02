#!/usr/bin/env python3
"""
Demo script for the Forex Arbitrage Bot
This script simulates the bot's functionality without requiring real API keys
"""

import asyncio
import time
import random
from datetime import datetime
from loguru import logger

# Configure logging for demo
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>\n",
    level="INFO"
)

class DemoExchange:
    """Simulated exchange for demo purposes"""
    
    def __init__(self, name: str, base_price: float):
        self.name = name
        self.base_price = base_price
        self.spread = 0.001  # 0.1% spread
    
    def get_ticker(self, symbol: str):
        """Simulate ticker data"""
        # Add some random variation to prices
        variation = random.uniform(-0.002, 0.002)  # ±0.2% variation
        current_price = self.base_price * (1 + variation)
        
        return {
            'exchange': self.name,
            'symbol': symbol,
            'bid': current_price * (1 - self.spread/2),
            'ask': current_price * (1 + self.spread/2),
            'last': current_price,
            'volume': random.uniform(1000, 10000),
            'timestamp': int(time.time() * 1000)
        }

class DemoArbitrageBot:
    """Demo version of the arbitrage bot"""
    
    def __init__(self):
        self.exchanges = {
            'binance': DemoExchange('binance', 1.2000),  # EUR/USD
            'coinbase': DemoExchange('coinbase', 1.2005),
            'kraken': DemoExchange('kraken', 1.1995)
        }
        self.running = False
        self.stats = {
            'opportunities_found': 0,
            'trades_executed': 0,
            'total_profit': 0.0
        }
    
    async def start(self):
        """Start the demo bot"""
        logger.info("🚀 Starting Forex Arbitrage Bot Demo")
        logger.info("📊 Monitoring 3 exchanges: Binance, Coinbase, Kraken")
        logger.info("💱 Trading pair: EUR/USD")
        logger.info("⏱️  Running for 60 seconds...")
        logger.info("=" * 50)
        
        self.running = True
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < 60:
            await self.check_arbitrage_opportunities()
            await asyncio.sleep(2)  # Check every 2 seconds
        
        self.running = False
        await self.show_final_stats()
    
    async def check_arbitrage_opportunities(self):
        """Check for arbitrage opportunities"""
        symbol = "EUR/USD"
        
        # Get prices from all exchanges
        prices = {}
        for name, exchange in self.exchanges.items():
            ticker = exchange.get_ticker(symbol)
            prices[name] = {
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'spread': ticker['ask'] - ticker['bid']
            }
        
        # Find arbitrage opportunities
        opportunities = self.find_arbitrage_opportunities(prices)
        
        if opportunities:
            for opp in opportunities:
                self.stats['opportunities_found'] += 1
                logger.info(f"🔍 Arbitrage Opportunity Found!")
                logger.info(f"   Buy: {opp['buy_exchange']} @ ${opp['buy_price']:.4f}")
                logger.info(f"   Sell: {opp['sell_exchange']} @ ${opp['sell_price']:.4f}")
                logger.info(f"   Profit: {opp['profit_percentage']:.3f}%")
                
                # Simulate trade execution
                if opp['profit_percentage'] > 0.05:  # Only execute if profit > 0.05%
                    await self.execute_trade(opp)
                else:
                    logger.info("   ⚠️  Profit too small, skipping trade")
                logger.info("")
        else:
            logger.debug("No arbitrage opportunities found")
    
    def find_arbitrage_opportunities(self, prices):
        """Find arbitrage opportunities between exchanges"""
        opportunities = []
        exchanges = list(prices.keys())
        
        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                exchange1 = exchanges[i]
                exchange2 = exchanges[j]
                
                price1 = prices[exchange1]
                price2 = prices[exchange2]
                
                # Check if we can buy on exchange1 and sell on exchange2
                if price1['ask'] < price2['bid']:
                    profit = price2['bid'] - price1['ask']
                    profit_percentage = (profit / price1['ask']) * 100
                    
                    opportunities.append({
                        'buy_exchange': exchange1,
                        'sell_exchange': exchange2,
                        'buy_price': price1['ask'],
                        'sell_price': price2['bid'],
                        'profit': profit,
                        'profit_percentage': profit_percentage
                    })
                
                # Check if we can buy on exchange2 and sell on exchange1
                if price2['ask'] < price1['bid']:
                    profit = price1['bid'] - price2['ask']
                    profit_percentage = (profit / price2['ask']) * 100
                    
                    opportunities.append({
                        'buy_exchange': exchange2,
                        'sell_exchange': exchange1,
                        'buy_price': price2['ask'],
                        'sell_price': price1['bid'],
                        'profit': profit,
                        'profit_percentage': profit_percentage
                    })
        
        return opportunities
    
    async def execute_trade(self, opportunity):
        """Simulate trade execution"""
        logger.info(f"💼 Executing Trade...")
        logger.info(f"   📈 Buying on {opportunity['buy_exchange']}")
        
        # Simulate order execution delay
        await asyncio.sleep(0.1)
        
        logger.info(f"   📉 Selling on {opportunity['sell_exchange']}")
        await asyncio.sleep(0.1)
        
        # Calculate profit (simplified)
        position_size = 1000  # $1000 position
        profit = opportunity['profit'] * position_size
        
        self.stats['trades_executed'] += 1
        self.stats['total_profit'] += profit
        
        logger.info(f"   ✅ Trade completed!")
        logger.info(f"   💰 Profit: ${profit:.2f}")
        logger.info(f"   📊 Total profit: ${self.stats['total_profit']:.2f}")
    
    async def show_final_stats(self):
        """Show final statistics"""
        logger.info("=" * 50)
        logger.info("📊 DEMO COMPLETED - FINAL STATISTICS")
        logger.info("=" * 50)
        logger.info(f"🔍 Opportunities found: {self.stats['opportunities_found']}")
        logger.info(f"💼 Trades executed: {self.stats['trades_executed']}")
        logger.info(f"💰 Total profit: ${self.stats['total_profit']:.2f}")
        
        if self.stats['trades_executed'] > 0:
            avg_profit = self.stats['total_profit'] / self.stats['trades_executed']
            logger.info(f"📈 Average profit per trade: ${avg_profit:.2f}")
        
        logger.info("=" * 50)
        logger.info("🎯 This was a simulation - no real trades were executed")
        logger.info("🔧 To run the real bot, configure API keys in .env file")
        logger.info("📖 See README.md for setup instructions")

async def main():
    """Main demo function"""
    bot = DemoArbitrageBot()
    await bot.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⏹️  Demo stopped by user")
    except Exception as e:
        logger.error(f"Demo error: {e}")