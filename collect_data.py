import sys
import os
import time
import csv
import numpy as np
import cv2

# Force Python to see Gazebo libraries
sys.path.append('/usr/lib/python3/dist-packages')

from gz.transport13 import Node
from gz.msgs10.image_pb2 import Image
from gz.msgs10.twist_pb2 import Twist

# ==========================================
# CONFIGURATION
# ==========================================
PROJECT_ROOT = "/mnt/d/Projects/gazebo-indoor-gen"
DATASET_NAME = "drone_dataset"
CURRENT_ENV  = "warehouse" 

SAVE_DIR = os.path.join(PROJECT_ROOT, DATASET_NAME, CURRENT_ENV)
IMAGE_DIR = os.path.join(SAVE_DIR, "images")
CSV_FILE  = os.path.join(SAVE_DIR, "commands.csv")

class DataCollector:
    def __init__(self):
        self.setup_directories()
        self.node = Node()
        self.last_image = None
        self.last_image_time = 0
        
        # Matches the 'gz topic -l' output you shared
        cam_topic = "/camera"
        cmd_topic = "/model/drone/cmd_vel"
        
        print(f"📡 Subscribing to Camera: {cam_topic}")
        print(f"🕹️ Subscribing to Teleop: {cmd_topic}")

        # Removed the extra string arguments to fix the TypeError
        self.node.subscribe(Image, cam_topic, self.image_callback)
        self.node.subscribe(Twist, cmd_topic, self.cmd_callback)

    def setup_directories(self):
        # Ensure folders exist on your D: drive
        os.makedirs(IMAGE_DIR, exist_ok=True)
        if not os.path.isfile(CSV_FILE):
            with open(CSV_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "image_path", "linear_x", "angular_z"])

    def image_callback(self, msg):
        self.last_image = msg
        self.last_image_time = msg.header.stamp.sec + (msg.header.stamp.nsec * 1e-9)

    def cmd_callback(self, msg):
        # Only log data if we have a camera frame to pair with the command
        if self.last_image is None: 
            return
        
        # Save the pair immediately when a command is received
        self.save_pair(self.last_image, msg.linear.x, msg.angular.z)

    def save_pair(self, image_msg, lx, az):
        ts_ms = int(self.last_image_time * 1000)
        img_name = f"frame_{ts_ms}.jpg"
        full_path = os.path.join(IMAGE_DIR, img_name)
        
        try:
            # Convert Gazebo raw bytes to a format OpenCV understands
            frame = np.frombuffer(image_msg.data, dtype=np.uint8).reshape((image_msg.height, image_msg.width, 3))
            
            # Save the image (RGB to BGR conversion for OpenCV)
            cv2.imwrite(full_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            
            # Record the telemetry to your CSV for the imitation learning training
            with open(CSV_FILE, 'a', newline='') as f:
                csv.writer(f).writerow([
                    self.last_image_time, 
                    os.path.join("images", img_name), 
                    lx, 
                    az
                ])
            
            print(f"✅ DATA LOGGED: {img_name} | Linear X: {lx:.2f} | Angular Z: {az:.2f}")
        except Exception as e:
            # Silently skip frames that fail to reshape (common during startup)
            pass

if __name__ == "__main__":
    try:
        collector = DataCollector()
        print("--- RECORDING IN PROGRESS ---")
        while True: 
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n--- STOPPED ---")