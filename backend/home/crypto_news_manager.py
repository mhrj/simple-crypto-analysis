import os
import sys
from typing import List, Dict, Union
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from constants import (NEWS_API_URL, NEWS_API_KEY)
from helpers import get_request

class CryptoNewsManager:
    """
    A class to handle interactions with the NewsAPI for fetching and formatting news articles.
    """

    BASE_URL = NEWS_API_URL

    def __init__(self, api_key: str = NEWS_API_KEY):
        """
        Initialize the NewsAPI class with the API key.
        Args:
            api_key (str): Your NewsAPI API key.
        """
        self.api_key = api_key

    def fetch_news_data(self, query: str, limit: int) -> Union[Dict, List[Dict]]:
        """
        Fetch news data from the NewsAPI.
        Args:
            query (str): The search query for news articles.
            limit (int): The number of articles to fetch.
        Returns:
            dict: A dictionary containing raw API response data or an error message.
        """
        params = {
            "q": query,
            "language": "en",
            "pageSize": limit,
            "apiKey": self.api_key
        }

        # Using the get_request helper for making the API call
        return get_request(self.BASE_URL, params)

    @staticmethod
    def format_news_articles(raw_data: Dict, limit: int) -> List[Dict]:
        """
        Format raw news API data into a list of article dictionaries.
        Args:
            raw_data (dict): The raw API response data.
            limit (int): The maximum number of articles to include in the result.
        Returns:
            list: A list of dictionaries with article details.
        """
        articles = raw_data.get("articles", [])
        news_list = []

        for article in articles[:limit]:
            news_list.append({article.get("title", "No title")})

        return news_list

    def fetch_latest_news(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Fetch the latest news based on the query and format the results.
        Args:
            query (str): The search query for news articles.
            limit (int): The number of latest news articles to fetch. Default is 5.
        Returns:
            list: A list of dictionaries containing the latest news articles or an error message.
        """
        raw_data = self.fetch_news_data(query, limit)
        if "error" in raw_data:
            return [{"error": raw_data["error"]}]
        return self.format_news_articles(raw_data, limit)

    def fetch_latest_crypto_news(self, limit: int = 5) -> List[Dict]:
        """
        Fetch the latest general cryptocurrency news.
        Args:
            limit (int): The number of latest news articles to fetch. Default is 5.
        Returns:
            list: A list of dictionaries containing the latest general crypto news.
        """
        # Now using self.fetch_latest_news
        return self.fetch_latest_news("cryptocurrency", limit)