"""
Scheduler Module
Handles scheduling of daily news calls at specified time window
"""

import logging
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable, Optional
import config

logger = logging.getLogger(__name__)


class NewsCallScheduler:
    """Manages scheduling of daily news call campaigns"""
    
    def __init__(self):
        self.timezone = pytz.timezone(config.TIMEZONE)
        self.scheduler = BackgroundScheduler(timezone=str(self.timezone))
        self.call_count = 0
        self.max_calls = config.CONSECUTIVE_DAYS
        self.start_hour = config.CALL_START_HOUR
        self.start_minute = config.CALL_START_MINUTE
        self.job_id = None
    
    def schedule_daily_call(self, callback_func: Callable) -> bool:
        """
        Schedule a daily call during the specified time window
        
        Args:
            callback_func: Function to call daily (should handle the news call logic)
            
        Returns:
            True if scheduled successfully, False otherwise
        """
        try:
            logger.info(f"Scheduling daily calls at {self.start_hour:02d}:{self.start_minute:02d} {config.TIMEZONE}")
            logger.info(f"Calls will run for {self.max_calls} consecutive days")
            
            # Create a wrapper function that respects the daily limit
            def wrapper_callback():
                if self.call_count < self.max_calls:
                    self.call_count += 1
                    logger.info(f"Executing call {self.call_count}/{self.max_calls}")
                    
                    try:
                        callback_func()
                    except Exception as e:
                        logger.error(f"Error executing callback: {str(e)}", exc_info=True)
                else:
                    logger.info(f"All {self.max_calls} calls completed. Job reached limit.")
                    # Optionally remove the job
                    # self.scheduler.remove_job(self.job_id)
            
            # Schedule using cron trigger for daily execution at specific time
            self.job_id = self.scheduler.add_job(
                wrapper_callback,
                trigger=CronTrigger(
                    hour=self.start_hour,
                    minute=self.start_minute,
                    timezone=str(self.timezone)
                ),
                id="daily_news_call",
                replace_existing=True
            )
            
            logger.info("Daily call scheduled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling daily call: {str(e)}")
            return False
    
    def schedule_window_call(self, callback_func: Callable, randomize: bool = True) -> bool:
        """
        Schedule call within a time window (11:00 AM - 11:30 AM)
        Can randomize within the window for natural variation
        
        Args:
            callback_func: Function to execute
            randomize: If True, call at random time within window
            
        Returns:
            True if scheduled successfully
        """
        try:
            if randomize:
                import random
                minute_offset = random.randint(0, 30)
                scheduled_minute = (self.start_minute + minute_offset) % 60
                
                logger.info(f"Scheduling call with randomized timing in window")
                logger.info(f"Time window: {self.start_hour}:{self.start_minute:02d} - {config.CALL_END_HOUR}:{config.CALL_END_MINUTE:02d}")
            else:
                scheduled_minute = self.start_minute
                logger.info(f"Scheduling call at fixed time: {self.start_hour}:{scheduled_minute:02d}")
            
            # Create wrapper for daily limit
            def wrapper_callback():
                if self.call_count < self.max_calls:
                    self.call_count += 1
                    logger.info(f"Executing call {self.call_count}/{self.max_calls}")
                    
                    try:
                        callback_func()
                    except Exception as e:
                        logger.error(f"Error executing callback: {str(e)}", exc_info=True)
            
            self.job_id = self.scheduler.add_job(
                wrapper_callback,
                trigger=CronTrigger(
                    hour=self.start_hour,
                    minute=scheduled_minute,
                    timezone=str(self.timezone)
                ),
                id="daily_news_call_window"
            )
            
            logger.info("Window-based call scheduled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling window call: {str(e)}")
            return False
    
    def schedule_interval_call(self, callback_func: Callable, 
                              days: int = 1, hours: int = 0, minutes: int = 0) -> bool:
        """
        Schedule call at regular intervals
        
        Args:
            callback_func: Function to execute
            days: Days interval
            hours: Hours interval
            minutes: Minutes interval
            
        Returns:
            True if scheduled successfully
        """
        try:
            logger.info(f"Scheduling call every {days}d {hours}h {minutes}m")
            
            def wrapper_callback():
                if self.call_count < self.max_calls:
                    self.call_count += 1
                    logger.info(f"Executing call {self.call_count}/{self.max_calls}")
                    
                    try:
                        callback_func()
                    except Exception as e:
                        logger.error(f"Error executing callback: {str(e)}", exc_info=True)
            
            # Use interval trigger
            from apscheduler.triggers.interval import IntervalTrigger
            
            self.job_id = self.scheduler.add_job(
                wrapper_callback,
                trigger=IntervalTrigger(
                    days=days,
                    hours=hours,
                    minutes=minutes,
                    timezone=str(self.timezone)
                ),
                id="interval_news_call"
            )
            
            logger.info("Interval-based call scheduled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling interval call: {str(e)}")
            return False
    
    def start(self) -> bool:
        """
        Start the scheduler
        
        Returns:
            True if started successfully
        """
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("Scheduler started")
                return True
            else:
                logger.warning("Scheduler already running")
                return True
                
        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")
            return False
    
    def stop(self) -> bool:
        """
        Stop the scheduler
        
        Returns:
            True if stopped successfully
        """
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Scheduler stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")
            return False
    
    def get_scheduled_jobs(self):
        """Get list of scheduled jobs"""
        return self.scheduler.get_jobs()
    
    def reset_counter(self):
        """Reset call counter"""
        self.call_count = 0
        logger.info("Call counter reset")
    
    def get_next_run_time(self) -> Optional[datetime]:
        """Get time of next scheduled call"""
        try:
            job = self.scheduler.get_job(self.job_id)
            if job:
                return job.next_run_time
        except Exception as e:
            logger.error(f"Error getting next run time: {str(e)}")
        
        return None


def get_scheduler_status() -> dict:
    """Get scheduler status information"""
    return {
        "timezone": config.TIMEZONE,
        "call_window": f"{config.CALL_START_HOUR:02d}:{config.CALL_START_MINUTE:02d} - {config.CALL_END_HOUR:02d}:{config.CALL_END_MINUTE:02d}",
        "duration": f"{config.CALL_DURATION_MIN}-{config.CALL_DURATION_MAX} seconds",
        "consecutive_days": config.CONSECUTIVE_DAYS,
        "recipient": f"{config.RECIPIENT_NAME} ({config.RECIPIENT_PHONE})"
    }
