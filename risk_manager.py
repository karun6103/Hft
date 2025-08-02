import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger
from config import config

class RiskManager:
    def __init__(self):
        self.daily_loss = 0.0
        self.daily_trades = 0
        self.active_trades = []
        self.max_drawdown = 0.0
        self.peak_balance = 0.0
        self.current_balance = 0.0
        self.last_reset = datetime.now().date()
    
    def can_execute_trade(self, opportunity: Dict) -> bool:
        """Check if a trade can be executed based on risk management rules"""
        # Reset daily counters if it's a new day
        self._reset_daily_counters()
        
        # Check daily loss limit
        if self.daily_loss >= config.max_daily_loss:
            logger.warning(f"Daily loss limit reached: ${self.daily_loss:.2f}")
            return False
        
        # Check maximum concurrent trades
        if len(self.active_trades) >= config.max_concurrent_trades:
            logger.warning(f"Maximum concurrent trades reached: {len(self.active_trades)}")
            return False
        
        # Check drawdown limit
        if self.max_drawdown >= 0.1:  # 10% maximum drawdown
            logger.warning(f"Maximum drawdown reached: {self.max_drawdown:.2%}")
            return False
        
        # Check if opportunity meets minimum profit requirements
        if opportunity['profit_percentage'] < config.arbitrage.min_profit_threshold * 100:
            return False
        
        # Check if spread is reasonable
        spread_percentage = opportunity['profit_percentage']
        if spread_percentage > 5.0:  # Suspiciously high spread
            logger.warning(f"Suspiciously high spread detected: {spread_percentage:.2f}%")
            return False
        
        return True
    
    def calculate_position_size(self, opportunity: Dict) -> float:
        """Calculate position size based on risk management rules"""
        # Get available balance (assuming USD balance)
        available_balance = self._get_available_balance()
        
        # Calculate risk amount based on risk per trade
        risk_amount = available_balance * config.arbitrage.risk_per_trade
        
        # Calculate position size based on potential loss
        potential_loss_percentage = 0.02  # Assume 2% potential loss
        position_size = risk_amount / potential_loss_percentage
        
        # Limit position size to maximum allowed
        max_position = config.arbitrage.max_position_size
        position_size = min(position_size, max_position)
        
        # Ensure position size doesn't exceed available balance
        position_size = min(position_size, available_balance * 0.8)  # Use 80% of balance
        
        # Round to appropriate decimal places
        position_size = round(position_size, 2)
        
        logger.info(f"Calculated position size: ${position_size:.2f}")
        return position_size
    
    def record_trade(self, trade_info: Dict):
        """Record a completed trade for risk analysis"""
        self.daily_trades += 1
        
        if trade_info['profit'] > 0:
            # Profitable trade
            self.current_balance += trade_info['profit']
            self.peak_balance = max(self.peak_balance, self.current_balance)
        else:
            # Losing trade
            loss = abs(trade_info['profit'])
            self.daily_loss += loss
            self.current_balance -= loss
            
            # Update drawdown
            if self.peak_balance > 0:
                current_drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
                self.max_drawdown = max(self.max_drawdown, current_drawdown)
        
        # Remove from active trades
        trade_id = trade_info.get('trade_id')
        if trade_id:
            self.active_trades = [t for t in self.active_trades if t['trade_id'] != trade_id]
    
    def add_active_trade(self, trade_info: Dict):
        """Add a new active trade"""
        self.active_trades.append({
            'trade_id': trade_info.get('trade_id'),
            'start_time': time.time(),
            'symbol': trade_info.get('symbol'),
            'buy_exchange': trade_info.get('buy_exchange'),
            'sell_exchange': trade_info.get('sell_exchange'),
            'position_size': trade_info.get('position_size'),
            'expected_profit': trade_info.get('expected_profit')
        })
    
    def _reset_daily_counters(self):
        """Reset daily counters if it's a new day"""
        today = datetime.now().date()
        if today > self.last_reset:
            self.daily_loss = 0.0
            self.daily_trades = 0
            self.last_reset = today
            logger.info("Reset daily risk management counters")
    
    def _get_available_balance(self) -> float:
        """Get available balance for trading"""
        # This would typically fetch from exchange manager
        # For now, return a default value
        return 10000.0  # $10,000 default balance
    
    def get_risk_metrics(self) -> Dict:
        """Get current risk metrics"""
        return {
            'daily_loss': self.daily_loss,
            'daily_trades': self.daily_trades,
            'active_trades': len(self.active_trades),
            'max_drawdown': self.max_drawdown,
            'current_balance': self.current_balance,
            'peak_balance': self.peak_balance,
            'daily_loss_limit': config.max_daily_loss,
            'max_concurrent_trades': config.max_concurrent_trades
        }
    
    def check_stop_loss(self, trade_info: Dict) -> bool:
        """Check if stop loss should be triggered"""
        if trade_info['profit_percentage'] < -config.stop_loss_percentage * 100:
            logger.warning(f"Stop loss triggered for trade {trade_info.get('trade_id')}")
            return True
        return False
    
    def calculate_risk_reward_ratio(self, opportunity: Dict) -> float:
        """Calculate risk/reward ratio for an opportunity"""
        potential_profit = opportunity['profit_percentage']
        potential_loss = 2.0  # Assume 2% potential loss
        
        if potential_loss == 0:
            return 0.0
        
        return potential_profit / potential_loss
    
    def should_skip_opportunity(self, opportunity: Dict) -> bool:
        """Determine if an opportunity should be skipped based on risk analysis"""
        # Check risk/reward ratio
        risk_reward_ratio = self.calculate_risk_reward_ratio(opportunity)
        if risk_reward_ratio < 1.5:  # Minimum 1.5:1 risk/reward ratio
            logger.info(f"Risk/reward ratio too low: {risk_reward_ratio:.2f}")
            return True
        
        # Check if we've had too many consecutive losses
        recent_trades = self._get_recent_trades(10)
        if len(recent_trades) >= 3:
            recent_losses = sum(1 for trade in recent_trades[-3:] if trade['profit'] < 0)
            if recent_losses >= 3:
                logger.warning("Too many consecutive losses, skipping opportunity")
                return True
        
        return False
    
    def _get_recent_trades(self, count: int) -> List[Dict]:
        """Get recent trades for analysis"""
        # This would typically fetch from database
        # For now, return empty list
        return []
    
    def update_balance(self, new_balance: float):
        """Update current balance"""
        self.current_balance = new_balance
        self.peak_balance = max(self.peak_balance, new_balance)
    
    def get_position_sizing_recommendation(self, opportunity: Dict) -> Dict:
        """Get position sizing recommendation"""
        position_size = self.calculate_position_size(opportunity)
        risk_amount = position_size * 0.02  # 2% risk
        
        return {
            'recommended_position_size': position_size,
            'risk_amount': risk_amount,
            'max_position_size': config.arbitrage.max_position_size,
            'available_balance': self._get_available_balance(),
            'risk_percentage': config.arbitrage.risk_per_trade * 100
        }