import googlemaps
import gpsd
import RPi.GPIO as GPIO
import time
import json

# Set up GPIO pins
MOTOR_PIN = 12  # GPIO pin for vibrating motor
GPIO.setmode(GPIO.BOARD)
GPIO.setup(MOTOR_PIN, GPIO.OUT)

# Set up Google Maps client
gmaps = googlemaps.Client(key="your_api_key_here")

# Define destination locations
destinations = {"Library": "Boston Public Library, MA", "Grocery Store": "Whole Foods Market, MA"}

# Connect to GPS sensor
gpsd.connect()

# Get user's current location from GPS sensor
current_location = (gpsd.get_current().lat, gpsd.get_current().lon)

# Download map data for current location
map_data = gmaps.offline_maps(
    location=current_location,
    zoom=14,
    type="roadmap",
    language="en",
    region="US",
    max_download_size=50000000,
)

# Download map data for each destination
for dest in destinations:
    # Search for nearby places of interest
    places_result = gmaps.places_nearby(location=current_location, radius=5000, keyword=destinations[dest])
    
    # Get details for top result and calculate directions
    if len(places_result["results"]) > 0:
        dest_location = (places_result["results"][0]["geometry"]["location"]["lat"], places_result["results"][0]["geometry"]["location"]["lng"])
        directions_result = gmaps.directions(
            origin=current_location,
            destination=dest_location,
            mode="walking",
            alternatives=True,
        )
        
        # Download map data for directions route
        for route in directions_result:
            map_data = gmaps.offline_maps(
                waypoints=[route["overview_polyline"]["points"]],
                zoom=14,
                type="roadmap",
                language="en",
                region="US",
                max_download_size=50000000,
            )

# Save map data to local storage
with open("map_data.json", "w") as f:
    f.write(json.dumps(map_data))
