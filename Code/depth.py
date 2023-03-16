import RPi.GPIO as GPIO
import time

# Set up GPIO pins
TRIG = 16  # GPIO pin for ultrasonic sensor trigger
ECHO = 18  # GPIO pin for ultrasonic sensor echo
MOTOR_PIN = 12  # GPIO pin for vibrating motor

GPIO.setmode(GPIO.BOARD)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(MOTOR_PIN, GPIO.OUT)

# Initialize variables
window_size = 5  # Moving average window size
distances = [0] * window_size  # Circular buffer for distances
index = 0  # Index of the current distance in the circular buffer

# Helper function to compute moving average
def moving_average(distances):
    return sum(distances) / len(distances)

# Helper function to alert user with motor
def alert_user():
    GPIO.output(MOTOR_PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(MOTOR_PIN, GPIO.LOW)

# Wait for sensor to settle
GPIO.output(TRIG, False)
print("Waiting for sensor to settle...")
time.sleep(2)

try:
    while True:
        # Trigger ultrasonic sensor
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        
        # Measure pulse duration
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
        
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
        
        pulse_duration = pulse_end - pulse_start
        
        # Convert pulse duration to distance
        distance = pulse_duration * 17150
        
        # Update circular buffer
        distances[index] = distance
        index = (index + 1) % window_size
        
        # Compute moving average of distances
        moving_avg = moving_average(distances)
        
        # Check for sudden change in depth
        if abs(distance - moving_avg) > 10:
            print("Sudden change detected!")
            alert_user()
        
        # Print distance
        print("Distance:", round(distance, 2), "cm")
        
        # Wait before next measurement
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopped")
    GPIO.cleanup()

"""
    In this code, we use a circular buffer to store the last window_size distance measurements and compute the moving average of those measurements. We then check for a sudden change in depth by comparing the current distance to the moving average, and if the difference is greater than a threshold (in this case, 10 cm), we alert the user with the vibrating motor. The alert_user function simply turns on the motor for half a second before turning it off again.

Note that this is just an example code and you may need to adjust the moving average window size and threshold to fit your specific requirements. Also, make sure to properly connect and configure the vibrating motor to the GPIO pin before running the code.
"""