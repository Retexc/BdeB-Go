import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# STM API Credentials
STM_API_KEY = os.getenv("STM_API_KEY")
STM_REALTIME_ENDPOINT = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates"
STM_VEHICLE_POSITIONS_ENDPOINT = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/vehiclePositions"
STM_ALERTS_ENDPOINT = "https://api.stm.info/pub/od/i3/v2/messages/etatservice"

# NEW Chrono API (replacing old Exo API)
CHRONO_TOKEN = os.getenv("CHRONO_TOKEN")
CHRONO_BASE_URL = "https://exo.chrono-saeiv.com/api/opendata/v1"

# Chrono GTFS-RT endpoints 
CHRONO_TRIP_UPDATE_URL = f"{CHRONO_BASE_URL}/exo/tripupdate?token={CHRONO_TOKEN}"
CHRONO_VEHICLE_POSITION_URL = f"{CHRONO_BASE_URL}/exo/vehicleposition?token={CHRONO_TOKEN}"
CHRONO_ALERTS_URL = f"{CHRONO_BASE_URL}/exo/alert?token={CHRONO_TOKEN}"

# Weather API key
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Global delay configuration
GLOBAL_DELAY_MINUTES = int(os.getenv("GLOBAL_DELAY_MINUTES", "0"))

if not STM_API_KEY:
    raise ValueError("STM_API_KEY not found in environment variables")
if not CHRONO_TOKEN:
    raise ValueError("CHRONO_TOKEN not found in environment variables")
if not WEATHER_API_KEY:
    raise ValueError("WEATHER_API_KEY not found in environment variables")