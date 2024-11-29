import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
import helpers
from constants import (CRYPTOCOMPARE_BASE_URL, CRYPTOCOMPARE_API_KEY)

class CryptoMarket:
    """
    Handles cryptocurrency market data using CryptoCompare API.
    """

    def __init__(self):
        self.market_cap_url = f"{CRYPTOCOMPARE_BASE_URL}/top/mktcapfull"
        self.coin_price_url = f"{CRYPTOCOMPARE_BASE_URL}/pricemultifull"
        self.api_key = CRYPTOCOMPARE_API_KEY

    def fetch_global_market_data():
        """
        Fetch global cryptocurrency market cap and 24-hour volume data.
        Returns:
            dict: Parsed global market data or None in case of failure.
        """
        params = {"limit": 10, "tsym": "USD", "api_key": CryptoMarket.api_key}
        data = helpers.get_request(CryptoMarket.market_cap_url, params)
        if not data:
            print("Failed to fetch market cap data.")
            return None

        try:
            # Sum market cap and volume for all listed cryptocurrencies
            total_market_cap = sum(coin["RAW"]["USD"]["MKTCAP"] for coin in data.get("Data", []))
            total_24h_volume = sum(coin["RAW"]["USD"]["TOTALVOLUME24H"] for coin in data.get("Data", []))
            return {
                "total_market_cap_usd": total_market_cap,
                "total_24h_volume_usd": total_24h_volume,
            }
        except KeyError:
            print("Error parsing market cap data.")
            return None

    def fetch_coin_data():
        """
        Fetch coin-specific data for BTC, ETH, and BNB.
        Returns:
            dict: Parsed coin data or None in case of failure.
        """
        params = {
            "fsyms": "BTC,ETH,BNB",
            "tsyms": "USD",
            "api_key": CryptoMarket.api_key,
        }
        data = helpers.get_request(CryptoMarket.coin_price_url, params)
        if not data:
            print("Failed to fetch coin data.")
            return None

        try:
            return data["RAW"]
        except KeyError:
            print("Error parsing coin data.")
            return None

    @staticmethod
    def calculate_top_gainer(coins_data):
        """
        Determine the top gainer from the provided coin data.
        Args:
            coins_data (dict): Cryptocurrency data with price change percentages.
        Returns:
            tuple: (Coin name, Percentage change) or (None, None) in case of failure.
        """
        try:
            changes = {
                symbol: coin_data["USD"]["CHANGEPCT24HOUR"]
                for symbol, coin_data in coins_data.items()
            }
            top_gainer = max(changes.items(), key=lambda item: item[1])
            return top_gainer[0], round(top_gainer[1], 2)
        except (KeyError, ValueError):
            print("Error calculating top gainer.")
            return None, None

    def fetch_market_summary():
        """
        Fetch and summarize the global cryptocurrency market data.
        Returns:
            dict: Market summary with market cap, 24h volume, and top gainer.
        """
        # Fetch global market data
        global_data = CryptoMarket.fetch_global_market_data()
        if not global_data:
            return {"error": "Failed to fetch global market data."}

        # Fetch coin-specific data for BTC, ETH, and BNB
        coins_data = CryptoMarket.fetch_coin_data()
        if not coins_data:
            return {"error": "Failed to fetch coin data."}

        # Calculate the top gainer
        top_gainer_coin, top_gainer_change = CryptoMarket.calculate_top_gainer(coins_data)

        # Return the final summary
        return {
            "market_cap_usd": helpers.format_large_number(global_data["total_market_cap_usd"]),
            "volume_24h_usd": helpers.format_large_number(global_data["total_24h_volume_usd"]),
            "top_gainer": {"coin": top_gainer_coin, "change": top_gainer_change}
        }