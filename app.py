# app.py

from flask import Flask, render_template
import time

# Local imports
from config import WEATHER_API_KEY
from utils import is_service_unavailable
from stm import (
    fetch_stm_alerts,
    fetch_stm_realtime_data,
    fetch_stm_vehicle_positions,
    load_stm_gtfs_trips,
    load_stm_stop_times,
    process_stm_trip_updates,       # We’ll slightly adjust the signature
    stm_map_occupancy_status        # If you need it for any occupancy merging
)
from exo import (
    fetch_exo_alerts,
    fetch_exo_realtime_data,
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
# Adjust paths if your GTFS files live elsewhere
# ====================================================================
stm_trips = load_stm_gtfs_trips("STM/trips.txt")
stm_stop_times = load_stm_stop_times("STM/stop_times.txt")
# If you have Exo’s trip definitions in exo.py, you’d do something like
# exo_trips = load_exo_trips("Exo/Train/trips.txt") 
# but from your code, it looks like that’s actually inside stm.py. So:
exo_trips = load_stm_gtfs_trips("Exo/Train/trips.txt")  # reusing that function
exo_stop_times = load_exo_stop_times("Exo/Train/stop_times.txt")


# ====================================================================
# ROUTE: Home Page
# ====================================================================
@app.route("/")
def index():
    # Fetch & process EXO real-time
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
    # 1) Fetch raw STM alerts -> process them (including weather)
    stm_alert_json = fetch_stm_alerts()
    processed_stm = process_stm_alerts(stm_alert_json, WEATHER_API_KEY) if stm_alert_json else []

    # 2) Fetch raw EXO alerts -> process them
    exo_alert_entities = fetch_exo_alerts()
    processed_exo = process_exo_alerts(exo_alert_entities)

    # Combine them
    all_alerts = processed_stm + processed_exo

    # ========== STM BUSES ==========
    stm_trip_entities = fetch_stm_realtime_data()
    stm_vehicle_entities = fetch_stm_vehicle_positions()

    # IMPORTANT FIX:
    # Pass `stm_stop_times` to process_stm_trip_updates, or else it can’t look up arrivals.
    buses = process_stm_trip_updates(stm_trip_entities, stm_trips, stm_stop_times)

    # If you want to merge occupancy from 'stm_vehicle_entities' into each bus item:
    # you could do something like:
    vehicle_data = []
    for entity in stm_vehicle_entities:
        if entity.HasField("vehicle"):
            v = entity.vehicle
            occupancy_status = v.occupancy_status if v.HasField("occupancy_status") else "UNKNOWN"
            vehicle_data.append({
                "trip_id": v.trip.trip_id,
                "occupancy": stm_map_occupancy_status(occupancy_status)
            })
    # Then merge occupant data:
    for bus in buses:
        for vd in vehicle_data:
            if bus["trip_id"] == vd["trip_id"]:
                bus["occupancy"] = vd["occupancy"]
                break

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
