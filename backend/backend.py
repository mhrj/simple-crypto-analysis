import requests
import pandas as pd
from typing import Dict, List

# Constants
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
CRYPTOCOMPARE_BASE_URL = "https://min-api.cryptocompare.com/data/v2"
API_KEY = "2ade0bdf98ef9e6f719bee6b0e58bf88497fdaaa1dc7e3948347ba1d65304981"

# Utility functions for API requests
def get_request(url: str, params: Dict[str, str]) -> Dict:
    """
    Makes a GET request and returns the JSON response.
    Args:
        url (str): Endpoint URL.
        params (Dict[str, str]): Query parameters.
    Returns:
        Dict: Parsed JSON response.
    """
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error making request to {url}: {e}")

# CoinGecko functions
def fetch_current_price(coin: str, currency: str = "usd") -> float:
    """
    Fetches the current price of a cryptocurrency from CoinGecko.
    Args:
        coin (str): Cryptocurrency ID (e.g., 'bitcoin', 'ethereum').
        currency (str): Target currency (default is 'usd').
    Returns:
        float: Current price.
    """
    url = f"{COINGECKO_BASE_URL}/simple/price"
    params = {
        "ids": coin,
        "vs_currencies": currency,
        "include_market_cap": "true",
    }
    data = get_request(url, params)
    return data[coin][currency]

def fetch_monthly_data(coin: str, currency: str = "usd") -> Dict[str, float]:
    """
    Fetches the highest, lowest, and average prices for the past 30 days.
    Args:
        coin (str): Cryptocurrency ID.
        currency (str): Target currency (default is 'usd').
    Returns:
        Dict[str, float]: Dictionary with highest, lowest, and average prices.
    """
    url = f"{COINGECKO_BASE_URL}/coins/{coin}/market_chart"
    params = {"vs_currency": currency, "days": 30}
    data = get_request(url, params)
    prices = [entry[1] for entry in data["prices"]]
    return {
        "highest": max(prices),
        "lowest": min(prices),
        "average": sum(prices) / len(prices),
    }

# Front calling function
# Function to fetch data for top table of each coin
def fetch_crypto_data(coin: str, currency: str = "usd") -> Dict[str, float]:
    """
    Fetches current and historical cryptocurrency data.
    Args:
        coin (str): Cryptocurrency ID.
        currency (str): Target currency.
    Returns:
        Dict[str, float]: Combined current and historical data.
    """
    return {
        "current_price": fetch_current_price(coin, currency),
        **fetch_monthly_data(coin, currency),
    }

# CryptoCompare functions
def fetch_historical_prices(coin: str, currency: str = "USD", days: int = 30) -> List[float]:
    """
    Fetches historical closing prices for a cryptocurrency.
    Args:
        coin (str): Cryptocurrency symbol (e.g., 'BTC', 'ETH').
        currency (str): Target currency (default is 'USD').
        days (int): Number of days to fetch (default is 30).
    Returns:
        List[float]: List of closing prices.
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

def equalize_length(prices_dict: Dict[str, List[float]]) -> Dict[str, List[float]]:
    """
    Equalizes the length of price lists to match the shortest one.
    Args:
        prices_dict (Dict[str, List[float]]): Dictionary of price lists.
    Returns:
        Dict[str, List[float]]: Equalized dictionary of price lists.
    """
    min_length = min(len(prices) for prices in prices_dict.values() if prices)
    return {coin: prices[:min_length] for coin, prices in prices_dict.items()}

def calculate_correlation_matrix(coins: List[str], currency: str = "USD", days: int = 30) -> Dict[str, Dict[str, float]]:
    """
    Calculates the correlation matrix for cryptocurrencies.
    Args:
        coins (List[str]): List of cryptocurrency symbols.
        currency (str): Target currency.
        days (int): Number of days to fetch.
    Returns:
        Dict[str, Dict[str, float]]: Correlation matrix as a dictionary.
    """
    prices_dict = {coin: fetch_historical_prices(coin, currency, days) for coin in coins}
    prices_dict = equalize_length(prices_dict)
    df = pd.DataFrame(prices_dict)
    df.columns = [coin.upper() for coin in coins]
    return df.corr().to_dict()

# Front calling function
# Function to fetch data for correlation matrix
def get_correlation_data() -> Dict[str, Dict[str, float]]:
    """
    Gets correlation data for BTC, ETH, and BNB.
    Returns:
        Dict[str, Dict[str, float]]: Correlation matrix.
    """
    coins = ["BTC", "ETH", "BNB"]
    return calculate_correlation_matrix(coins)
