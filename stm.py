import requests
import os
import csv
import time
from datetime import datetime
from google.transit import gtfs_realtime_pb2
from config import (
    STM_API_KEY,
    STM_REALTIME_ENDPOINT,
    STM_VEHICLE_POSITIONS_ENDPOINT,
    STM_ALERTS_ENDPOINT
)
from utils import load_csv_dict  # or not used if you prefer your direct CSV logic

# Dynamically construct paths for GTFS files
script_dir = os.path.dirname(os.path.abspath(__file__))

def fetch_stm_realtime_data():
    headers = {
        "accept": "application/x-protobuf",
        "apiKey": STM_API_KEY,
    }
    response = requests.get(STM_REALTIME_ENDPOINT, headers=headers)
    if response.status_code == 200:
        print("API Fetch Success")
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        return feed.entity
    else:
        print(f"API Error: {response.status_code} - {response.text}")
        return []
    
def fetch_stm_vehicle_positions():
    headers = {
        "accept": "application/x-protobuf",
        "apiKey": STM_API_KEY,
    }
    response = requests.get(STM_VEHICLE_POSITIONS_ENDPOINT, headers=headers)
    if response.status_code == 200:
        print("Vehicle Positions Fetch Success")
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        return feed.entity
    else:
        print(f"API Error: {response.status_code} - {response.text}")
        return []   

def fetch_stm_alerts():
    headers = {
        "accept": "application/json",
        "apiKey": STM_API_KEY,
    }
    try:
        response = requests.get(STM_ALERTS_ENDPOINT, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching alerts: {str(e)}")
        return None

def load_stm_stop_times(filepath):
    """
    Your single, correct STM stop_times loader (dict => {(trip_id, stop_id): arrival_time}).
    """
    stop_times = {}
    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = (row["trip_id"], row["stop_id"])
            stop_times[key] = row["arrival_time"]
    return stop_times

def load_stm_gtfs_trips(filepath):
    """
    Load STM GTFS trips => {trip_id: route_id}.
    """
    trips_data = {}
    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            trips_data[row["trip_id"]] = row["route_id"]
    return trips_data

def stm_map_occupancy_status(status):
    """
    Convert numeric occupancy code to a human-friendly string.
    """
    mapping = {
        1: "Near_Empty",
        2: "Light",
        3: "Medium",
        4: "Null",
        5: "Full",
    }
    return mapping.get(status, "Unknown")         

def validate_trip(trip_id, route_id, gtfs_trips):
    """
    Check if the trip_id is valid for the given route_id according to static GTFS data.
    """
    return gtfs_trips.get(trip_id) == route_id

def process_stm_trip_updates(entities, stm_trips, stm_stop_times):
    """
    Core logic for parsing bus times, arrival predictions, occupancy, etc.
    NOTE: Make sure to pass in stm_stop_times from your app.py so it’s available.
    """
    desired_routes = ["171", "180", "164", "171_Ouest", "180_Ouest"]  # Removed "164_Ouest"
    closest_buses = {route: None for route in desired_routes}

    route_metadata = {
        "171": {"direction": "Est", "location": "Collège de Bois-de-Boulogne"},
        "180": {"direction": "Est", "location": "Collège de Bois-de-Boulogne"},
        "164": {"direction": "Est", "location": "Collège de Bois-de-Boulogne"},
        "171_Ouest": {"direction": "Ouest", "location": "Henri-Bourassa/du Bois-de-Boulogne"},
        "180_Ouest": {"direction": "Ouest", "location": "Henri-Bourassa/du Bois-de-Boulogne"},
    }

    stop_ids_of_interest = ["50270", "62374"]

    for entity in entities:
        if entity.HasField("trip_update") or entity.HasField("vehicle"):
            trip = entity.trip_update.trip if entity.HasField("trip_update") else None
            stop_time_updates = entity.trip_update.stop_time_update if entity.HasField("trip_update") else []
            vehicle = entity.vehicle if entity.HasField("vehicle") else None

            route_id = trip.route_id if trip else vehicle.trip.route_id
            trip_id = trip.trip_id if trip else vehicle.trip.trip_id
            occupancy_status = vehicle.occupancy_status if (vehicle and vehicle.HasField("occupancy_status")) else "UNKNOWN"
            vehicle_stop_id = vehicle.stop_id if (vehicle and vehicle.HasField("stop_id")) else None

            if route_id in desired_routes and validate_trip(trip_id, route_id, stm_trips):
                for stop_time in stop_time_updates:
                    if stop_time.stop_id in stop_ids_of_interest:
                        # Skip 164 if it's at "62374" for some reason
                        if route_id == "164" and stop_time.stop_id == "62374":
                            continue
                        
                        scheduled_arrival_str = stm_stop_times.get((trip_id, stop_time.stop_id))
                        arrival_time = stop_time.arrival.time if stop_time.HasField("arrival") else None

                        delay_minutes = None
                        scheduled_formatted = "Inconnu"

                        if scheduled_arrival_str and arrival_time:
                            try:
                                h, m, s = map(int, scheduled_arrival_str.split(":"))
                                if h >= 24:
                                    h = 0  # fix invalid hour
                                # Convert scheduled to a timestamp (approx. today’s date + h,m,s)
                                scheduled_ts = datetime.now().replace(hour=h, minute=m, second=s, microsecond=0).timestamp()
                                scheduled_formatted = f"{h:02d}:{m:02d}"
                                # Calculate difference (seconds)
                                delay_seconds = arrival_time - scheduled_ts
                                delay_minutes = delay_seconds // 60
                            except ValueError as e:
                                print(f"Error parsing scheduled arrival time: {scheduled_arrival_str} => {e}")
                                delay_minutes = None

                        # Time until arrival in minutes
                        minutes_to_arrival = (arrival_time - int(time.time())) // 60 if arrival_time else None

                        # Delay text for Chrono format
                        if delay_minutes is not None:
                            if delay_minutes > 0:
                                delayed_text = f"En retard (prévu à {scheduled_formatted})"
                            elif delay_minutes < 0:
                                delayed_text = f"En avance (prévu à {scheduled_formatted})"
                            else:
                                delayed_text = None
                        else:
                            delayed_text = None

                        if minutes_to_arrival is not None:
                            route_key = f"{route_id}_Ouest" if stop_time.stop_id == "62374" else route_id
                            if (
                                closest_buses.get(route_key) is None
                                or minutes_to_arrival < closest_buses[route_key]["arrival_time"]
                            ):
                                closest_buses[route_key] = {
                                    "route_id": route_id,
                                    "trip_id": trip_id,
                                    "stop_id": stop_time.stop_id,
                                    "arrival_time": minutes_to_arrival,
                                    "occupancy": stm_map_occupancy_status(occupancy_status),
                                    "direction": route_metadata.get(route_key, {}).get("direction", "Unknown"),
                                    "location": route_metadata.get(route_key, {}).get("location", "Unknown"),
                                    "delayed_text": delayed_text,
                                    "early_text": None,
                                    "at_stop": (vehicle_stop_id == stop_time.stop_id)
                                }

    # For routes that have no bus found, fill in a default
    for route in desired_routes:
        if route.startswith("164") and "Ouest" in route:
            continue  # skip 164 Ouest
        if closest_buses.get(route) is None:
            closest_buses[route] = {
                "route_id": route,
                "trip_id": "N/A",
                "stop_id": "50270" if "Ouest" not in route else "62374",
                "arrival_time": "Indisponible (Route annulée)",
                "occupancy": "Unknown",
                "direction": route_metadata.get(route, {}).get("direction", "Unknown"),
                "location": route_metadata.get(route, {}).get("location", "Unknown"),
                "delayed_text": None,
                "early_text": None,
                "at_stop": False
            }

    buses = list(closest_buses.values())
    return buses
