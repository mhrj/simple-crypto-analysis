import requests
import pyRserve

def fetch_global_market_data(api_url):
    """
    Fetch global market data from the specified API URL.
    Returns:
        dict: Parsed global market data or None in case of failure.
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json().get("data", {})
    except requests.RequestException as e:
        print(f"Error fetching global market data: {e}")
        return None

def fetch_coin_data(api_url, params):
    """
    Fetch coin-specific data from the specified API URL with parameters.
    Returns:
        dict: Parsed coin data or None in case of failure.
    """
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching coin data: {e}")
        return None

def calculate_top_gainer(coins_data):
    """
    Determine the top gainer from the provided coin data.
    """
    try:
        # Find the coin with the highest 24h change
        top_gainer = max(
            coins_data.items(),
            key=lambda item: item[1].get("usd_24h_change", float("-inf"))
        )
        return top_gainer[0].capitalize(), round(top_gainer[1].get("usd_24h_change", 0), 2)
    except (KeyError, ValueError):
        print("Error calculating top gainer.")
        return None, None

def fetch_market_summary():
    """
    Fetch the global cryptocurrency market summary including:
    - Total market capitalization
    - Total 24h volume of trades
    - Top gainer between BTC, ETH, and BNB
    Returns:
        dict: A dictionary containing the market data and top gainer information.
    """
    # API endpoint for global market data
    global_url = "https://api.coingecko.com/api/v3/global"

    # API endpoint for specific coin data
    coins_url = "https://api.coingecko.com/api/v3/simple/price"

    # Parameters for fetching BTC, ETH, and BNB data
    coins_params = {
        "ids": "bitcoin,ethereum,binancecoin",
        "vs_currencies": "usd",
        "include_24hr_change": "true",
    }

    # Fetch global market data
    global_data = fetch_global_market_data(global_url)
    if not global_data:
        return {"error": "Failed to fetch global market data."}

    # Fetch coin-specific data for BTC, ETH, and BNB
    coins_data = fetch_coin_data(coins_url, coins_params)
    if not coins_data:
        return {"error": "Failed to fetch coin data."}

    # Calculate the top gainer
    top_gainer_coin, top_gainer_change = calculate_top_gainer(coins_data)

    # Extract market cap and 24h volume
    market_cap_usd = global_data.get("total_market_cap", {}).get("usd")
    volume_24h_usd = global_data.get("total_volume", {}).get("usd")

    # Return the final data in the desired format
    return {
        "market_cap_usd": market_cap_usd,
        "volume_24h_usd": volume_24h_usd,
        "top_gainer": {"coin": top_gainer_coin, "change": top_gainer_change},
    }

def fetch_news_data(query, limit, api_key):
    """
    Fetch news data from the NewsAPI.
    Args:
        query (str): The search query for news articles.
        limit (int): The number of articles to fetch.
        api_key (str): Your NewsAPI API key.
    Returns:
        dict: A dictionary containing raw API response data or an error message.
    """
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "pageSize": limit,
        "apiKey": api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"API Request failed: {e}"}

def format_news_articles(raw_data, limit):
    """
    Format raw news API data into a list of article dictionaries.
    Args:
        raw_data (dict): The raw API response data.
        limit (int): The maximum number of articles to include in the result.
    Returns:
        list: A list of dictionaries with article details.
    """
    articles = raw_data.get("articles", [])
    news_list = []

    for article in articles[:limit]:
        news_list.append({
            "title": article.get("title", "No title"),
            "description": article.get("description", "No description"),
            "url": article.get("url", "No URL"),
            "published_at": article.get("publishedAt", "Unknown Date")
        })

    return news_list

def fetch_latest_general_crypto_news(limit=5, api_key="fbf8172bf41c423f8667eb92b88cc692"):
    """
    Fetch the latest general cryptocurrency news.
    Args:
        limit (int): The number of latest news articles to fetch. Default is 5.
        api_key (str): Your NewsAPI API key.
    Returns:
        list: A list of dictionaries containing the latest general crypto news or an error message.
    """
    raw_data = fetch_news_data("cryptocurrency", limit, api_key)
    if "error" in raw_data:
        return [{"error": raw_data["error"]}]  # Return the error message in a list
    return format_news_articles(raw_data, limit)

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

def fetch_current_price_cryptocompare(coin_id, vs_currency="USD"):
    """
    Fetch the current price of a single cryptocurrency from CryptoCompare.
    Args:
        coin_id (str): The symbol of the cryptocurrency (e.g., "BTC", "ETH").
        vs_currency (str): The fiat or crypto currency to compare against (default is "USD").
    Returns:
        dict: A dictionary containing the current price and related data for the coin.
    """
    url = "https://min-api.cryptocompare.com/data/pricemultifull"
    params = {
        "fsyms": coin_id,
        "tsyms": vs_currency
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        if "RAW" in data and coin_id in data["RAW"] and vs_currency in data["RAW"][coin_id]:
            return data["RAW"][coin_id][vs_currency]
        return {"error": f"Data for {coin_id} not available"}
    except requests.RequestException as e:
        return {"error": f"API Request failed: {e}"}

def fetch_crypto_data_cryptocompare(coins, vs_currency="USD"):
    """
    Fetch cryptocurrency data for a list of coins from CryptoCompare.
    Args:
        coins (list): A list of cryptocurrency symbols (e.g., ["BTC", "ETH"]).
        vs_currency (str): The fiat or crypto currency to compare against (default is "USD").
    Returns:
        dict: A dictionary with raw data for each coin, keyed by coin symbol.
    """
    data = {}
    for coin in coins:
        coin_data = fetch_current_price_cryptocompare(coin, vs_currency)
        if "error" in coin_data:
            return {"error": f"Failed to fetch data for {coin}: {coin_data['error']}"}
        data[coin] = coin_data
    return data

def format_crypto_data_as_dict_cryptocompare(data, coins):
    """
    Format the cryptocurrency data from CryptoCompare into a dictionary.
    Args:
        data (dict): The raw API data for cryptocurrencies.
        coins (list): The list of cryptocurrencies to process.
    Returns:
        dict: A dictionary with coin symbols as keys and detailed data as values.
    """
    crypto_dict = {}

    for coin in coins:
        coin_data = data.get(coin, {})
        crypto_dict[coin] = {
            "coin": coin,
            "current_price": coin_data.get("PRICE"),
            "24h_change": round(coin_data.get("CHANGE24HOUR", 0), 2) if coin_data.get("CHANGE24HOUR") else None,
            "market_cap": coin_data.get("MKTCAP"),
            "24h_volume": coin_data.get("TOTALVOLUME24H"),
            "supply": coin_data.get("SUPPLY"),
        }

    return crypto_dict

def fetch_crypto_table_data_as_dict_cryptocompare(coins, vs_currency="USD"):
    """
    Fetch and format cryptocurrency data as a dictionary using CryptoCompare.
    Args:
        coins (list): A list of cryptocurrency symbols.
        vs_currency (str): The fiat or crypto currency to compare against (default is "USD").
    Returns:
        dict: A dictionary with coin symbols as keys and detailed data as values, or an error message.
    """
    raw_data = fetch_crypto_data_cryptocompare(coins, vs_currency)
    if "error" in raw_data:
        return raw_data  # Return the error if API request failed
    return format_crypto_data_as_dict_cryptocompare(raw_data, coins)
