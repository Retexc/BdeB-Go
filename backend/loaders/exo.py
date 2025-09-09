import requests
import os
import csv
import time
from datetime import datetime, timedelta
from google.transit import gtfs_realtime_pb2
from ..config import (
    # New Chrono endpoints
    CHRONO_TRIP_UPDATE_URL,
    CHRONO_VEHICLE_POSITION_URL,
    CHRONO_ALERTS_URL,
)
from ..utils import load_csv_dict
import logging
logger = logging.getLogger('BdeB-GTFS.exo')

script_dir = os.path.dirname(os.path.abspath(__file__))

def normalize_trip_id(trip_id):
    return trip_id.split('-')[0].strip()

def fetch_exo_realtime_data():
    headers = { "accept": "application/x-protobuf" }
    
    trip_updates_response = requests.get(CHRONO_TRIP_UPDATE_URL, headers=headers)
    vehicle_positions_response = requests.get(CHRONO_VEHICLE_POSITION_URL, headers=headers)

    if trip_updates_response.status_code == 429:
        print("Chrono API rate limited for trip updates")
    if vehicle_positions_response.status_code == 429:
        print("Chrono API rate limited for vehicle positions")
    print(f"=== FETCH_EXO_REALTIME_DATA CALLED AT {time.strftime('%H:%M:%S')} ===")
    if trip_updates_response.status_code == 200 and vehicle_positions_response.status_code == 200:
        print("Chrono API Fetch Success")
        trip_updates_feed = gtfs_realtime_pb2.FeedMessage()
        vehicle_positions_feed = gtfs_realtime_pb2.FeedMessage()
        trip_updates_feed.ParseFromString(trip_updates_response.content)
        vehicle_positions_feed.ParseFromString(vehicle_positions_response.content)    
        return trip_updates_feed.entity, vehicle_positions_feed.entity
    else:
        print(f"Chrono API Error: {trip_updates_response.status_code}, {vehicle_positions_response.status_code}")
        return [], []

def fetch_exo_alerts():
    """Updated function to use new Chrono API"""
    headers = { "accept": "application/x-protobuf" }
    print(f"DEBUG: fetch_exo_alerts calling URL: {CHRONO_ALERTS_URL}")  
    try:
        response = requests.get(CHRONO_ALERTS_URL, headers=headers)
        if response.status_code == 200:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)
            return feed.entity
        return []
    except Exception as e:
        print(f"Error fetching Chrono alerts: {str(e)}")
        return []


def load_exo_gtfs_trips(filepath):
    """Load Exo trips with full trip_id (including suffixes)."""
    trips_data = {}
    with open(filepath, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            trips_data[row["trip_id"]] = {  
                "route_id": row["route_id"],
                "direction_id": row.get("direction_id", "0"),
                "wheelchair_accessible": row.get("wheelchair_accessible", "0"),
                "bikes_allowed": row.get("bikes_allowed", "0")
            }
    return trips_data

def load_exo_stop_times(filepath):
    stop_times_data = []
    with open(filepath, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            stop_times_data.append(row)
    return stop_times_data

def exo_map_occupancy_status(status):
    mapping = {
        "MANY_SEATS_AVAILABLE": "MANY_SEATS_AVAILABLE",
        "FEW_SEATS_AVAILABLE": "FEW_SEATS_AVAILABLE",
        "STANDING_ROOM_ONLY": "STANDING_ROOM_ONLY",
        "FULL": "FULL",
        "NOT_ACCEPTING_PASSENGERS": "NOT_ACCEPTING_PASSENGERS",
        "UNKNOWN": "UNKNOWN"
    }
    
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
        return mapping.get(status.upper(), "UNKNOWN")
    else:
        return "UNKNOWN"

# For route 6 stops, we use this mapping.
stop_id_map = {
    "MTL7B": "Gare Bois-de-Boulogne",
    "MTL7D": "Gare Bois-de-Boulogne",
    "MTL59A": "Gare Ahuntsic",
}

def exo_map_train_details(schedule, trips_data, stop_id_map):
    mapped_schedule = []
    for train in schedule:
        trip_id = train["trip_id"]
        route_id = train["route_id"]
        stop_id = train["stop_id"]

        if route_id == "4":
            if stop_id == "MTL7D":
                direction = "Lucien-L'allier"
            elif stop_id == "MTL7B":
                direction = "Saint-Jérôme"
            else:
                direction = "Unknown"
        elif route_id == "6":
            direction_id = trips_data.get(train["trip_id"], {}).get("direction_id", "0")
            direction = (
                "Mascouche" if direction_id == "0"
                else "Unknown"
            )
        else:
            direction = "Unknown"
        
        if route_id == "4":
            stop_name = stop_id_map.get(stop_id, "Unknown")
        else:
            stop_name = stop_id_map.get(stop_id, "Unknown")
        
        minutes_remaining = train.get("minutes_remaining")
        mapped_train = {
            "route_id": route_id,
            "arrival_time": train.get("arrival_time", "Unknown"),
            "original_arrival_time": train.get("original_arrival_time"),
            "direction": direction,
            "location": stop_name,
            "occupancy": train.get("occupancy", "UNKNOWN"),
            "delayed_text": train.get("delayed_text"),
            "early_text": train.get("early_text"),
            "wheelchair_accessible": trips_data.get(train["trip_id"], {}).get("wheelchair_accessible", "0") == "1",
            "bikes_allowed": trips_data.get(train["trip_id"], {}).get("bikes_allowed", "0") == "1",
            "minutes_remaining": minutes_remaining,
            "stop_id": stop_id,
            "at_stop": train.get("at_stop", False),
        }
        mapped_schedule.append(mapped_train)
    return mapped_schedule

def process_exo_vehicle_positions(entities, stop_times):
    desired_stops = {"MTL7D", "MTL7B", "MTL59A"}
    closest_vehicles = {stop_id: None for stop_id in desired_stops}

    for entity in entities:
        if entity.HasField("vehicle"):
            vehicle = entity.vehicle
            raw_trip_id = vehicle.trip.trip_id
            trip_id = normalize_trip_id(raw_trip_id)
            route_id = vehicle.trip.route_id
            exo_occupancy_status = vehicle.occupancy_status if vehicle.HasField("occupancy_status") else "UNKNOWN"
            for stop_time in stop_times:
                csv_trip_id = normalize_trip_id(stop_time["trip_id"])
                candidate_stop = stop_time["stop_id"].strip()
                logger.debug(f"Comparing realtime trip_id: {trip_id} with CSV trip_id: {csv_trip_id} for stop {candidate_stop}")
                if csv_trip_id == trip_id and candidate_stop in desired_stops:
                    stop_id = candidate_stop
                    arrival_time_str = stop_time["arrival_time"]
                    h, m, s = map(int, arrival_time_str.split(":"))
                    arrival_time_seconds = h * 3600 + m * 60 + s

                    current_time = datetime.now()
                    current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second

                    if arrival_time_seconds < current_seconds:
                        continue

                    if (closest_vehicles[stop_id] is None or
                            arrival_time_seconds < closest_vehicles[stop_id]["arrival_time_seconds"]):
                        closest_vehicles[stop_id] = {
                            "trip_id": trip_id,
                            "route_id": route_id,
                            "occupancy": exo_map_occupancy_status(exo_occupancy_status),
                            "stop_id": stop_id,
                            "arrival_time_seconds": arrival_time_seconds,
                        }
                        logger.debug(f"Match found for stop {stop_id}: {closest_vehicles[stop_id]}")
                        
    filtered_vehicles = []
    for vehicle in closest_vehicles.values():
        if vehicle:
            seconds = vehicle["arrival_time_seconds"]
            hours = (seconds // 3600) % 24
            minutes = (seconds % 3600) // 60
            arrival_dt = datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
            arrival_str = arrival_dt.strftime("%I:%M %p")
            
            filtered_vehicles.append({
                "trip_id": vehicle["trip_id"],
                "route_id": vehicle["route_id"],
                "occupancy": vehicle["occupancy"],
                "stop_id": vehicle["stop_id"],
                "arrival_time": arrival_str,
            })

    print("Filtered Chrono Vehicle Positions with Stop IDs:", filtered_vehicles)
    return filtered_vehicles

def process_exo_train_schedule_with_occupancy(exo_stop_times, exo_trips, vehicle_positions, exo_trip_updates):
    from datetime import datetime, timedelta
    current_time = datetime.now()
    current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second

    occupancy_lookup = {}
    for vehicle in vehicle_positions:
        key = (vehicle["trip_id"], vehicle["route_id"])
        occupancy_lookup[key] = vehicle.get("occupancy", "UNKNOWN")
        logger.debug(f"Cached occupancy - Trip: {vehicle['trip_id']}, Route: {vehicle['route_id']} -> {occupancy_lookup[key]}")

    real_delays = {}
    for entity in exo_trip_updates:
        if entity.HasField('trip_update'):
            raw_trip_id = entity.trip_update.trip.trip_id
            trip_id = normalize_trip_id(raw_trip_id)
            for stop_update in entity.trip_update.stop_time_update:
                stop_id = stop_update.stop_id.strip()
                delay_seconds = stop_update.arrival.delay if stop_update.HasField('arrival') else 0
                real_delays[(trip_id, stop_id)] = delay_seconds // 60

    desired_stops = {"MTL7D", "MTL7B", "MTL59A"}
    closest_trains = {stop: None for stop in desired_stops}

    for stop_time in exo_stop_times:
        candidate_stop = stop_time["stop_id"].strip()
        if candidate_stop not in desired_stops:
            continue

        raw_trip_id = stop_time["trip_id"]
        trip_id = normalize_trip_id(raw_trip_id)  
        trip_data = exo_trips.get(raw_trip_id, {})
        route_id = trip_data.get("route_id")
        direction_id = trip_data.get("direction_id")

        if route_id not in ("4", "6"):
            continue

        exo_occupancy_status = occupancy_lookup.get((trip_id, route_id), "UNKNOWN")
        logger.debug(f"[Train] Looking up occupancy for {(trip_id, route_id)}: {exo_occupancy_status}")

        original_time_str = stop_time["departure_time"]
        original_datetime = datetime.strptime(original_time_str, "%H:%M:%S")
        actual_delay = real_delays.get((trip_id, candidate_stop), 0)
        adjusted_datetime = original_datetime + timedelta(minutes=actual_delay)
        original_arrival_time = original_datetime.strftime("%I:%M %p")
        adjusted_arrival_time = adjusted_datetime.strftime("%I:%M %p")

        arrival_time_seconds = (original_datetime.hour * 3600 +
                                original_datetime.minute * 60 +
                                original_datetime.second)
        if arrival_time_seconds < current_seconds:
            arrival_time_seconds += 24 * 3600

        minutes_remaining = (arrival_time_seconds - current_seconds) // 60

        delayed_text = None
        early_text = None
        if actual_delay > 0:
            delayed_text = f"En retard (prévu à {original_arrival_time})"
        elif actual_delay < 0:
            early_text = f"En avance (prévu à {original_arrival_time})"

        at_stop_flag = (minutes_remaining < 2)

        train_info = {
            "stop_id": candidate_stop,
            "trip_id": trip_id,
            "route_id": route_id,
            "arrival_time": adjusted_arrival_time,
            "original_arrival_time": original_arrival_time,
            "minutes_remaining": minutes_remaining,
            "occupancy": exo_occupancy_status,
            "delayed_text": delayed_text,
            "early_text": early_text,
            "at_stop": at_stop_flag,
        }

        prev = closest_trains[candidate_stop]
        if (prev is None) or (minutes_remaining < prev["minutes_remaining"]):
            closest_trains[candidate_stop] = train_info

    filtered_schedule = [train for train in closest_trains.values() if train]

    from .exo import exo_map_train_details, stop_id_map
    prioritized_schedule = exo_map_train_details(filtered_schedule, exo_trips, stop_id_map)

    for train in prioritized_schedule:
        mr = train.get("minutes_remaining", None)
        if isinstance(mr, int) and mr < 30:
            train["display_time"] = f"{mr} min"
        else:
            train["display_time"] = train.get("arrival_time", "Unknown")

    return prioritized_schedule