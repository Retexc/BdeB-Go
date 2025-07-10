import requests
import os
import csv
import time
from datetime import datetime, timedelta
from google.transit import gtfs_realtime_pb2
from config import (
    STM_API_KEY,
    STM_REALTIME_ENDPOINT,
    STM_VEHICLE_POSITIONS_ENDPOINT,
    STM_ALERTS_ENDPOINT
)
from ..utils import load_csv_dict  
# Cache for calendar data
_calendar_data = None
_calendar_dates_data = None

script_dir = os.path.dirname(os.path.abspath(__file__))

def load_calendar_data():
    global _calendar_data
    if _calendar_data is None:
        cal_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "STM", "calendar.txt")
        _calendar_data = {}
        try:
            with open(cal_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    service_id = row["service_id"]
                    _calendar_data[service_id] = row
        except Exception as e:
            print("Error loading calendar.txt:", e)
    return _calendar_data

def load_calendar_dates_data():
    global _calendar_dates_data
    if _calendar_dates_data is None:
        cal_dates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "STM", "calendar_dates.txt")
        _calendar_dates_data = {}
        try:
            with open(cal_dates_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    service_id = row["service_id"]
                    if service_id not in _calendar_dates_data:
                        _calendar_dates_data[service_id] = []
                    _calendar_dates_data[service_id].append(row)
        except Exception as e:
            print("Error loading calendar_dates.txt:", e)
    return _calendar_dates_data

def serviceRunsToday(service_id):
    today = datetime.now().date()
    run_today = False

    cal_data = load_calendar_data()
    cal_dates = load_calendar_dates_data()

    # Check the regular calendar
    if service_id in cal_data:
        row = cal_data[service_id]
        try:
            start_date = datetime.strptime(row["start_date"], "%Y%m%d").date()
            end_date = datetime.strptime(row["end_date"], "%Y%m%d").date()
        except Exception as e:
            print(f"Error parsing dates for service_id {service_id}: {e}")
            return False
        weekday = today.weekday()  # Monday=0, Sunday=6
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        if start_date <= today <= end_date and row[days[weekday]] == "1":
            run_today = True
    else:
        print(f"Service_id {service_id} not found in calendar.txt")

    # Apply exceptions from calendar_dates.txt
    if service_id in cal_dates:
        for row in cal_dates[service_id]:
            try:
                exception_date = datetime.strptime(row["date"], "%Y%m%d").date()
            except Exception as e:
                print(f"Error parsing exception date for service_id {service_id}: {e}")
                continue
            if exception_date == today:
                # exception_type "1" means added service, "2" means removed service.
                if row["exception_type"] == "2":
                    run_today = False
                elif row["exception_type"] == "1":
                    run_today = True
    return run_today

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

def load_stm_routes(routes_file):
    routes_data = {}
    with open(routes_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            real_id = row["route_id"]              # e.g. "1"
            short_name = row["route_short_name"]   # e.g. "171"
            routes_data[real_id] = short_name
    return routes_data

def load_stm_stop_times(filepath):
    stop_times = {}
    with open(filepath, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = (row["trip_id"], row["stop_id"])
            stop_times[key] = row["arrival_time"]
    return stop_times

def load_stm_gtfs_trips(filepath, routes_map):
    trips_data = {}
    with open(filepath, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            trip_id = row["trip_id"]
            real_route_id = row["route_id"]   # e.g. "1"
            # Convert real_route_id -> short_name
            short_name = routes_map.get(real_route_id, real_route_id)
            w_str = row.get("wheelchair_accessible", "0")
            trips_data[trip_id] = {
                "route_id": short_name,  # store the short name, e.g. "171"
                "wheelchair_accessible": w_str
            }
    return trips_data



def stm_map_occupancy_status(status):
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
    import time
    from datetime import datetime, timedelta

    # The combos we care about
    desired_combos = [
        ("171","50270","171_Est"),
        ("171","62374","171_Ouest"),
        ("180","50270","180_Est"),
        ("180","62374","180_Ouest"),
        ("164","50270","164_Est"),
        ("164","62374","164_Ouest"),
    ]

    combo_info = {
        "171_Est":   {"direction": "Est",    "location": "Collège de Bois-de-Boulogne"},
        "171_Ouest": {"direction": "Ouest",  "location": "Henri-Bourassa/du Bois-de-Boulogne"},
        "180_Est":   {"direction": "Est",    "location": "Collège de Bois-de-Boulogne"},
        "180_Ouest": {"direction": "Ouest",  "location": "Henri-Bourassa/du Bois-de-Boulogne"},
        "164_Est":   {"direction": "Est",    "location": "Collège de Bois-de-Boulogne"},
        "164_Ouest": {"direction": "Ouest",  "location": "Henri-Bourassa/du Bois-de-Boulogne"},
    }

    closest_buses = { combo[2]: None for combo in desired_combos }

    # 1) Real‑time updates
    for entity in trip_entities:
        if not entity.HasField("trip_update"):
            continue

        t_update = entity.trip_update
        route_id = t_update.trip.route_id
        trip_id  = t_update.trip.trip_id

        if route_id not in ["171","180","164"]:
            continue
        if not validate_trip(trip_id, route_id, stm_trips):
            continue

        w_str = stm_trips.get(trip_id, {}).get("wheelchair_accessible", "0")
        wheelchair_accessible = (w_str == "1")

        for stop_time in t_update.stop_time_update:
            arrival_unix = stop_time.arrival.time if stop_time.HasField("arrival") else None
            if not arrival_unix:
                continue

            stop_id = stop_time.stop_id
            final_key = None
            for (gtfs_route, wanted_stop, key_name) in desired_combos:
                if route_id == gtfs_route and stop_id == wanted_stop:
                    final_key = key_name
                    break
            if not final_key:
                continue

            # Minutes until arrival (floor)
            now_ts = time.time()
            minutes_to_arrival = (arrival_unix - now_ts) // 60

            # —— SIMPLIFIED LATE‑ONLY LOGIC —— 
            scheduled_arrival_str = stm_stop_times.get((trip_id, stop_id))
            delay_text = None
            if scheduled_arrival_str:
                try:
                    # scheduled datetime today (or tomorrow if already past)
                    h, m, s = map(int, scheduled_arrival_str.split(":"))
                    sched_dt = datetime.now().replace(hour=h % 24, minute=m, second=s, microsecond=0)
                    if sched_dt < datetime.now():
                        sched_dt += timedelta(days=1)

                    predicted_dt = datetime.fromtimestamp(arrival_unix)
                    if predicted_dt > sched_dt:
                        delay_text = f"En retard (prévu à {sched_dt.strftime('%I:%M %p')})"
                except Exception:
                    pass

            # Occupancy
            pos_info = positions_dict.get((route_id, trip_id), {})
            raw_occ = pos_info.get("occupancy")
            occ_str = stm_map_occupancy_status(raw_occ) if raw_occ else "Unknown"

            at_stop_flag = isinstance(minutes_to_arrival, (int, float)) and minutes_to_arrival < 2

            bus_obj = {
                "route_id": route_id,
                "trip_id": trip_id,
                "stop_id": stop_id,
                "arrival_time": minutes_to_arrival,
                "occupancy": occ_str,
                "direction": combo_info[final_key]["direction"],
                "location": combo_info[final_key]["location"],
                "delayed_text": delay_text,
                "early_text": None,                 # always None now
                "at_stop": at_stop_flag,
                "wheelchair_accessible": wheelchair_accessible
            }

            existing = closest_buses[final_key]
            if existing is None or (
                isinstance(existing["arrival_time"], (int, float)) and
                isinstance(minutes_to_arrival, (int, float)) and
                minutes_to_arrival < existing["arrival_time"]
            ):
                closest_buses[final_key] = bus_obj

    # 2) Fallback to schedule-only if no real-time found
    now = datetime.now()
    for (gtfs_route, wanted_stop, final_key) in desired_combos:
        if closest_buses[final_key] is None:
            nextScheduled = None
            route_trip_ids = {
                tid for tid, data in stm_trips.items() if data["route_id"] == gtfs_route
            }
            for (trip_id, stop_id), schedTimeStr in stm_stop_times.items():
                if trip_id not in route_trip_ids or stop_id != wanted_stop:
                    continue
                try:
                    parts = schedTimeStr.split(":")
                    hours = int(parts[0]) % 24
                    mins  = int(parts[1])
                    secs  = int(parts[2]) if len(parts) > 2 else 0
                    schedDt = datetime(now.year, now.month, now.day, hours, mins, secs)
                    if schedDt <= now:
                        schedDt += timedelta(days=1)
                    if nextScheduled is None or schedDt < nextScheduled:
                        nextScheduled = schedDt
                except:
                    continue

            arrival_str = nextScheduled.strftime("%I:%M %p") if nextScheduled else "Indisponible"
            fallback = {
                "route_id": gtfs_route,
                "trip_id": "N/A",
                "stop_id": wanted_stop,
                "arrival_time": arrival_str,
                "occupancy": "Unknown",
                "direction": combo_info[final_key]["direction"],
                "location": combo_info[final_key]["location"],
                "delayed_text": None,
                "early_text": None,
                "at_stop": False,
                "wheelchair_accessible": False
            }
            closest_buses[final_key] = fallback

    # 3) Return in desired order
    order = ["171_Est","171_Ouest","180_Est","180_Ouest","164_Est"]
    return [closest_buses[k] for k in order if closest_buses[k] is not None]



def debug_print_stm_occupancy_status(desired_routes, stm_trips):
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


