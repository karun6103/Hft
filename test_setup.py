#!/usr/bin/env python3
"""
Test script to verify the Forex Arbitrage Bot setup
"""

import sys
import asyncio
from loguru import logger

def test_imports():
    """Test if all required modules can be imported"""
    logger.info("Testing imports...")
    
    try:
        import config
        logger.success("✓ config module imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import config: {e}")
        return False
    
    try:
        import models
        logger.success("✓ models module imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import models: {e}")
        return False
    
    try:
        import exchange_manager
        logger.success("✓ exchange_manager module imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import exchange_manager: {e}")
        return False
    
    try:
        import risk_manager
        logger.success("✓ risk_manager module imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import risk_manager: {e}")
        return False
    
    try:
        import notification_manager
        logger.success("✓ notification_manager module imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import notification_manager: {e}")
        return False
    
    try:
        import arbitrage_engine
        logger.success("✓ arbitrage_engine module imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import arbitrage_engine: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    logger.info("Testing configuration...")
    
    try:
        from config import config
        
        # Test basic config structure
        assert hasattr(config, 'exchanges'), "Config missing exchanges"
        assert hasattr(config, 'trading_pairs'), "Config missing trading_pairs"
        assert hasattr(config, 'arbitrage'), "Config missing arbitrage settings"
        
        logger.success("✓ Configuration loaded successfully")
        logger.info(f"  - {len(config.exchanges)} exchanges configured")
        logger.info(f"  - {len(config.trading_pairs)} trading pairs configured")
        
        return True
    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False

def test_database():
    """Test database initialization"""
    logger.info("Testing database...")
    
    try:
        from models import DatabaseManager
        
        db = DatabaseManager()
        logger.success("✓ Database initialized successfully")
        
        # Test session creation
        session = db.get_session()
        session.close()
        logger.success("✓ Database session test passed")
        
        return True
    except Exception as e:
        logger.error(f"✗ Database test failed: {e}")
        return False

async def test_notifications():
    """Test notification system"""
    logger.info("Testing notifications...")
    
    try:
        from notification_manager import NotificationManager
        
        notification_manager = NotificationManager()
        logger.success("✓ Notification manager initialized")
        
        # Test console notification
        await notification_manager._send_console_message("Test notification")
        logger.success("✓ Console notification test passed")
        
        return True
    except Exception as e:
        logger.error(f"✗ Notification test failed: {e}")
        return False

def test_risk_manager():
    """Test risk management system"""
    logger.info("Testing risk management...")
    
    try:
        from risk_manager import RiskManager
        
        risk_manager = RiskManager()
        logger.success("✓ Risk manager initialized")
        
        # Test risk metrics
        metrics = risk_manager.get_risk_metrics()
        assert isinstance(metrics, dict), "Risk metrics should be a dictionary"
        logger.success("✓ Risk metrics test passed")
        
        return True
    except Exception as e:
        logger.error(f"✗ Risk management test failed: {e}")
        return False

def test_exchange_manager():
    """Test exchange manager (without actual API calls)"""
    logger.info("Testing exchange manager...")
    
    try:
        from exchange_manager import ExchangeManager
        
        exchange_manager = ExchangeManager()
        logger.success("✓ Exchange manager initialized")
        
        # Test that exchanges dict exists
        assert hasattr(exchange_manager, 'exchanges'), "Exchange manager missing exchanges"
        logger.success("✓ Exchange manager structure test passed")
        
        return True
    except Exception as e:
        logger.error(f"✗ Exchange manager test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("=" * 50)
    logger.info("FOREX ARBITRAGE BOT - SETUP TEST")
    logger.info("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Database Test", test_database),
        ("Risk Manager Test", test_risk_manager),
        ("Exchange Manager Test", test_exchange_manager),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning {test_name}...")
        if test_func():
            passed += 1
        else:
            logger.error(f"{test_name} failed!")
    
    # Test async functions
    logger.info("\nRunning async tests...")
    try:
        asyncio.run(test_notifications())
        passed += 1
        total += 1
    except Exception as e:
        logger.error(f"Async notification test failed: {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"TEST RESULTS: {passed}/{total} tests passed")
    logger.info("=" * 50)
    
    if passed == total:
        logger.success("🎉 All tests passed! The bot is ready to use.")
        logger.info("\nNext steps:")
        logger.info("1. Copy .env.example to .env")
        logger.info("2. Add your exchange API keys to .env")
        logger.info("3. Run: python main.py")
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()