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
    """Load Exo trips with direction, wheelchair, and bikes allowed information."""
    trips_data = {}
    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            trips_data[row["trip_id"]] = {
                "route_id": row["route_id"],
                "direction_id": row.get("direction_id", "0"),
                "wheelchair_accessible": row.get("wheelchair_accessible", "0"),  # '1' means accessible
                "bikes_allowed": row.get("bikes_allowed", "0")                   # '1' means bikes allowed
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
    """
    Maps the GTFS-Realtime occupancy status (which may be provided as an int or string)
    to a string that matches the STM occupancy mapping.
    """
    # Define a mapping for string values as returned by GTFS-Realtime JSON conversion
    mapping = {
        "MANY_SEATS_AVAILABLE": "MANY_SEATS_AVAILABLE",
        "FEW_SEATS_AVAILABLE": "FEW_SEATS_AVAILABLE",
        "STANDING_ROOM_ONLY": "STANDING_ROOM_ONLY",
        "FULL": "FULL",
        "NOT_ACCEPTING_PASSENGERS": "NOT_ACCEPTING_PASSENGERS",
        "UNKNOWN": "UNKNOWN"
    }
    
    # If the status is an integer (native enum), convert it to a string first.
    if isinstance(status, int):
        int_mapping = {
            0: "UNKNOWN",
            1: "MANY_SEATS_AVAILABLE",
            2: "FEW_SEATS_AVAILABLE",
            3: "STANDING_ROOM_ONLY",
            4: "FULL",
            5: "NOT_ACCEPTING_PASSENGERS"
        }
        status_str = int_mapping.get(status, "UNKNOWN")
        return mapping.get(status_str, "UNKNOWN")
    elif isinstance(status, str):
        # If it's already a string, return the mapped value (or "UNKNOWN" if not found)
        return mapping.get(status, "UNKNOWN")
    else:
        return "UNKNOWN"


stop_id_map = {
    "MTL7B": "Gare Bois-de-Boulogne",
    "MTL7D": "Gare Bois-de-Boulogne",
    "MTL59A": "Gare Ahuntsic",
    "MTL59C": "Gare Ahuntsic",
}

# Map trip details to route and direction
def exo_map_train_details(schedule, trips_data, stop_id_map):
    """
    Maps the raw schedule (including minutes_remaining, arrival_time, etc.)
    into a final list of trains with route/direction, plus wheelchair/bike info.
    """
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
            else "Mascouche"       if route_id == "6" and direction_id == "1"
            else "Gare Centrale"   if route_id == "6" and direction_id == "0"
            else "Unknown"
        )
        
        # Get stop name from the map
        stop_name = stop_id_map.get(stop_id, "Unknown")

        # Preserve minutes_remaining if present
        minutes_remaining = train.get("minutes_remaining")

        mapped_train = {
            # Convert route_id=4 => '12', route_id=6 => '15', else just use the original
            "route_id": "12" if route_id == "4" else "15" if route_id == "6" else route_id,
            "arrival_time": train.get("arrival_time", "Unknown"),          # adjusted arrival time
            "original_arrival_time": train.get("original_arrival_time"),   # scheduled arrival time
            "direction": direction,
            "location": stop_name,
            "occupancy": train.get("occupancy", "Unknown"),
            "delayed_text": train.get("delayed_text"),
            "early_text": train.get("early_text"),
            "wheelchair_accessible": trips_data.get(trip_id, {}).get("wheelchair_accessible", "0") == "1",
            "bikes_allowed": trips_data.get(trip_id, {}).get("bikes_allowed", "0") == "1",
            "minutes_remaining": minutes_remaining,  # keep it for display logic
            "stop_id": stop_id,
            "at_stop": train.get("at_stop", False),
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
    """
    1) Reads the Exo trip updates => real-time delays
    2) Reads vehicle_positions => occupancy info
    3) Merges with static stop_times to find the next arrival for each desired stop
    4) For each train, calculates minutes_remaining
    5) Sets a 'display_time' that shows either "X min" (if < 60) or "HH:MM"
    """
    from datetime import datetime, timedelta
    current_time = datetime.now()
    current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second

    # ====== Step 1: Build a dictionary of real-time delays (in minutes) ======
    real_delays = {}
    for entity in exo_trip_updates:
        if entity.HasField('trip_update'):
            trip_id = entity.trip_update.trip.trip_id
            for stop_update in entity.trip_update.stop_time_update:
                stop_id = stop_update.stop_id
                delay_seconds = stop_update.arrival.delay if stop_update.HasField('arrival') else 0
                real_delays[(trip_id, stop_id)] = delay_seconds // 60  # convert to minutes

    # ====== Step 2: We'll track the next arrival for each "desired" stop ======
    desired_stops = {"MTL7D", "MTL7B", "MTL59A", "MTL59C"}
    closest_trains = {stop: None for stop in desired_stops}

    # ====== Step 3: Merge static stop_times with real-time delays & occupancy ======
    for stop_time in exo_stop_times:
        stop_id = stop_time["stop_id"]
        if stop_id not in desired_stops:
            continue

        trip_id = stop_time["trip_id"]
        trip_data = exo_trips.get(trip_id, {})
        route_id = trip_data.get("route_id")
        direction_id = trip_data.get("direction_id")

        # We only care about route_id=4 (Saint-Jérôme) or 6 (Mascouche) in this example
        if route_id not in ("4", "6"):
            continue

        # Convert scheduled time to a datetime
        original_time_str = stop_time["departure_time"]
        original_datetime = datetime.strptime(original_time_str, "%H:%M:%S")

        # Real-time delay from feed (in minutes)
        actual_delay = real_delays.get((trip_id, stop_id), 0)

        # Adjust scheduled time by that delay
        adjusted_datetime = original_datetime + timedelta(minutes=actual_delay)
        original_arrival_time = original_datetime.strftime("%I:%M %p")
        adjusted_arrival_time = adjusted_datetime.strftime("%I:%M %p")   # HH:MM

        # Convert scheduled time to "seconds from midnight"
        arrival_time_seconds = (original_datetime.hour * 3600
                                + original_datetime.minute * 60
                                + original_datetime.second)
        # If it's past midnight (the train is next day)
        if arrival_time_seconds < current_seconds:
            arrival_time_seconds += 24 * 3600

        minutes_remaining = (arrival_time_seconds - current_seconds) // 60

        # Occupancy from vehicle_positions
        exo_occupancy_status = "Unknown"
        for vehicle in vehicle_positions:
            if trip_id == vehicle["trip_id"]:
                exo_occupancy_status = vehicle.get("occupancy", "Unknown")
                break

        # Build delayed/early text using the original scheduled time
        delayed_text = None
        early_text = None
        if actual_delay > 0:
            delayed_text = f"En retard (prévu à {original_arrival_time})"
        elif actual_delay < 0:
            early_text = f"En avance (prévu à {original_arrival_time})"

        # Decide "at_stop" if minutes_remaining < 2
        at_stop_flag = (minutes_remaining < 2)

        # This dictionary holds the raw info before final mapping
        train_info = {
            "stop_id": stop_id,
            "trip_id": trip_id,
            "route_id": route_id,
            "arrival_time": adjusted_arrival_time,      # real-time arrival
            "original_arrival_time": original_arrival_time,
            "minutes_remaining": minutes_remaining,
            "occupancy": exo_occupancy_status,
            "delayed_text": delayed_text,
            "early_text": early_text,
            "at_stop": at_stop_flag,
        }

        # Keep only the closest arrival for each stop
        prev = closest_trains[stop_id]
        if (prev is None) or (minutes_remaining < prev["minutes_remaining"]):
            closest_trains[stop_id] = train_info

    # Filter out any stops that had no data
    filtered_schedule = [train for train in closest_trains.values() if train]

    # ====== Step 4: Convert them to final structure (route/direction, wheelchair, etc.) ======
    from exo import exo_map_train_details, stop_id_map
    prioritized_schedule = exo_map_train_details(filtered_schedule, exo_trips, stop_id_map)

    # ====== Step 5: Set a 'display_time' based on minutes_remaining vs. arrival_time ======
    for train in prioritized_schedule:
        mr = train.get("minutes_remaining", None)
        if isinstance(mr, int) and mr < 30:
            train["display_time"] = f"{mr} min"
        else:
            # Since arrival_time is already formatted as "HH:MM AM/PM", use it directly.
            train["display_time"] = train.get("arrival_time", "Unknown")

    return prioritized_schedule
