import asyncio
import time
from typing import Dict, List, Optional
from loguru import logger
from config import config
from exchange_manager import ExchangeManager
from models import DatabaseManager
from risk_manager import RiskManager
from notification_manager import NotificationManager

class ArbitrageEngine:
    def __init__(self):
        self.exchange_manager = ExchangeManager()
        self.risk_manager = RiskManager()
        self.notification_manager = NotificationManager()
        self.db = DatabaseManager()
        self.running = False
        self.active_trades = {}
        self.daily_stats = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_profit': 0.0,
            'total_loss': 0.0
        }
    
    async def start(self):
        """Start the arbitrage engine"""
        logger.info("Starting Forex Arbitrage Bot...")
        self.running = True
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._monitor_prices()),
            asyncio.create_task(self._check_arbitrage_opportunities()),
            asyncio.create_task(self._monitor_active_trades()),
            asyncio.create_task(self._update_daily_stats())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Shutting down arbitrage engine...")
            self.running = False
        except Exception as e:
            logger.error(f"Error in arbitrage engine: {e}")
            self.running = False
    
    async def _monitor_prices(self):
        """Monitor prices from all exchanges"""
        while self.running:
            try:
                for symbol in config.trading_pairs:
                    tickers = await self.exchange_manager.get_all_tickers(symbol)
                    if tickers:
                        logger.debug(f"Updated prices for {symbol}: {len(tickers)} exchanges")
                
                await asyncio.sleep(config.price_update_interval)
            except Exception as e:
                logger.error(f"Error monitoring prices: {e}")
                await asyncio.sleep(1)
    
    async def _check_arbitrage_opportunities(self):
        """Check for arbitrage opportunities"""
        while self.running:
            try:
                for symbol in config.trading_pairs:
                    opportunities = self.exchange_manager.find_arbitrage_opportunities(symbol)
                    
                    for opportunity in opportunities:
                        if self._should_execute_opportunity(opportunity):
                            await self._execute_arbitrage(opportunity)
                
                await asyncio.sleep(config.arbitrage_check_interval)
            except Exception as e:
                logger.error(f"Error checking arbitrage opportunities: {e}")
                await asyncio.sleep(1)
    
    def _should_execute_opportunity(self, opportunity: Dict) -> bool:
        """Determine if an arbitrage opportunity should be executed"""
        # Check minimum profit threshold
        if opportunity['profit_percentage'] < config.arbitrage.min_profit_threshold * 100:
            return False
        
        # Check risk management rules
        if not self.risk_manager.can_execute_trade(opportunity):
            return False
        
        # Check if we have sufficient balance
        buy_exchange = opportunity['buy_exchange']
        sell_exchange = opportunity['sell_exchange']
        
        buy_balance = self.exchange_manager.get_balance(buy_exchange, 'USD')
        sell_balance = self.exchange_manager.get_balance(sell_exchange, 'USD')
        
        if not buy_balance or not sell_balance:
            return False
        
        # Check if opportunity is still valid (prices haven't moved too much)
        current_prices = self.exchange_manager.get_best_prices(opportunity['symbol'])
        
        if not current_prices.get(buy_exchange) or not current_prices.get(sell_exchange):
            return False
        
        current_buy_price = current_prices[buy_exchange]['ask']
        current_sell_price = current_prices[sell_exchange]['bid']
        
        # Check if prices are still favorable
        if current_buy_price > opportunity['buy_price'] * (1 + config.arbitrage.max_slippage):
            return False
        
        if current_sell_price < opportunity['sell_price'] * (1 - config.arbitrage.max_slippage):
            return False
        
        return True
    
    async def _execute_arbitrage(self, opportunity: Dict):
        """Execute an arbitrage trade"""
        trade_id = f"arb_{int(time.time() * 1000)}"
        
        try:
            logger.info(f"Executing arbitrage trade {trade_id}: {opportunity}")
            
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(opportunity)
            
            # Place buy order
            buy_order = self.exchange_manager.place_order(
                exchange_name=opportunity['buy_exchange'],
                symbol=opportunity['symbol'],
                side='buy',
                amount=position_size,
                price=None  # Market order
            )
            
            if not buy_order:
                logger.error(f"Failed to place buy order for trade {trade_id}")
                return
            
            # Wait for buy order to be filled
            await asyncio.sleep(config.arbitrage.execution_delay)
            
            # Check buy order status
            buy_status = self.exchange_manager.get_order_status(
                opportunity['buy_exchange'], 
                buy_order['id']
            )
            
            if not buy_status or buy_status['status'] != 'closed':
                logger.error(f"Buy order not filled for trade {trade_id}")
                self.exchange_manager.cancel_order(opportunity['buy_exchange'], buy_order['id'])
                return
            
            # Place sell order
            sell_order = self.exchange_manager.place_order(
                exchange_name=opportunity['sell_exchange'],
                symbol=opportunity['symbol'],
                side='sell',
                amount=position_size,
                price=None  # Market order
            )
            
            if not sell_order:
                logger.error(f"Failed to place sell order for trade {trade_id}")
                return
            
            # Wait for sell order to be filled
            await asyncio.sleep(config.arbitrage.execution_delay)
            
            # Check sell order status
            sell_status = self.exchange_manager.get_order_status(
                opportunity['sell_exchange'], 
                sell_order['id']
            )
            
            if not sell_status or sell_status['status'] != 'closed':
                logger.error(f"Sell order not filled for trade {trade_id}")
                self.exchange_manager.cancel_order(opportunity['sell_exchange'], sell_order['id'])
                return
            
            # Calculate actual profit
            actual_buy_price = buy_status['price']
            actual_sell_price = sell_status['price']
            actual_profit = (actual_sell_price - actual_buy_price) * position_size
            
            # Calculate fees
            buy_fees = self.exchange_manager.calculate_fees(
                opportunity['buy_exchange'], 
                opportunity['symbol'], 
                position_size, 
                actual_buy_price
            )
            
            sell_fees = self.exchange_manager.calculate_fees(
                opportunity['sell_exchange'], 
                opportunity['symbol'], 
                position_size, 
                actual_sell_price
            )
            
            total_fees = buy_fees + sell_fees
            net_profit = actual_profit - total_fees
            
            # Record trade in database
            trade_id_db = self.db.add_trade(
                pair=opportunity['symbol'],
                exchange_buy=opportunity['buy_exchange'],
                exchange_sell=opportunity['sell_exchange'],
                buy_price=actual_buy_price,
                sell_price=actual_sell_price,
                quantity=position_size,
                profit=actual_profit,
                profit_percentage=(actual_profit / (actual_buy_price * position_size)) * 100,
                fees=total_fees,
                notes=f"Arbitrage trade {trade_id}"
            )
            
            # Update statistics
            if net_profit > 0:
                self.daily_stats['successful_trades'] += 1
                self.daily_stats['total_profit'] += net_profit
            else:
                self.daily_stats['failed_trades'] += 1
                self.daily_stats['total_loss'] += abs(net_profit)
            
            self.daily_stats['total_trades'] += 1
            
            # Send notification
            await self.notification_manager.send_trade_notification({
                'trade_id': trade_id,
                'symbol': opportunity['symbol'],
                'buy_exchange': opportunity['buy_exchange'],
                'sell_exchange': opportunity['sell_exchange'],
                'profit': net_profit,
                'profit_percentage': (net_profit / (actual_buy_price * position_size)) * 100
            })
            
            logger.info(f"Successfully executed arbitrage trade {trade_id}: Net profit ${net_profit:.2f}")
            
        except Exception as e:
            logger.error(f"Error executing arbitrage trade {trade_id}: {e}")
            self.daily_stats['failed_trades'] += 1
    
    async def _monitor_active_trades(self):
        """Monitor active trades and handle timeouts"""
        while self.running:
            try:
                current_time = time.time()
                expired_trades = []
                
                for trade_id, trade_info in self.active_trades.items():
                    if current_time - trade_info['start_time'] > 30:  # 30 second timeout
                        expired_trades.append(trade_id)
                
                for trade_id in expired_trades:
                    logger.warning(f"Trade {trade_id} timed out, cancelling orders")
                    # Cancel any pending orders
                    del self.active_trades[trade_id]
                
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Error monitoring active trades: {e}")
                await asyncio.sleep(1)
    
    async def _update_daily_stats(self):
        """Update daily statistics"""
        while self.running:
            try:
                # Calculate win rate
                total_trades = self.daily_stats['total_trades']
                if total_trades > 0:
                    win_rate = (self.daily_stats['successful_trades'] / total_trades) * 100
                    self.daily_stats['win_rate'] = win_rate
                
                # Calculate average profit
                successful_trades = self.daily_stats['successful_trades']
                if successful_trades > 0:
                    avg_profit = self.daily_stats['total_profit'] / successful_trades
                    self.daily_stats['average_profit'] = avg_profit
                
                # Calculate net profit
                self.daily_stats['net_profit'] = self.daily_stats['total_profit'] - self.daily_stats['total_loss']
                
                logger.info(f"Daily Stats: {self.daily_stats}")
                
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Error updating daily stats: {e}")
                await asyncio.sleep(1)
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary"""
        return {
            'daily_stats': self.daily_stats,
            'active_trades': len(self.active_trades),
            'risk_metrics': self.risk_manager.get_risk_metrics()
        }
    
    def stop(self):
        """Stop the arbitrage engine"""
        logger.info("Stopping arbitrage engine...")
        self.running = False