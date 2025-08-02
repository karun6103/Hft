from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional
import json

Base = declarative_base()

class ArbitrageOpportunity(Base):
    __tablename__ = 'arbitrage_opportunities'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    pair = Column(String(20), nullable=False)
    exchange1 = Column(String(50), nullable=False)
    exchange2 = Column(String(50), nullable=False)
    price1 = Column(Float, nullable=False)
    price2 = Column(Float, nullable=False)
    spread = Column(Float, nullable=False)
    profit_percentage = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    executed = Column(Boolean, default=False)
    notes = Column(Text)

class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    pair = Column(String(20), nullable=False)
    exchange_buy = Column(String(50), nullable=False)
    exchange_sell = Column(String(50), nullable=False)
    buy_price = Column(Float, nullable=False)
    sell_price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)
    profit_percentage = Column(Float, nullable=False)
    status = Column(String(20), default='pending')  # pending, executed, failed, cancelled
    fees = Column(Float, default=0.0)
    net_profit = Column(Float, nullable=False)
    execution_time = Column(Float)  # in milliseconds
    notes = Column(Text)

class PerformanceMetrics(Base):
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    total_trades = Column(Integer, default=0)
    successful_trades = Column(Integer, default=0)
    failed_trades = Column(Integer, default=0)
    total_profit = Column(Float, default=0.0)
    total_loss = Column(Float, default=0.0)
    net_profit = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    average_profit = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)

class ExchangePrice(Base):
    __tablename__ = 'exchange_prices'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    exchange = Column(String(50), nullable=False)
    pair = Column(String(20), nullable=False)
    bid = Column(Float, nullable=False)
    ask = Column(Float, nullable=False)
    last = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

class DatabaseManager:
    def __init__(self, db_url: str = "sqlite:///arbitrage_bot.db"):
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()
    
    def add_arbitrage_opportunity(self, pair: str, exchange1: str, exchange2: str, 
                                 price1: float, price2: float, spread: float, 
                                 profit_percentage: float, volume: float, notes: str = None):
        session = self.get_session()
        try:
            opportunity = ArbitrageOpportunity(
                pair=pair,
                exchange1=exchange1,
                exchange2=exchange2,
                price1=price1,
                price2=price2,
                spread=spread,
                profit_percentage=profit_percentage,
                volume=volume,
                notes=notes
            )
            session.add(opportunity)
            session.commit()
            return opportunity.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_trade(self, pair: str, exchange_buy: str, exchange_sell: str,
                  buy_price: float, sell_price: float, quantity: float,
                  profit: float, profit_percentage: float, fees: float = 0.0,
                  execution_time: float = None, notes: str = None):
        session = self.get_session()
        try:
            net_profit = profit - fees
            trade = Trade(
                pair=pair,
                exchange_buy=exchange_buy,
                exchange_sell=exchange_sell,
                buy_price=buy_price,
                sell_price=sell_price,
                quantity=quantity,
                profit=profit,
                profit_percentage=profit_percentage,
                fees=fees,
                net_profit=net_profit,
                execution_time=execution_time,
                notes=notes
            )
            session.add(trade)
            session.commit()
            return trade.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_exchange_price(self, exchange: str, pair: str, bid: float, 
                          ask: float, last: float, volume: float):
        session = self.get_session()
        try:
            price = ExchangePrice(
                exchange=exchange,
                pair=pair,
                bid=bid,
                ask=ask,
                last=last,
                volume=volume
            )
            session.add(price)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_recent_opportunities(self, limit: int = 100):
        session = self.get_session()
        try:
            return session.query(ArbitrageOpportunity).order_by(
                ArbitrageOpportunity.timestamp.desc()
            ).limit(limit).all()
        finally:
            session.close()
    
    def get_recent_trades(self, limit: int = 100):
        session = self.get_session()
        try:
            return session.query(Trade).order_by(
                Trade.timestamp.desc()
            ).limit(limit).all()
        finally:
            session.close()
    
    def get_daily_performance(self, date: datetime):
        session = self.get_session()
        try:
            return session.query(PerformanceMetrics).filter(
                PerformanceMetrics.date >= date
            ).first()
        finally:
            session.close()