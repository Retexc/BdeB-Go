# app.py
import os, sys, time, json, logging, subprocess, threading, re, requests
from datetime import datetime
from flask_cors import CORS
from flask import Flask, render_template, request, jsonify, redirect

from flask import Flask, render_template, request, jsonify
# ────── PACKAGE IMPORTS ───────────────────────────────────────
from .config            import WEATHER_API_KEY
from .utils             import is_service_unavailable

from .loaders.stm       import (
    fetch_stm_alerts,
    fetch_stm_realtime_data,
    fetch_stm_positions_dict,
    load_stm_gtfs_trips,
    load_stm_stop_times,
    load_stm_routes,
    process_stm_trip_updates,
    stm_map_occupancy_status,
    debug_print_stm_occupancy_status,
    validate_trip,
)

from .loaders.exo       import (
    fetch_exo_alerts,
    fetch_exo_realtime_data,
    load_exo_gtfs_trips,
    load_exo_stop_times,
    process_exo_vehicle_positions,
    process_exo_train_schedule_with_occupancy,
)

from .alerts            import process_stm_alerts, process_exo_alerts

# ────────────────────────────────────────────────────────────────

print("__name__:", __name__)
print("__package__:", __package__)
print("sys.path:", sys.path)

_weather_cache = {
    "ts":   0,     # last fetch timestamp
    "data": None,  # cached weather dict
}

CACHE_TTL = 5 * 60  # seconds (5 minutes)
logger = logging.getLogger('BdeB-GTFS')
app = Flask(__name__)
CORS(app)
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
GTFS_BASE = os.path.join(PACKAGE_DIR, "GTFS")  # points to backend/GTFS
STM_DIR = os.path.join(GTFS_BASE, "stm")
EXO_TRAIN_DIR = os.path.join(GTFS_BASE, "exo")

os.makedirs(STM_DIR,       exist_ok=True)
os.makedirs(EXO_TRAIN_DIR, exist_ok=True)

# ─── check for required GTFS files ────────────────────────────
required_stm = ["routes.txt", "trips.txt", "stop_times.txt"]
required_exo = ["trips.txt",   "stop_times.txt"]

missing = []
for fname in required_stm:
    if not os.path.isfile(os.path.join(STM_DIR, fname)):
        missing.append(f"stm/{fname}")
for fname in required_exo:
    if not os.path.isfile(os.path.join(EXO_TRAIN_DIR, fname)):
        missing.append(f"exo/{fname}")

if missing:
    print("Fichiers GTFS manquants:")
    for m in missing:
        print(f"   • {m}")
    print("\nS'il-vous-plaît, téléchargez les fichiers manquants dans le menu paramètres et relancez l'application.")
    sys.exit(1)
# ────────────────────────────────────────────────────────────────

# ====================================================================
# Load static GTFS data once at startup
# ====================================================================
stm_routes_fp      = os.path.join(STM_DIR,       "routes.txt")
stm_trips_fp       = os.path.join(STM_DIR,       "trips.txt")
stm_stop_times_fp  = os.path.join(STM_DIR,       "stop_times.txt")
exo_trips_fp       = os.path.join(EXO_TRAIN_DIR, "trips.txt")
exo_stop_times_fp  = os.path.join(EXO_TRAIN_DIR, "stop_times.txt")

routes_map      = load_stm_routes(stm_routes_fp)
stm_trips       = load_stm_gtfs_trips(stm_trips_fp,      routes_map)
stm_stop_times  = load_stm_stop_times(stm_stop_times_fp)
exo_trips       = load_exo_gtfs_trips(exo_trips_fp)
exo_stop_times  = load_exo_stop_times(exo_stop_times_fp)

def get_weather():
    """Fetch weather from WeatherAPI at most once per CACHE_TTL."""
    now = time.time()
    # if cache is stale, refresh it
    if now - _weather_cache["ts"] > CACHE_TTL:
        try:
            resp = requests.get(
                f"http://api.weatherapi.com/v1/current.json"
                f"?key={WEATHER_API_KEY}"
                "&q=Montreal,QC"
                "&aqi=no"
                "&lang=fr",
                timeout=5
            ).json()
            _weather_cache["data"] = {
                "icon": "https:" + resp["current"]["condition"]["icon"],
                "text":  resp["current"]["condition"]["text"],
                "temp":  int(round(resp["current"]["temp_c"])),
            }
        except Exception:
            # leave last good data or None
            pass
        _weather_cache["ts"] = now

    return _weather_cache["data"] or {"icon":"", "text":"", "temp":""}

# ====================================================================
# Metro Alerts Processing Functions
# ====================================================================
def process_metro_alerts():
    """
    Fetch and process metro line alerts from STM API.
    Returns a list of metro lines with their current status.
    """
    try:
        alerts_data = fetch_stm_alerts()
        if not alerts_data:
            logger.warning("No metro alerts data received")
            return get_default_metro_status()
        
        # Handle case where alerts_data might be a string (JSON string)
        if isinstance(alerts_data, str):
            try:
                alerts_data = json.loads(alerts_data)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse alerts_data as JSON: {e}")
                return get_default_metro_status()
        
        # Handle different response formats from STM API
        alerts_list = []
        if isinstance(alerts_data, dict):
            # If it's a dict, look for common keys that contain the alerts list
            if 'alerts' in alerts_data:
                alerts_list = alerts_data['alerts']
            elif 'entity' in alerts_data:
                alerts_list = alerts_data['entity']
            elif 'data' in alerts_data:
                alerts_list = alerts_data['data']
            else:
                # If none of the common keys exist, treat the dict as a single alert
                alerts_list = [alerts_data]
        elif isinstance(alerts_data, list):
            alerts_list = alerts_data
        else:
            logger.error(f"Unexpected alerts_data type: {type(alerts_data)}")
            return get_default_metro_status()
        
        logger.info(f"Processing {len(alerts_list)} alerts for metro status")
        
        # Initialize metro lines with default normal status
        metro_status = {
            "1": {
                "name": "Ligne 1",
                "color": "Verte", 
                "status": "Service normal du métro",
                "statusColor": "text-green-400",
                "icon": "green-line",
                "is_normal": True
            },
            "2": {
                "name": "Ligne 2",
                "color": "Orange",
                "status": "Service normal du métro", 
                "statusColor": "text-green-400",
                "icon": "orange-line",
                "is_normal": True
            },
            "4": {
                "name": "Ligne 4", 
                "color": "Jaune",
                "status": "Service normal du métro",
                "statusColor": "text-green-400", 
                "icon": "yellow-line",
                "is_normal": True
            },
            "5": {
                "name": "Ligne 5",
                "color": "Bleue", 
                "status": "Service normal du métro",
                "statusColor": "text-green-400",
                "icon": "blue-line", 
                "is_normal": True
            }
        }
        
        # Process alerts from API
        for alert in alerts_list:
            try:
                # Ensure alert is a dictionary
                if not isinstance(alert, dict):
                    logger.warning(f"Expected alert to be a dict, got {type(alert)}: {alert}")
                    continue
                
                # Check if alert has informed_entities for metro lines
                informed_entities = alert.get("informed_entities", [])
                if not isinstance(informed_entities, list):
                    continue
                    
                for entity in informed_entities:
                    if not isinstance(entity, dict):
                        continue
                        
                    route_short_name = entity.get("route_short_name")
                    
                    # Only process metro lines (1, 2, 4, 5)
                    if route_short_name in ["1", "2", "4", "5"]:
                        # Get French description text
                        description_texts = alert.get("description_texts", [])
                        if not isinstance(description_texts, list):
                            continue
                            
                        french_description = None
                        
                        for desc in description_texts:
                            if isinstance(desc, dict) and desc.get("language") == "fr":
                                french_description = desc.get("text", "")
                                break
                        
                        if french_description:
                            # Check if it's a normal service message
                            is_normal_service = "service normal" in french_description.lower()
                            
                            metro_status[route_short_name]["status"] = french_description
                            metro_status[route_short_name]["is_normal"] = is_normal_service
                            metro_status[route_short_name]["statusColor"] = "text-green-400" if is_normal_service else "text-red-400"
                            
                            logger.info(f"Updated metro line {route_short_name}: {french_description[:50]}...")
                            
            except Exception as e:
                logger.error(f"Error processing individual metro alert: {e}")
                logger.error(f"Alert data: {alert}")
                continue
        
        # Convert to list format expected by frontend
        metro_lines = []
        for line_id, line_data in metro_status.items():
            metro_lines.append({
                "id": int(line_id),
                "name": line_data["name"],
                "color": line_data["color"],
                "status": line_data["status"],
                "statusColor": line_data["statusColor"],
                "icon": line_data["icon"],
                "is_normal": line_data["is_normal"]
            })
        
        # Sort by line ID to maintain consistent order
        metro_lines.sort(key=lambda x: x["id"])
        
        logger.info(f"Processed {len(metro_lines)} metro lines with alerts")
        return metro_lines
        
    except Exception as e:
        logger.error(f"Error in process_metro_alerts: {e}")
        logger.error(f"alerts_data type: {type(alerts_data) if 'alerts_data' in locals() else 'undefined'}")
        return get_default_metro_status()

def get_default_metro_status():
    """
    Returns default metro status when API is unavailable.
    """
    return [
        {
            "id": 1,
            "name": "Ligne 1",
            "color": "Verte",
            "status": "Données non disponibles pour le moment",
            "statusColor": "text-green-400",
            "icon": "green-line",
            "is_normal": True
        },
        {
            "id": 2,
            "name": "Ligne 2", 
            "color": "Orange",
            "status": "Données non disponibles pour le moment",
            "statusColor": "text-green-400",
            "icon": "orange-line",
            "is_normal": True
        },
        {
            "id": 4,
            "name": "Ligne 4",
            "color": "Jaune", 
            "status": "Données non disponibles pour le moment",
            "statusColor": "text-green-400",
            "icon": "yellow-line",
            "is_normal": True
        },
        {
            "id": 5,
            "name": "Ligne 5",
            "color": "Bleue",
            "status": "Données non disponibles pour le moment", 
            "statusColor": "text-green-400",
            "icon": "blue-line",
            "is_normal": True
        }
    ]

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
    alert description contains "annulé","déplacé" or "relocalisé", append a styled HTML badge
    next to the bus's location.
    """
    for bus in buses:
        route_id = bus.get("route_id", "").strip()
        bus_location = bus.get("location", "").strip()
        for alert in stm_alerts:
            if route_id in alert.get("routes", ""):
                if bus_location in alert.get("stop", ""):
                    desc = alert.get("description", "").lower()
                    if "déplacé" in desc:
                        bus["location"] = f"{bus_location} <span class='alert-badge alert-deplace'>Arrêt déplacé</span>"
                        break
                    elif "relocalisé" in desc:
                        bus["location"] = f"{bus_location} <span class='alert-badge alert-relocalise'>Arrêt relocalisé</span>"
                        break
                    elif "annulé" in desc:
                        bus["location"] = f"{bus_location} <span class='alert-badge alert-annule'>Arrêt annulé</span>"
                        bus["canceled"] = True 
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
    # Redirect to your Vue.js app instead of rendering old template
    return redirect("http://localhost:3000") 

# ====================================================================
# ROUTE: API JSON Data for buses, trains, metro, and alerts
# ====================================================================
@app.route("/api/data")
def api_data():
    # ========== ALERTS ==========
    stm_alert_json = fetch_stm_alerts()
    processed_stm = process_stm_alerts(stm_alert_json, WEATHER_API_KEY) if stm_alert_json else []

    exo_alert_entities = fetch_exo_alerts()
    print(f"DEBUG: EXO alerts returned: {len(exo_alert_entities) if exo_alert_entities else 0} entities")
    processed_exo = process_exo_alerts(exo_alert_entities)
    print(f"DEBUG: Processed EXO alerts: {len(processed_exo)} alerts")
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

    # ========== METRO LINES ==========
    metro_lines = process_metro_alerts()

    weather = get_weather()

    return {
        "buses":       buses,
        "next_trains": exo_trains,
        "metro_lines": metro_lines,  # Add metro lines to the response
        "current_time": time.strftime("%I:%M:%S %p"),
        "alerts":      filtered_alerts,
        "weather":     weather        
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