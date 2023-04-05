import requests
import json
from geopy import distance, Point
from geopy.geocoders import Nominatim
from gpiozero import PWMOutputDevice
from time import sleep

# Define your Bing Maps API key
api_key = "AotC3UEmdrbiepfsoX3VlEe4dsIuRcjomR7tYL63Q0iRxx6a3SafACafGgkdgYTZ"

# Define the source and destination addresses
[latitude, longitude] = ["19.1338", "72.917"] #get_pos()
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

# Define the GPIO pin connected to the vibration motor
motor_pin = 17

# Create a PWMOutputDevice object for the vibration motor
motor = PWMOutputDevice(motor_pin)

# Define the haptic feedback levels for different maneuver types
feedback_levels = {
    'DepartStart': 1.0,  # Strong vibration for departure
    'TurnLeft': 0.5,  # Medium vibration for left turn
    'TurnRight': 0.5,  # Medium vibration for right turn
    'GoStraight': 0.2,  # Weak vibration for straight path
    'ArriveFinish': 1.0,  # Strong vibration for arrival
}

# Loop through the itinerary items and extract the left-right directions and maneuver points
maneuver_points = []
for item in items:
    location = item['maneuverPoint']['coordinates']
    maneuver_points.append(Point(location[1], location[0]))

# Define the minimum distance threshold for triggering haptic feedback
min_distance = 10.0  # in meters

# Initialize the current maneuver index to 0
current_maneuver_index = 0

print(maneuver_points)

# Loop continuously to check the user's location and trigger haptic feedback
while True:
    # Get the user's current location
    [user_latitude, user_longitude] = ["19.1338", "72.917"] #get_pos()

    # Calculate the distance between the user's location and the current maneuver
    current_maneuver = maneuver_points[current_maneuver_index]
    distance_to_maneuver = distance.distance((user_latitude, user_longitude), current_maneuver).meters

    # If the user is close enough to the current maneuver, trigger haptic feedback and move to the next maneuver
    if distance_to_maneuver < min_distance or True:
        # Get the current maneuver information
        item = items[current_maneuver_index]
        instruction = item['instruction']['text']
        maneuver_type = item['details'][0]['maneuverType']

        # Determine the appropriate haptic feedback based on the maneuver type
        feedback_level = feedback_levels.get(maneuver_type, 0.2)

        # Set the vibration motor to the appropriate feedback level for a duration of 1 second
        motor.value = feedback_level
        sleep(1)
        motor.value = 0

        # Print the instruction text
        print(instruction)

    # Check if the user has reached the final destination
    if current_maneuver_index >= len(maneuver_points):
        break

    # Check if the right arrow key is pressed
    tmp = input('next point?')
    if tmp == 'n':
        # Move to the next maneuver
        current_maneuver_index += 1


# Clean up the GPIO pins
motor.close()
