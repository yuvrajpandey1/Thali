"""
Test Script for News Call System
Run this to verify all components are working correctly
"""

import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_imports():
    """Test if all required modules can be imported"""
    print("\n" + "=" * 80)
    print("TEST 1: Checking Dependencies")
    print("=" * 80)
    
    modules = [
        ('newsapi', 'NewsAPI'),
        ('requests', 'Requests'),
        ('dotenv', 'Python-Dotenv'),
        ('twilio', 'Twilio'),
        ('apscheduler', 'APScheduler'),
        ('pytz', 'Pytz'),
    ]
    
    failed = []
    
    for module, display_name in modules:
        try:
            __import__(module)
            print(f"✓ {display_name}")
        except ImportError as e:
            print(f"✗ {display_name}: {str(e)}")
            failed.append(display_name)
    
    if failed:
        print(f"\n⚠️  Missing: {', '.join(failed)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("\n✓ All dependencies installed!")
    return True


def test_config():
    """Test if configuration loads correctly"""
    print("\n" + "=" * 80)
    print("TEST 2: Configuration Loading")
    print("=" * 80)
    
    try:
        import config
        
        print(f"✓ Config module loaded")
        print(f"  • Recipient: {config.RECIPIENT_NAME}")
        print(f"  • Phone: {config.RECIPIENT_PHONE}")
        print(f"  • Timezone: {config.TIMEZONE}")
        print(f"  • Call time: {config.CALL_START_HOUR:02d}:{config.CALL_START_MINUTE:02d}")
        print(f"  • Duration: {config.CALL_DURATION_MIN}-{config.CALL_DURATION_MAX}s")
        print(f"  • Days: {config.CONSECUTIVE_DAYS}")
        print(f"  • Test mode: {config.TEST_MODE}")
        
        # Check API keys
        if config.NEWS_API_KEY:
            print(f"✓ NewsAPI key configured")
        else:
            print(f"✗ NewsAPI key missing (set in .env)")
        
        if config.TWILIO_ACCOUNT_SID:
            print(f"✓ Twilio configured")
        else:
            print(f"✗ Twilio not configured (set in .env)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error loading config: {str(e)}")
        return False


def test_news_fetcher():
    """Test news fetching"""
    print("\n" + "=" * 80)
    print("TEST 3: News Fetcher")
    print("=" * 80)
    
    try:
        from news_fetcher import NewsFetcher
        
        fetcher = NewsFetcher()
        print("✓ NewsFetcher initialized")
        
        print("Attempting to fetch news...")
        articles = fetcher.fetch_top_news()
        
        if articles:
            print(f"✓ Successfully fetched {len(articles)} articles")
            for i, article in enumerate(articles, 1):
                print(f"  {i}. {article['title'][:60]}...")
            return True
        else:
            print("✗ No articles fetched")
            return False
            
    except Exception as e:
        print(f"✗ Error in news fetcher: {str(e)}")
        return False


def test_ollama():
    """Test Ollama connection"""
    print("\n" + "=" * 80)
    print("TEST 4: Ollama Connection (Local LLM)")
    print("=" * 80)
    
    try:
        import requests
        import config
        
        response = requests.get(f"{config.OLLAMA_API_URL}/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print(f"✓ Ollama is running")
                print(f"✓ Available models:")
                for model in models:
                    print(f"  • {model.get('name')}")
                return True
            else:
                print("✗ No models found. Run: ollama pull mistral")
                return False
        else:
            print(f"✗ Ollama API error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to Ollama")
        print(f"  Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"✗ Error testing Ollama: {str(e)}")
        return False


def test_summarizer():
    """Test AI summarization"""
    print("\n" + "=" * 80)
    print("TEST 5: AI Summarizer")
    print("=" * 80)
    
    try:
        from ai_summarizer import AISummarizer
        
        summarizer = AISummarizer()
        print("✓ AISummarizer initialized")
        
        # Test with sample text
        test_title = "Scientists Discover New Element"
        test_content = "Researchers announced the discovery of a new chemical element that could revolutionize battery technology. The element has properties never before seen in nature."
        
        print("Testing summarization...")
        summary = summarizer.summarize_article(test_title, test_content)
        
        if summary:
            print(f"✓ Summarization successful")
            print(f"  Summary: {summary}")
            return True
        else:
            print("✗ Summarization failed")
            return False
            
    except Exception as e:
        print(f"✗ Error in summarizer: {str(e)}")
        return False


def test_tts():
    """Test Text-to-Speech"""
    print("\n" + "=" * 80)
    print("TEST 6: Text-to-Speech (Coqui TTS)")
    print("=" * 80)
    
    try:
        from tts_processor import get_tts_processor
        
        processor = get_tts_processor()
        print("✓ TTS processor initialized")
        
        test_text = "Good morning. This is a test message for the automated news call system."
        
        print("Generating audio...")
        audio_file = processor.text_to_speech(test_text, "test_audio.wav")
        
        if audio_file:
            print(f"✓ Audio generated successfully")
            print(f"  File: {audio_file}")
            return True
        else:
            print("✗ Audio generation failed")
            print("  Check that FFmpeg is installed")
            return False
            
    except Exception as e:
        print(f"✗ Error in TTS: {str(e)}")
        return False


def test_twilio():
    """Test Twilio configuration"""
    print("\n" + "=" * 80)
    print("TEST 7: Twilio Configuration")
    print("=" * 80)
    
    try:
        import config
        
        if config.TWILIO_ACCOUNT_SID and config.TWILIO_AUTH_TOKEN:
            print("✓ Twilio credentials configured")
            print(f"  Account SID: {config.TWILIO_ACCOUNT_SID[:10]}...")
            print(f"  Phone: {config.TWILIO_PHONE_NUMBER}")
            print("✓ Ready to make calls")
            return True
        else:
            print("✗ Twilio credentials missing")
            print("  Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN in .env")
            return False
            
    except Exception as e:
        print(f"✗ Error checking Twilio: {str(e)}")
        return False


def test_scheduler():
    """Test scheduler initialization"""
    print("\n" + "=" * 80)
    print("TEST 8: Scheduler")
    print("=" * 80)
    
    try:
        from scheduler import NewsCallScheduler
        
        scheduler = NewsCallScheduler()
        print("✓ Scheduler initialized")
        print(f"  Timezone: {scheduler.timezone}")
        print(f"  Call time: {scheduler.start_hour:02d}:{scheduler.start_minute:02d}")
        print(f"  Max calls: {scheduler.max_calls}")
        return True
        
    except Exception as e:
        print(f"✗ Error in scheduler: {str(e)}")
        return False


def test_system():
    """Test full system initialization"""
    print("\n" + "=" * 80)
    print("TEST 9: Full System Initialization")
    print("=" * 80)
    
    try:
        from main import NewsCallSystem
        
        system = NewsCallSystem()
        print("✓ NewsCallSystem initialized successfully")
        
        # Get system status
        status = system.get_system_status()
        print("\nSystem Status:")
        for key, value in status.items():
            print(f"  • {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error initializing system: {str(e)}")
        return False


def run_all_tests():
    """Run all tests and generate report"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "   AI-DRIVEN AUTOMATED NEWS CALL SYSTEM - DIAGNOSTIC TEST".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    tests = [
        ("Dependencies", test_imports),
        ("Configuration", test_config),
        ("News Fetcher", test_news_fetcher),
        ("Ollama (LLM)", test_ollama),
        ("AI Summarizer", test_summarizer),
        ("Text-to-Speech", test_tts),
        ("Twilio", test_twilio),
        ("Scheduler", test_scheduler),
        ("Full System", test_system),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "🎉 " * 20)
        print("ALL TESTS PASSED! System is ready to go.")
        print("🎉 " * 20)
        print("\nNext steps:")
        print("1. Make sure TEST_MODE=True in .env to test without real calls")
        print("2. Run: python -c \"from main import NewsCallSystem; NewsCallSystem().test_call()\"")
        print("3. When ready, set TEST_MODE=False and run: python start_scheduler.py")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. See details above.")
        print("\nTroubleshooting:")
        print("- Check SETUP_GUIDE.md for installation help")
        print("- Verify all prerequisite services are running (Ollama, etc.)")
        print("- Check .env file has correct API keys")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
