import requests
import json
from geopy import distance, Point
from geopy.geocoders import Nominatim
from gps import get_pos

# Define your Bing Maps API key
api_key = "AotC3UEmdrbiepfsoX3VlEe4dsIuRcjomR7tYL63Q0iRxx6a3SafACafGgkdgYTZ"

# Define the source and destination addresses
[latitude, longitude] = get_pos()
destination = "CSMT"

# Use geopy to get the latitude and longitude of the source and destination
geolocator = Nominatim(user_agent="NaviCane")
destination_location = geolocator.geocode(destination)

# Define the Bing Maps API endpoint
url = f"https://dev.virtualearth.net/REST/V1/Routes/Walking?o=json&wp.0={latitude},{longitude}&wp.1={destination_location.latitude},{destination_location.longitude}&key={api_key}"

# Send a GET request to the Bing Maps API endpoint to get the route data
response = requests.get(url)

# Parse the response JSON and extract the route data
data = response.json()
items = data["resourceSets"][0]["resources"][0]['routeLegs'][0]['itineraryItems']

# Initialize the current maneuver point index
current_maneuver_index = 0

# Get the current location and the next maneuver point
current_location = Point(get_pos()[0], get_pos()[1])
next_maneuver_point = maneuver_points[current_maneuver_index]

# Loop through the itinerary items and extract the maneuver points
maneuver_points = []
for item in items:
    location = item['maneuverPoint']['coordinates']
    maneuver_points.append(Point(location[1], location[0]))

# Loop forever, checking the current location and sending haptic feedback
while True:
    # Get the current position
    [latitude, longitude] = get_pos()
    current_point = Point(latitude, longitude)

    # Find the closest maneuver point to the current position
    closest_point, closest_distance = distance.distance(current_point, maneuver_points).closest()

    # If the closest maneuver point is within 10 meters of the current position, send haptic feedback
    if closest_distance < 10:
        index = maneuver_points.index(closest_point)
        if index < len(maneuver_points) - 1:
            next_point = maneuver_points[index + 1]
            bearing = distance.distance(closest_point, next_point).bearing
            relative_bearing = bearing - heading
            if relative_bearing > 180:
                relative_bearing -= 360
            elif relative_bearing < -180:
                relative_bearing += 360
            if relative_bearing > 20:
                feedback = 'Turn left'
            elif relative_bearing < -20:
                feedback = 'Turn right'
            else:
                feedback = 'Go straight'
        else:
            feedback = 'Arrive at your destination'
        print(feedback)

    # Wait for 1 second before checking again
    time.sleep(1)
