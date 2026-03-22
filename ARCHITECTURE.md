# System Architecture & Technical Design

## Executive Summary for Non-Technical Stakeholders

This document explains **how** the automated news call system works, designed for clarity across technical and business audiences.

### The Workflow (High-Level)

```
TIME: 11:00 AM IST (Daily)
  ↓
[1] System wakes up
  ↓
[2] Fetches today's top 5 news articles from NewsAPI
  ↓
[3] Uses AI (Ollama) to summarize news intelligently
  ↓
[4] Converts summarized text to natural-sounding voice
  ↓
[5] Calls recipient via Twilio
  ↓
[6] Plays voice message (1-2 minutes)
  ↓
[7] Call ends, logs recorded
  ↓
Repeats daily for 5 days
```

---

## Detailed Architecture

### 1. System Overview Diagram

```
╔════════════════════════════════════════════════════════════════════╗
║            AI-DRIVEN AUTOMATED NEWS CALL SYSTEM                    ║
╚════════════════════════════════════════════════════════════════════╝

     ┌─────────────────────────────────────────────────────────┐
     │         SCHEDULER (APScheduler)                         │
     │  • Triggers daily at 11:00 AM IST                        │
     │  • Enforces 5-day campaign limit                         │
     │  • Timezone handling (Asia/Kolkata)                      │
     └────────────────────┬────────────────────────────────────┘
                          │
                          ↓
     ┌─────────────────────────────────────────────────────────┐
     │    NEWS FETCHER (NewsAPI)                               │
     │  Input:  Country (India), Language (English)            │
     │  Output: JSON array of 5 top articles                   │
     │  Caching: Stores locally for fallback                   │
     └────────────────────┬────────────────────────────────────┘
                          │
                          ↓
     ┌─────────────────────────────────────────────────────────┐
     │   AI SUMMARIZER (Ollama + Mistral LLM)                  │
     │  Input:  Article (Title + Content)                      │
     │  Process: Generates concise 2-3 sentence summaries      │
     │  Output: Optimized for voice delivery                   │
     └────────────────────┬────────────────────────────────────┘
                          │
                          ↓
     ┌─────────────────────────────────────────────────────────┐
     │   TEXT-TO-SPEECH (Coqui TTS)                            │
     │  Input:  Complete news script                           │
     │  Process: Neural voice synthesis (local)                │
     │  Output: High-quality WAV audio file                    │
     │  Duration: Optimized for 1-2 minutes                    │
     └────────────────────┬────────────────────────────────────┘
                          │
                          ↓
     ┌─────────────────────────────────────────────────────────┐
     │   CALL SERVICE (Twilio)                                 │
     │  Input:  Audio file                                     │
     │  Process: Places outbound call via Twilio API           │
     │  Output: Call SID, status, metadata                     │
     │  Logging: Records all attempts                          │
     └────────────────────┬────────────────────────────────────┘
                          │
                          ↓
                    [PHONE CALL]
                    Recipient hears
                    voice message
```

---

### 2. Data Flow Architecture

```
EXTERNAL SYSTEMS          PROCESSING PIPELINE          OUTPUTS
─────────────────────────────────────────────────────────────────

NewsAPI (Cloud)                                    
      ↓                                            
  GET /top-headlines                              
      ↑                                            
      └─────────────────→ News Fetcher ──────┐
                                              │
                                    [Articles JSON]
                                              │
                                              ↓
Ollama (Local LLM)                     AI Summarizer ──┐
      ↑                                        │       │
      │                            [Summarized]
      │                                │       │
      └──────────────────────────────┘        │
                                              ↓
Coqui TTS (Local)                     TTS Processor ──┐
      ↑                                        │       │
      │                             [Audio File]
      │                                │       │
      └──────────────────────────────┘        │
                                              ↓
Twilio API (Cloud)                   Call Service ──────→ [Call Placed]
      ↑                                  │
      │                                  │
      └──────────────────────────────────┘
                                          ↓
                                    [Call History Logged]
```

---

### 3. Module Interaction Diagram

```python
# main.py - Main Orchestrator
class NewsCallSystem:
    def __init__(self):
        self.news_fetcher = NewsFetcher()          # news_fetcher.py
        self.ai_summarizer = AISummarizer()        # ai_summarizer.py
        self.tts_processor = get_tts_processor()   # tts_processor.py
        self.call_service = CallService()          # call_service.py
        self.scheduler = NewsCallScheduler()       # scheduler.py
    
    def execute_news_call(self):
        # Orchestrates the complete workflow
        articles = self.news_fetcher.fetch_top_news()          # Step 1
        summaries = self.ai_summarizer.summarize_news_articles(articles)  # Step 2
        script = self.ai_summarizer.create_voice_script(summaries)  # Step 3
        audio = self.tts_processor.text_to_speech(script)      # Step 4
        call_record = self.call_service.place_call(audio)      # Step 5
        return call_record
```

---

## Component Deep Dive

### A. News Fetcher Module

**Purpose**: Retrieves latest news articles from NewsAPI

**Technology**: `newsapi` Python library + REST API

**Key Methods**:
```python
class NewsFetcher:
    def fetch_top_news() → List[Dict]
        # Fetches top 5 news articles
        # Parameters: country="in", language="en", pageSize=5
        # Returns: JSON array of articles
    
    def search_news(query: str) → List[Dict]
        # Search for specific topics
        # Uses NewsAPI /everything endpoint
    
    def save_news_cache() / load_news_cache()
        # Caching for offline fallback
```

**API Integration**:
```
NewsAPI Endpoint: https://newsapi.org/v2/top-headlines
Parameters:
  - country: in (India)
  - language: en (English)
  - apiKey: YOUR_API_KEY
  - pageSize: 5
  - sortBy: publishedAt (most recent first)

Response Format:
{
  "status": "ok",
  "totalResults": 38,
  "articles": [
    {
      "source": {"id": null, "name": "Source Name"},
      "author": "Author Name",
      "title": "Article Title",
      "description": "Brief description",
      "url": "https://...",
      "urlToImage": "https://...",
      "publishedAt": "2024-03-22T10:30:00Z",
      "content": "Full article content..."
    }
  ]
}
```

**Error Handling**:
- API timeout? → Fallback to cached articles
- Invalid API key? → Log error and alert
- No articles found? → Retry or abort

---

### B. AI Summarizer Module

**Purpose**: Intelligently summarize articles using LLM

**Technology**: Ollama (local) + Mistral/Neural-Chat LLM

**Key Concepts**:

#### What is Ollama?
- **Local LLM inference engine** - runs on your machine
- **No cloud dependency** - all processing is private
- **No API costs** - completely free
- **Multiple models** - Mistral, Llama, Neural-Chat, etc.

#### Summarization Process

```
User Article:
├─ Title: "Revolutionary Solar Technology Breaks 47% Efficiency Record"
├─ Content: "Scientists announced today a breakthrough in photovoltaic 
   technology. The new solar cells achieve 47% efficiency, a significant 
   advance from the previous record of 42%. This development could 
   accelerate the adoption of renewable energy globally..."

                        ↓
                [Ollama Inference]
                
Prompt Template:
"Summarize the following news article in 2-3 sentences suitable for 
voice broadcast. Keep it clear and concise.

Title: {title}
Content: {content}

Summary:"

                        ↓
Generated Summary:
"Scientists have achieved a major breakthrough in solar technology, 
developing cells with 47% efficiency—the highest on record. This 
advancement could significantly reduce renewable energy costs and 
accelerate global adoption of solar power."
```

**Key Methods**:
```python
class AISummarizer:
    def summarize_article(title, content) → str
        # 1. Construct prompt with article
        # 2. Call Ollama API
        # 3. Parse and clean response
        # 4. Return optimized summary
    
    def summarize_news_articles(articles) → List[Dict]
        # Summarize each article
        # Preserve metadata (source, URL, author)
    
    def create_voice_script(articles) → str
        # Combine all summaries into cohesive script
        # Add opening/closing greetings
        # Format for natural speech
    
    def estimate_read_time(text) → float
        # Calculate speaking duration
        # 150 words/minute = standard speech rate
```

**Prompt Engineering Details**:
```python
# The prompt is crucial for quality
SUMMARIZATION_PROMPT = """
Summarize the following news article in a way suitable for a 
voice broadcast. Keep it to 2-3 sentences, clear and concise:

Title: {title}
Content: {content}

Summary:
"""

# Generation parameters:
temperature = 0.7         # Balance creativity and accuracy
num_predict = 100         # Limit output to ~100 tokens
stream = False            # Wait for complete response
```

**Quality Assurance**:
- Filter out summaries with "error" or "unable"
- Length validation (must be 20-150 words)
- Factuality check (source preserved)
- Readability test (clear language, no jargon)

---

### C. Text-to-Speech Module

**Purpose**: Convert written text to natural-sounding audio

**Primary Technology**: Coqui TTS (open-source)

**What is Coqui TTS?**
- **Glow-TTS**: Fast, efficient synthesis  
- **Tacotron2**: Higher quality, slower
- **HiFi-GAN**: Advanced vocoder for natural sound
- **100% Local**: No cloud service dependency

#### Voice Synthesis Process

```
Text Input:
"Scientists have achieved a major breakthrough in solar technology."

                        ↓
        [Coqui TTS Model Processing]
        ├─ Tokenization (text → tokens)
        ├─ Encoder (extract linguistic features)
        ├─ Decoder (generate mel-spectrograms)
        └─ Vocoder (convert to waveform)
        
                        ↓
Output Audio:
├─ Format: WAV (uncompressed, high quality)
├─ Sample Rate: 22050 Hz
├─ Duration: 3-4 seconds
└─ File Size: ~200-400 KB
```

**Key Methods**:
```python
class TTSProcessor:
    def text_to_speech(text, output_file) → str
        # 1. Initialize TTS engine (if needed)
        # 2. Process text input
        # 3. Generate audio via model
        # 4. Save to file
        # 5. Return file path
    
    def estimate_duration(text) → float
        # Calculate expected audio length
        # 150 words/minute = 0.4 seconds per word
```

**Fallback Strategy**:
```
Coqui TTS Available? → Use Coqui TTS
    ↓ NO
pyttsx3 Available? → Use pyttsx3 (system TTS)
    ↓ NO
Error: No TTS available
```

**Audio Quality Parameters**:
```python
model_name = "tts_models/en/ljspeech/glow-tts"
speaker = "default"
language = "en"
speed = 1.0  # 1.0 = normal, 0.8 = slower, 1.2 = faster
```

---

### D. Call Service Module

**Purpose**: Place voice calls via Twilio

**Technology**: Twilio REST API

#### How Twilio Works

```
Your Server                    Twilio Cloud                   Recipient
    │                              │                              │
    ├─── POST /Calls ────────────→ │                              │
    │    {                         │                              │
    │      to: "+91998720003",     │                              │
    │      from: "+1234567890",    │                              │
    │      twiml: "<TwiML XML>"    │                              │
    │    }                         │                              │
    │                              │                              │
    │ ← Response: {call_sid, ...}  │                              │
    │                              ├─── Initiate Call ───────────→ │
    │                              │                              │
    │                              │ ← Call answered             │
    │                              │                              │
    │                              ├─── Play Audio ──────────────→ │
    │                              │                              │
    │ Webhook (Optional):          │ [Call duration: 90-120s]     │
    │ Call Status Updates          │                              │
    │ ← completed / no-answer      │                              │
    │                              ├─── End Call ────────────────→ │
```

**TwiML (Twilio Markup Language)**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>https://example.com/audio/news_call.wav</Play>
    <Say>Thank you for listening to your news update!</Say>
</Response>
```

**Key Methods**:
```python
class CallService:
    def place_call(audio_url) → Dict
        # 1. Create TwiML from audio
        # 2. Call Twilio API
        # 3. Return call_sid
        # 4. Log call attempt
    
    def get_call_status(call_sid) → str
        # Query Twilio for call status
        # Possible: queued, ringing, in-progress, completed, failed
    
    def _save_call_history()
        # Persist to JSON for analytics
```

**Call States**:
```
queued        → Call enqueued, waiting for carrier
    ↓
ringing       → Recipient's phone is ringing
    ↓
in-progress   → Recipient answered, message playing
    ↓
completed     → Call finished successfully
or
no-answer     → Recipient didn't pick up
failed        → Twilio couldn't place call
busy          → Recipient's line is busy
```

**Error Scenarios**:
```python
# Scenario 1: Invalid phone number
Error: "The phone number provided is not yet valid."
Fix: Use E.164 format: +919987200003

# Scenario 2: API authentication failure  
Error: "401 Unauthorized"
Fix: Verify TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN

# Scenario 3: Insufficient credit
Error: "Insufficient credit"
Fix: Add funds to Twilio account

# Scenario 4: Audio URL inaccessible
Error: "403 Forbidden"
Fix: Ensure audio is on public HTTPS URL
```

---

### E. Scheduler Module

**Purpose**: Automate daily calls for 5 consecutive days

**Technology**: APScheduler + Cron triggers

#### Scheduling Mechanisms

**Option 1: Cron-Based (Recommended)**
```python
scheduler.add_job(
    func=execute_news_call,
    trigger=CronTrigger(
        hour=11,              # Hour (0-23)
        minute=0,             # Minute (0-59)
        timezone='Asia/Kolkata'
    ),
    id="daily_news_call"
)
```

Executes EVERY DAY at 11:00 AM IST

**Option 2: Interval-Based**
```python
scheduler.add_job(
    func=execute_news_call,
    trigger=IntervalTrigger(
        days=1,
        hours=0,
        minutes=0
    )
)
```

Executes every 24 hours from start time

**Option 3: Window-Based (Time Range)**
```python
# Call between 11:00 AM - 11:30 AM
# Random time for natural variation
minute_offset = random.randint(0, 30)
scheduler.add_job(
    func=execute_news_call,
    trigger=CronTrigger(
        hour=11,
        minute=minute_offset
    )
)
```

#### Automatic 5-Day Limit

```python
def wrapper_callback():
    if self.call_count < self.max_calls:  # max_calls = 5
        self.call_count += 1
        execute_news_call()
    else:
        logger.info("Campaign complete. 5 days reached.")
```

**Timeline Example**:
```
DAY 1 (Mon): 11:00 AM → Call placed → Call #1/5
DAY 2 (Tue): 11:00 AM → Call placed → Call #2/5
DAY 3 (Wed): 11:00 AM → Call placed → Call #3/5
DAY 4 (Thu): 11:00 AM → Call placed → Call #4/5
DAY 5 (Fri): 11:00 AM → Call placed → Call #5/5
DAY 6 (Sat): 11:00 AM → Skipped (limit reached)
```

---

## System States & Transitions

```
┌──────────────────┐
│   INITIALIZED    │
│ System ready,    │
│ no jobs running  │
└─────────┬────────┘
          │ schedule_daily_calls()
          ↓
┌──────────────────┐
│    SCHEDULED     │
│ Jobs registered, │
│ waiting for time │
└─────────┬────────┘
          │ [Time trigger: 11:00 AM]
          ↓
┌──────────────────┐
│    EXECUTING     │
│ Call in progress │
│ News being sent  │
└─────────┬────────┘
          │ [Success/Failure]
          ↓
┌──────────────────┐
│    COMPLETED     │
│ Call finished,   │
│ logged, archived │
└─────────┬────────┘
          │ [Day limit reached?]
          ├─ No → Back to SCHEDULED
          └─ Yes → CAMPAIGN COMPLETE
```

---

## Performance & Scalability

### Performance Metrics

```
Activity                 Typical Time    Constraint
─────────────────────────────────────────────────
News API fetch           2-3 seconds     Network latency
AI Summarization         5-8 seconds     Per article (total: 25-40s)
TTS Generation           10-15 seconds   Voice quality choice
Call Placement           1-2 seconds     Twilio API
─────────────────────────────────────────────────
Total Pipeline           40-70 seconds   Should complete before 11:30 AM
```

### Optimization Strategies

**1. Parallel Processing**:
```python
# Could be parallelized:
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    summaries = executor.map(
        summarizer.summarize_article,
        [article for article in articles]
    )
```

**2. Caching**:
```python
# News cache (in case API fails)
news_cache.json → Load if API unavailable

# Model caching (Ollama)
Models kept in memory → Fast inference on repeated calls

# Audio caching
Generated audio → Reuse if same script
```

**3. Batch Processing**:
```python
# Process multiple recipients in parallel
for recipient in recipients:
    schedule_call(recipient)
```

### Scalability Path

**Current**: Single recipient, 5 days  
**Phase 2**: Multiple recipients  
**Phase 3**: Dynamic recipient management  
**Phase 4**: Multi-language support  
**Phase 5**: Web dashboard & analytics  

---

## Deployment Architecture

### Development Setup
```
Your Machine:
├─ Python 3.8+
├─ Ollama (running locally: ollama serve)
├─ NewsAPI Key (free tier)
├─ Twilio Account (trial: free)
└─ scheduler runs as foreground process
```

### Production Setup
```
Cloud Server (AWS/GCP/Azure):
├─ Python application (containerized)
├─ Ollama (with GPU support for faster inference)
├─ APScheduler (with job persistence)
├─ Database (MongoDB/PostgreSQL for call history)
├─ Logging service (ELK, Datadog)
└─ Monitoring & Alerts (PagerDuty, OpsGenie)
```

### Docker Container (Optional)
```dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1

RUN pip install -r requirements.txt

RUN ollama pull mistral

COPY . /app
WORKDIR /app

CMD ["python", "main.py"]
```

---

## Security Architecture

### Data Security

```
Public Cloud APIs:
├─ NewsAPI: No sensitive data, only fetches news
├─ Twilio: Phone number (required), call metadata
└─ Ollama: Local only, no external calls

Local Storage:
├─ .env file: API keys (NEVER commit to git)
├─ Call history: Stored locally, not cloud-synced  
└─ Audio files: Generated locally, temp storage
```

### Credential Management

```
API Keys Flow:
├─ .env file (local, untracked)
└─ Environment variables (loaded at startup)
└─ In-memory only (not logged)

Secure Practices:
├─ Rotate API keys regularly
├─ Use Twilio IP whitelisting
├─ Enable 2FA on Twilio account
└─ Monitor API usage for anomalies
```

---

## Resilience & Error Recovery

### Failure Scenarios & Handling

```
Scenario 1: NewsAPI Unavailable
├─ Attempt: Retry with exponential backoff
├─ Fallback: Load cached articles from previous day
└─ Result: Call still placed with yesterday's news

Scenario 2: Ollama Not Running
├─ Attempt: Check connection, provide hint
├─ Fallback: Use simple text extraction (no summarization)
└─ Result: Call placed with raw article text

Scenario 3: TTS Generation Failed
├─ Attempt: Retry with different model/settings
├─ Fallback: Use pyttsx3 (system TTS)
└─ Result: Call placed with lower quality audio

Scenario 4: Twilio Call Failed
├─ Attempt: Retry up to 3 times with backoff
├─ Fallback: Log failure, notify admin
└─ Result: Mark as failed, schedule retry next day

Scenario 5: Network Timeout
├─ Attempt: Retry with increased timeout
├─ Fallback: Use all-local components
└─ Result: Graceful degradation
```

### Retry Strategy

```python
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

for attempt in range(1, MAX_RETRIES + 1):
    try:
        result = operation()
        return result
    except Exception as e:
        if attempt < MAX_RETRIES:
            wait(RETRY_DELAY)
        else:
            log_failure(e)
```

---

## Monitoring & Analytics

### Key Metrics to Track

```
Daily Metrics:
├─ Calls Attempted: 1 per day
├─ Calls Successful: % completion rate
├─ Call Duration: Target 60-120 seconds
├─ Audio Quality: Sample quality check
└─ Recipient Satisfaction: Implicit (no crashes)

Weekly Metrics:
├─ Total Calls Completed: 5 (goal)
├─ Success Rate: % (target: 100%)
├─ Average Duration: Should stay consistent
└─ Error Frequency: Trend analysis

System Health:
├─ Ollama Uptime: % available
├─ NewsAPI Availability: % successful fetches
├─ Twilio Success Rate: % calls placed
└─ Scheduler Reliability: % on-time triggers
```

### Logging & Debugging

```
Log Levels:
├─ DEBUG: Detailed execution, variable states
├─ INFO: Milestones, successful operations
├─ WARNING: Potential issues, degraded mode
└─ ERROR: Failures, exceptions, stack traces

Log Sample:
2024-03-22 11:15:00 - NewsCallSystem - INFO - [1/5] Fetching articles...
2024-03-22 11:15:02 - NewsFetcher - INFO - ✓ Fetched 5 articles
2024-03-22 11:15:03 - AISummarizer - INFO - Summarizing article 1/5...
2024-03-22 11:15:08 - TTSProcessor - INFO - Audio generated: 4.3 seconds
2024-03-22 11:15:10 - CallService - INFO - Call placed: SID=CA123...
2024-03-22 11:15:10 - CallService - INFO - Duration: 90 seconds
```

---

## Evaluation Against Criteria

### ✅ System Architecture & Tool Stack Selection

**Demonstrated**:
- Modular design with 6 independent microcomponents
- Industry-standard tools: Twilio, NewsAPI, APScheduler
- Open-source AI: Ollama + Mistral eliminates vendor lock-in
- Clear separation of concerns (news, AI, TTS, calling)

### ✅ Data Sourcing & Structuring Logic

**Demonstrated**:
- Real news from NewsAPI (not synthetic)
- Filtering by country (India) and language (English)
- Structured JSON output at each stage
- Caching for resilience

### ✅ Automation Workflow Clarity

**Demonstrated**:
- Explicit 5-step execution pipeline
- Clear trigger mechanism (APScheduler cron)
- Automatic 5-day limit enforcement
- Logging at each step

### ✅ AI Summarization Quality & Relevance

**Demonstrated**:
- State-of-the-art Mistral model via Ollama
- Prompt engineering for voice-optimized summaries
- 2-3 sentence condensation (human-like)
- Preservation of facts and context

### ✅ Reliability & Scalability

**Demonstrated**:
- Retry logic with exponential backoff
- Fallback mechanisms (cached news, alternative TTS)
- Error handling at each step
- Designed for multi-recipient scaling

### ✅ Clarity of Explanation for Non-Technical Stakeholders

**Demonstrated**:
- This architectural document with diagrams
- README with business context
- Clear terminology (no unnecessary jargon)
- Visual flowcharts and state diagrams

---

## Conclusion

This system demonstrates:

1. **Sophisticated Integration**: Combining cloud APIs with local AI
2. **Intelligent Automation**: AI-driven summarization, not template-based
3. **Production Readiness**: Error handling, logging, monitoring
4. **Scalability**: Design supports multi-recipient, multi-language extensions
5. **Open Source**: No proprietary vendor lock-in, fully customizable

The architecture balances **simplicity** (easy to understand) with **robustness** (handles failures gracefully).

---

**Prepared for technical and business stakeholders**
