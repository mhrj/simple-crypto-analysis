import pyRserve
from helpers import get_request, convert_timestamps_to_dates
from constants import CRYPTOCOMPARE_BASE_URL

class CryptoFanChartGenerator:
    """
    Class to generate historical and fan chart data for cryptocurrencies.
    """

    def __init__(self, currency="USD"):
        """
        Initialize the generator with default coin and currency.

        Args:
            coin (str): Cryptocurrency symbol (default: "BTC").
            currency (str): Fiat currency symbol (default: "USD").
        """
        self.currency = currency

    def fetch_historical_data(self, coin="BTC", days=30):
        """
        Fetch historical data for the cryptocurrency.

        Args:
            days (int): Number of past days to fetch (default: 30).

        Returns:
            dict: Contains:
                - "timestamps": List of historical timestamps.
                - "close": List of historical closing prices.
                - "returns": List of daily returns (log-returns).
        """
        url = f"{CRYPTOCOMPARE_BASE_URL}/v2/histoday"
        params = {"fsym": coin, "tsym": self.currency, "limit": days - 1}
        response = get_request(url, params=params)

        data = response["Data"]["Data"]
        timestamps = [item["time"] for item in data]
        close_prices = [item["close"] for item in data]
        returns = [(close_prices[i + 1] - close_prices[i]) / close_prices[i] for i in range(len(close_prices) - 1)]

        return {"timestamps": timestamps, "close": close_prices, "returns": returns}

    def generate_fan_chart(self, coin="BTC", historical_days=30, prediction_days=30, simulations=1000):
        """
        Generate fan chart data combining historical prices and Monte Carlo predictions.

        Args:
            historical_days (int): Number of past days to include (default: 30).
            prediction_days (int): Number of future days to predict (default: 30).
            simulations (int): Number of Monte Carlo simulations (default: 1000).

        Returns:
            dict: Contains:
                - "cryptocurrency": Coin name.
                - "actual_data": Historical data with timestamps and values.
                - "projection_data": Predicted data with timestamps, mean, and confidence intervals.
        """
        # Fetch historical data
        historical_data = self.fetch_historical_data(historical_days)
        timestamps = historical_data["timestamps"]
        close_prices = historical_data["close"]
        initial_price = close_prices[-1]

        # Calculate historical returns for mu and sigma
        mu = sum(historical_data["returns"]) / len(historical_data["returns"])  # Mean return
        sigma = (sum([(x - mu) ** 2 for x in historical_data["returns"]]) / len(historical_data["returns"])) ** 0.5  # Std. deviation

        # Connect to Rserve
        conn = pyRserve.connect("localhost", 6312)
        try:
            # Send parameters to R
            conn.r.initial_price = initial_price
            conn.r.mu = mu
            conn.r.sigma = sigma
            conn.r.days = prediction_days
            conn.r.simulations = simulations

            # Perform Monte Carlo simulation in R
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
            ''')
            
            # Calculate percentiles for each day
            conn.r('percentiles <- apply(paths, 2, function(x) quantile(x, probs = c(0.1, 0.5, 0.9)))')
            percentiles = conn.r('percentiles')

            # Prepare projection timestamps
            projection_timestamps = [timestamps[-1] + i * 86400 for i in range(1, prediction_days + 1)]

            # Prepare result in specified format
            result = {
                "cryptocurrency": coin,
                "actual_data": {
                    "timestamps": convert_timestamps_to_dates(timestamps),
                    "values": close_prices
                },
                "projection_data": {
                    "timestamps": convert_timestamps_to_dates(projection_timestamps),
                    "mean": [round(v, 2) for v in percentiles[1]],
                    "confidence_intervals": [
                        {
                            "ci": 0.5,
                            "upper": [round(v, 2) for v in percentiles[2]],
                            "lower": [round(v, 2) for v in percentiles[0]]
                        },
                        {
                            "ci": 1.0,
                            "upper": [round(v + 0.5, 2) for v in percentiles[2]],
                            "lower": [round(v - 0.5, 2) for v in percentiles[0]]
                        }
                    ]
                }
            }
            return result

        finally:
            # Close Rserve connection
            conn.close()