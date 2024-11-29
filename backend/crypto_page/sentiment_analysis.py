import os
import sys
import praw
import pyRserve
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from helpers import get_request
from constants import (NEWS_API_URL, NEWS_API_KEY, CURRENTS_API_KEY, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT)

class NewsAggregator:
    """
    Fetches news for cryptocurrency-related news.
    """
    def __init__(self, days: int = 30):
        """
        Initialize the aggregator with the default number of days for fetching data.
        """
        self.days = days

    @staticmethod
    def _from_to_date(days: int) -> Dict[str, str]:
        """
        Calculate date range for API queries.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return {
            "from_date": start_date.strftime("%Y-%m-%d"),
            "to_date": end_date.strftime("%Y-%m-%d")
        }

    def _fetch_newsapi(self, query: str) -> Dict[str, List[str]]:
        """
        Fetch news from NewsAPI.
        """
        url = NEWS_API_URL
        date_range = self._from_to_date(self.days)
        params = {
            "q": query,
            "from": date_range["from_date"],
            "to": date_range["to_date"],
            "sortBy": "relevance",
            "language": "en",
            "apiKey": NEWS_API_KEY
        }
        response = get_request(url, params)
        articles = response.get("articles", [])
        return {
            "title": [article["title"] for article in articles]
        }

    def _fetch_currentsapi(self, query: str) -> Dict[str, List[str]]:
        """
        Fetch news from CurrentsAPI.
        """
        url = "https://api.currentsapi.services/v1/search"
        date_range = self._from_to_date(self.days)
        params = {
            "keywords": query,
            "start_date": date_range["from_date"],
            "end_date": date_range["to_date"],
            "language": "en",
            "apiKey": CURRENTS_API_KEY
        }
        response = get_request(url, params)
        articles = response.get("news", [])
        return {
            "title": [article["title"] for article in articles]
        }

    def _fetch_reddit(self, query: str) -> Dict[str, List[str]]:
        """
        Fetch posts from Reddit using PRAW (Python Reddit API Wrapper).
        """
        reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                            client_secret=REDDIT_CLIENT_SECRET,
                            user_agent=REDDIT_USER_AGENT)
        subreddit = reddit.subreddit("all")
        start_time = int((datetime.now() - timedelta(days=self.days)).timestamp())
        posts = subreddit.search(query, time_filter="month", sort="relevance")
        titles, sources = [], []
        for post in posts:
            if post.created_utc >= start_time:
                titles.append(post.title)
                sources.append("Reddit")
        return {
            "title": titles
        }

    def fetch_all_news(self, query: str) -> pd.DataFrame:
        """
        Combine news from all sources into a single DataFrame.
        """
        # Fetch data from all sources
        newsapi_data = self._fetch_newsapi(query)
        currents_data = self._fetch_currentsapi(query)
        reddit_data = self._fetch_reddit(query)

        # Combine all data into a dictionary
        combined_data = {
            "title": (
                newsapi_data["title"] + currents_data["title"] + reddit_data["title"]
            )
        }

        # Convert to DataFrame
        return combined_data
    
class SentimentAnalysis:
    """
    Handles sentiment analysis for cryptocurrency-related news.
    """
    def __init__(self, days):
        """
        Initialize with a NewsAggregator instance.
        """
        self.news_aggregator = NewsAggregator(days)

    @staticmethod
    def _cut_nans(data_dict: Dict) -> Dict:
        """
        Removes leading NaN values from a data dictionary.
        """
        max_nans = max(len([v for v in value if pd.isna(v)]) for value in data_dict.values() if isinstance(value, list))
        return {key: value[max_nans:] if isinstance(value, list) else value for key, value in data_dict.items()}

    def calculate_sentiment_score(self, coin_name: str) -> Optional[float]:
        """
        Calculates the overall sentiment score for a given cryptocurrency.
        """
        news_data = self.news_aggregator.fetch_all_news(coin_name)
        if not news_data:
            return None
        conn = pyRserve.connect("localhost", 6312)
        conn.eval('library(syuzhet)')
        conn.r.news_titles = news_data['title']
        sentiment_score = conn.eval("""
            mean(get_sentiment(unlist(news_titles), method = 'syuzhet'), na.rm = TRUE)
        """)
        conn.close()
        return sentiment_score

    def calculate_sentiment_distribution(self, coin_name: str) -> Dict[str, float]:
        """
        Calculates the sentiment distribution for a given cryptocurrency.
        """
        news_data = self.news_aggregator.fetch_all_news(coin_name)
        if not news_data:
            return {"positive": 0, "neutral": 0, "negative": 0}
        conn = pyRserve.connect("localhost", 6312)
        conn.eval('library(syuzhet)')
        conn.r.news_titles = news_data['title']
        sentiment_distribution = conn.eval("""
            calculate_distribution <- function(titles) {
                scores <- get_sentiment(titles, method = 'syuzhet')
                positive_count <- sum(scores > 0.1)
                neutral_count <- sum(scores >= -0.1 & scores <= 0.1)
                negative_count <- sum(scores < -0.1)
                total <- length(scores)
                list(
                    positive = round((positive_count / total) * 100, 2),
                    neutral = round((neutral_count / total) * 100, 2),
                    negative = round((negative_count / total) * 100, 2)
                )
            }
            calculate_distribution(unlist(news_titles))
        """)
        conn.close()
        return {
            "positive": sentiment_distribution['positive'],
            "neutral": sentiment_distribution['neutral'],
            "negative": sentiment_distribution['negative']
        }