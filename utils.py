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
    """
    Fetch current weather for the given city.
    If the weather condition is among a set of 'bad' conditions that can
    cause delays (for buses and trains), return a weather alert message.
    Otherwise, return an empty list.
    """
    url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}&aqi=no"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        condition = data.get("current", {}).get("condition", {})

        # Define a set of weather condition codes considered "bad" for transit.
        # (Codes based on WeatherAPI documentation and your criteria)
        bad_codes = {
            1087,  # Thundery outbreaks possible
            1114,  # Blowing snow
            1117,  # Blizzard
            1147,  # Freezing fog
            1168,  # Freezing drizzle
            1171,  # Heavy freezing drizzle
            1186,  # Moderate rain at times
            1189,  # Moderate rain
            1192,  # Heavy rain at times
            1195,  # Heavy rain
            1198,  # Light freezing rain
            1201,  # Moderate or heavy freezing rain
            1204,  # Light sleet
            1207,  # Moderate or heavy sleet
            1216,  # Patchy moderate snow
            1219,  # Moderate snow
            1222,  # Patchy heavy snow
            1225,  # Heavy snow
            1237,  # Ice pellets
            1243,  # Moderate or heavy rain shower
            1246,  # Torrential rain shower
            1252,  # Moderate or heavy sleet showers
            1258,  # Moderate or heavy snow showers
            1264,  # Moderate or heavy showers of ice pellets
            1276,  # Moderate or heavy rain with thunder
            1282   # Moderate or heavy snow with thunder
        }

        if condition.get("code") in bad_codes:
            return [{
                'header': "🚨 Avertissement météo",
                'description': "Conditions météorologiques difficiles: " + condition.get("text", ""),
                'severity': "weather_alert",
                'routes': "Tous",
                'stop': "STM et Exo"
            }]
        return []
    except requests.exceptions.RequestException as err:
        print(f"Error fetching weather alerts: {err}")
        return []
