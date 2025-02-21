# app.py

from flask import Flask, render_template
import time
import os, json

from config import WEATHER_API_KEY
from utils import is_service_unavailable
from stm import (
    fetch_stm_alerts,
    fetch_stm_realtime_data,
    fetch_stm_positions_dict,      # new helper to get lat/lon
    load_stm_gtfs_trips,
    load_stm_stop_times,
    process_stm_trip_updates,       # merges arrival + positions
    stm_map_occupancy_status,
    debug_print_stm_occupancy_status,
    validate_trip
)
from exo import (
    fetch_exo_alerts,
    fetch_exo_realtime_data,
    load_exo_gtfs_trips,
    load_exo_stop_times,
    process_exo_vehicle_positions,
    process_exo_train_schedule_with_occupancy
)
from alerts import (
    process_stm_alerts,
    process_exo_alerts
)

app = Flask(__name__)

# ====================================================================
# Load static GTFS data once at startup
# ====================================================================
stm_trips = load_stm_gtfs_trips("STM/trips.txt")
stm_stop_times = load_stm_stop_times("STM/stop_times.txt")
exo_trips = load_exo_gtfs_trips("Exo/Train/trips.txt")
exo_stop_times = load_exo_stop_times("Exo/Train/stop_times.txt")

@app.route("/debug-occupancy")
def debug_occupancy():
    desired = ["171", "164", "180"]
    debug_print_stm_occupancy_status(desired, stm_trips)
    return "Check your console logs for occupancy info!"

# ====================================================================
# ROUTE: Home Page
# ====================================================================
@app.route("/")
def index():
    exo_trip_updates, exo_vehicle_positions = fetch_exo_realtime_data()
    exo_vehicle_data = process_exo_vehicle_positions(exo_vehicle_positions, exo_stop_times)
    
    exo_trains = process_exo_train_schedule_with_occupancy(
        exo_stop_times,
        exo_trips,
        exo_vehicle_data,
        exo_trip_updates
    )
    
    current_time = time.strftime("%I:%M:%S %p")
    return render_template(
        "index.html",
        next_trains=exo_trains,
        current_time=current_time
    )

# ====================================================================
# ROUTE: API JSON Data
# ====================================================================
@app.route("/api/data")
def api_data():
    # ========== ALERTS ==========
    stm_alert_json = fetch_stm_alerts()
    processed_stm = process_stm_alerts(stm_alert_json, WEATHER_API_KEY) if stm_alert_json else []

    exo_alert_entities = fetch_exo_alerts()
    processed_exo = process_exo_alerts(exo_alert_entities)
    all_alerts = processed_stm + processed_exo

    # === Custom Alert Logic ===
    custom_path = os.path.join(os.path.dirname(__file__), "custom_messages.json")
    if os.path.exists(custom_path):
        with open(custom_path, "r", encoding="utf-8") as f:
            try:
                custom_alerts = json.load(f)  # Expecting a list of alert objects
                if not isinstance(custom_alerts, list):
                    custom_alerts = []
            except:
                custom_alerts = []

        # For each alert object in custom_alerts, append to all_alerts
        for c in custom_alerts:
            all_alerts.append({
                "header": c.get("header", "Message"),
                "description": c.get("description", ""),
                "severity": c.get("severity", "alert"),
                "routes": "Custom",
                "stop": "Message"
            })

    # ========== STM BUSES ==========
    # 1) Trip updates
    stm_trip_entities = fetch_stm_realtime_data()
    # 2) Vehicle positions => positions_dict
    positions_dict = fetch_stm_positions_dict(["171","180","164"], stm_trips)
    # 3) Merge into final buses
    buses = process_stm_trip_updates(
        stm_trip_entities,
        stm_trips,
        stm_stop_times,
        positions_dict
    )

    print("----- DEBUG: Final Merged STM Buses -----")
    status_map = {0: "INCOMING_AT", 1: "STOPPED_AT", 2: "IN_TRANSIT_TO"}

    for b in buses:
        # If b["current_status"] is numeric, map it; otherwise just show whatever string is there
        raw_stat = b.get("current_status")
        if isinstance(raw_stat, int):
            stat_str = status_map.get(raw_stat, f"Unknown({raw_stat})")
        else:
            # If it's a string like "2" or "STOPPED_AT" already, just pass it along
            stat_str = str(raw_stat)

        print(
            f"Route={b['route_id']}, Trip={b['trip_id']}, "
            f"Stop={b['stop_id']}, ArrTime={b['arrival_time']}, "
            f"Occupancy={b['occupancy']}, AtStop={b['at_stop']}, "
            f"Lat={b.get('lat')}, Lon={b.get('lon')}, Dist={b.get('distance_m')}m, "
            f"currentStatus={stat_str}"
        )
    print("-----------------------------------------")


    # ========== EXO TRAINS ==========
    exo_trip_updates, exo_vehicle_positions = fetch_exo_realtime_data()
    exo_vehicle_data = process_exo_vehicle_positions(exo_vehicle_positions, exo_stop_times)
    exo_trains = process_exo_train_schedule_with_occupancy(
        exo_stop_times,
        exo_trips,
        exo_vehicle_data,
        exo_trip_updates
    )

    # ========== NO-SERVICE DAYS? ==========
    if is_service_unavailable():
        for train in exo_trains:
            train["no_service_text"] = "Aucun service aujourd'hui"
            train["arrival_time"] = "N/A"
            train["delayed_text"] = None
            train["early_text"] = None

    return {
        "buses": buses,
        "next_trains": exo_trains,
        "current_time": time.strftime("%I:%M:%S %p"),
        "alerts": all_alerts
    }

if __name__ == "__main__":
    app.run(debug=True)
