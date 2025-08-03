# STM API Credentials
STM_API_KEY = "l71d29e015f26e423ea8fe728229d220bc"
STM_REALTIME_ENDPOINT = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates"
STM_VEHICLE_POSITIONS_ENDPOINT = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/vehiclePositions"
STM_ALERTS_ENDPOINT = "https://api.stm.info/pub/od/i3/v2/messages/etatservice"

# Exo API
EXO_TOKEN = "JX0ZCLTPDE"
EXO_BASE_URL = "https://opendata.exo.quebec/ServiceGTFSR"
EXO_TRIP_UPDATE_URL = f"{EXO_BASE_URL}/TripUpdate.pb?token={EXO_TOKEN}"
EXO_VEHICLE_POSITION_URL = f"{EXO_BASE_URL}/VehiclePosition.pb?token={EXO_TOKEN}"
EXO_ALERTS_URL = f"{EXO_BASE_URL}/Alert.pb?token={EXO_TOKEN}"

# Weather API key
WEATHER_API_KEY = "8c3e9fd5e6a445feb48114525251702"

# Global delay configuration
GLOBAL_DELAY_MINUTES = 0