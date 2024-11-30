import os
import sys
from typing import Dict, List
import helpers
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from constants import CRYPTOCOMPARE_BASE_URL

class CryptoMarketData:
    """
    A class to interact with the CryptoCompare API for fetching and formatting cryptocurrency data.
    """

    BASE_URL = f"{CRYPTOCOMPARE_BASE_URL}"

    def fetch_current_prices(self, coin_ids: List[str], vs_currency: str = "USD") -> Dict:
        """
        Fetch the current prices of multiple cryptocurrencies from CryptoCompare.
        Args:
            coin_ids (List[str]): A list of cryptocurrency symbols (e.g., ["BTC", "ETH", "DOGE"]).
            vs_currency (str): The fiat or crypto currency to compare against (default is "USD").
        Returns:
            Dict: A dictionary with cryptocurrency symbols as keys and their current prices as values.
        """
        url = f"{self.BASE_URL}/pricemultifull"
        params = {"fsyms": ",".join(coin_ids), "tsyms": vs_currency.upper()}

        data = helpers.get_request(url, params)  # Use the reusable helper function
        raw_data = data.get("RAW", {})

        # Process each coin to extract the price
        prices = {}
        for coin in coin_ids:
            coin_data = raw_data.get(coin.upper(), {}).get(vs_currency.upper(), {})
            if not coin_data:
                prices[coin.upper()] = {"error": f"Data for {coin} not available"}
            else:
                prices[coin.upper()] = {
                    "coin": coin.upper(),
                    "current_price": round(coin_data.get("PRICE"), 2)
                }

        return prices

    def fetch_crypto_data(self, coins: List[str], vs_currency: str = "USD") -> Dict:
        """
        Fetch cryptocurrency data for a list of coins from CryptoCompare.
        Args:
            coins (List[str]): A list of cryptocurrency symbols (e.g., ["BTC", "ETH"]).
            vs_currency (str): The fiat or crypto currency to compare against (default is "USD").
        Returns:
            Dict: A dictionary with formatted data for each coin, keyed by coin symbol.
        """
        url = f"{self.BASE_URL}/pricemultifull"
        params = {"fsyms": ",".join(coin.upper() for coin in coins), "tsyms": vs_currency.upper()}

        raw_data = helpers.get_request(url, params)  # Use the reusable helper function
        if "RAW" not in raw_data:
            return {"error": "Failed to fetch data from CryptoCompare"}

        formatted_data = {}
        for coin in coins:
            coin_data = raw_data["RAW"].get(coin.upper(), {}).get(vs_currency.upper(), {})
            if not coin_data:
                formatted_data[coin.upper()] = {"error": f"Data for {coin} not available"}
            else:
                formatted_data[coin.upper()] = {
                    "coin": coin.upper(),
                    "current_price": round(coin_data.get("PRICE"), 2),
                    "24h_change": round(coin_data.get("CHANGE24HOUR", 0), 2) if "CHANGE24HOUR" in coin_data else None,
                    "market_cap": helpers.format_large_number(round(coin_data.get("MKTCAP"), 2)),
                    "24h_volume": helpers.format_large_number(round(coin_data.get("TOTALVOLUME24H"), 2)),
                    "supply": helpers.format_large_number(round(coin_data.get("SUPPLY"), 2))
                }

        return formatted_data