import os
import requests
import gtfs_realtime_pb2
import time
import csv
from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

# STM API Credentials
STM_API_KEY = "l71d29e015f26e423ea8fe728229d220bc"
STM_REALTIME_ENDPOINT = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates"
STM_VEHICLE_POSITIONS_ENDPOINT = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/vehiclePositions"

# Exo API Information
EXO_TOKEN = "JX0ZCLTPDE"
EXO_BASE_URL = "https://opendata.exo.quebec/ServiceGTFSR"
EXO_TRIP_UPDATE_URL = f"{EXO_BASE_URL}/TripUpdate.pb?token={EXO_TOKEN}"
EXO_VEHICLE_POSITION_URL = f"{EXO_BASE_URL}/VehiclePosition.pb?token={EXO_TOKEN}"

# Dynamically construct paths for GTFS files
script_dir = os.path.dirname(os.path.abspath(__file__))

# Root directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# STM GTFS file paths
stm_routes_path = os.path.join(script_dir, "routes.txt")
stm_stops_path = os.path.join(script_dir, "stops.txt")
stm_trips_path = os.path.join(script_dir, "trips.txt")

# Exo GTFS file paths
exo_base_dir = os.path.join(script_dir, "Exo", "Train")
exo_stop_times_path = os.path.join(exo_base_dir, "stop_times.txt")
exo_trips_path = os.path.join(exo_base_dir, "trips.txt")
exo_routes_path = os.path.join(exo_base_dir, "routes.txt")

stop_id_map = {
    "MTL7B": "Gare Bois-de-Boulogne",
    "MTL7D": "Gare Bois-de-Boulogne",
    "MTL59A": "Gare Ahuntsic"
}




# Load STM GTFS trips
def load_stm_gtfs_trips(filepath):
    trips_data = {}
    with open(filepath, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            trips_data[row["trip_id"]] = row["route_id"]
    return trips_data

# Load Exo GTFS trips with direction_id
def load_exo_gtfs_trips(filepath):
    trips_data = {}
    with open(filepath, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            trips_data[row["trip_id"]] = {
                "route_id": row["route_id"],
                "direction_id": row.get("direction_id", "0"),  # Default to "0" if direction_id is missing
            }
    return trips_data


# Load Exo GTFS stop times
def load_exo_stop_times(filepath):
    stop_times_data = []
    with open(filepath, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            stop_times_data.append(row)
    return stop_times_data


# Validate trip_id and route_id from the static file
def validate_trip(trip_id, route_id, gtfs_trips):
    return gtfs_trips.get(trip_id) == route_id

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
          # Print vehicle positions
        return feed.entity
    else:
        print(f"API Error: {response.status_code} - {response.text}")
        return []
    
# Fetch real-time data from STM API
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
          # Print trip updates
        return feed.entity
    else:
        print(f"API Error: {response.status_code} - {response.text}")
        return []

# Process real-time data for buses
# Process real-time data for buses with occupancy status
def process_stm_trip_updates(entities, stm_trips):
    buses = []
    desired_routes = ["171", "180", "164"]
    closest_buses = {route: None for route in desired_routes}

    route_metadata = {
        "171": {"direction": "Est", "location": "Collège de Bois-de-Boulogne"},
        "180": {"direction": "Est", "location": "Collège de Bois-de-Boulogne"},
        "164": {"direction": "Est", "location": "Collège de Bois-de-Boulogne"},
    }


    for entity in entities:
        if entity.HasField("trip_update") or entity.HasField("vehicle"):
            trip = entity.trip_update.trip if entity.HasField("trip_update") else None
            stop_time_updates = entity.trip_update.stop_time_update if entity.HasField("trip_update") else []
            vehicle = entity.vehicle if entity.HasField("vehicle") else None

            route_id = trip.route_id if trip else vehicle.trip.route_id
            trip_id = trip.trip_id if trip else vehicle.trip.trip_id
            occupancy_status = vehicle.occupancy_status if vehicle and vehicle.HasField("occupancy_status") else "UNKNOWN"
            

            if route_id in desired_routes and validate_trip(trip_id, route_id, stm_trips):
                for stop_time in stop_time_updates:
                    if stop_time.stop_id == "50270":
                        arrival_time = stop_time.arrival.time if stop_time.HasField("arrival") else None
                        minutes_to_arrival = (arrival_time - int(time.time())) // 60 if arrival_time else None

                        if minutes_to_arrival is not None:
                            if closest_buses[route_id] is None or minutes_to_arrival < closest_buses[route_id]["arrival_time"]:
                                closest_buses[route_id] = {
                                    "route_id": route_id,
                                    "trip_id": trip_id,
                                    "stop_id": "50270",
                                    "arrival_time": minutes_to_arrival,
                                    "occupancy": stm_map_occupancy_status(occupancy_status),  # Map occupancy status
                                    "direction": route_metadata.get(route_id, {}).get("direction", "Unknown"),
                                    "location": route_metadata.get(route_id, {}).get("location", "Unknown"),
                                }

    for route in desired_routes:
        if closest_buses[route] is None:
            closest_buses[route] = {
                "route_id": route,
                "trip_id": "N/A",
                "stop_id": "50270",
                "arrival_time": "Unavailable (Route Canceled)",
                "occupancy": "Unknown",
                "direction": route_metadata.get(route, {}).get("direction", "Unknown"),
                "location": route_metadata.get(route, {}).get("location", "Unknown"),
            }

    buses = [bus for bus in closest_buses.values()]
    return buses

# Map occupancy status to a readable format
def stm_map_occupancy_status(status):
    mapping = {
        1: "Near_Empty",
        2: "Light",
        3: "Medium",
        4: "Null",
        5: "Full",  

    }
    return mapping.get(status, "Unknown")


# Fetch real-time data from Exo API
def fetch_exo_realtime_data():
    headers = {
        "accept": "application/x-protobuf",
    }
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
    
# Simulate "real-time" schedule in minutes using static data
def get_exo_train_schedule(stop_times, stop_id, current_time, trips_data):
    schedule = []
    current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second  # Current time in seconds
    for stop_time in stop_times:
        if stop_time["stop_id"] == stop_id:
            trip_id = stop_time["trip_id"]
            route_id = trips_data.get(trip_id, "Unknown")  # Get route_id from trips data
            arrival_time_str = stop_time["arrival_time"]
            h, m, s = map(int, arrival_time_str.split(":"))  # Parse the arrival time
            arrival_time_seconds = h * 3600 + m * 60 + s  # Convert time to seconds

            # Handle day rollover: if arrival_time_seconds < current_seconds, add 24 hours to arrival time
            if arrival_time_seconds < current_seconds:
                arrival_time_seconds += 24 * 3600

            # Add only upcoming trains
            if arrival_time_seconds > current_seconds:
                minutes_remaining = (arrival_time_seconds - current_seconds) // 60
                schedule.append({
                    "trip_id": trip_id,
                    "route_id": route_id,
                    "arrival_time": f"{h:02}:{m:02}:{s:02}",  # Format as hh:mm:ss
                    "minutes_remaining": minutes_remaining,
                })

    return sorted(schedule, key=lambda x: x["minutes_remaining"])  # Sort by nearest train




# Map trip details to route and direction
def exo_map_train_details(schedule, trips_data, stop_id_map):
    mapped_schedule = []
    for train in schedule:
        trip_id = train["trip_id"]
        route_id = train["route_id"]
        stop_id = train["stop_id"]  # Add this if stop_id is available in the schedule
        direction_id = trips_data.get(trip_id, {}).get("direction_id", "0")
        
        # Determine the direction based on route_id and direction_id
        direction = "Saint-Jérôme" if route_id == "4" and direction_id == "1" else "Lucien-L'allier" if route_id == "4" and direction_id == "0" else "Mascouche" if route_id == "6" else "Unknown"
        
        # Get stop name from the map
        stop_name = stop_id_map.get(stop_id, "Unknown")
        
        # Logic to display time based on minutes remaining
        minutes_remaining = train["minutes_remaining"]
        if minutes_remaining <= 30:
            display_time = f"{minutes_remaining} min"  # Display minutes remaining
        else:
            h, m, _ = map(int, train["arrival_time"].split(":"))  # Strip out the seconds
            display_time = f"{h:02}h{m:02}"  # Display only hours and minutes

        mapped_train = {
            "route_id": "12" if route_id == "4" else "15" if route_id == "6" else route_id,
            "arrival_time": display_time,  # Display the formatted time
            "direction": direction,
            "location": stop_name,  # Use the mapped stop name
        }
        mapped_schedule.append(mapped_train)
    return mapped_schedule


def exo_map_occupancy_status(status):
    mapping = {
        1: "Near_Empty",  # Example: 1 means the train is nearly empty
        2: "Light",       # Example: 2 means light occupancy
        3: "Medium",      # Example: 3 means moderate occupancy
        4: "Full",        # Example: 4 means the train is full
    }
    return mapping.get(status, "Unknown")  # Return "Unknown" if the status is not in the mapping



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






# Modify process_exo_train_schedule to include occupancy
def process_exo_train_schedule_with_occupancy(exo_stop_times, exo_trips, vehicle_positions):
    current_time = datetime.now()
    current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second

    # Stop and direction mapping
    stop_id_map = {
        "MTL7B": "Gare Bois-de-Boulogne",
        "MTL7D": "Gare Bois-de-Boulogne",
        "MTL59A": "Gare Ahuntsic",
    }
    direction_map = {
        "4": {"0": "Lucien-L'allier", "1": "Saint-Jérôme"},
        "6": {"1": "Mascouche"},
    }

    # Only these stops should be processed
    desired_stops = {"MTL7D", "MTL7B", "MTL59A"}

    # Initialize a dictionary to store the closest train for each stop
    closest_trains = {stop: None for stop in desired_stops}

    for stop_time in exo_stop_times:
        stop_id = stop_time["stop_id"]
        if stop_id in desired_stops:
            trip_id = stop_time["trip_id"]
            trip_data = exo_trips.get(trip_id, {})
            route_id = trip_data.get("route_id")
            direction_id = trip_data.get("direction_id")

            if route_id in direction_map and direction_id in direction_map[route_id]:
                arrival_time_str = stop_time["arrival_time"]
                h, m, s = map(int, arrival_time_str.split(":"))
                arrival_time_seconds = h * 3600 + m * 60 + s

                if arrival_time_seconds < current_seconds:
                    arrival_time_seconds += 24 * 3600

                minutes_remaining = (arrival_time_seconds - current_seconds) // 60
                exo_occupancy_status = "Unknown"  # Default occupancy status

                # Match vehicle positions for occupancy
                for vehicle in vehicle_positions:
                    if trip_id == vehicle["trip_id"]:
                        exo_occupancy_status = vehicle.get("occupancy", "Unknown")
                        break

                train_info = {
                    "stop_id": stop_id,
                    "trip_id": trip_id,
                    "route_id": route_id,
                    "direction": direction_map[route_id][direction_id],
                    "arrival_time": arrival_time_str,
                    "minutes_remaining": minutes_remaining,
                    "occupancy": exo_occupancy_status,  # Add occupancy to the train info
                }

                # Update the closest train for the stop
                if (closest_trains[stop_id] is None or
                        minutes_remaining < closest_trains[stop_id]["minutes_remaining"]):
                    closest_trains[stop_id] = train_info

    # Prepare the final list
    filtered_schedule = [train for train in closest_trains.values() if train is not None]
    prioritized_schedule = exo_map_train_details(filtered_schedule, exo_trips, stop_id_map)

    print("Final Exo Train Schedule with Occupancy:", prioritized_schedule)  # Debugging
    return prioritized_schedule





















    
# Load trips data from GTFS static file
#gtfs_trips = load_gtfs_trips(os.path.join(script_dir, "trips.txt"))
#stop_times = load_stop_times(stop_times_path)

# Load STM data
stm_trips = load_stm_gtfs_trips(stm_trips_path)

# Load Exo data
exo_trips = load_exo_gtfs_trips(exo_trips_path)
exo_stop_times = load_exo_stop_times(exo_stop_times_path)


# Debug to confirm data is loaded correctly
#print("Loaded STM Trips:", stm_trips)
#print("Loaded Exo Trips:", exo_trips)
#print("Loaded Exo Stop Times:", exo_stop_times)

@app.route("/")
def index():
    exo_trip_updates, exo_vehicle_positions = fetch_exo_realtime_data()
    processed_vehicle_positions = process_exo_vehicle_positions(exo_vehicle_positions, exo_stop_times)
    exo_trains = process_exo_train_schedule_with_occupancy(exo_stop_times, exo_trips, processed_vehicle_positions)
    current_time = time.strftime("%I:%M:%S %p")
    return render_template(
        "index.html",
        next_trains=exo_trains,
        current_time=current_time
    )

@app.route("/api/data")
def api_data():
    # Fetch real-time data for STM
    trip_entities = fetch_stm_realtime_data()  # Fetch STM trip updates
    vehicle_entities = fetch_stm_vehicle_positions()  # Fetch STM vehicle positions

    # Process STM buses
    buses = process_stm_trip_updates(trip_entities, stm_trips)
    vehicle_data = process_vehicle_positions(vehicle_entities)
    
    # Match STM buses with occupancy
    for bus in buses:
        for vehicle in vehicle_data:
            if bus["trip_id"] == vehicle["trip_id"]:  # Match trip IDs
                bus["occupancy"] = vehicle["occupancy"]  # Update occupancy
                break

    for bus in buses:
        if bus["route_id"] == "171":  # Filter for route 171
            print(f"Route 171 Occupancy: {bus.get('occupancy', 'Unknown')}")  # Log the occupancy            

    # Fetch real-time data for Exo trains
    exo_trip_updates, exo_vehicle_positions = fetch_exo_realtime_data()
    processed_vehicle_positions = process_exo_vehicle_positions(exo_vehicle_positions, exo_stop_times)
    exo_trains = process_exo_train_schedule_with_occupancy(exo_stop_times, exo_trips, processed_vehicle_positions)

    # Debugging
    print("Final Exo Trains with Occupancy:", exo_trains)

    # Return JSON response
    return {
        "buses": buses,
        "next_trains": exo_trains,  # Ensure each train includes an "occupancy" field
        "current_time": time.strftime("%I:%M:%S %p"),
    }

def process_vehicle_positions(entities):
    vehicle_data = []
    for entity in entities:
        if entity.HasField("vehicle"):
            vehicle = entity.vehicle
            trip_id = vehicle.trip.trip_id
            route_id = vehicle.trip.route_id
            occupancy_status = vehicle.occupancy_status if vehicle.HasField("occupancy_status") else "UNKNOWN"
            
            vehicle_data.append({
                "trip_id": trip_id,
                "route_id": route_id,
                "occupancy": stm_map_occupancy_status(occupancy_status),  # Map to readable format
            })
            
    return vehicle_data



if __name__ == "__main__":
    app.run(debug=True)
