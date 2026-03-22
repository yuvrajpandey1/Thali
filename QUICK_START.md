# Quick Start Guide (5 Minutes)

For the impatient developer! This gets you running in 5 minutes.

## Prerequisites
- Python 3.8+ installed
- Ollama running (`ollama serve`)
- API keys ready (NewsAPI, Twilio)

## Installation (2 minutes)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy & edit environment variables
cp .env.example .env
# → Edit .env with your API keys

# Download Ollama models (if not done)
ollama pull mistral
```

## Run Test (3 minutes)

```bash
# Start with test mode (no real calls)
python -c "
from main import NewsCallSystem
system = NewsCallSystem()
print('Testing system...')
system.test_call()
"
```

**Expected Output**:
```
[1/5] Fetching top news articles...
✓ Fetched 5 articles

[2/5] Summarizing articles with AI...
✓ Summarized 5 articles

[3/5] Creating voice script...
✓ Voice script created

[4/5] Converting text to speech...
✓ Audio generated

[5/5] Placing voice call...
✓ Call placed successfully!
```

## Go Live

```bash
# Change in .env:
TEST_MODE=False

# Then run:
python -c "
from main import NewsCallSystem
system = NewsCallSystem()
system.schedule_daily_calls()
# Keep this running
"
```

System will call at **11:00 AM IST** for **5 consecutive days**.

---

## File Structure Quick Reference

```
your_project/
├── main.py               ← Start here
├── config.py             ← Customize settings
├── news_fetcher.py       ← Get news
├── ai_summarizer.py      ← Summarize with AI
├── tts_processor.py      ← Convert to audio
├── call_service.py       ← Place calls
├── scheduler.py          ← Schedule daily
├── .env                  ← Your API keys ⚠️ SECRET
├── requirements.txt      ← Dependencies
├── README.md             ← Full documentation
├── ARCHITECTURE.md       ← Technical details
├── SETUP_GUIDE.md        ← Installation help
└── QUICK_START.md        ← This file
```

## System Flow

```
11:00 AM IST
    ↓
Fetch news (NewsAPI)
    ↓
Summarize (Ollama)
    ↓
Convert to audio (Coqui TTS)
    ↓
Call recipient (Twilio)
    ↓
Done! Repeat next day
```

## Key Commands

| What | Command |
|------|---------|
| Test system | `python test_call.py` |
| Start scheduler | `python start_scheduler.py` |
| Check status | `python -c "from main import NewsCallSystem; system = NewsCallSystem(); print(system.get_system_status())"` |
| View logs | `tail -f logs/news_call_system.log` |

## Common Issues

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Ollama connection failed | Run `ollama serve` in another terminal |
| Twilio API error | Check .env credentials |
| Audio not generating | Run `ollama pull mistral` |

## Environment Variables

```env
# Required
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
NEWS_API_KEY=your_key

# Optional (has defaults)
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=mistral
TEST_MODE=True    # Start with True
```

## Next Steps

1. **Read**: Check `README.md` for full documentation
2. **Understand**: See `ARCHITECTURE.md` for how it works  
3. **Deploy**: Follow `SETUP_GUIDE.md` for production setup
4. **Monitor**: Check `logs/news_call_system.log` for execution

---

**That's it! Your automated news call system is ready.** 🚀

For questions, see the detailed documentation files.
