import requests
from typing import Dict
from datetime import datetime
import pytz

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

def format_large_number(number: float) -> str:
    """
    Format a large number into a human-readable string with Million, Billion, or Trillion.
    Args:
        number (float): The number to format.
    Returns:
        str: The formatted string.
    """
    if number >= 1_000_000_000_000:
        return f"{number / 1_000_000_000_000:.2f} Trillion"
    elif number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f} Billion"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.2f} Million"
    else:
        return f"{number:.2f}"  # Return the number with 2 decimal places for smaller values
    
def convert_timestamps_to_clock(timestamps: list) -> list:
    """
    Convert a list of UNIX timestamps to their respective clock times in HH:MM format in Iran's time zone (IRST).

    Args:
        timestamps (list): List of UNIX timestamps.

    Returns:
        list: List of times in HH:MM format in Iran's time zone.
    """
    iran_tz = pytz.timezone('Asia/Tehran')  # Define the Iran time zone (IRST)
    clock_times = [
        datetime.fromtimestamp(ts, tz=pytz.utc).astimezone(iran_tz).strftime('%H:%M')
        for ts in timestamps
    ]
    return clock_times

def process_timestamps(timestamps):

    # Convert timestamps to MM-DD format
    dates = [datetime.utcfromtimestamp(ts).strftime('%m-%d') for ts in timestamps]
    return dates