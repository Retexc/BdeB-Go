# app.py

from flask import Flask, render_template, request, jsonify
import time
import sys
import os, json
from datetime import datetime
import re
import logging
import subprocess
import threading
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import WEATHER_API_KEY
from utils import is_service_unavailable
from stm import (
    fetch_stm_alerts,
    fetch_stm_realtime_data,
    fetch_stm_positions_dict,      
    load_stm_gtfs_trips,
    load_stm_stop_times,
    load_stm_routes,
    process_stm_trip_updates,       
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BdeB-GTFS')
app = Flask(__name__)
# ====================================================================
# Load static GTFS data once at startup
# ====================================================================
routes_map = load_stm_routes("STM/routes.txt")
stm_trips = load_stm_gtfs_trips("STM/trips.txt", routes_map)
stm_stop_times = load_stm_stop_times("STM/stop_times.txt")
exo_trips = load_exo_gtfs_trips("Exo/Train/trips.txt")
exo_stop_times = load_exo_stop_times("Exo/Train/stop_times.txt")

@app.route("/debug-occupancy")
def debug_occupancy():
    desired = ["171", "164", "180"]
    debug_print_stm_occupancy_status(desired, stm_trips)
    return "Check your console logs for occupancy info!"

# ====================================================================
# Merge STM alerts into bus rows and update location styling
# ====================================================================
def merge_alerts_into_buses(buses, stm_alerts):
    """
    For each bus row, check if there's a matching STM alert that references the same
    route and stop (based on the processed alert's "routes" and "stop" fields). If the
    alert description contains "déplacé" or "relocalisé", append a styled HTML badge
    next to the bus's location.
    """
    for bus in buses:
        route_id = bus.get("route_id", "").strip()
        bus_location = bus.get("location", "").strip()
        for alert in stm_alerts:
            # Check if the bus's route appears in the alert's routes field.
            if route_id in alert.get("routes", ""):
                # Check if the bus's location is part of the alert's stop field.
                if bus_location in alert.get("stop", ""):
                    desc = alert.get("description", "").lower()
                    if "déplacé" in desc:
                        bus["location"] = f"{bus_location} <span class='alert-badge alert-deplace'>Arrêt déplacé</span>"
                        break
                    elif "relocalisé" in desc:
                        bus["location"] = f"{bus_location} <span class='alert-badge alert-relocalise'>Arrêt relocalisé</span>"
                        break
    return buses

# ====================================================================
# Load background image from Background Manager
# ====================================================================        
def get_active_background(css_path):
    """
    Reads the MULTISLOT block from the CSS file and returns the URL (string)
    of the slot whose date range includes today's date.
    Returns None if no slot is active.
    """
    if not os.path.isfile(css_path):
        return None

    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    # Look for a block starting with "/* MULTISLOT:" and ending with "*/"
    pattern_block = re.compile(r"/\*\s*MULTISLOT:\s*(.*?)\*/", re.IGNORECASE | re.DOTALL)
    match = pattern_block.search(css_content)
    if not match:
        return None

    block_text = match.group(1).strip()
    today = datetime.today().date()
    active_bg = None

    # Each line should be like:
    # SLOT1: /static/assets/images/Printemps - Banner Big.png from 2025-03-19 to 2025-06-12
    for line in block_text.splitlines():
        line = line.strip()
        m = re.match(r"SLOT\d+:\s+(.*?)\s+from\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})", line, re.IGNORECASE)
        if m:
            bg_url = m.group(1).strip()
            start_str = m.group(2).strip()
            end_str = m.group(3).strip()
            try:
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
            except ValueError:
                continue
            if start_date <= today <= end_date:
                active_bg = bg_url
                break

    return active_bg      

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
    active_bg = get_active_background("./static/index.css")
    return render_template(
        "index.html",
        next_trains=exo_trains,
        current_time=current_time,
        active_bg=active_bg
    )

# ====================================================================
# ROUTE: API JSON Data for buses, trains, and alerts
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
    # Path to the custom_messages.json file in GTFSManager/public folder
    custom_path = os.path.join(
        os.path.dirname(__file__),
        "GTFSManager",
        "public",
        "custom_messages.json"
    )
    if os.path.exists(custom_path):
        with open(custom_path, "r", encoding="utf-8") as f:
            try:
                custom_alerts = json.load(f)
                if not isinstance(custom_alerts, list):
                    custom_alerts = []
            except:
                custom_alerts = []
        # Append custom messages as they are (including keys such as status and scheduledTime)
        for c in custom_alerts:
            all_alerts.append(c)

    # ========= Filtering Out Pending Alerts =========
    now = datetime.now()
    filtered_alerts = []
    for alert in all_alerts:
        # If alert is pending and has a scheduledTime, check if it should be displayed.
        if alert.get("status") == "pending":
            st = alert.get("scheduledTime")
            if st:
                try:
                    scheduled_dt = datetime.fromisoformat(st)
                    if scheduled_dt > now:
                        continue
                except Exception as e:
                    pass
        filtered_alerts.append(alert)

    # ========== STM BUSES ==========
    stm_trip_entities = fetch_stm_realtime_data()
    positions_dict = fetch_stm_positions_dict(["171", "180", "164"], stm_trips)
    buses = process_stm_trip_updates(
        stm_trip_entities,
        stm_trips,
        stm_stop_times,
        positions_dict
    )

    logger.info("----- DEBUG: Final Merged STM Buses -----")
    status_map = {0: "INCOMING_AT", 1: "STOPPED_AT", 2: "IN_TRANSIT_TO"}
    for b in buses:
        raw_stat = b.get("current_status")
        if isinstance(raw_stat, int):
            stat_str = status_map.get(raw_stat, f"Unknown({raw_stat})")
        else:
            stat_str = str(raw_stat)
        logger.info(
            f"Route={b['route_id']}, Trip={b['trip_id']}, "
            f"Stop={b['stop_id']}, ArrTime={b['arrival_time']}, "
            f"Occupancy={b['occupancy']}, AtStop={b['at_stop']}, "
            f"Lat={b.get('lat')}, Lon={b.get('lon')}, Dist={b.get('distance_m')}m, "
            f"currentStatus={stat_str}"
        )
    logger.info("-----------------------------------------")

    # Merge alerts into bus rows – update bus location with styled alert badges.
    buses = merge_alerts_into_buses(buses, processed_stm)

    # ========== EXO TRAINS ==========
    exo_trip_updates, exo_vehicle_positions = fetch_exo_realtime_data()
    exo_vehicle_data = process_exo_vehicle_positions(exo_vehicle_positions, exo_stop_times)
    exo_trains = process_exo_train_schedule_with_occupancy(
        exo_stop_times,
        exo_trips,
        exo_vehicle_data,
        exo_trip_updates
    )
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
        "alerts": filtered_alerts
    }

# ====================================================================
# NEW: API endpoint to get and update custom messages
# ====================================================================
@app.route("/api/messages", methods=["GET", "POST"])
def api_messages():
    custom_path = os.path.join(
        os.path.dirname(__file__),
        "GTFSManager",
        "public",
        "custom_messages.json"
    )
    if request.method == "GET":
        if os.path.exists(custom_path):
            with open(custom_path, "r", encoding="utf-8") as f:
                messages = json.load(f)
            return jsonify(messages)
        else:
            return jsonify([]), 404
    elif request.method == "POST":
        data = request.get_json()
        try:
            with open(custom_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return jsonify({"status": "success"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
  
@app.route("/api/raw-stm-alerts")
def raw_stm_alerts():
    raw_alerts = fetch_stm_alerts()
    return jsonify(raw_alerts)

@app.route("/admin")
def admin_dashboard():
    return render_template("home.html")


app.config['APP_RUNNING'] = False
main_app_logs = []
app_process = None  # This will hold the subprocess.Popen object

def capture_app_logs(process):
    """Continuously read output from the process and append to main_app_logs."""
    while True:
        line = process.stdout.readline()
        if not line:  # Process terminated and stdout closed.
            break
        main_app_logs.append(line.rstrip())
    app.config['APP_RUNNING'] = False

@app.route('/admin/start', methods=['POST'])
def admin_start():
    global app_process
    if not app.config['APP_RUNNING']:
        try:
            # Spawn the main application as a subprocess.
            cmd = [PYTHON_EXEC, "-u", "app.py"]  
           
            app_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            app.config['APP_RUNNING'] = True
            main_app_logs.append(f"{datetime.now()} - Main app started.")
            # Start a background thread to capture the process logs:
            threading.Thread(target=capture_app_logs, args=(app_process,), daemon=True).start()
            return jsonify({'status': 'started'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'error': str(e)}), 500
    else:
        return jsonify({'status': 'already_running'}), 200

@app.route('/admin/logs_data')
def logs_data():
    return "\n".join(main_app_logs)

from waitress import serve
if __name__ == "__main__":
    serve(app,
          host="127.0.0.1",
          port=5000,
          threads=8)

#serve(app, host="0.0.0.0", port=5000)
