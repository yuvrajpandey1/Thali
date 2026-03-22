"""
News Fetcher Module
Fetches top news articles from NewsAPI
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import config

logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetches and manages news articles"""
    
    def __init__(self):
        self.api_key = config.NEWS_API_KEY
        self.base_url = config.NEWS_API_BASE_URL
        self.country = config.NEWS_COUNTRY
        self.language = config.NEWS_LANGUAGE
        self.top_news_count = config.TOP_NEWS_COUNT
        
        if not self.api_key:
            logger.warning("NEWS_API_KEY not set. News fetching will fail.")
    
    def fetch_top_news(self) -> Optional[List[Dict]]:
        """
        Fetch top news articles for India
        
        Returns:
            List of news article dictionaries or None if failed
        """
        try:
            logger.info("Fetching top news articles...")
            
            # Using top-headlines endpoint for current news
            url = f"{self.base_url}/top-headlines"
            
            params = {
                "country": self.country,
                "language": self.language,
                "apiKey": self.api_key,
                "sortBy": config.NEWS_SORT_BY,
                "pageSize": self.top_news_count
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                logger.error(f"API returned error: {data.get('message')}")
                return None
            
            articles = data.get("articles", [])
            
            # Filter and clean articles
            cleaned_articles = self._clean_articles(articles[:self.top_news_count])
            
            logger.info(f"Successfully fetched {len(cleaned_articles)} articles")
            return cleaned_articles
            
        except requests.exceptions.Timeout:
            logger.error("News API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in fetch_top_news: {str(e)}")
            return None
    
    def _clean_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Clean and validate articles
        
        Args:
            articles: Raw articles from API
            
        Returns:
            Cleaned articles list
        """
        cleaned = []
        
        for idx, article in enumerate(articles, 1):
            cleaned_article = {
                "id": idx,
                "title": article.get("title", "No title"),
                "description": article.get("description", ""),
                "content": article.get("content", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "url": article.get("url", ""),
                "image_url": article.get("urlToImage", ""),
                "published_at": article.get("publishedAt", ""),
                "author": article.get("author", "Unknown")
            }
            
            # Ensure we have meaningful content
            if cleaned_article["title"] and (cleaned_article["description"] or cleaned_article["content"]):
                cleaned.append(cleaned_article)
        
        return cleaned[:self.top_news_count]
    
    def search_news(self, query: str, days_back: int = 7) -> Optional[List[Dict]]:
        """
        Search for specific news articles
        
        Args:
            query: Search query
            days_back: Search articles from past N days
            
        Returns:
            List of matching articles
        """
        try:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            url = f"{self.base_url}/everything"
            
            params = {
                "q": query,
                "language": self.language,
                "apiKey": self.api_key,
                "sortBy": "publishedAt",
                "pageSize": self.top_news_count,
                "from": start_date
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                logger.error(f"Search API returned error: {data.get('message')}")
                return None
            
            articles = data.get("articles", [])
            return self._clean_articles(articles[:self.top_news_count])
            
        except Exception as e:
            logger.error(f"Error searching news: {str(e)}")
            return None
    
    def save_news_cache(self, articles: List[Dict], filename: str = None):
        """Save articles to cache file"""
        try:
            if filename is None:
                filename = config.NEWS_CACHE_FILE
            
            # Ensure directory exists
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "articles": articles
            }
            
            with open(filename, "w") as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"Saved {len(articles)} articles to cache")
            
        except Exception as e:
            logger.error(f"Error saving news cache: {str(e)}")
    
    def load_news_cache(self, filename: str = None) -> Optional[List[Dict]]:
        """Load articles from cache file"""
        try:
            if filename is None:
                filename = config.NEWS_CACHE_FILE
            
            with open(filename, "r") as f:
                cache_data = json.load(f)
            
            return cache_data.get("articles", [])
            
        except FileNotFoundError:
            logger.info("No news cache file found")
            return None
        except Exception as e:
            logger.error(f"Error loading news cache: {str(e)}")
            return None


def get_news_for_call() -> Optional[List[Dict]]:
    """
    Convenience function to fetch news ready for voice call
    
    Returns:
        List of top 5 news articles
    """
    fetcher = NewsFetcher()
    articles = fetcher.fetch_top_news()
    
    if articles:
        fetcher.save_news_cache(articles)
    
    return articles
