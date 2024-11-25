import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List

# Constants
CRYPTOCOMPARE_BASE_URL = "https://min-api.cryptocompare.com/data/v2"
API_KEY = "2ade0bdf98ef9e6f719bee6b0e58bf88497fdaaa1dc7e3948347ba1d65304981"

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
        "api_key": API_KEY,
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
        "api_key": API_KEY,
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
        "api_key": API_KEY,
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
