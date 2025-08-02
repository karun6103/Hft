import ccxt
import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Tuple
from loguru import logger
from config import config
from models import DatabaseManager

class ExchangeManager:
    def __init__(self):
        self.exchanges = {}
        self.prices = {}
        self.db = DatabaseManager()
        self._initialize_exchanges()
    
    def _initialize_exchanges(self):
        """Initialize exchange connections"""
        for exchange_name, exchange_config in config.exchanges.items():
            try:
                if exchange_config.api_key and exchange_config.secret_key:
                    exchange_class = getattr(ccxt, exchange_name)
                    self.exchanges[exchange_name] = exchange_class({
                        'apiKey': exchange_config.api_key,
                        'secret': exchange_config.secret_key,
                        'sandbox': exchange_config.sandbox,
                        'rateLimit': exchange_config.rate_limit,
                        'enableRateLimit': True
                    })
                    logger.info(f"Initialized {exchange_name} exchange")
                else:
                    logger.warning(f"No API credentials for {exchange_name}")
            except Exception as e:
                logger.error(f"Failed to initialize {exchange_name}: {e}")
    
    def get_ticker(self, exchange_name: str, symbol: str) -> Optional[Dict]:
        """Get ticker data from exchange"""
        try:
            exchange = self.exchanges.get(exchange_name)
            if not exchange:
                return None
            
            ticker = exchange.fetch_ticker(symbol)
            return {
                'exchange': exchange_name,
                'symbol': symbol,
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'last': ticker['last'],
                'volume': ticker['baseVolume'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            logger.error(f"Error fetching ticker from {exchange_name} for {symbol}: {e}")
            return None
    
    async def get_all_tickers(self, symbol: str) -> Dict[str, Dict]:
        """Get ticker data from all exchanges for a symbol"""
        tickers = {}
        tasks = []
        
        for exchange_name in self.exchanges.keys():
            task = asyncio.create_task(self._async_get_ticker(exchange_name, symbol))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            exchange_name = list(self.exchanges.keys())[i]
            if isinstance(result, Exception):
                logger.error(f"Error getting ticker from {exchange_name}: {result}")
            elif result:
                tickers[exchange_name] = result
                # Store in database
                self.db.add_exchange_price(
                    exchange=exchange_name,
                    pair=symbol,
                    bid=result['bid'],
                    ask=result['ask'],
                    last=result['last'],
                    volume=result['volume']
                )
        
        return tickers
    
    async def _async_get_ticker(self, exchange_name: str, symbol: str) -> Optional[Dict]:
        """Async wrapper for get_ticker"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_ticker, exchange_name, symbol)
    
    def get_balance(self, exchange_name: str, currency: str = 'USD') -> Optional[float]:
        """Get balance for a specific currency on an exchange"""
        try:
            exchange = self.exchanges.get(exchange_name)
            if not exchange:
                return None
            
            balance = exchange.fetch_balance()
            return balance.get(currency, {}).get('free', 0.0)
        except Exception as e:
            logger.error(f"Error fetching balance from {exchange_name}: {e}")
            return None
    
    def place_order(self, exchange_name: str, symbol: str, side: str, 
                   amount: float, price: Optional[float] = None) -> Optional[Dict]:
        """Place an order on an exchange"""
        try:
            exchange = self.exchanges.get(exchange_name)
            if not exchange:
                return None
            
            order_type = 'market' if price is None else 'limit'
            order = exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price
            )
            
            logger.info(f"Placed {side} order on {exchange_name}: {amount} {symbol} at {price or 'market'}")
            return order
        except Exception as e:
            logger.error(f"Error placing order on {exchange_name}: {e}")
            return None
    
    def get_order_status(self, exchange_name: str, order_id: str) -> Optional[Dict]:
        """Get status of an order"""
        try:
            exchange = self.exchanges.get(exchange_name)
            if not exchange:
                return None
            
            return exchange.fetch_order(order_id)
        except Exception as e:
            logger.error(f"Error fetching order status from {exchange_name}: {e}")
            return None
    
    def cancel_order(self, exchange_name: str, order_id: str) -> bool:
        """Cancel an order"""
        try:
            exchange = self.exchanges.get(exchange_name)
            if not exchange:
                return False
            
            exchange.cancel_order(order_id)
            logger.info(f"Cancelled order {order_id} on {exchange_name}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order on {exchange_name}: {e}")
            return False
    
    def get_exchange_info(self, exchange_name: str) -> Optional[Dict]:
        """Get exchange information and trading rules"""
        try:
            exchange = self.exchanges.get(exchange_name)
            if not exchange:
                return None
            
            markets = exchange.load_markets()
            return {
                'name': exchange_name,
                'markets': markets,
                'fees': exchange.fees,
                'limits': exchange.limits
            }
        except Exception as e:
            logger.error(f"Error fetching exchange info from {exchange_name}: {e}")
            return None
    
    def calculate_fees(self, exchange_name: str, symbol: str, amount: float, price: float) -> float:
        """Calculate trading fees for an order"""
        try:
            exchange_info = self.get_exchange_info(exchange_name)
            if not exchange_info:
                return 0.0
            
            market = exchange_info['markets'].get(symbol)
            if not market:
                return 0.0
            
            # Get fee structure
            fees = exchange_info['fees']
            trading_fee = fees.get('trading', {}).get('maker', 0.001)  # Default 0.1%
            
            # Calculate fee based on order value
            order_value = amount * price
            fee = order_value * trading_fee
            
            return fee
        except Exception as e:
            logger.error(f"Error calculating fees for {exchange_name}: {e}")
            return 0.0
    
    def get_best_prices(self, symbol: str) -> Dict[str, Dict]:
        """Get best bid/ask prices from all exchanges for a symbol"""
        best_prices = {}
        
        for exchange_name in self.exchanges.keys():
            ticker = self.get_ticker(exchange_name, symbol)
            if ticker:
                best_prices[exchange_name] = {
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'spread': ticker['ask'] - ticker['bid'],
                    'spread_percentage': ((ticker['ask'] - ticker['bid']) / ticker['bid']) * 100
                }
        
        return best_prices
    
    def find_arbitrage_opportunities(self, symbol: str) -> List[Dict]:
        """Find arbitrage opportunities for a symbol across all exchanges"""
        opportunities = []
        prices = self.get_best_prices(symbol)
        
        if len(prices) < 2:
            return opportunities
        
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
                    
                    if profit_percentage >= config.arbitrage.min_profit_threshold * 100:
                        opportunities.append({
                            'symbol': symbol,
                            'buy_exchange': exchange1,
                            'sell_exchange': exchange2,
                            'buy_price': price1['ask'],
                            'sell_price': price2['bid'],
                            'profit': profit,
                            'profit_percentage': profit_percentage,
                            'volume': min(price1.get('volume', 0), price2.get('volume', 0))
                        })
                
                # Check if we can buy on exchange2 and sell on exchange1
                if price2['ask'] < price1['bid']:
                    profit = price1['bid'] - price2['ask']
                    profit_percentage = (profit / price2['ask']) * 100
                    
                    if profit_percentage >= config.arbitrage.min_profit_threshold * 100:
                        opportunities.append({
                            'symbol': symbol,
                            'buy_exchange': exchange2,
                            'sell_exchange': exchange1,
                            'buy_price': price2['ask'],
                            'sell_price': price1['bid'],
                            'profit': profit,
                            'profit_percentage': profit_percentage,
                            'volume': min(price1.get('volume', 0), price2.get('volume', 0))
                        })
        
        return opportunities