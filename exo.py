import requests
import os
import csv
from datetime import datetime, timedelta
from google.transit import gtfs_realtime_pb2
from config import (
    EXO_TRIP_UPDATE_URL,
    EXO_VEHICLE_POSITION_URL,
    EXO_ALERTS_URL,
)
from utils import load_csv_dict

script_dir = os.path.dirname(os.path.abspath(__file__))

def fetch_exo_realtime_data():
    headers = { "accept": "application/x-protobuf" }
    trip_updates_response = requests.get(EXO_TRIP_UPDATE_URL, headers=headers)
    vehicle_positions_response = requests.get(EXO_VEHICLE_POSITION_URL, headers=headers)

    if trip_updates_response.status_code == 200 and vehicle_positions_response.status_code == 200:
        print("Exo API Fetch Success")
        trip_updates_feed = gtfs_realtime_pb2.FeedMessage()
        vehicle_positions_feed = gtfs_realtime_pb2.FeedMessage()
        trip_updates_feed.ParseFromString(trip_updates_response.content)
        vehicle_positions_feed.ParseFromString(vehicle_positions_response.content)
        return trip_updates_feed.entity, vehicle_positions_feed.entity
    else:
        print(f"Exo API Error: {trip_updates_response.status_code}, {vehicle_positions_response.status_code}")
        return [], []

def fetch_exo_alerts():
    headers = { "accept": "application/x-protobuf" }
    try:
        response = requests.get(EXO_ALERTS_URL, headers=headers)
        if response.status_code == 200:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)
            return feed.entity
        return []
    except Exception as e:
        print(f"Error fetching EXO alerts: {str(e)}")
        return []

def load_exo_gtfs_trips(filepath):
    """If you need to load Exo trips with direction_id, do it here."""
    trips_data = {}
    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            trips_data[row["trip_id"]] = {
                "route_id": row["route_id"],
                "direction_id": row.get("direction_id", "0"),
            }
    return trips_data

def load_exo_stop_times(filepath):
    stop_times_data = []
    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            stop_times_data.append(row)
    return stop_times_data

def exo_map_occupancy_status(status):
    mapping = {
        1: "Near_Empty",
        2: "Light",
        3: "Medium",
        4: "Full",
    }
    return mapping.get(status, "Unknown")

stop_id_map = {
    "MTL7B": "Gare Bois-de-Boulogne",
    "MTL7D": "Gare Bois-de-Boulogne",
    "MTL59A": "Gare Ahuntsic",
    "MTL59C": "Gare Ahuntsic",
}

# Map trip details to route and direction
def exo_map_train_details(schedule, trips_data, stop_id_map):
    mapped_schedule = []
    for train in schedule:
        trip_id = train["trip_id"]
        route_id = train["route_id"]
        stop_id = train["stop_id"]
        direction_id = trips_data.get(trip_id, {}).get("direction_id", "0")
        
        # Determine the direction based on route_id and direction_id
        direction = (
        "Saint-Jérôme" if route_id == "4" and direction_id == "1"
        else "Lucien-L'allier" if route_id == "4" and direction_id == "0"
        else "Mascouche" if route_id == "6" and direction_id == "1"
        else "Gare Centrale" if route_id == "6" and direction_id == "0"
        else "Unknown"
    )
        
        # Get stop name from the map
        stop_name = stop_id_map.get(stop_id, "Unknown")

        # Include both original and delayed arrival times
        mapped_train = {
            "route_id": "12" if route_id == "4" else "15" if route_id == "6" else route_id,
            "arrival_time": train.get("arrival_time", "Unknown"),
            "original_arrival_time": train.get("original_arrival_time", "Unknown"),
            "direction": direction,
            "location": stop_name,
            "occupancy": train.get("occupancy", "Unknown"),  # Add occupancy
            "delayed_text": train.get("delayed_text", None),  # Delayed text
            "early_text": train.get("early_text", None),
        }
        mapped_schedule.append(mapped_train)
    return mapped_schedule
    
# Process Exo Vehicle Positions
def process_exo_vehicle_positions(entities, stop_times):
    # Define desired stops
    desired_stops = {"MTL7D", "MTL7B", "MTL59A"}

    # Initialize a dictionary to track the closest vehicle per stop
    closest_vehicles = {stop_id: None for stop_id in desired_stops}

    for entity in entities:
        if entity.HasField("vehicle"):
            vehicle = entity.vehicle
            trip_id = vehicle.trip.trip_id
            route_id = vehicle.trip.route_id
            exo_occupancy_status = vehicle.occupancy_status if vehicle.HasField("occupancy_status") else "UNKNOWN"

            # Match with stop_times to find the stop_id and arrival time
            for stop_time in stop_times:
                if stop_time["trip_id"] == trip_id and stop_time["stop_id"] in desired_stops:
                    stop_id = stop_time["stop_id"]
                    arrival_time_str = stop_time["arrival_time"]
                    h, m, s = map(int, arrival_time_str.split(":"))
                    arrival_time_seconds = h * 3600 + m * 60 + s

                    current_time = datetime.now()
                    current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second

                    # Handle times that roll over past midnight
                    if arrival_time_seconds < current_seconds:
                        arrival_time_seconds += 24 * 3600

                    # If this is the closest vehicle so far, update the dictionary
                    if (closest_vehicles[stop_id] is None or
                            arrival_time_seconds < closest_vehicles[stop_id]["arrival_time_seconds"]):
                        closest_vehicles[stop_id] = {
                            "trip_id": trip_id,
                            "route_id": route_id,
                            "occupancy": exo_map_occupancy_status(exo_occupancy_status),
                            "stop_id": stop_id,
                            "arrival_time_seconds": arrival_time_seconds,
                        }

    # Prepare the final list
    filtered_vehicles = [
        {
            "trip_id": vehicle["trip_id"],
            "route_id": vehicle["route_id"],
            "occupancy": vehicle["occupancy"],
            "stop_id": vehicle["stop_id"],
        }
        for vehicle in closest_vehicles.values() if vehicle is not None
    ]

    print("Filtered Exo Vehicle Positions with Stop IDs:", filtered_vehicles)  # Debugging
    return filtered_vehicles

def process_exo_train_schedule_with_occupancy(exo_stop_times, exo_trips, vehicle_positions, exo_trip_updates):
    current_time = datetime.now()
    current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second

    real_delays = {}
    
    # Parse real-time delays from Exo API
    for entity in exo_trip_updates:
        if entity.HasField('trip_update'):
            trip_id = entity.trip_update.trip.trip_id
            for stop_update in entity.trip_update.stop_time_update:
                stop_id = stop_update.stop_id
                delay_seconds = stop_update.arrival.delay if stop_update.HasField('arrival') else 0
                real_delays[(trip_id, stop_id)] = delay_seconds // 60  # Convert to minutes

    # Stop and direction mapping
    direction_map = {
        "4": {"0": "Lucien-L'allier", "1": "Saint-Jérôme"},
        "6": {"0": "Gare centrale", "1": "Mascouche"},
    }

    desired_stops = {"MTL7D", "MTL7B", "MTL59A", "MTL59C"}
    closest_trains = {stop: None for stop in desired_stops}

    for stop_time in exo_stop_times:
        stop_id = stop_time["stop_id"]
        if stop_id in desired_stops:
            trip_id = stop_time["trip_id"]
            trip_data = exo_trips.get(trip_id, {})
            route_id = trip_data.get("route_id")
            direction_id = trip_data.get("direction_id")

            if route_id in direction_map and direction_id in direction_map[route_id]:
                original_time_str = stop_time["departure_time"]
                original_datetime = datetime.strptime(original_time_str, "%H:%M:%S")
                
                # Get actual delay from real-time data
                actual_delay = real_delays.get((trip_id, stop_id), 0)
                adjusted_datetime = original_datetime + timedelta(minutes=actual_delay)
                original_arrival_time = original_datetime.strftime("%H:%M")
                adjusted_arrival_time = adjusted_datetime.strftime("%H:%M")

                # Calculate minutes remaining
                arrival_time_seconds = original_datetime.hour * 3600 + original_datetime.minute * 60
                if arrival_time_seconds < current_seconds:
                    arrival_time_seconds += 24 * 3600
                minutes_remaining = (arrival_time_seconds - current_seconds) // 60

                # Determine occupancy
                exo_occupancy_status = "Unknown"
                for vehicle in vehicle_positions:
                    if trip_id == vehicle["trip_id"]:
                        exo_occupancy_status = vehicle.get("occupancy", "Unknown")
                        break

                # Create status text for all stops
                delayed_text = None
                early_text = None
                if actual_delay > 0:
                    delayed_text = f"En retard (+{actual_delay}min)"
                elif actual_delay < 0:
                    early_text = f"En avance ({abs(actual_delay)}min)"

                train_info = {
                    "stop_id": stop_id,
                    "trip_id": trip_id,
                    "route_id": route_id,
                    "direction": direction_map[route_id][direction_id],
                    "arrival_time": adjusted_arrival_time,
                    "original_arrival_time": original_arrival_time,
                    "minutes_remaining": minutes_remaining,
                    "occupancy": exo_occupancy_status,
                    "delayed_text": delayed_text,
                    "early_text": early_text,
                }

                if (closest_trains[stop_id] is None or
                    minutes_remaining < closest_trains[stop_id]["minutes_remaining"]):
                    closest_trains[stop_id] = train_info

    filtered_schedule = [train for train in closest_trains.values() if train is not None]
    prioritized_schedule = exo_map_train_details(filtered_schedule, exo_trips, stop_id_map)
    return prioritized_schedule