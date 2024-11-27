import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import pyRserve
from newsapi import NewsApiClient
import praw

# Constants
CRYPTOCOMPARE_BASE_URL = "https://min-api.cryptocompare.com/data/v2"
CRYPTOCOMPARE_API_KEY = "2ade0bdf98ef9e6f719bee6b0e58bf88497fdaaa1dc7e3948347ba1d65304981"
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

# Front calling function
# Function to fetch current price of a coin
def get_current_price(coin: str, currency: str = "USD") -> float:
    """
    Fetches the current price of the specified cryptocurrency.
    Variables to fill:
    - coin (str): The cryptocurrency symbol. Example: "BTC"
    - currency (str, optional): The fiat currency. Default is "USD". Example: "EUR"
    Return value:
    - A float representing the current price of the cryptocurrency in the specified fiat currency.
      Example: 50000.0
    """
    url = f"https://min-api.cryptocompare.com/data/price"
    params = {
        "fsym": coin.upper(),
        "tsyms": currency.upper(),
        "api_key": CRYPTOCOMPARE_API_KEY,
    }
    data = get_request(url, params)
    return data.get(currency.upper(), 0.0)

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
    
    # Get current price using the new function
    current_price = get_current_price(coin, currency)
    
    return {
        "current_price": current_price,
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

# Front calling function
# Fetch data for price over time graph
def fetch_crypto_prices(coin: str, currency: str = "USD", limit: int = 60) -> Dict:
    """
    Fetches price data for a given cryptocurrency.
    Parameters:
    - coin (str): Cryptocurrency symbol (e.g., "BTC").
    - currency (str): Fiat currency symbol (e.g., "USD"). Default is "USD".
    - limit (int): Number of data points to fetch. Default is 60.
    Process:
    - Fetch historical minute-level price data using CryptoCompare's API.
    - Extract the 'time' and 'close' (price) values from the API response.
    - If `limit=1`, return a single timestamp and price.
    - If `limit>1`, return lists of timestamps and prices.
    Returns:
    - Dictionary containing 'time' and 'price'. For limit=1, returns single values.
      Example (limit=60): {'time': [...], 'price': [...]}
      Example (limit=1): {'time': <int>, 'price': <float>}
    """
    url = f"{CRYPTOCOMPARE_BASE_URL}/histominute"
    params = {
        "fsym": coin.upper(),
        "tsym": currency.upper(),
        "limit": limit,
        "api_key": CRYPTOCOMPARE_API_KEY,
    }

    # API request and error handling
    response = get_request(url, params)
    if response.get("Response") != "Success":
        raise RuntimeError(f"Error fetching data: {response.get('Message', 'Unknown error')}")

    # Extract relevant data
    data = response["Data"]["Data"]
    time_data, price_data = zip(*((entry["time"], entry["close"]) for entry in data))

    # Return single entry if limit=1, otherwise full lists
    if limit == 1:
        return {
            "time": time_data[-1],
            "price": price_data[-1]
        }
    return {
        "time": list(time_data), 
        "price": list(price_data)
    }

# Helper fetch data for indicators
def fetch_crypto_data(symbol, api_key, currency='USD', limit=100, interval='day'):
    """
    Fetch historical price data for a cryptocurrency from CryptoCompare.
    """
    url = f"https://min-api.cryptocompare.com/data/v2/histo{interval}"
    params = {
        'fsym': symbol,
        'tsym': currency,
        'limit': limit,
        'api_key': api_key
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        prices = [point['close'] for point in data['Data']['Data']]
        timestamps = [datetime.utcfromtimestamp(point['time']).isoformat() for point in data['Data']['Data']]
        
        return {'prices': prices, 'timestamps': timestamps}
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Helper cut nan values
def cut_nans(data_dict):
    """
    Remove leading NaN values from the data dictionary.
    """
    max_nans = 0
    for key, value in data_dict.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                max_nans = max(max_nans, len([v for v in sub_value if pd.isna(v)]))
        else:
            max_nans = max(max_nans, len([v for v in value if pd.isna(v)]))
    
    cut_data = {'timestamps': data_dict['timestamps'][max_nans:]}
    for key, value in data_dict.items():
        if isinstance(value, dict):
            cut_data[key] = {sub_key: sub_value[max_nans:] for sub_key, sub_value in value.items()}
        else:
            cut_data[key] = value[max_nans:]
    return cut_data

# Helper function to calculate indicators using R
def calculate_indicators(data, timestamps, ema_period=14, sma_period=14, rsi_period=14, macd_params=(12, 26, 9)):
    """
    Calculate EMA, SMA, RSI, and MACD using R via PyRserve.
    """
    try:
        conn = pyRserve.connect("localhost", 6312)
        
        conn.r.data = data
        conn.r.ema_period = ema_period
        conn.r.sma_period = sma_period
        conn.r.rsi_period = rsi_period
        conn.r.macd_fast = macd_params[0]
        conn.r.macd_slow = macd_params[1]
        conn.r.macd_signal = macd_params[2]

        r_script = """
        library(TTR)
        data <- as.numeric(data)
        ema <- EMA(data, n=ema_period)
        sma <- SMA(data, n=sma_period)
        rsi <- RSI(data, n=rsi_period)
        macd_matrix <- MACD(data, nFast=macd_fast, nSlow=macd_slow, nSig=macd_signal)
        macd <- list(
            macd = macd_matrix[, "macd"],
            signal = macd_matrix[, "signal"]
        )
        list(
            ema = ema,
            sma = sma,
            rsi = rsi,
            macd = macd
        )
        """
        indicators = conn.r(r_script)
        
        result = {
            'timestamps': timestamps,
            'EMA': list(indicators['ema']),
            'SMA': list(indicators['sma']),
            'RSI': list(indicators['rsi']),
            'MACD': {
                'MACD': list(indicators['macd']['macd']),
                'Signal': list(indicators['macd']['signal'])
            }
        }
        return cut_nans(result)
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        print(f"Error calculating indicators: {e}")
        return None

# Front caliing function
def get_crypto_data_with_indicators(symbol, currency='USD', limit=100, interval='day', 
                                     ema_period=14, sma_period=14, rsi_period=14, 
                                     macd_params=(12, 26, 9), api_key=CRYPTOCOMPARE_API_KEY):
    """
    Fetch historical price data for a cryptocurrency and calculate indicators.
    """
    data = fetch_crypto_data(symbol, api_key, currency, limit, interval)
    if not data:
        return None
    
    prices = data['prices']
    timestamps = data['timestamps']
    prices = [price for price in prices if isinstance(price, (int, float)) and price is not None]
    
    indicators = calculate_indicators(prices, timestamps, ema_period, sma_period, rsi_period, macd_params)
    return indicators