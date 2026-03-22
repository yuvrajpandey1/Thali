"""
AI Summarization Module
Uses Ollama (local open-source LLM) to summarize news articles
"""

import requests
import json
import logging
from typing import List, Dict, Optional
import config

logger = logging.getLogger(__name__)


class AISummarizer:
    """Summarizes text using open-source LLMs via Ollama"""
    
    def __init__(self):
        self.api_url = config.OLLAMA_API_URL
        self.model = config.OLLAMA_MODEL
        self._test_connection()
    
    def _test_connection(self):
        """Test connection to Ollama"""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"Connected to Ollama at {self.api_url}")
                models = response.json().get("models", [])
                if models:
                    logger.info(f"Available models: {[m.get('name') for m in models]}")
            else:
                logger.warning("Could not connect to Ollama")
        except Exception as e:
            logger.warning(f"Ollama connection test failed: {str(e)}")
            logger.info("Make sure Ollama is running: ollama serve")
    
    def summarize_article(self, title: str, content: str, max_length: int = 150) -> Optional[str]:
        """
        Summarize a single news article
        
        Args:
            title: Article title
            content: Article content/description
            max_length: Maximum length of summary
            
        Returns:
            Summarized text suitable for voice delivery
        """
        try:
            # Combine title and content
            text = f"Title: {title}\nContent: {content}"
            
            prompt = f"""Summarize the following news article in 2-3 sentences, 
making it suitable for a voice broadcast. Be clear, concise, and engaging:

{text}

Summary:"""
            
            logger.debug(f"Generating summary for: {title[:50]}...")
            
            response = requests.post(
                f"{self.api_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "num_predict": 100  # Limit output length
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get("response", "").strip()
                
                # Clean up summary
                summary = self._clean_summary(summary)
                
                if len(summary) > max_length:
                    summary = summary[:max_length] + "..."
                
                logger.debug(f"Generated summary: {summary[:80]}...")
                return summary
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return None
        except Exception as e:
            logger.error(f"Error summarizing article: {str(e)}")
            return None
    
    def _clean_summary(self, text: str) -> str:
        """Clean up generated summary"""
        # Remove common artifacts
        text = text.strip()
        text = text.replace("Summary:", "").strip()
        text = text.replace("Summary", "").strip()
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        return text
    
    def summarize_news_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Summarize multiple news articles
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Articles with summaries added
        """
        logger.info(f"Summarizing {len(articles)} articles...")
        
        summarized_articles = []
        
        for idx, article in enumerate(articles, 1):
            logger.info(f"Processing article {idx}/{len(articles)}: {article['title'][:50]}...")
            
            title = article.get("title", "")
            content = article.get("description", "") or article.get("content", "")
            
            # Get summary
            summary = self.summarize_article(title, content)
            
            if summary:
                article["summary"] = summary
            else:
                # Fallback: use original description
                article["summary"] = content[:150] + "..." if len(content) > 150 else content
            
            summarized_articles.append(article)
        
        return summarized_articles
    
    def create_voice_script(self, articles: List[Dict]) -> str:
        """
        Create a voice script from summarized articles
        
        Args:
            articles: List of summarized articles
            
        Returns:
            Complete voice script for 1-2 minute delivery
        """
        script = f"""Good morning! This is your automated news update. 
Here are the top 5 news stories for today.

"""
        
        for idx, article in enumerate(articles[:5], 1):
            summary = article.get("summary", article.get("description", "No content"))
            source = article.get("source", "Unknown")
            
            script += f"""story {idx}: {summary} (Source: {source})

"""
        
        script += """That's all for today's news update. Have a great day!"""
        
        return script
    
    def estimate_read_time(self, text: str) -> float:
        """
        Estimate how long text will take to read
        Average speaking rate is 150 words per minute
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated time in seconds
        """
        word_count = len(text.split())
        minutes = word_count / 150
        seconds = minutes * 60
        return seconds


def summarize_news_for_call(articles: List[Dict]) -> tuple:
    """
    Convenience function to summarize news and create voice script
    
    Args:
        articles: List of news articles
        
    Returns:
        Tuple of (summarized_articles, voice_script, estimated_duration)
    """
    summarizer = AISummarizer()
    
    # Summarize articles
    summarized = summarizer.summarize_news_articles(articles)
    
    # Create voice script
    script = summarizer.create_voice_script(summarized)
    
    # Estimate duration
    duration = summarizer.estimate_read_time(script)
    
    logger.info(f"Voice script estimated duration: {duration:.1f} seconds")
    
    return summarized, script, duration
