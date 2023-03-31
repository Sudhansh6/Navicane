import RPi.GPIO as GPIO
import time

# Set GPIO mode and pin numbers
GPIO.setmode(GPIO.BCM)
trigger_pin = 18
echo_pin = 19
motor_pin = 12

# Set up GPIO pins
GPIO.setup(trigger_pin, GPIO.OUT)
GPIO.setup(echo_pin, GPIO.IN)
GPIO.setup(motor_pin, GPIO.OUT)

# Function to measure distance using ultrasonic sensor
def measure_distance():
    # Send 10us pulse to trigger pin
    GPIO.output(trigger_pin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trigger_pin, GPIO.LOW)
    
    # Wait for echo to go high and then low
    pulse_start = time.time()
    while GPIO.input(echo_pin) == 0:
        pulse_start = time.time()
    pulse_end = time.time()
    while GPIO.input(echo_pin) == 1:
        pulse_end = time.time()
    
    # Calculate distance in cm
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    
    return distance

# Main loop to detect overhead obstacles and alert user
def obstacle_detection():
    while True:
        distance = measure_distance()
        if distance <= 30:
            # If distance is less than or equal to 30cm, obstacle is detected
            GPIO.output(motor_pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(motor_pin, GPIO.LOW)
            time.sleep(0.5)
        else:
            # If distance is greater than 30cm, no obstacle is detected
            GPIO.output(motor_pin, GPIO.LOW)
            time.sleep(0.5)

if __name__ == "__main__":
    try:
        obstacle_detection()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Program object stopped by user. GPIO cleanup completed.")