"""
Start Script for Automated News Call System
Run this to start the daily news calling campaign
"""

import sys
import os
import time
from datetime import datetime

def check_requirements():
    """Check if all requirements are met"""
    print("\nChecking system requirements...\n")
    
    # Check Python version
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8+ required")
        return False
    print(f"✓ Python {version.major}.{version.minor} installed")
    
    # Check dependencies
    required_modules = ['newsapi', 'twilio', 'apscheduler', 'requests']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module} installed")
        except ImportError:
            missing.append(module)
            print(f"✗ {module} NOT installed")
    
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True


def check_configuration():
    """Check if configuration is complete"""
    print("\nChecking configuration...\n")
    
    try:
        import config
        
        # Check API keys
        if not config.NEWS_API_KEY:
            print("✗ NEWS_API_KEY not configured in .env")
            return False
        print("✓ NewsAPI configured")
        
        if not config.TWILIO_ACCOUNT_SID:
            print("✗ Twilio not configured in .env")
            return False
        print("✓ Twilio configured")
        
        # Check recipient
        print(f"✓ Recipient: {config.RECIPIENT_NAME}")
        print(f"✓ Phone: {config.RECIPIENT_PHONE}")
        print(f"✓ Timezone: {config.TIMEZONE}")
        print(f"✓ Call window: {config.CALL_START_HOUR:02d}:{config.CALL_START_MINUTE:02d} - "
              f"{config.CALL_END_HOUR:02d}:{config.CALL_END_MINUTE:02d}")
        print(f"✓ Campaign duration: {config.CONSECUTIVE_DAYS} days")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration error: {str(e)}")
        return False


def check_services():
    """Check if required services are running"""
    print("\nChecking external services...\n")
    
    import config
    import requests
    
    # Check Ollama
    try:
        response = requests.get(f"{config.OLLAMA_API_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print("✓ Ollama is running")
                print(f"  Available models: {', '.join([m.get('name') for m in models])}")
            else:
                print("✗ No models in Ollama")
                print("  Run: ollama pull mistral")
                return False
        else:
            print("✗ Ollama not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Ollama is not running")
        print("  Start it with: ollama serve")
        return False
    except Exception as e:
        print(f"✗ Error checking Ollama: {str(e)}")
        return False
    
    return True


def confirm_start():
    """Get user confirmation before starting"""
    print("\n" + "=" * 80)
    print("CONFIRM SYSTEM START")
    print("=" * 80)
    
    import config
    
    print(f"\nThis will START the automated news calling system:")
    print(f"  • Recipient: {config.RECIPIENT_NAME} ({config.RECIPIENT_PHONE})")
    print(f"  • Schedule: Daily at {config.CALL_START_HOUR:02d}:{config.CALL_START_MINUTE:02d} IST")
    print(f"  • Duration: {config.CONSECUTIVE_DAYS} consecutive days")
    print(f"  • Real calls: {'NO' if config.TEST_MODE else 'YES'}")
    
    if config.TEST_MODE:
        print(f"\n  ⚠️  TEST MODE ENABLED - Calls will be simulated (not real)")
    else:
        print(f"\n  ⚠️  REAL MODE - Actual phone calls will be placed!")
    
    print("\n" + "-" * 80)
    response = input("Proceed? (yes/no): ").strip().lower()
    
    return response in ['yes', 'y']


def start_system():
    """Start the news call system"""
    print("\n" + "=" * 80)
    print("STARTING SYSTEM")
    print("=" * 80)
    
    try:
        from main import NewsCallSystem
        
        print("\nInitializing system...")
        system = NewsCallSystem()
        
        print("Scheduling daily calls...")
        if system.schedule_daily_calls():
            print("✓ System started successfully!")
            
            print("\n" + "=" * 80)
            print("SYSTEM RUNNING")
            print("=" * 80)
            
            status = system.get_system_status()
            print(f"\nStatus: {status['status']}")
            print(f"Recipient: {status['recipient']}")
            print(f"Timezone: {status['timezone']}")
            next_run = status.get('next_run')
            if next_run:
                print(f"Next run: {next_run}")
            
            print("\n" + "-" * 80)
            print("System is running in the background.")
            print("Calls will be placed daily until campaign completes.")
            print("\nMonitor logs:")
            print("  tail -f logs/news_call_system.log")
            print("\nTo stop: Press Ctrl+C")
            print("-" * 80 + "\n")
            
            # Keep system running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\nShutting down system...")
                system.stop()
                print("✓ System stopped")
                print("\nGoodbye!")
                return True
        else:
            print("✗ Failed to schedule calls")
            return False
            
    except Exception as e:
        print(f"✗ Error starting system: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "   AI-DRIVEN AUTOMATED NEWS CALL SYSTEM - LAUNCHER".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Check requirements
    if not check_requirements():
        print("\n✗ Requirements not met. Please install dependencies:")
        print("  pip install -r requirements.txt")
        return 1
    
    # Check configuration
    if not check_configuration():
        print("\n✗ Configuration incomplete. Please set up .env file:")
        print("  cp .env.example .env")
        print("  # Edit .env with your API keys")
        return 1
    
    # Check services
    if not check_services():
        print("\n✗ Required services not running.")
        print("  Start Ollama: ollama serve")
        return 1
    
    print("\n✓ All checks passed!")
    
    # Get confirmation
    if not confirm_start():
        print("\nStartup cancelled.")
        return 0
    
    # Start system
    if start_system():
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
