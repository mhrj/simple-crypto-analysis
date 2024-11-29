import pyRserve
import pandas as pd
from typing import Dict, Optional
from news_aggregator import NewsAggregator

class SentimentAnalysis:
    """
    Handles sentiment analysis for cryptocurrency-related news.
    """
    def __init__(self, news_aggregator: NewsAggregator):
        """
        Initialize with a NewsAggregator instance.
        """
        self.news_aggregator = news_aggregator

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
            "negative": sentiment_distribution['negative'],
        }