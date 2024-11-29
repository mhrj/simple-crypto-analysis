import requests
from typing import Dict

def get_request(url: str, params: Dict) -> Dict:
    """
    Make a GET request and handle errors.
    """
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return {}