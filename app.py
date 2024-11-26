from flask import Flask, render_template
import requests
import time
import gtfs_realtime_pb2  # Import the generated GTFS-Realtime Protobuf module

app = Flask(__name__)

# STM API credentials
STM_API_KEY = "l719ebd45028394df8a685460891da2772"
STM_REALTIME_ENDPOINT = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates"

# List of desired bus routes
DESIRED_ROUTES = ["171", "164", "180"]

def get_bus_data():
    headers = {
        "apiKey": STM_API_KEY,
        "accept": "application/x-protobuf"
    }
    response = requests.get(STM_REALTIME_ENDPOINT, headers=headers)

    if response.status_code == 200:
        # Parse the Protobuf response
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        buses = []
        for entity in feed.entity:
            if entity.HasField("trip_update"):
                trip_update = entity.trip_update
                route_id = trip_update.trip.route_id
                if route_id not in DESIRED_ROUTES:
                    continue  # Skip routes not in the desired list

                for stop_time_update in trip_update.stop_time_update:
                    stop_id = stop_time_update.stop_id
                    arrival_time = stop_time_update.arrival.time

                    buses.append({
                        "route_id": route_id,
                        "direction": "Ouest",  # Placeholder for direction
                        "stop_name": stop_id,  # Replace this with a stop name mapping if available
                        "arrival_time": arrival_time
                    })
        return buses
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

@app.template_filter('time_difference')
def time_difference_filter(epoch_time):
    current_time = int(time.time())
    difference = epoch_time - current_time
    return max(difference // 60, 0)  # Convert seconds to minutes

@app.route("/")
def index():
    buses = get_bus_data()
    current_time = time.strftime('%H:%M')  # Format current time as HH:MM
    return render_template("index.html", buses=buses, current_time=current_time)

if __name__ == "__main__":
    app.run(debug=True)
