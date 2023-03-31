import RPi.GPIO as GPIO
import multiprocessing
import time
from depth import depth_estimation as depth
from object import object_detection as object
from navigation import navigate

# Define GPIO pins for each button
DEPTH_BUTTON_PIN = 22
OBJECT_BUTTON_PIN = 23
NAVIGATION_BUTTON_PIN = 24

# Define function to run depth estimation code
def depth_estimation():
    while True:
        # Your depth estimation code here
        depth()
        time.sleep(0.1)

# Define function to run object detection code
def object_detection():
    while True:
        # Your object detection code here
        object()
        time.sleep(0.1)

# Define function to run navigation code
def navigation():
    while True:
        # Your navigation code here
        time.sleep(0.1)

# Define function to start and stop each process
def run_process(process, button_pin):
    while True:
        # Wait for button press
        GPIO.wait_for_edge(button_pin, GPIO.RISING)

        # Start process if not already running
        if not process.is_alive():
            process.start()

        # Wait for button release
        GPIO.wait_for_edge(button_pin, GPIO.FALLING)

        # Terminate process if running
        if process.is_alive():
            process.terminate()
            process.join()

# Initialize GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(DEPTH_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(OBJECT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(NAVIGATION_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Create processes for each function
depth_process = multiprocessing.Process(target=depth_estimation)
object_process = multiprocessing.Process(target=object_detection)
navigation_process = multiprocessing.Process(target=navigation)

# Start separate threads for each button and process combination
depth_thread = multiprocessing.Process(target=run_process, args=(depth_process, DEPTH_BUTTON_PIN))
object_thread = multiprocessing.Process(target=run_process, args=(object_process, OBJECT_BUTTON_PIN))
navigation_thread = multiprocessing.Process(target=run_process, args=(navigation_process, NAVIGATION_BUTTON_PIN))

# Start each thread
depth_thread.start()
object_thread.start()
navigation_thread.start()
