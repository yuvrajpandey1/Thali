"""
Configuration file for AI-Driven Automated News Call System
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==================== CALL CONFIGURATION ====================
RECIPIENT_NAME = "Aditya Kaji"
RECIPIENT_PHONE = "+91 99872 00003"  # E.164 format required
TIMEZONE = "Asia/Kolkata"  # IST - Indian Standard Time
CALL_START_HOUR = 11  # 11:00 AM
CALL_START_MINUTE = 0
CALL_END_HOUR = 11
CALL_END_MINUTE = 30  # 11:00 AM - 11:30 AM window
CALL_DURATION_MIN = 60  # 1 minute in seconds
CALL_DURATION_MAX = 120  # 2 minutes in seconds
CONSECUTIVE_DAYS = 5  # Run for 5 days

# ==================== TWILIO CONFIGURATION ====================
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")  # Your Twilio number

# ==================== NEWS CONFIGURATION ====================
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_API_BASE_URL = "https://newsapi.org/v2"
NEWS_COUNTRY = "in"  # India
NEWS_LANGUAGE = "en"  # English
TOP_NEWS_COUNT = 5  # Top 5 news articles
NEWS_SORT_BY = "publishedAt"  # Most recent first

# ==================== LLM CONFIGURATION (Ollama - Local) ====================
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")  # Free open-source model
SUMMARIZATION_PROMPT_TEMPLATE = """
Summarize the following news article in a way suitable for a 
voice broadcast. Keep it to 2-3 sentences, clear and concise:

Title: {title}
Content: {content}

Summary:
"""

# ==================== TEXT-TO-SPEECH CONFIGURATION ====================
TTS_ENGINE = "coqui"  # Using open-source Coqui TTS
TTS_MODEL_NAME = "tts_models/en/ljspeech/glow-tts"
TTS_SPEAKER = "default"
AUDIO_OUTPUT_DIR = "./audio_cache"
TTS_SPEED = 1.0  # Speech speed (normal speed)
TTS_EMOTION = "neutral"

# ==================== LOGGING CONFIGURATION ====================
LOG_LEVEL = "INFO"
LOG_FILE = "./logs/news_call_system.log"
LOG_DIR = "./logs"

# ==================== SYSTEM CONFIGURATION ====================
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
TEST_MODE = os.getenv("TEST_MODE", "False").lower() == "true"  # For testing without actual calls
DRY_RUN = os.getenv("DRY_RUN", "False").lower() == "true"  # Simulate without calling
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# ==================== DATABASE/STORAGE ====================
CALL_HISTORY_FILE = "./data/call_history.json"
NEWS_CACHE_FILE = "./data/news_cache.json"
DATA_DIR = "./data"

# ==================== VOICE SETTINGS ====================
VOICE_LANGUAGE = "en"
VOICE_ACCENT = "en-US"
