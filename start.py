#!/usr/bin/env python3
"""
Startup script for the Forex Arbitrage Bot
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_environment():
    """Check if environment is properly set up"""
    print("🔍 Checking environment...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  .env file not found!")
        print("📝 Creating .env from template...")
        if Path(".env.example").exists():
            subprocess.run(["cp", ".env.example", ".env"])
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your API keys before running the bot")
            return False
        else:
            print("❌ .env.example not found!")
            return False
    
    # Check if requirements are installed
    try:
        import ccxt
        import fastapi
        import loguru
        print("✅ All required packages are installed")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("📦 Installing requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return False
    
    return True

def run_tests():
    """Run setup tests"""
    print("🧪 Running setup tests...")
    result = subprocess.run([sys.executable, "test_setup.py"])
    return result.returncode == 0

def start_bot():
    """Start the arbitrage bot"""
    print("🚀 Starting Forex Arbitrage Bot...")
    subprocess.run([sys.executable, "main.py"])

def start_dashboard():
    """Start the web dashboard"""
    print("📊 Starting Web Dashboard...")
    print("🌐 Dashboard will be available at: http://localhost:8000")
    subprocess.run([sys.executable, "web_dashboard.py"])

def main():
    parser = argparse.ArgumentParser(description="Forex Arbitrage Bot Startup")
    parser.add_argument("--mode", choices=["bot", "dashboard", "test"], 
                       default="bot", help="Mode to run (default: bot)")
    parser.add_argument("--skip-tests", action="store_true", 
                       help="Skip setup tests")
    parser.add_argument("--check-only", action="store_true", 
                       help="Only check environment and run tests")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("🚀 FOREX ARBITRAGE BOT STARTUP")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed!")
        print("Please fix the issues above and try again.")
        sys.exit(1)
    
    # Run tests unless skipped
    if not args.skip_tests:
        if not run_tests():
            print("\n❌ Setup tests failed!")
            print("Please fix the issues above and try again.")
            sys.exit(1)
    
    if args.check_only:
        print("\n✅ Environment check and tests completed successfully!")
        return
    
    # Start the appropriate mode
    if args.mode == "bot":
        start_bot()
    elif args.mode == "dashboard":
        start_dashboard()
    elif args.mode == "test":
        run_tests()

if __name__ == "__main__":
    main()