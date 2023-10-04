import requests
import json
from geopy import distance, Point
from geopy.geocoders import Nominatim

# Define your Bing Maps API key
api_key = "AotC3UEmdrbiepfsoX3VlEe4dsIuRcjomR7tYL63Q0iRxx6a3SafACafGgkdgYTZ"

# Define the source and destination addresses
source = "IIT Bombay"
destination = "Powai"

# Use geopy to get the latitude and longitude of the source and destination
geolocator = Nominatim(user_agent="my-application")
source_location = geolocator.geocode(source)
destination_location = geolocator.geocode(destination)

# Define the Bing Maps API endpoint
url = f"https://dev.virtualearth.net/REST/V1/Routes/Walking?o=json&wp.0={source_location.latitude},{source_location.longitude}&wp.1={destination_location.latitude},{destination_location.longitude}&key={api_key}"

# Send a GET request to the Bing Maps API endpoint to get the route data
response = requests.get(url)

# Parse the response JSON and extract the route data
data = response.json()
items = data["resourceSets"][0]["resources"][0]['routeLegs'][0]['itineraryItems']

# Loop through the itinerary items and extract the left-right directions and maneuver points
maneuver_points = []
for item in items:
    instruction = item['instruction']['text']
    maneuver_type = item['details'][0]['maneuverType']
    location = item['maneuverPoint']['coordinates']

    # Determine the appropriate haptic feedback based on the maneuver type
    if maneuver_type == 'DepartStart':
        feedback = instruction
    elif maneuver_type == 'TurnLeft':
        feedback = instruction
    elif maneuver_type == 'TurnRight':
        feedback = instruction
    elif maneuver_type == 'GoStraight':
        feedback = instruction
    elif maneuver_type == 'ArriveFinish':
        feedback = 'Arrive at your destination'
        
    # Add the maneuver point to the list
    maneuver_points.append(Point(location[1], location[0]))

    # Send the haptic feedback to the vibration motors
    print(feedback)

# Get the closest walking distance-enabled locations to the source and destination
source_location = min(geolocator.reverse((source_location.latitude, source_location.longitude), exactly_one=True, timeout=10), key=lambda x: distance.distance(Point(x.latitude, x.longitude), Point(source_location.latitude, source_location.longitude)).km)
destination_location = min(geolocator.reverse((destination_location.latitude, destination_location.longitude), exactly_one=True, timeout=10), key=lambda x: distance.distance(Point(x.latitude, x.longitude), Point(destination_location.latitude, destination_location.longitude)).km)

# Create a dictionary with the route data and maneuver points
route_data = {
    'source': source_location.address,
    'destination': destination_location.address,
    'maneuver_points': [str(point) for point in maneuver_points]
}

# Save the route data as a JSON file
with open("route_data.json", "w") as outfile:
    json.dump(route_data, outfile)
