import pyRserve
import requests

def fetch_historical_data(coin, currency, days):
    """
    Fetch historical data for the specified cryptocurrency.

    Args:
        coin (str): Cryptocurrency symbol (e.g., "BTC").
        currency (str): Fiat currency symbol (e.g., "USD").
        days (int): Number of past days to fetch.

    Returns:
        dict: Contains:
            - "close": List of historical closing prices.
            - "returns": List of daily returns (log-returns).
    """
    url = f"https://min-api.cryptocompare.com/data/v2/histoday"
    params = {"fsym": coin, "tsym": currency, "limit": days - 1}  # Fetch `days` of data
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()["Data"]["Data"]
    close_prices = [item["close"] for item in data]
    returns = [(close_prices[i + 1] - close_prices[i]) / close_prices[i] for i in range(len(close_prices) - 1)]

    return {"close": close_prices, "returns": returns}

def generate_fan_chart_with_history(coin, currency, historical_days, prediction_days, simulations):
    """
    Generate fan chart data combining historical prices and Monte Carlo predictions.

    Args:
        coin (str): Cryptocurrency symbol (e.g., "BTC").
        currency (str): Fiat currency symbol (e.g., "USD").
        historical_days (int): Number of past days to include.
        prediction_days (int): Number of future days to predict.
        simulations (int): Number of Monte Carlo simulations.

    Returns:
        dict: Contains:
            - "time": Combined time steps (e.g., [-30, ..., 0, 1, ..., prediction_days]).
            - "real_prices": Historical closing prices with None for future days.
            - "percentiles": Prediction percentiles (10th, 50th, 90th) with None for historical days.
    """
    # Fetch historical data
    historical_data = fetch_historical_data(coin, currency, historical_days)
    real_prices = historical_data["close"]
    initial_price = real_prices[-1]  # Most recent closing price

    # Calculate historical returns for mu and sigma
    mu = sum(historical_data["returns"]) / len(historical_data["returns"])  # Mean return
    sigma = (sum([(x - mu) ** 2 for x in historical_data["returns"]]) / len(historical_data["returns"])) ** 0.5  # Std. deviation

    # Connect to Rserve
    conn = pyRserve.connect("localhost",6312)
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

        # Prepare percentiles with `None` for historical days
        prediction_percentiles = {
            "10th": [None] * historical_days + [round(v, 2) for v in percentiles[0]],
            "50th": [None] * historical_days + [round(v, 2) for v in percentiles[1]],
            "90th": [None] * historical_days + [round(v, 2) for v in percentiles[2]],
        }

        # Prepare real prices with `None` for future days
        real_prices_with_none = real_prices + [None] * prediction_days

        # Prepare result
        result = {
            "time": list(range(-historical_days, 0)) + list(range(1, prediction_days + 1)),  # Full timeline
            "real_prices": real_prices_with_none,
            "percentiles": prediction_percentiles,
        }
        return result

    finally:
        # Close Rserve connection
        conn.close()