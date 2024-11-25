import requests
from typing import Dict

BASE_URL = "https://api.coingecko.com/api/v3"

def fetch_current_price(coin: str, currency: str = "usd") -> float:
    """
    Fetches the current price of the specified cryptocurrency.
    """
    url = f"{BASE_URL}/simple/price"
    params = {
        "ids": coin,
        "vs_currencies": currency,
        "include_market_cap": "true",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()[coin][currency]

def fetch_monthly_data(coin: str, currency: str = "usd") -> Dict[str, float]:
    """
    Fetches the highest, lowest, and average prices for the past 30 days.
    """
    url = f"{BASE_URL}/coins/{coin}/market_chart"
    params = {"vs_currency": currency, "days": 30}
    response = requests.get(url, params=params)
    response.raise_for_status()

    prices = [entry[1] for entry in response.json()["prices"]]
    return {
        "highest": max(prices),
        "lowest": min(prices),
        "average": sum(prices) / len(prices),
    }

# Function to fetch data for ui
def fetch_crypto_data(coin: str, currency: str = "usd") -> Dict[str, float]:
    """
    Fetches current and monthly historical cryptocurrency data.
    """
    return {
        "current_price": fetch_current_price(coin, currency),
        **fetch_monthly_data(coin, currency)
    }
