"""
Main Application Module
Orchestrates the news call system - integrating all components
"""

import logging
import logging.handlers
import os
from datetime import datetime
import pytz
import config

# Setup logging
def setup_logging():
    """Configure logging for the application"""
    os.makedirs(config.LOG_DIR, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Initialize logging
logger = setup_logging()


class NewsCallSystem:
    """Main orchestrator for the automated news call system"""
    
    def __init__(self):
        logger.info("=" * 80)
        logger.info("Initializing AI-Driven Automated News Call System")
        logger.info("=" * 80)
        
        # Import components
        from news_fetcher import NewsFetcher
        from ai_summarizer import AISummarizer
        from tts_processor import get_tts_processor
        from call_service import CallService, MockCallService
        from scheduler import NewsCallScheduler
        
        self.news_fetcher = NewsFetcher()
        self.ai_summarizer = AISummarizer()
        self.tts_processor = get_tts_processor()
        
        if config.TEST_MODE or config.DRY_RUN:
            self.call_service = MockCallService()
            logger.info("Using MOCK call service (test mode)")
        else:
            self.call_service = CallService()
        
        self.scheduler = NewsCallScheduler()
        self.call_count = 0
        
        logger.info("System initialization complete")
        self._log_configuration()
    
    def _log_configuration(self):
        """Log system configuration"""
        logger.info("\n" + "=" * 80)
        logger.info("SYSTEM CONFIGURATION")
        logger.info("=" * 80)
        logger.info(f"Recipient: {config.RECIPIENT_NAME} ({config.RECIPIENT_PHONE})")
        logger.info(f"Timezone: {config.TIMEZONE}")
        logger.info(f"Call Window: {config.CALL_START_HOUR:02d}:{config.CALL_START_MINUTE:02d} - "
                   f"{config.CALL_END_HOUR:02d}:{config.CALL_END_MINUTE:02d}")
        logger.info(f"Call Duration: {config.CALL_DURATION_MIN}-{config.CALL_DURATION_MAX} seconds")
        logger.info(f"Consecutive Days: {config.CONSECUTIVE_DAYS}")
        logger.info(f"News Source: NewsAPI (Top 5 articles)")
        logger.info(f"AI Model: {config.OLLAMA_MODEL}")
        logger.info(f"TTS Engine: {config.TTS_ENGINE}")
        logger.info(f"Debug Mode: {config.DEBUG_MODE}")
        logger.info(f"Test Mode: {config.TEST_MODE}")
        logger.info(f"Dry Run: {config.DRY_RUN}")
        logger.info("=" * 80 + "\n")
    
    def execute_news_call(self):
        """
        Main function that orchestrates the news call process
        This is called daily by the scheduler
        """
        self.call_count += 1
        
        logger.info(f"\n{'=' * 80}")
        logger.info(f"NEWS CALL EXECUTION #{self.call_count}")
        logger.info(f"Time: {datetime.now(pytz.timezone(config.TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        logger.info(f"{'=' * 80}\n")
        
        try:
            # Step 1: Fetch news articles
            logger.info("[1/5] Fetching top news articles...")
            articles = self.news_fetcher.fetch_top_news()
            
            if not articles:
                logger.error("Failed to fetch news. Aborting call.")
                return False
            
            logger.info(f"✓ Fetched {len(articles)} articles")
            
            # Log article titles
            for article in articles:
                logger.debug(f"  - {article['title'][:60]}...")
            
            # Step 2: Summarize articles
            logger.info("\n[2/5] Summarizing articles with AI...")
            summarized_articles = self.ai_summarizer.summarize_news_articles(articles)
            logger.info(f"✓ Summarized {len(summarized_articles)} articles")
            
            # Step 3: Create voice script
            logger.info("\n[3/5] Creating voice script...")
            voice_script = self.ai_summarizer.create_voice_script(summarized_articles)
            
            # Estimate duration
            estimated_duration = self.ai_summarizer.estimate_read_time(voice_script)
            logger.info(f"✓ Voice script created (estimated duration: {estimated_duration:.1f}s)")
            
            # Check duration constraints
            if estimated_duration < config.CALL_DURATION_MIN or estimated_duration > config.CALL_DURATION_MAX:
                logger.warning(f"Duration {estimated_duration:.1f}s outside target range "
                             f"({config.CALL_DURATION_MIN}-{config.CALL_DURATION_MAX}s)")
                # Could adjust script here if needed
            
            # Step 4: Generate audio
            logger.info("\n[4/5] Converting text to speech...")
            audio_file = self.tts_processor.text_to_speech(
                voice_script,
                output_file=f"news_call_{self.call_count}.wav"
            )
            
            if not audio_file:
                logger.error("Failed to generate audio. Aborting call.")
                return False
            
            logger.info(f"✓ Audio generated: {audio_file}")
            
            # Step 5: Place call
            logger.info("\n[5/5] Placing voice call...")
            call_record = self.call_service.place_call(audio_file, is_test=config.TEST_MODE)
            
            if call_record:
                logger.info(f"✓ Call placed successfully!")
                logger.info(f"  Call SID: {call_record.get('call_sid')}")
                logger.info(f"  Status: {call_record.get('status')}")
                return True
            else:
                logger.error("Failed to place call")
                return False
            
        except Exception as e:
            logger.error(f"Error during news call execution: {str(e)}", exc_info=True)
            return False
        
        finally:
            logger.info(f"\n{'=' * 80}\n")
    
    def schedule_daily_calls(self) -> bool:
        """
        Schedule daily calls for the specified number of days
        
        Returns:
            True if scheduling successful
        """
        logger.info("Scheduling daily news calls...")
        
        # Schedule the daily call at the specified time
        success = self.scheduler.schedule_daily_call(self.execute_news_call)
        
        if success:
            self.scheduler.start()
            logger.info("Daily call scheduling activated")
            return True
        else:
            logger.error("Failed to schedule daily calls")
            return False
    
    def test_call(self) -> bool:
        """
        Execute a test call immediately to verify system setup
        Useful for validating all components before running the scheduler
        
        Returns:
            True if test call successful
        """
        logger.info("\n*** EXECUTING TEST CALL ***\n")
        
        # Temporarily set test mode
        original_test_mode = config.TEST_MODE
        config.TEST_MODE = True
        
        result = self.execute_news_call()
        
        config.TEST_MODE = original_test_mode
        
        return result
    
    def get_system_status(self) -> dict:
        """Get current system status"""
        return {
            "status": "running" if self.scheduler.scheduler.running else "stopped",
            "calls_executed": self.call_count,
            "calls_remaining": config.CONSECUTIVE_DAYS - self.call_count,
            "next_run": str(self.scheduler.get_next_run_time()),
            "recipient": f"{config.RECIPIENT_NAME} ({config.RECIPIENT_PHONE})",
            "timezone": config.TIMEZONE,
            "news_api_configured": bool(config.NEWS_API_KEY),
            "twilio_configured": bool(config.TWILIO_ACCOUNT_SID)
        }
    
    def run_now(self) -> bool:
        """Execute a news call immediately (for manual testing)"""
        logger.info("\n*** EXECUTING MANUAL NEWS CALL ***\n")
        return self.execute_news_call()
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.stop()
        logger.info("System stopped")


def main():
    """
    Main entry point for the application
    
    Usage:
        python main.py  # Start scheduler for automated calls
    """
    try:
        # Create system instance
        system = NewsCallSystem()
        
        # Show usage options
        logger.info("\n" + "=" * 80)
        logger.info("SYSTEM READY")
        logger.info("=" * 80)
        logger.info("\nTo use the system:")
        logger.info("1. To start automated scheduling:")
        logger.info("   system.schedule_daily_calls()")
        logger.info("\n2. To execute a test call immediately:")
        logger.info("   system.test_call()")
        logger.info("\n3. To manually trigger a call:")
        logger.info("   system.run_now()")
        logger.info("\n4. To check system status:")
        logger.info("   system.get_system_status()")
        logger.info("\n5. To stop the system:")
        logger.info("   system.stop()")
        logger.info("=" * 80 + "\n")
        
        # Uncomment to auto-start:
        # system.schedule_daily_calls()
        # import time
        # while True:
        #     time.sleep(1)
        
        return system
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        return None


if __name__ == "__main__":
    system = main()
    
    # Keep the application running
    if system:
        try:
            import time
            logger.info("System is ready. Press Ctrl+C to exit.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nShutting down...")
            system.stop()
