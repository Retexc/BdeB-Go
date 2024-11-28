import os
import requests
import gtfs_realtime_pb2
import time
import csv
from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

# STM API Credentials
STM_API_KEY = "l719ebd45028394df8a685460891da2772"
STM_REALTIME_ENDPOINT = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates"

# Dynamically construct paths for GTFS files
script_dir = os.path.dirname(os.path.abspath(__file__))

stop_times_path = os.path.join(script_dir, "Exo", "Train", "stop_times.txt")
trips_path = os.path.join(script_dir, "Exo", "Train", "trips.txt")
stops_path = os.path.join(script_dir, "Exo", "Train", "stops.txt")

# Load static GTFS trips for validation
def load_gtfs_trips(filepath):
    trips_data = {}
    with open(filepath, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            trips_data[row["trip_id"]] = row["route_id"]
    return trips_data

# Validate trip_id and route_id from the static file
def validate_trip(trip_id, route_id, gtfs_trips):
    return gtfs_trips.get(trip_id) == route_id

# Fetch real-time data from STM API
def fetch_realtime_data():
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

# Process real-time data for buses
def process_trip_updates(entities, gtfs_trips):
    buses = []
    desired_routes = ["171", "180", "164"]
    closest_buses = {route: None for route in desired_routes}

    for entity in entities:
        if entity.HasField("trip_update"):
            trip = entity.trip_update.trip
            stop_time_updates = entity.trip_update.stop_time_update
            route_id = trip.route_id
            trip_id = trip.trip_id

            if route_id in desired_routes and validate_trip(trip_id, route_id, gtfs_trips):
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
                                }

    for route in desired_routes:
        if closest_buses[route] is None:
            closest_buses[route] = {
                "route_id": route,
                "trip_id": "N/A",
                "stop_id": "50270",
                "arrival_time": "Unavailable (Route Canceled)",
            }

    buses = [bus for bus in closest_buses.values()]
    return buses

# Process static data for the Saint-Jérôme train
def process_train_data():
    train_stops = {
        "MTL7B": "4",  # Gare Bois-de-Boulogne, direction Saint-Jérôme
        "MTL7D": "4",  # Gare Bois-de-Boulogne, direction Montreal-Ouest
        "MTL59A": "6",  # Gare Ahuntsic, direction Mascouche
    }
    current_time = datetime.now()
    train_schedule = []

    trip_to_route = {}
    with open(trips_path, "r") as trips_file:
        reader = csv.DictReader(trips_file)
        for row in reader:
            if row["route_id"] in train_stops.values():
                trip_to_route[row["trip_id"]] = row["route_id"]

    with open(stop_times_path, "r") as stop_times_file:
        reader = csv.DictReader(stop_times_file)
        for row in reader:
            stop_id = row["stop_id"]
            trip_id = row["trip_id"]
            if stop_id in train_stops and trip_id in trip_to_route:
                arrival_time_str = row["arrival_time"]
                arrival_time = datetime.strptime(arrival_time_str, "%H:%M:%S").replace(
                    year=current_time.year, month=current_time.month, day=current_time.day
                )
                if arrival_time < current_time:
                    continue  # Skip past trains

                train_schedule.append({
                    "route_id": trip_to_route[trip_id],
                    "stop_id": stop_id,
                    "trip_id": trip_id,
                    "scheduled_time": arrival_time.strftime("%I:%M %p"),
                    "real_time": None,  # Placeholder for real-time data
                })

    train_schedule.sort(key=lambda x: datetime.strptime(x["scheduled_time"], "%I:%M %p"))
    
    
    # Deduplicate by direction (Saint-Jérôme, Montreal-Ouest, Mascouche)
    unique_trains = []
    seen_directions = set()
    for train in train_schedule:
        direction_key = train["stop_id"]
        if direction_key not in seen_directions:
            unique_trains.append(train)
            seen_directions.add(direction_key)
        if len(unique_trains) == 3:  # Limit to 3 unique trains
            break

    return unique_trains




def test_fetch_scheduled_times():
    train_stops = {
        "MTL7D": "4",  # Gare Bois-de-Boulogne, direction Montreal-Ouest
        "MTL7B": "4",  # Gare Bois-de-Boulogne, direction Saint-Jérôme
        "MTL59A": "6",  # Gare Ahuntsic, direction Mascouche
    }
    current_time = datetime.now()
    train_schedule = []

    # Map trip IDs to their route IDs
    trip_to_route = {}
    with open(trips_path, "r") as trips_file:
        reader = csv.DictReader(trips_file)
        for row in reader:
            if row["route_id"] in train_stops.values():
                trip_to_route[row["trip_id"]] = row["route_id"]

    # Read stop times for each train stop
    with open(stop_times_path, "r") as stop_times_file:
        reader = csv.DictReader(stop_times_file)
        for row in reader:
            stop_id = row["stop_id"]
            trip_id = row["trip_id"]
            if stop_id in train_stops and trip_id in trip_to_route:
                arrival_time_str = row["arrival_time"]
                arrival_time = datetime.strptime(arrival_time_str, "%H:%M:%S").replace(
                    year=current_time.year, month=current_time.month, day=current_time.day
                )

                # Format time for display
                formatted_time = arrival_time.strftime("%I:%M %p")

                # Add to the train schedule
                train_schedule.append({
                    "route_id": trip_to_route[trip_id],
                    "stop_id": stop_id,
                    "trip_id": trip_id,
                    "scheduled_time": formatted_time,
                })

    # Sort by scheduled time
    train_schedule.sort(key=lambda x: datetime.strptime(x["scheduled_time"], "%I:%M %p"))

    # Print results to check the data
    print("Test Fetch Scheduled Times:")
    for train in train_schedule[:5]:  # Print the next 5 trains
        print(train)


# Call the function to test
test_fetch_scheduled_times()




# Load trips data from GTFS static file
gtfs_trips = load_gtfs_trips(os.path.join(script_dir, "trips.txt"))

@app.route("/")
def index():
    entities = fetch_realtime_data()
    buses = process_trip_updates(entities, gtfs_trips)
    next_train = process_train_data()  # Only the next train
    current_time = time.strftime("%I:%M:%S %p")

    return render_template(
        "index.html",
        buses=buses,
        next_train=next_train,
        current_time=current_time
    )

@app.route("/api/data")
def api_data():
    entities = fetch_realtime_data()
    buses = process_trip_updates(entities, gtfs_trips)
    next_trains = process_train_data()  # Return all relevant train directions
    return {
        "buses": buses,
        "next_trains": next_trains,
        "current_time": time.strftime("%I:%M:%S %p")
    }


if __name__ == "__main__":
    app.run(debug=True)
