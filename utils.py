# utils.py
import os
import csv
from datetime import datetime
import requests

def load_no_service_days(filepath="no_service_days.txt"):
    """Load no-service days from a text file."""
    no_service_dates = set()
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            for line in file:
                date_str = line.strip()
                try:
                    no_service_dates.add(datetime.strptime(date_str, "%Y-%m-%d").date())
                except ValueError:
                    print(f"Skipping invalid date format: {date_str}")
    return no_service_dates


def is_service_unavailable():
    """Check if today is a no-service day or weekend."""
    today = datetime.today().date()
    no_service_dates = load_no_service_days()
    return (today.weekday() >= 5) or (today in no_service_dates)


def load_csv_dict(filepath):
    """Load a CSV into a list of dict rows."""
    data = []
    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data


def get_weather_alerts(weather_api_key, city="Montreal"):
    """Fetch weather alerts from WeatherAPI."""
    url = f"http://api.weatherapi.com/v1/alerts.json?key={weather_api_key}&q={city}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('alerts', [])
    except requests.exceptions.RequestException as err:
        print(f"Error fetching weather alerts: {err}")
        return []
