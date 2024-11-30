import os
import sys
import pyRserve
from typing import Dict, List
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
import helpers
from constants import CRYPTOCOMPARE_BASE_URL

class CryptoFanChartGenerator:
    """
    Provides functionalities for generating fan charts and analyzing cryptocurrency data.
    """

    @staticmethod
    def _fetch_historical_data(coin: str, currency: str = "USD", days: int = 30) -> Dict[str, List[float]]:
        """
        Fetches historical data for a cryptocurrency.

        Args:
            coin (str): Cryptocurrency symbol (e.g., "BTC").
            currency (str): Fiat currency symbol (default is "USD").
            days (int): Number of days of historical data to fetch.

        Returns:
            Dict: Contains historical timestamps, close prices, and log returns.
        """
        url = f"{CRYPTOCOMPARE_BASE_URL}/v2/histoday"
        params = {
            "fsym": coin.upper(),
            "tsym": currency.upper(),
            "limit": days - 1,
        }
        data = helpers.get_request(url, params)

        if data.get("Response") == "Success":
            historical_data = data["Data"]["Data"]
            timestamps = [entry["time"] for entry in historical_data]
            close_prices = [entry["close"] for entry in historical_data]
            returns = [(close_prices[i + 1] - close_prices[i]) / close_prices[i] for i in range(len(close_prices) - 1)]
            return {"timestamps": timestamps, "close": close_prices, "returns": returns}

        raise RuntimeError(f"Error fetching historical data: {data.get('Message', 'Unknown error')}")

    @staticmethod
    def generate_fan_chart(coin: str, currency: str = "USD", historical_days: int = 30, prediction_days: int = 30,
                           simulations: int = 1000) -> Dict:
        """
        Generate fan chart data based on historical and simulated data.

        Args:
            coin (str): Cryptocurrency symbol (e.g., "BTC").
            currency (str): Fiat currency symbol (default is "USD").
            historical_days (int): Number of past days to include.
            prediction_days (int): Number of future days to predict.
            simulations (int): Number of Monte Carlo simulations.

        Returns:
            Dict: Fan chart data including historical and projection data.
        """
        historical_data = CryptoFanChartGenerator._fetch_historical_data(coin, currency, historical_days)
        timestamps = historical_data["timestamps"]
        close_prices = historical_data["close"]
        returns = historical_data["returns"]

        if not close_prices:
            raise ValueError("Insufficient historical data for fan chart generation.")

        initial_price = close_prices[-1]
        mu = sum(returns) / len(returns)  # Mean log-return
        sigma = (sum([(x - mu) ** 2 for x in returns]) / len(returns)) ** 0.5  # Standard deviation

        conn = pyRserve.connect("localhost", 6312)
        try:
            # Send parameters to R
            conn.r.initial_price = initial_price
            conn.r.mu = mu
            conn.r.sigma = sigma
            conn.r.days = prediction_days
            conn.r.simulations = simulations

            conn.r('''
            simulate_prices <- function(initial_price, mu, sigma, days, simulations) {
                paths <- matrix(0, nrow = simulations, ncol = days)
                for (i in 1:simulations) {
                    daily_returns <- rnorm(days, mean = mu, sd = sigma)
                    price_path <- initial_price * cumprod(1 + daily_returns)
                    paths[i, ] <- price_path
                }
                return(paths)
            }
            paths <- simulate_prices(initial_price, mu, sigma, days, simulations)
            percentiles <- apply(paths, 2, function(x) quantile(x, probs = c(0.1, 0.5, 0.9)))
            ''')

            percentiles = conn.r('percentiles')
            projection_timestamps = [timestamps[-1] + i * 86400 for i in range(1, prediction_days + 1)]

            return {
                "cryptocurrency": coin,
                "actual_data": {
                    "timestamps": helpers.convert_timestamps_to_dates(timestamps),
                    "values": close_prices,
                },
                "projection_data": {
                    "timestamps": helpers.convert_timestamps_to_dates(projection_timestamps),
                    "mean": [round(v, 2) for v in percentiles[1]],
                    "confidence_intervals": [
                        {
                            "ci": 0.5,
                            "upper": [round(v, 2) for v in percentiles[2]],
                            "lower": [round(v, 2) for v in percentiles[0]],
                        },
                        {
                            "ci": 1.0,
                            "upper": [round(v + 0.5, 2) for v in percentiles[2]],
                            "lower": [round(v - 0.5, 2) for v in percentiles[0]],
                        },
                    ],
                },
            }

        finally:
            conn.close()