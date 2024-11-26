import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
import pyRserve
from datetime import datetime, timedelta
import requests
from newsapi import NewsApiClient
import praw
import pandas as pd

# Constants
CRYPTOCOMPARE_BASE_URL = "https://min-api.cryptocompare.com/data/v2"
CRYPTOCOMPARE_API_KEY = "2ade0bdf98ef9e6f719bee6b0e58bf88497fdaaa1dc7e3948347ba1d65304981"
# Constants
# Replace with your NewsAPI key
NEWS_API_KEY = "fbf8172bf41c423f8667eb92b88cc692"
# Replace with your Currents API key
CURRENTS_API_KEY = "_dUfjDeqhDH6Ih01lA0BI7DDHoIHSr1uJnxF31IbYX0IAZ_H"
# Replace with your GNews API key
GNEWS_API_KEY = "40e4850744ac6843fff8810cece0477f"
REDDIT_CLIENT_ID = "nDTxu8XLeNek6jdijItXQw"
REDDIT_CLIENT_SECRET = "VXxSVS8fRNL5jgalWW_dDvLX2JGc-w"
REDDIT_USER_AGENT = "CryptoSentimentBot/1.0 by CautiousPerception23"

# Utility function for API requests
def get_request(url: str, params: Dict[str, str]) -> Dict:
    """
    Makes a GET request and returns the JSON response.
    """
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error making request to {url}: {e}")

# Function to fetch data for top table of each coin
def fetch_crypto_data(coin: str, currency: str = "USD") -> Dict[str, float]:
    """
    Fetches current price, highest, lowest, and average prices for the last 30 days.
    Variables to fill:
    - coin (str): The cryptocurrency symbol. Example: "BTC"
    - currency (str, optional): The fiat currency. Default is "USD". Example: "EUR"
    Return value:
    - A dictionary with price statistics.
      Example: {"current_price": 50000.0, "highest": 60000.0, "lowest": 40000.0, "average": 50000.0}
    """
    url = f"{CRYPTOCOMPARE_BASE_URL}/histoday"
    params = {
        "fsym": coin.upper(),
        "tsym": currency.upper(),
        "limit": 30,
        "api_key": CRYPTOCOMPARE_API_KEY,
    }
    data = get_request(url, params)
    
    if data.get("Response") != "Success":
        raise RuntimeError(f"Error fetching data: {data.get('Message', 'Unknown error')}")
    
    prices = [day["close"] for day in data["Data"]["Data"]]
    return {
        "current_price": prices[-1],
        "highest": max(prices),
        "lowest": min(prices),
        "average": sum(prices) / len(prices),
    }

# Helper function for correlation matrix
def fetch_historical_prices(coin: str, currency: str = "USD", days: int = 30) -> List[float]:
    """
    Fetches historical closing prices for a cryptocurrency.
    """
    url = f"{CRYPTOCOMPARE_BASE_URL}/histoday"
    params = {
        "fsym": coin.upper(),
        "tsym": currency.upper(),
        "limit": days,
        "api_key": CRYPTOCOMPARE_API_KEY,
    }
    data = get_request(url, params)
    if data.get("Response") == "Success":
        return [day["close"] for day in data["Data"]["Data"]]
    raise RuntimeError(f"Error fetching historical prices: {data.get('Message', 'Unknown error')}")

# Helper function for correlation matrix
def equalize_length(prices_dict: Dict[str, List[float]]) -> Dict[str, List[float]]:
    """
    Equalizes the length of price lists to match the shortest one.
    """
    min_length = min(len(prices) for prices in prices_dict.values() if prices)
    return {coin: prices[:min_length] for coin, prices in prices_dict.items()}

# Function to fetch data for correlation matrix
def get_correlation_data() -> Dict[str, Dict[str, float]]:
    """
    Calculates the correlation matrix for BTC, ETH, and BNB over the last 30 days.
    Variables to fill:
    - None directly; the function internally fetches data for BTC, ETH, and BNB.
    Return value:
    - A nested dictionary representing the correlation matrix.
      Example: {"BTC": {"BTC": 1.0, "ETH": 0.8, "BNB": 0.75}, ...}
    """
    coins = ["BTC", "ETH", "BNB"]
    prices_dict = {
        coin: fetch_historical_prices(coin, "USD", 30) for coin in coins
    }
    prices_dict = equalize_length(prices_dict)
    df = pd.DataFrame(prices_dict)
    df.columns = [coin.upper() for coin in coins]
    return df.corr().to_dict()

# Function to fetch data for daily growth table
def fetch_daily_growth(coin: str, currency: str = "USD") -> Dict[str, float]:
    """
    Fetch and calculate the daily growth of a cryptocurrency for the last three days.
    Variables to fill:
    - coin (str): The cryptocurrency symbol. Example: "BNB"
    - currency (str, optional): The fiat currency. Default is "USD". Example: "USD"
    Return value:
    - A dictionary with dates as keys and growth percentages as values.
      Example: {"2024-11-23": 2.5, "2024-11-24": -1.8, "2024-11-25": 0.5}
    """
    today = datetime.utcnow()
    date_labels = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(3)]
    growth_data = {}

    url = f"{CRYPTOCOMPARE_BASE_URL}/histoday"
    params = {
        "fsym": coin.upper(),
        "tsym": currency.upper(),
        "limit": 3,
        "api_key": CRYPTOCOMPARE_API_KEY,
    }
    data = get_request(url, params)

    if data.get("Response") != "Success":
        raise RuntimeError(f"API Error: {data.get('Message', 'Unknown error')}")

    prices = [day["close"] for day in data["Data"]["Data"]]
    if len(prices) < 4:
        raise ValueError("Insufficient data to calculate daily growth.")

    for i in range(3):
        opening_price = prices[i]
        closing_price = prices[i + 1]
        growth_percentage = ((closing_price - opening_price) / opening_price) * 100
        growth_data[date_labels[i]] = round(growth_percentage, 2)

    return growth_data

# Helper for time span
def from_to_date(days=30):
    """
    Calculates the date range (from_date and to_date) based on the current date and the number of past days.
    """
    today = datetime.now()
    from_date = (today - timedelta(days=days)).strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')
    return {"from_date":from_date, "to_date":to_date}

# Fetching news from NewsAPI
def fetch_news_newsapi(query, days=30):
    """
    Fetches news articles related to the query from NewsAPI and returns their headlines.
    """
    from_to = from_to_date(days)

    newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    articles = newsapi.get_everything(
        q=query,
        from_param=from_to["from_date"],
        to=from_to["to_date"],
        language='en',
        sort_by='relevancy'
    )
    
    headlines = [article['title'] for article in articles['articles'] if article['title']]
    return pd.DataFrame(headlines, columns=['Title'])

# Fetching news from Currents API
def fetch_news_currents(query, days=30):
    """
    Fetches news articles related to the query from currents API and returns their headlines.
    """
    url = f"https://api.currentsapi.services/v1/search"
    params = {
        'apiKey': CURRENTS_API_KEY,
        'query': query,
        'language': 'en',
        'date': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
        'max': 100
    }
    
    response = requests.get(url, params=params).json()
    headlines = [article['title'] for article in response.get('news', [])]
    return pd.DataFrame(headlines, columns=['Title'])

# Fetching news from GNews API
def fetch_news_gnews(query, days=30):
    """
    Fetches news articles related to the query from gnews API and returns their headlines.
    """
    url = f"https://gnews.io/api/v4/search"
    params = {
        'q': query,
        'lang': 'en',
        'from': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
        'max': 100,
        'token': GNEWS_API_KEY
    }
    
    response = requests.get(url, params=params).json()
    headlines = [article['title'] for article in response.get('articles', [])]
    return pd.DataFrame(headlines, columns=['Title'])

# Fetching Reddit posts
def fetch_news_reddit(query, days=30):
    """
    Fetches subreddits related to the query from reddit API and returns their headlines.
    """
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                         client_secret=REDDIT_CLIENT_SECRET,
                         user_agent=REDDIT_USER_AGENT)
    
    posts = reddit.subreddit('all').search(query, time_filter='month', limit=100)
    headlines = [post.title for post in posts]
    return pd.DataFrame(headlines, columns=['Title'])

# Function to combine all news sources
def fetch_all_news(query, days=30):
    """
    Combines news headlines from multiple sources (NewsAPI, Currents, GNews, and Reddit).
    """
    news_data = pd.DataFrame()

    # Fetch news from all sources
    news_data = pd.concat([
        fetch_news_newsapi(query, days),
        fetch_news_currents(query, days),
        fetch_news_gnews(query, days),
        fetch_news_reddit(query, days),
    ], ignore_index=True)

    return news_data

# Front calling function
# Function to calculate sentiment score
def calculate_sentiment_score(coin_name):
    """
    Fetches news related to the query to calculate the overall sentiment score.
    Variables to fill:
    - query: The topic for which sentiment needs to be calculated (e.g., "Bitcoin").
    Process:
    - Fetch news headlines related to the query from NewsAPI.
    - Send the data to R for sentiment analysis using the 'syuzhet' library.
    Return value:
    - A float representing the overall sentiment score for the given query.
      Example: 0.45 (positive sentiment) or -0.3 (negative sentiment).
    """
    news_data = fetch_all_news(coin_name)
    if news_data.empty:
        return None

    conn = pyRserve.connect("localhost", 6312)
    conn.eval('library(syuzhet)')
    conn.r.news_titles = news_data['Title'].tolist()

    sentiment_score = conn.eval("""
    mean(get_sentiment(unlist(news_titles), method = 'syuzhet'), na.rm = TRUE)
    """)

    conn.close()

    return sentiment_score

# Front calling function
# Function to calculate sentiment distribution
def calculate_sentiment_distribution(coin_name):
    """
    Fetches news related to the query to calculate sentiment distribution (positive, negative, neutral).
    Variables to fill:
    - query: The topic for which sentiment distribution needs to be calculated (e.g., "Bitcoin").
    Process:
    - Fetch news headlines related to the query from NewsAPI.
    - Send the data to R for detailed sentiment classification using the 'syuzhet' library.
    - Calculate the percentage of positive, negative, and neutral sentiments.
    Return value:
    - A dictionary with sentiment distribution percentages.
      Example: {"Positive": 60.0, "Negative": 25.0, "Neutral": 15.0}.
    """
    news_data = fetch_all_news(coin_name)
    if news_data.empty:
        return {"positive": 0, "neutral": 0, "negative": 0}

    conn = pyRserve.connect("localhost", 6312)
    conn.eval('library(syuzhet)')
    conn.r.news_titles = news_data['Title'].tolist()

    sentiment_distribution = conn.eval("""
    calculate_distribution <- function(titles) {
        scores <- get_sentiment(titles, method = 'syuzhet')
        positive_count <- sum(scores > 0.1)
        neutral_count <- sum(scores >= -0.1 & scores <= 0.1)
        negative_count <- sum(scores < -0.1)
        total <- length(scores)
        if (total == 0) {
            return(list(positive = 0, neutral = 0, negative = 0))
        }
        list(
            positive = round((positive_count / total) * 100, 2),
            neutral = round((neutral_count / total) * 100, 2),
            negative = round((negative_count / total) * 100, 2)
        )
    }
    calculate_distribution(unlist(news_titles))
    """)

    conn.close()

    # Convert R list to Python dictionary
    sentiment_distribution_dict = {
        "positive": sentiment_distribution['positive'],
        "neutral": sentiment_distribution['neutral'],
        "negative": sentiment_distribution['negative']
    }

    return sentiment_distribution_dict

