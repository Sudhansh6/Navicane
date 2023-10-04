import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

# Set up GPIO pins
MOTOR_PIN = 12  # GPIO pin for vibrating motor
GPIO.setmode(GPIO.BOARD)
GPIO.setup(MOTOR_PIN, GPIO.OUT)

# Helper function to alert user with motor
def alert_user():
    GPIO.output(MOTOR_PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(MOTOR_PIN, GPIO.LOW)

# Load YOLO object detection model
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# Initialize video capture from camera
cap = cv2.VideoCapture(0)

while True:
    # Capture frame from camera
    ret, frame = cap.read()
    
    # Get image dimensions and prepare input blob for YOLO
    height, width, channels = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    # Pass input blob through YOLO network
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Parse YOLO output and detect objects
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5 and class_id in [2, 3, 5, 7]:
                # Object is a vehicle, animal, or truck
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])
    
    # Check for approaching objects
    if len(boxes) > 0:
        print("Approaching object detected!")
        alert_user()
    
    # Draw bounding boxes around detected objects
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    font = cv2.FONT_HERSHEY_SIMPLEX
    colors = np.random.uniform(0, 255, size=(len(boxes), 3))
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = classes[class_ids[i]]
            color = colors[i]
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label
