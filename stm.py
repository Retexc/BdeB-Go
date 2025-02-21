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
    Load STM GTFS trips into a dict keyed by trip_id.
    Each value is a dict: {"route_id": ..., "wheelchair_accessible": ...}.
    """
    trips_data = {}
    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            trip_id = row["trip_id"]
            route_id = row["route_id"]
            # If the CSV has a column named "wheelchair_accessible" with "1" or "2" or blank:
            w_str = row.get("wheelchair_accessible", "0")  # default "0" if missing
            trips_data[trip_id] = {
                "route_id": route_id,
                "wheelchair_accessible": w_str
            }
    return trips_data


def stm_map_occupancy_status(status):
    """
    Convert numeric occupancy code to a human-friendly string
    based on STM doc:
      1 -> MANY_SEATS_AVAILABLE
      2 -> FEW_SEATS_AVAILABLE
      3 -> STANDING_ROOM_ONLY
      4 -> FULL
    """
    mapping = {
        1: "MANY_SEATS_AVAILABLE",
        2: "FEW_SEATS_AVAILABLE",
        3: "STANDING_ROOM_ONLY",
        4: "FULL",
    }
    return mapping.get(status, "Unknown")
      

def validate_trip(trip_id, route_id, gtfs_trips):
    trip_info = gtfs_trips.get(trip_id)
    if not trip_info:
        return False
    return trip_info["route_id"] == route_id


def fetch_stm_positions_dict(desired_routes, stm_trips):
    """
    Fetch from STM_VEHICLE_POSITIONS_ENDPOINT, build dict keyed by (route_id, trip_id)
    => { "lat": ..., "lon": ..., "occupancy": ..., "stop_id": ..., "current_status": ... } if present
    """
    positions = {}
    entities = fetch_stm_vehicle_positions()
    if not entities:
        return positions  # empty
    
    for entity in entities:
        if entity.HasField("vehicle"):
            vehicle = entity.vehicle
            route_id = vehicle.trip.route_id
            trip_id = vehicle.trip.trip_id

            # only store if it's a route/trip we care about & is valid
            if route_id in desired_routes and validate_trip(trip_id, route_id, stm_trips):
                bus_lat = bus_lon = None
                if vehicle.HasField("position"):
                    bus_lat = vehicle.position.latitude
                    bus_lon = vehicle.position.longitude
                
                # occupancy_status => numeric
                occupancy_raw = None
                if vehicle.HasField("occupancy_status"):
                    occupancy_raw = vehicle.occupancy_status
                
                feed_stop_id = vehicle.stop_id if vehicle.HasField("stop_id") else None

                # currentStatus => e.g. IN_TRANSIT_TO, STOPPED_AT, etc.
                # In the proto, it might be "current_status" or "current_status_value"
                # We'll assume it's "current_status" in the Python-generated code.
                current_status_str = None
                if vehicle.HasField("current_status"):
                    current_status_str = vehicle.current_status  # This is an enum or string. Might be something like 2 => "IN_TRANSIT_TO"

                # Build a positions entry
                positions[(route_id, trip_id)] = {
                    "lat": bus_lat,
                    "lon": bus_lon,
                    "occupancy": occupancy_raw,
                    "feed_stop_id": feed_stop_id,
                    "current_status": current_status_str,
                }
    return positions


def process_stm_trip_updates(trip_entities, stm_trips, stm_stop_times, positions_dict):
    """
    Combine real-time TripUpdates with lat/lon info and wheelchair info.
    Return a list of bus objects with fields like:
      route_id, trip_id, stop_id, arrival_time, occupancy, direction, location,
      delayed_text, early_text, at_stop, wheelchair_accessible
    """

    import math, time
    from datetime import datetime

    # The routes we care about (Example)
    desired_routes = ["171", "180", "164", "171_Ouest", "180_Ouest"]

    # Prepare a dict to hold the closest bus for each route
    closest_buses = {r: None for r in desired_routes}

    # Basic route -> direction/ location (Example)
    route_metadata = {
        "171": {"direction": "Est", "location": "Collège de Bois-de-Boulogne"},
        "180": {"direction": "Est", "location": "Collège de Bois-de-Boulogne"},
        "164": {"direction": "Est", "location": "Collège de Bois-de-Boulogne"},
        "171_Ouest": {"direction": "Ouest", "location": "Henri-Bourassa/du Bois-de-Boulogne"},
        "180_Ouest": {"direction": "Ouest", "location": "Henri-Bourassa/du Bois-de-Boulogne"},
    }

    # Stop IDs we care about (Example)
    stop_ids_of_interest = ["50270", "62374"]

    for entity in trip_entities:
        if entity.HasField("trip_update"):
            t_update = entity.trip_update
            route_id = t_update.trip.route_id
            trip_id = t_update.trip.trip_id

            # Skip if route not in our desired list (Optional)
            if route_id not in ["171", "180", "164"]:
                # if route_id is "171_Ouest" or "180_Ouest" you might handle differently
                # or you can handle them by a separate logic. Adjust as needed.
                continue

            # Validate that trip_id in stm_trips matches route_id
            if not validate_trip(trip_id, route_id, stm_trips):
                continue

            # Lookup wheelchair flag from stm_trips
            # We assume "1" means accessible; else "0" or "2" means not
            trip_info = stm_trips.get(trip_id, {})
            w_str = trip_info.get("wheelchair_accessible", "0")
            wheelchair_accessible = (w_str == "1")

            for stop_time in t_update.stop_time_update:
                # Skip if stop not in interest
                if stop_time.stop_id not in stop_ids_of_interest:
                    continue

                # Skip route 164 if it's at 62374 (Optional)
                if route_id == "164" and stop_time.stop_id == "62374":
                    continue

                # Grab scheduled arrival from stop_times
                scheduled_arrival_str = stm_stop_times.get((trip_id, stop_time.stop_id))
                # Grab real arrival from the feed
                arrival_unix = stop_time.arrival.time if stop_time.HasField("arrival") else None
                if not arrival_unix:
                    continue

                # Compute minutes until arrival
                now_ts = time.time()
                minutes_to_arrival = (arrival_unix - now_ts) // 60

                # Build a delay text if we have scheduled + real
                delay_text = None
                if scheduled_arrival_str:
                    try:
                        h, m, s = map(int, scheduled_arrival_str.split(":"))
                        if h >= 24:
                            h = 0
                        sched_ts = datetime.now().replace(hour=h, minute=m, second=s, microsecond=0).timestamp()
                        diff_min = (arrival_unix - sched_ts) // 60
                        if diff_min > 0:
                            delay_text = f"En retard (prévu à {h:02d}:{m:02d})"
                        elif diff_min < 0:
                            delay_text = f"En avance (prévu à {h:02d}:{m:02d})"
                    except ValueError:
                        pass

                # If the stop is 62374, we might treat route as route_id+"_Ouest" (Example)
                route_key = route_id
                if stop_time.stop_id == "62374" and not route_id.endswith("_Ouest"):
                    route_key = f"{route_id}_Ouest"

                # Occupancy from positions_dict
                pos_info = positions_dict.get((route_id, trip_id), {})
                raw_occ = pos_info.get("occupancy")
                occ_str = stm_map_occupancy_status(raw_occ) if raw_occ else "Unknown"

                # If minutes_to_arrival < 2 => at_stop
                at_stop_flag = isinstance(minutes_to_arrival, (int, float)) and (minutes_to_arrival < 2)

                # Build the bus object
                bus_obj = {
                    "route_id": route_id,
                    "trip_id": trip_id,
                    "stop_id": stop_time.stop_id,
                    "arrival_time": minutes_to_arrival,
                    "occupancy": occ_str,
                    "direction": route_metadata.get(route_key, {}).get("direction", "Unknown"),
                    "location": route_metadata.get(route_key, {}).get("location", "Unknown"),
                    "delayed_text": delay_text,
                    "early_text": None,
                    "at_stop": at_stop_flag,
                    "wheelchair_accessible": wheelchair_accessible  # New field
                }

                # Keep only earliest arrival for that route
                existing = closest_buses.get(route_key)
                if existing is None:
                    closest_buses[route_key] = bus_obj
                else:
                    # Compare times if both are numeric
                    if (isinstance(existing["arrival_time"], (int, float))
                        and isinstance(minutes_to_arrival, (int, float))
                        and minutes_to_arrival < existing["arrival_time"]):
                        closest_buses[route_key] = bus_obj

    # Fill missing routes
    for r in desired_routes:
        if closest_buses[r] is None:
            closest_buses[r] = {
                "route_id": r,
                "trip_id": "N/A",
                "stop_id": "50270" if "Ouest" not in r else "62374",
                "arrival_time": "Indisponible (Route annulée)",
                "occupancy": "Unknown",
                "direction": route_metadata.get(r, {}).get("direction", "Unknown"),
                "location": route_metadata.get(r, {}).get("location", "Unknown"),
                "delayed_text": None,
                "early_text": None,
                "at_stop": False,
                "wheelchair_accessible": False  # default
            }

    # Return a list of bus objects
    return list(closest_buses.values())







    return buses

def debug_print_stm_occupancy_status(desired_routes, stm_trips):
    """
    Fetch the latest STM vehicle positions and print occupancyStatus
    ONLY for the bus routes we care about.
    Also prints out latitude/longitude + currentStatus if present.
    """
    entities = fetch_stm_vehicle_positions()
    
    if not entities:
        print("No STM vehicle positions found.")
        return
    
    print("----- STM Vehicle Positions (Occupancy + Position + currentStatus) -----")
    for entity in entities:
        if entity.HasField("vehicle"):
            vehicle = entity.vehicle
            route_id = vehicle.trip.route_id
            trip_id = vehicle.trip.trip_id
            
            if route_id in desired_routes and validate_trip(trip_id, route_id, stm_trips):
                
                # Occupancy
                if vehicle.HasField("occupancy_status"):
                    raw_status = vehicle.occupancy_status
                    mapped_status = stm_map_occupancy_status(raw_status)
                else:
                    mapped_status = "Unknown"
                
                # Position
                lat_str = "no position"
                lon_str = ""
                if vehicle.HasField("position"):
                    pos = vehicle.position
                    lat_str = f"{pos.latitude:.6f}"
                    lon_str = f"{pos.longitude:.6f}"

                # currentStatus
                current_stat_str = "No current_status"
                if vehicle.HasField("current_status"):
                    current_stat_str = str(vehicle.current_status)  # or map from numeric to string

                print(
                    f"Route={route_id}, Trip={trip_id}, "
                    f"Occupancy={mapped_status}, "
                    f"Lat/Lon={lat_str}{', '+lon_str if lon_str else ''}, "
                    f"currentStatus={current_stat_str}"
                )
    print("--------------------------------------------------------------------------")


