import praw
import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta
from helpers import get_request
from constants import (NEWS_API_KEY, CURRENTS_API_KEY, GNEWS_API_KEY, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT)

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
            "to_date": end_date.strftime("%Y-%m-%d"),
        }

    def _fetch_newsapi(self, query: str) -> Dict[str, List[str]]:
        """
        Fetch news from NewsAPI.
        """
        url = "https://newsapi.org/v2/everything"
        date_range = self._from_to_date(self.days)
        params = {
            "q": query,
            "from": date_range["from_date"],
            "to": date_range["to_date"],
            "sortBy": "relevance",
            "language": "en",
            "apiKey": NEWS_API_KEY,
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
            "apiKey": CURRENTS_API_KEY,
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
