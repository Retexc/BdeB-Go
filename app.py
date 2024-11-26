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
    headers = {"apikey": STM_API_KEY}
    response = requests.get(STM_REALTIME_ENDPOINT, headers=headers)
    if response.status_code == 200:
        # Parse Protobuf data
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        buses = []
        for entity in feed.entity:
            if entity.HasField("trip_update"):
                trip = entity.trip_update.trip
                stop_time_updates = entity.trip_update.stop_time_update
                route_id = trip.route_id
                if route_id in DESIRED_ROUTES and stop_time_updates:
                    buses.append({
                        "route_id": route_id,
                        "direction": "Ouest",  # Static for now, update with real data if needed
                        "stop_name": "Henri-Bourassa / du Bois-de-Boulogne",  # Static, update dynamically if possible
                        "arrival_time": int(stop_time_updates[0].departure.time)
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
    # Limit to only the first 3 items
    buses = buses[:3]
    current_time = time.strftime('%H:%M')  # Format current time as HH:MM
    return render_template("index.html", buses=buses, current_time=current_time)


if __name__ == "__main__":
    app.run(debug=True)
