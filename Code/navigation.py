import json
import RPi.GPIO as GPIO
import time
from math import radians, sin, cos, sqrt, atan2

# Set up GPIO pins
MOTOR_PIN = 12  # GPIO pin for vibrating motor
GPIO.setmode(GPIO.BOARD)
GPIO.setup(MOTOR_PIN, GPIO.OUT)
# Connect to GPS sensor
gpsd.connect()
EARTH_RADIUS = 6371.0  # Radius of the earth in kilometers
WALKING_SPEED = 1.4  # Average walking speed in meters per second

# Define vibration patterns for each turn
STRAIGHT = [0.5, 0.5]  # Vibrate for 0.5 seconds, pause for 0.5 seconds (straight ahead)
LEFT_TURN = [0.5, 0.1, 0.5, 0.1, 0.5]  # Vibrate for 0.5 seconds, pause for 0.1 seconds, repeat 3 times (left turn)
RIGHT_TURN = [0.5, 0.1, 0.5]  # Vibrate for 0.5 seconds, pause for 0.1 seconds, repeat 1 time (right turn)

# Load map data from file
with open("map_data.json", "r") as f:
    map_data = json.loads(f.read())
    
def get_next_waypoint(current_location, instruction):
    for route in map_data:
        # Check if the current location is on the current route segment
        if current_location in route["overview_polyline"]["points"]:
            index = route["overview_polyline"]["points"].index(current_location)
            
            # Get the index of the next waypoint based on the instruction
            if instruction == "left":
                next_index = index - 1
            elif instruction == "right":
                next_index = index + 1
            else:
                next_index = index + 1
            
            # Return the coordinates of the next waypoint
            return route["overview_polyline"]["points"][next_index]

def get_delay(current_location, instruction):
    # Get the coordinates of the next waypoint based on the instruction
    next_waypoint = get_next_waypoint(current_location, instruction)

    # Calculate the distance between the current location and the next waypoint
    lat1, lon1 = current_location
    lat2, lon2 = next_waypoint
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = EARTH_RADIUS * c * 1000  # Convert to meters

    # Calculate the time it would take to walk to the next waypoint at the average walking speed
    time_to_waypoint = distance / WALKING_SPEED

    # Add some buffer time based on the instruction
    if instruction == "left" or instruction == "right":
        buffer_time = 2  # Add 2 seconds for turns
    else:
        buffer_time = 0.5 

# Define a function to get the next turn instruction for the current location
def get_next_instruction(current_location):
    for route in map_data:
        # Check if the current location is on the current route segment
        if current_location in route["overview_polyline"]["points"]:
            index = route["overview_polyline"]["points"].index(current_location)
            
            # Check if there is a turn in the next segment
            if index + 1 < len(route["overview_polyline"]["points"]):
                next_location = route["overview_polyline"]["points"][index + 1]
                for step in route["legs"][0]["steps"]:
                    if next_location in step["polyline"]["points"]:
                        # Determine the turn direction
                        if step["maneuver"]["type"] == "turn":
                            if step["maneuver"]["modifier"] == "left":
                                return "left"
                            elif step["maneuver"]["modifier"] == "right":
                                return "right"
                        break
            break
            
    # No turn found, continue straight
    return "straight"

while True:
    # Get user's current location from GPS sensor
    current_location = (gpsd.get_current().lat, gpsd.get_current().lon)


    # Get the next turn instruction for the current location
    instruction = get_next_instruction(current_location)

    # Determine delay based on current location and next instruction
    delay = get_delay(current_location, instruction)

    # Vibrate the motor based on the turn instruction and delay
    if instruction == "straight":
        GPIO.output(MOTOR_PIN, GPIO.HIGH)
        time.sleep(STRAIGHT[0])
        GPIO.output(MOTOR_PIN, GPIO.LOW)
        time.sleep(delay)
    elif instruction == "left":
        for i in range(3):
            GPIO.output(MOTOR_PIN, GPIO.HIGH)
            time.sleep(LEFT_TURN[0])
            GPIO.output(MOTOR_PIN, GPIO.LOW)
            time.sleep(LEFT_TURN[1])
            GPIO.output(MOTOR_PIN, GPIO.HIGH)
            time.sleep(LEFT_TURN[2])
            GPIO.output(MOTOR_PIN, GPIO.LOW)
            time.sleep(LEFT_TURN[3])
        time.sleep(delay)
    elif instruction == "right":
        for i in range(1):
            GPIO.output(MOTOR_PIN, GPIO.HIGH)
            time.sleep(RIGHT_TURN[0])
            GPIO.output(MOTOR_PIN, GPIO.LOW)
            time.sleep(RIGHT_TURN[1])
            GPIO.output(MOTOR_PIN, GPIO.HIGH)
            time.sleep(RIGHT_TURN[2])
            GPIO.output(MOTOR_PIN, GPIO.LOW)
            time.sleep(delay)
