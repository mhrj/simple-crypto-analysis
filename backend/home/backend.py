import requests

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
