import os
import sys
import pyRserve
import pandas as pd
from datetime import datetime
from typing import Dict, List, Union
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from constants import (CRYPTOCOMPARE_BASE_URL, CRYPTOCOMPARE_API_KEY)
import helpers

class CryptoAnalysis:
    """
    Provides functionalities for fetching cryptocurrency data.
    """
    @staticmethod
    def _fetch_historical_prices(coin: str, currency: str = "USD", days: int = 30) -> List[float]:
        """
        Fetches historical closing prices for a cryptocurrency.
        """
        url = f"{CRYPTOCOMPARE_BASE_URL}/v2/histoday"
        params = {
            "fsym": coin.upper(),
            "tsym": currency.upper(),
            "limit": days,
            "api_key": CRYPTOCOMPARE_API_KEY
        }
        data = helpers.get_request(url, params)
        if data.get("Response") == "Success":
            return [day["close"] for day in data["Data"]["Data"]]
        raise RuntimeError(f"Error fetching historical prices: {data.get('Message', 'Unknown error')}")

    @staticmethod
    def _cut_nans(data_dict: Dict) -> Dict:
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
    
    def get_correlation_matrix(coin_ids: list, vs_currency: str = "USD", days: int = 30) -> Dict:
        """
        Fetch historical price data for multiple cryptocurrencies and calculate the correlation matrix.
        
        Args:
            coin_ids (list): List of cryptocurrency symbols (e.g., ["BTC", "ETH", "BNB"]).
            vs_currency (str): The fiat currency to compare against (default is "USD").
            days (int): Number of days of historical data to fetch (default is 30).
            
        Returns:
            Dict: A correlation matrix for the specified cryptocurrencies as a nested dictionary.
        """
        base_url = f"{CRYPTOCOMPARE_BASE_URL}/v2/histoday"
        historical_prices = {}
        
        for coin in coin_ids:
            params = {
                "fsym": coin.upper(),
                "tsym": vs_currency.upper(),
                "limit": days - 1  # CryptoCompare returns `limit + 1` days
            }
            data = helpers.get_request(base_url, params)
            if data.get("Response") == "Success":
                prices = [day["close"] for day in data["Data"]["Data"]]
                historical_prices[coin] = prices
            else:
                print(f"Error fetching data for {coin}: {data.get('Message', 'Unknown error')}")
        
        # Create a DataFrame from the historical prices
        df = pd.DataFrame(historical_prices)
        
        # Compute the correlation matrix
        correlation_matrix = df.corr()
        
        # Return the correlation matrix as a dictionary
        return correlation_matrix.to_dict()

    def calculate_daily_growth(coin_id: str, vs_currency: str = "USD") -> Dict:
        """
        Calculate the percentage growth of a cryptocurrency over the last three days, including the dates.

        Args:
            coin_id (str): The cryptocurrency symbol (e.g., "BTC").
            vs_currency (str): The fiat or crypto currency to compare against (default is "USD").
            
        Returns:
            Dict: A dictionary with the growth percentages for each day, overall growth, and the dates.
        """
        base_url = "https://min-api.cryptocompare.com/data/v2/histoday"
        params = {
            "fsym": coin_id.upper(),
            "tsym": vs_currency.upper(),
            "limit": 3
        }

        # Fetch historical data
        data = helpers.get_request(base_url, params)
        if data.get("Response") != "Success":
            return {"error": data.get("Message", "Unknown error")}
        
        # Extract the timestamps and closing prices
        timestamps = [day["time"] for day in data["Data"]["Data"]]
        prices = [day["close"] for day in data["Data"]["Data"]]

        # Ensure we have at least 4 data points (to calculate three intervals)
        if len(prices) < 4:
            return {"error": "Insufficient data to calculate three-day growth"}

        # Convert timestamps to dates
        dates = [datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d') for ts in timestamps]

        # Calculate daily growth percentages
        growth = []
        for i in range(1, len(prices)):
            day_growth = ((prices[i] - prices[i - 1]) / prices[i - 1]) * 100
            growth.append(round(day_growth, 2))

        return {
            "dates": dates[1:],
            "daily_growth": growth,
        }

    def get_current_price(coin: str, currency: str = "USD") -> float:
        """
        Fetches the current price of the specified cryptocurrency.
        """
        url = f"{CRYPTOCOMPARE_BASE_URL}/price"
        params = {
            "fsym": coin.upper(),
            "tsyms": currency.upper(),
            "api_key": CRYPTOCOMPARE_API_KEY
        }
        data = helpers.get_request(url, params)
        return data.get(currency.upper(), 0.0)

    def fetch_crypto_price_data(coin: str, currency: str = "USD") -> Dict[str, float]:
        """
        Fetches price statistics for the last 30 days for a cryptocurrency.
        """
        prices = CryptoAnalysis._fetch_historical_prices(coin, currency, 30)
        return {
            "highest": max(prices),
            "lowest": min(prices),
            "average": round(sum(prices) / len(prices), 2)
        }

    def fetch_crypto_prices_over_time(coin: str, limit: int = 60, currency: str = "USD") -> Dict:
        """
        Fetches price data for a given cryptocurrency over a time period.
        """
        url = f"{CRYPTOCOMPARE_BASE_URL}/v2/histominute"
        params = {
            "fsym": coin.upper(),
            "tsym": currency.upper(),
            "limit": limit,
            "api_key": CRYPTOCOMPARE_API_KEY
        }
        response = helpers.get_request(url, params)
        if response.get("Response") != "Success":
            raise RuntimeError(f"Error fetching data: {response.get('Message', 'Unknown error')}")
        data = response["Data"]["Data"]
        time_data, price_data = zip(*((entry["time"], entry["close"]) for entry in data))
        return {"timestamps": helpers.convert_timestamps_to_clock(list(time_data)), "prices": list(price_data)}

    def calculate_indicators(coin: str, limit_days: int = 100, currency: str = "USD", calculate_for: int = 1,
                            ema_period: int = 14, sma_period: int = 14) -> Union[Dict, None]:
        """
        Calculate EMA, SMA.
        """
        try:
            # Fetch historical data for the full range
            historical_data = CryptoAnalysis._fetch_historical_prices(coin, currency, days=limit_days)
            
            # Ensure we have enough data for calculations
            if len(historical_data) < ema_period:
                raise ValueError("Not enough data for the specified indicator periods.")

            # Extract the last `calculate_for` days of data
            data_for_calculation = historical_data[-(calculate_for * 24 * 60):]
            timestamps = list(range(len(data_for_calculation)))

            # Connect to Rserve and perform calculations
            conn = pyRserve.connect("localhost", 6312)
            conn.r.data = data_for_calculation
            conn.r.ema_period = ema_period
            conn.r.sma_period = sma_period

            r_script = """
            library(TTR)
            data <- as.numeric(data)
            ema <- EMA(data, n=ema_period)
            sma <- SMA(data, n=sma_period)
            list(
                ema = ema,
                sma = sma
            )
            """
            indicators = conn.r(r_script)

            # Format results and return
            result = {
                'timestamps': timestamps,
                'prices': historical_data,
                'EMA': list(indicators['ema']),
                'SMA': list(indicators['sma'])
            }
            return CryptoAnalysis._cut_nans(result)
        except Exception as e:
            if 'conn' in locals():
                conn.close()
            print(f"Error calculating indicators: {e}")
            return None
        