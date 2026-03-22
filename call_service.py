"""
Voice Call Service Module
Handles placing automated calls using Twilio
"""

import logging
from typing import Optional, Dict
import json
from datetime import datetime
import config

logger = logging.getLogger(__name__)

# Try importing Twilio
try:
    from twilio.rest import Client
    HAS_TWILIO = True
except ImportError:
    HAS_TWILIO = False
    logger.warning("Twilio SDK not installed. Install with: pip install twilio")


class CallService:
    """Manages voice calls using Twilio"""
    
    def __init__(self):
        self.recipient_name = config.RECIPIENT_NAME
        self.recipient_phone = config.RECIPIENT_PHONE
        self.twilio_phone = config.TWILIO_PHONE_NUMBER
        self.account_sid = config.TWILIO_ACCOUNT_SID
        self.auth_token = config.TWILIO_AUTH_TOKEN
        
        self.client = None
        self._initialize_client()
        self.call_history = []
    
    def _initialize_client(self):
        """Initialize Twilio client"""
        if not HAS_TWILIO:
            logger.warning("Twilio not available")
            return
        
        if not self.account_sid or not self.auth_token:
            logger.warning("Twilio credentials not configured in .env file")
            return
        
        try:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("Twilio client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {str(e)}")
            self.client = None
    
    def place_call(self, audio_url: str, is_test: bool = False) -> Optional[Dict]:
        """
        Place a voice call with audio
        
        Args:
            audio_url: URL to the audio file to play during call
            is_test: If True, simulates the call without actually placing it
            
        Returns:
            Call details dict or None if failed
        """
        if is_test or config.DRY_RUN:
            return self._simulate_call(audio_url)
        
        if not self.client:
            logger.error("Twilio client not initialized")
            return self._simulate_call(audio_url)
        
        try:
            logger.info(f"Placing call to {self.recipient_name} ({self.recipient_phone})")
            
            # Create TwiML for the call
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{audio_url}</Play>
    <Say>Thank you for listening to your news update. Have a great day!</Say>
</Response>"""
            
            # Place the call
            call = self.client.calls.create(
                to=self.recipient_phone,
                from_=self.twilio_phone,
                twiml=twiml
            )
            
            logger.info(f"Call placed successfully. Call SID: {call.sid}")
            
            call_record = {
                "timestamp": datetime.now().isoformat(),
                "recipient": self.recipient_name,
                "phone": self.recipient_phone,
                "call_sid": call.sid,
                "status": call.status,
                "audio_url": audio_url
            }
            
            self.call_history.append(call_record)
            self._save_call_history()
            
            return call_record
            
        except Exception as e:
            logger.error(f"Error placing call: {str(e)}")
            return None
    
    def _simulate_call(self, audio_url: str) -> Dict:
        """Simulate a call for testing purposes"""
        logger.info(f"[SIMULATION] Would place call to {self.recipient_name} ({self.recipient_phone})")
        logger.info(f"[SIMULATION] Audio URL: {audio_url}")
        
        call_record = {
            "timestamp": datetime.now().isoformat(),
            "recipient": self.recipient_name,
            "phone": self.recipient_phone,
            "call_sid": f"SIM_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "simulated",
            "audio_url": audio_url,
            "is_simulation": True
        }
        
        self.call_history.append(call_record)
        self._save_call_history()
        
        return call_record
    
    def get_call_status(self, call_sid: str) -> Optional[str]:
        """
        Get status of a placed call
        
        Args:
            call_sid: Twilio Call SID
            
        Returns:
            Call status string or None if failed
        """
        if not self.client:
            logger.error("Twilio client not initialized")
            return None
        
        try:
            call = self.client.calls(call_sid).fetch()
            return call.status
        except Exception as e:
            logger.error(f"Error fetching call status: {str(e)}")
            return None
    
    def _save_call_history(self):
        """Save call history to file"""
        try:
            import os
            os.makedirs(config.DATA_DIR, exist_ok=True)
            
            with open(config.CALL_HISTORY_FILE, "w") as f:
                json.dump(self.call_history, f, indent=2)
            
            logger.debug(f"Saved call history: {len(self.call_history)} calls")
        except Exception as e:
            logger.error(f"Error saving call history: {str(e)}")
    
    def load_call_history(self):
        """Load call history from file"""
        try:
            with open(config.CALL_HISTORY_FILE, "r") as f:
                self.call_history = json.load(f)
            logger.info(f"Loaded call history: {len(self.call_history)} calls")
        except FileNotFoundError:
            logger.info("No previous call history found")
            self.call_history = []
        except Exception as e:
            logger.error(f"Error loading call history: {str(e)}")
            self.call_history = []


class MockCallService:
    """Mock service for testing without Twilio"""
    
    def __init__(self):
        self.recipient_name = config.RECIPIENT_NAME
        self.recipient_phone = config.RECIPIENT_PHONE
        self.call_history = []
    
    def place_call(self, audio_url: str, is_test: bool = False) -> Dict:
        """Mock place call"""
        logger.info(f"[MOCK] Placing call to {self.recipient_name}")
        
        call_record = {
            "timestamp": datetime.now().isoformat(),
            "recipient": self.recipient_name,
            "phone": self.recipient_phone,
            "call_sid": f"MOCK_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "completed",
            "audio_url": audio_url,
            "is_mock": True
        }
        
        self.call_history.append(call_record)
        return call_record


def place_news_call(audio_file_path: str) -> Optional[Dict]:
    """
    Convenience function to place a news call
    
    Args:
        audio_file_path: Local path to audio file
        
    Returns:
        Call record or None if failed
    """
    # In production, you would upload audio_file_path to a CDN/server
    # and get a public URL. For testing, we can use a file:// URL
    audio_url = audio_file_path  # This should be a public HTTP(S) URL
    
    if config.TEST_MODE:
        service = MockCallService()
    else:
        service = CallService()
    
    call_record = service.place_call(audio_url, is_test=config.TEST_MODE)
    
    return call_record
