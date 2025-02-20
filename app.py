import os
import requests
import gtfs_realtime_pb2
import time
import csv
from flask import Flask, render_template
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
app = Flask(__name__)

# STM API Credentials
STM_API_KEY = "l71d29e015f26e423ea8fe728229d220bc"
STM_REALTIME_ENDPOINT = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates"
STM_VEHICLE_POSITIONS_ENDPOINT = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/vehiclePositions"
STM_ALERTS_ENDPOINT = "https://api.stm.info/pub/od/i3/v2/messages/etatservice"

# Exo API Information
EXO_TOKEN = "JX0ZCLTPDE"
EXO_BASE_URL = "https://opendata.exo.quebec/ServiceGTFSR"
EXO_TRIP_UPDATE_URL = f"{EXO_BASE_URL}/TripUpdate.pb?token={EXO_TOKEN}"
EXO_VEHICLE_POSITION_URL = f"{EXO_BASE_URL}/VehiclePosition.pb?token={EXO_TOKEN}"
EXO_ALERTS_URL = f"{EXO_BASE_URL}/Alert.pb?token={EXO_TOKEN}"


# Global delay configuration
GLOBAL_DELAY_MINUTES = 0


# Dynamically construct paths for GTFS files
script_dir = os.path.dirname(os.path.abspath(__file__))

# Root directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# STM GTFS file paths
stm_base_dir = os.path.join(script_dir, "STM")
stm_routes_path = os.path.join(stm_base_dir, "routes.txt")
stm_stops_path = os.path.join(stm_base_dir, "stops.txt")
stm_trips_path = os.path.join(stm_base_dir, "trips.txt")
stm_stop_times_path = os.path.join(stm_base_dir, "stop_times.txt")

# Exo GTFS file paths
exo_base_dir = os.path.join(script_dir, "Exo", "Train")
exo_stop_times_path = os.path.join(exo_base_dir, "stop_times.txt")
exo_trips_path = os.path.join(exo_base_dir, "trips.txt")
exo_routes_path = os.path.join(exo_base_dir, "routes.txt")

stop_id_map = {
    "MTL7B": "Gare Bois-de-Boulogne",
    "MTL7D": "Gare Bois-de-Boulogne",
    "MTL59A": "Gare Ahuntsic",
    "MTL59C": "Gare Ahuntsic",
    "50270": "Collège de Bois-de-Boulogne",
    "62374": "Henri-Bourassa/du Bois-de-Boulogne",
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

def load_stm_stop_times(filepath):
    stop_times = {}
    with open(filepath, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = (row["trip_id"], row["stop_id"])
            stop_times[key] = row["arrival_time"]
    return stop_times



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
    
def get_weather_alerts():
    api_key = "8c3e9fd5e6a445feb48114525251702"  # Replace with your actual API key
    url = f"http://api.weatherapi.com/v1/alerts.json?key={api_key}&q=Montreal"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get('alerts', [])
    except requests.exceptions.HTTPError as err:
        print(f"Error fetching weather alerts: {err}")
        return []
    except requests.exceptions.RequestException as err:
        print(f"Error fetching weather alerts: {err}")
        return []


def process_alerts(alerts_data):
    filtered_alerts = []
    weather_alerts = get_weather_alerts()  # Fetch weather alerts, no parameters needed

    for alert in alerts_data.get('alerts', []):
        affected_routes = set()
        direction_match = False
        stop_match = False
        
        for entity in alert.get('informed_entities', []):
            if entity.get('route_short_name') in ['171', '164', '180']:
                affected_routes.add(entity.get('route_short_name'))
            if entity.get('direction_id') == 'E':  
                direction_match = True
            if entity.get('stop_code') == '50270':
                stop_match = True
        
        if affected_routes and direction_match and stop_match:
            fr_text = next((t['text'] for t in alert['header_texts'] if t['language'] == 'fr'), '')
            fr_desc = next((t['text'] for t in alert['description_texts'] if t['language'] == 'fr'), '')

            route_numbers = ", ".join(sorted(affected_routes))  
            filtered_alerts.append({
                'header': fr_text,
                'description': fr_desc,
                'severity': alert.get('effect', 'alert'),
                'routes': route_numbers,
                'stop': "Collège de Bois-de-Boulogne"
            })

    # **Only Add Weather Alerts If They Exist**
    if weather_alerts and weather_alerts.get("alert"):  # Check if there are alerts
        weather_message = "En raison des conditions météorologiques extrêmes, les bus et trains peuvent subir des retards. Faites attention en sortant et prévoyez suffisamment de temps pour vos déplacements. Veuillez vérifier les horaires avant de partir."

        filtered_alerts.append({
            'header': "🚨 Avertissement météorologique",
            'description': weather_message,
            'severity': "weather_alert",
            'routes': "Tous le réseaux",
            'stop': "STM et Exo"
        })

    return filtered_alerts



# Example usage
alerts_data = {
    'alerts': [
        {
            'informed_entities': [{'route_short_name': '171', 'direction_id': 'E', 'stop_code': '50270'}],
            'header_texts': [{'language': 'fr', 'text': 'Attention!'}],
            'description_texts': [{'language': 'fr', 'text': 'There is an alert due to weather conditions.'}],
            'effect': 'alert'
        }
    ]
}
filtered_alerts = process_alerts(alerts_data)
#print("Filtered Alerts:", filtered_alerts)


def process_stm_trip_updates(entities, stm_trips):
    buses = []
    desired_routes = ["171", "180", "164", "171_Ouest", "180_Ouest"]  # Removed "164_Ouest"
    closest_buses = {route: None for route in desired_routes}

    route_metadata = {
        "171": {"direction": "Est", "location": "Collège de Bois-de-Boulogne"},
        "180": {"direction": "Est", "location": "Collège de Bois-de-Boulogne"},
        "164": {"direction": "Est", "location": "Collège de Bois-de-Boulogne"},
        "171_Ouest": {"direction": "Ouest", "location": "Henri-Bourassa/du Bois-de-Boulogne"},
        "180_Ouest": {"direction": "Ouest", "location": "Henri-Bourassa/du Bois-de-Boulogne"},
    }

    stop_ids_of_interest = ["50270", "62374"]  # Stops to check for vehicle presence

    for entity in entities:
        if entity.HasField("trip_update") or entity.HasField("vehicle"):
            trip = entity.trip_update.trip if entity.HasField("trip_update") else None
            stop_time_updates = entity.trip_update.stop_time_update if entity.HasField("trip_update") else []
            vehicle = entity.vehicle if entity.HasField("vehicle") else None

            route_id = trip.route_id if trip else vehicle.trip.route_id
            trip_id = trip.trip_id if trip else vehicle.trip.trip_id
            occupancy_status = vehicle.occupancy_status if vehicle and vehicle.HasField("occupancy_status") else "UNKNOWN"
            vehicle_stop_id = vehicle.stop_id if vehicle and vehicle.HasField("stop_id") else None  # Stop where the bus is detected

            if route_id in desired_routes and validate_trip(trip_id, route_id, stm_trips):
                for stop_time in stop_time_updates:
                    if stop_time.stop_id in stop_ids_of_interest:
                        if route_id == "164" and stop_time.stop_id == "62374":
                            continue  # Skip since 164 Ouest is unavailable

                        scheduled_arrival_str = stm_stop_times.get((trip_id, stop_time.stop_id), None)
                        arrival_time = stop_time.arrival.time if stop_time.HasField("arrival") else None
                        delay_minutes = None
                        scheduled_formatted = "Inconnu"

                        if scheduled_arrival_str and arrival_time:
                            try:
                                h, m, s = map(int, scheduled_arrival_str.split(":"))
                                if h >= 24:
                                    h = 0  # Fix invalid hour
                                scheduled_ts = datetime.now().replace(hour=h, minute=m, second=s, microsecond=0).timestamp()

                                # Format scheduled time for display (hh:mm)
                                scheduled_formatted = f"{h:02d}:{m:02d}"

                                # Calculate delay
                                delay_seconds = arrival_time - scheduled_ts
                                delay_minutes = delay_seconds // 60  # Convert to minutes
                            except ValueError as e:
                                print(f"Error parsing scheduled arrival time: {scheduled_arrival_str} - {e}")
                                scheduled_ts = None
                                delay_minutes = None

                        # Calculate time until arrival
                        minutes_to_arrival = (arrival_time - int(time.time())) // 60 if arrival_time else None

                        # Set delay format to match Chrono
                        if delay_minutes is not None:
                            if delay_minutes > 0:
                                delayed_text = f"En retard (prévu à {scheduled_formatted})"
                            elif delay_minutes < 0:
                                delayed_text = f"En avance (prévu à {scheduled_formatted})"
                            else:
                                delayed_text = None  # On time
                        else:
                            delayed_text = None  # Default if data is missing

                        if minutes_to_arrival is not None:
                            route_key = f"{route_id}_Ouest" if stop_time.stop_id == "62374" else route_id
                            if closest_buses.get(route_key) is None or minutes_to_arrival < closest_buses[route_key]["arrival_time"]:
                                closest_buses[route_key] = {
                                    "route_id": route_id,
                                    "trip_id": trip_id,
                                    "stop_id": stop_time.stop_id,
                                    "arrival_time": minutes_to_arrival,
                                    "occupancy": stm_map_occupancy_status(occupancy_status),
                                    "direction": route_metadata.get(route_key, {}).get("direction", "Unknown"),
                                    "location": route_metadata.get(route_key, {}).get("location", "Unknown"),
                                    "delayed_text": delayed_text,
                                    "early_text": None,  # Not needed with Chrono format
                                    "at_stop": vehicle_stop_id == stop_time.stop_id  # True if the vehicle is detected at this stop
                                }

    # Handle cases where no buses are found for a route
    for route in desired_routes:
        if route.startswith("164") and "Ouest" in route:
            continue  # Skip since 164 Ouest is unavailable
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
                "at_stop": False  # No vehicle detected at stop
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

def fetch_exo_alerts():
    headers = {
        "accept": "application/x-protobuf",
    }
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
    
def process_exo_alerts(entities):
    filtered_alerts = []
    
    # Mapping stop_id to train direction names
    stop_id_to_route = {
        "MTL7D": "Dir Lucien l'Allier",
        "MTL7B": "Saint-Jérôme",
        "MTL59A": "Mascouche"
    }
    
    # List of stop_ids to filter
    valid_stop_ids = set(stop_id_to_route.keys())
    
    for entity in entities:
        if entity.HasField('alert'):
            alert = entity.alert
            #print(f"Alert data: {alert}")  # Debug log to inspect alert
            
            for informed_entity in alert.informed_entity:
                #print(f"Informed entity: {informed_entity}")  # Debug log to inspect informed_entity
                
                if informed_entity.HasField('stop_id'):
                    stop_id = informed_entity.stop_id
                    #print(f"Stop ID: {stop_id}")  # Debug log to check stop_id
                    
                    if stop_id in valid_stop_ids:
                        # Retrieve the corresponding train direction name
                        train_route = stop_id_to_route.get(stop_id, "Train inconnu")
                        #print(f"Mapped Train Route: {train_route}")  # Debug log

                        # Get the description in French
                        fr_description = ''
                        for translation in alert.description_text.translation:
                            if translation.language == 'fr':
                                fr_description = translation.text
                                break
                        if not fr_description:
                            fr_description = 'Description non disponible en français'
                        
                        # Add the filtered alert with relevant details
                        alert_data = {
                            'header': f"🚨🚊 Info Train",
                            'description': fr_description,
                            'severity': alert.effect,
                            'stop_id': stop_id,
                            'train_route': train_route
                        }
                        #print(f"Final Alert Data: {alert_data}")  # Debug log before adding
                        filtered_alerts.append(alert_data)
    
    return filtered_alerts


# Test fetching and processing EXO alerts
exo_alerts = fetch_exo_alerts()
if exo_alerts:
    processed_alerts = process_exo_alerts(exo_alerts)
    print(f"Processed EXO Alerts: {processed_alerts}")
else:
    print("No EXO alerts found.")
  

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
                    print(f"Skipping invalid date format in no_service_days.txt: {date_str}")
    return no_service_dates
    
def is_service_unavailable():
    """Check if today is a no-service day."""
    today = datetime.today().date()
    no_service_dates = load_no_service_days()
    
    # Check if today is a weekend or a no-service holiday
    return today.weekday() >= 5 or today in no_service_dates

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

def add_simulated_delay_by_stop(stop_times, target_stop_id, delay_minutes=7):
    """
    Add a simulated delay to trains stopping at a specific stop ID.

    Args:
        stop_times (list): List of stop time dictionaries.
        target_stop_id (str): The stop ID to filter trains for adding the delay.
        delay_minutes (int): Number of minutes to delay the arrival time.

    Returns:
        list: Updated stop times with delays applied.
    """
    updated_stop_times = []
    for stop in stop_times:
        # Check if the stop_id matches the target_stop_id
        if stop["stop_id"] == target_stop_id:
            # Parse the arrival time
            arrival_time = stop["arrival_time"]
            h, m, s = map(int, arrival_time.split(":"))
            
            # Add the delay
            new_time = datetime(2000, 1, 1, h, m, s) + timedelta(minutes=delay_minutes)
            stop["arrival_time"] = new_time.strftime("%H:%M:%S")
        
        updated_stop_times.append(stop)
    
    return updated_stop_times

    


# Modify process_exo_train_schedule to include occupancy
# Modify process_exo_train_schedule_with_occupancy
def process_exo_train_schedule_with_occupancy(exo_stop_times, exo_trips, vehicle_positions):
    current_time = datetime.now()
    current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second

    # Stop and direction mapping
    stop_id_map = {
        "MTL7B": "Gare Bois-de-Boulogne",
        "MTL7D": "Gare Bois-de-Boulogne",
        "MTL59A": "Gare Ahuntsic",
        "MTL59C": "Gare Ahuntsic",
    }
    direction_map = {
        "4": {"0": "Lucien-L'allier", "1": "Saint-Jérôme"},
        "6": {"0": "Gare centrale", "1": "Mascouche"},
    }

    # Only these stops should be processed
    desired_stops = {"MTL7D", "MTL7B", "MTL59A", "MTL59C"}

    # Initialize a dictionary to store the closest train for each stop
    closest_trains = {stop: None for stop in desired_stops}

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








def process_vehicle_positions(entities):
    vehicle_data = []
    for entity in entities:
        if entity.HasField("vehicle"):
            vehicle = entity.vehicle
            trip_id = vehicle.trip.trip_id
            route_id = vehicle.trip.route_id
            occupancy_status = vehicle.occupancy_status if vehicle.HasField("occupancy_status") else "UNKNOWN"
            latitude = vehicle.position.latitude if vehicle.HasField("position") else None
            longitude = vehicle.position.longitude if vehicle.HasField("position") else None
            stop_id = vehicle.stop_id if vehicle.HasField("stop_id") else None
            
            vehicle_data.append({
                "trip_id": trip_id,
                "route_id": route_id,
                "occupancy": stm_map_occupancy_status(occupancy_status),
                "latitude": latitude,
                "longitude": longitude,
                "stop_id": stop_id,  # Indicates if the vehicle is at a stop
                "at_stop": stop_id is not None  # True if vehicle is at a stop
            })
            
    return vehicle_data

    

# Load STM data
stm_trips = load_stm_gtfs_trips(stm_trips_path)
stm_stop_times = load_stm_stop_times(stm_stop_times_path)


# Load Exo data
exo_trips = load_exo_gtfs_trips(exo_trips_path)
def prepare_exo_stop_times():
    """Load Exo stop times without modifications."""
    return load_exo_stop_times(exo_stop_times_path)




@app.route("/")
def index():
    exo_trip_updates, exo_vehicle_positions = fetch_exo_realtime_data()
    exo_stop_times = prepare_exo_stop_times()  # Remove target_stop_id parameter
    processed_vehicle_positions = process_exo_vehicle_positions(exo_vehicle_positions, exo_stop_times)
    
    # Add exo_trip_updates argument ▼
    exo_trains = process_exo_train_schedule_with_occupancy(
        exo_stop_times,
        exo_trips,
        processed_vehicle_positions,
        exo_trip_updates  # This was missing
    )
    
    current_time = time.strftime("%I:%M:%S %p")
    return render_template(
        "index.html",
        next_trains=exo_trains,
        current_time=current_time
    )

@app.route("/api/data")
def api_data():
    # Fetch STM alerts
    stm_alerts_data = fetch_stm_alerts()
    processed_stm_alerts = process_alerts(stm_alerts_data) if stm_alerts_data else []
    
    # Fetch EXO alerts
    exo_alerts_entities = fetch_exo_alerts()
    processed_exo_alerts = process_exo_alerts(exo_alerts_entities)
    
    # Combine STM and EXO alerts
    all_alerts = processed_stm_alerts + processed_exo_alerts
    
    # Fetch and process STM and EXO real-time data (existing code)
    trip_entities = fetch_stm_realtime_data()
    vehicle_entities = fetch_stm_vehicle_positions()
    buses = process_stm_trip_updates(trip_entities, stm_trips)
    vehicle_data = process_vehicle_positions(vehicle_entities)
    
    for bus in buses:
        for vehicle in vehicle_data:
            if bus["trip_id"] == vehicle["trip_id"]:
                bus["occupancy"] = vehicle["occupancy"]
                break

    exo_trip_updates, exo_vehicle_positions = fetch_exo_realtime_data()
    exo_stop_times = prepare_exo_stop_times()
    processed_vehicle_positions = process_exo_vehicle_positions(exo_vehicle_positions, exo_stop_times)

    exo_trains = process_exo_train_schedule_with_occupancy(
        exo_stop_times, 
        exo_trips, 
        processed_vehicle_positions,
        exo_trip_updates
    )

    if is_service_unavailable():
        for train in exo_trains:
            train["no_service_text"] = "Aucun service aujourd'hui"
            train["arrival_time"] = "N/A"
            train["delayed_text"] = None
            train["early_text"] = None

    # Return the data with alerts included
    return {
        "buses": buses,
        "next_trains": [
            {
                **train,
                "delayed_text": train.get("delayed_text", None),
                "early_text": train.get("early_text", None)
            }
            for train in exo_trains
        ],
        "current_time": time.strftime("%I:%M:%S %p"),
        "alerts": all_alerts  # Include combined alerts, including weather alerts
    }





if __name__ == "__main__":
    app.run(debug=True)
