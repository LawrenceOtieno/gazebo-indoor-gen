import sys
import os
import time
import csv
import numpy as np
import cv2

# Force Python to see the Gazebo libraries
sys.path.append('/usr/lib/python3/dist-packages')

from gz.transport13 import Node
from gz.msgs10.image_pb2 import Image
from gz.msgs10.twist_pb2 import Twist

# ==========================================
# CONFIGURATION - THE D: DRIVE FIX
# ==========================================
PROJECT_ROOT = "/mnt/d/Projects/gazebo-indoor-gen"
DATASET_NAME = "drone_dataset"
CURRENT_ENV  = "warehouse"  # Toggle to "office" for other environment

# Construct Absolute Paths
SAVE_DIR = os.path.join(PROJECT_ROOT, DATASET_NAME, CURRENT_ENV)
IMAGE_DIR = os.path.join(SAVE_DIR, "images")
CSV_FILE  = os.path.join(SAVE_DIR, "commands.csv")

class DataCollector:
    def __init__(self):
        self.setup_directories()
        
        self.node = Node()
        self.last_image = None
        self.last_image_time = 0
        
        # Subscribe to topics
        self.node.subscribe(Image, "/model/drone/device/depth_camera/image", self.image_callback)
        self.node.subscribe(Twist, "/model/drone/cmd_vel", self.cmd_callback)
        
        print(f"--- Data Collection Initialized ---")
        print(f"Target Path: {SAVE_DIR}")

    def setup_directories(self):
        if not os.path.exists(PROJECT_ROOT):
            print(f"CRITICAL ERROR: {PROJECT_ROOT} not found! Check D: drive mount.")
            sys.exit(1)
            
        for path in [SAVE_DIR, IMAGE_DIR]:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)

        if not os.path.isfile(CSV_FILE):
            with open(CSV_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "image_path", "linear_x", "angular_z"])

    def image_callback(self, msg):
        self.last_image = msg
        self.last_image_time = msg.header.stamp.sec + (msg.header.stamp.nsec * 1e-9)

    def cmd_callback(self, msg):
        if self.last_image is None:
            return

        cmd_time = msg.header.stamp.sec + (msg.header.stamp.nsec * 1e-9)
        time_diff = abs(self.last_image_time - cmd_time)
        
        # Sync Logic (100ms window)
        if time_diff < 0.1:
            self.save_pair(self.last_image, msg)

    def save_pair(self, image_msg, cmd_msg):
        # 1. Generate Filename
        timestamp_ms = int(self.last_image_time * 1000)
        img_name = f"frame_{timestamp_ms}.jpg"
        full_img_path = os.path.join(IMAGE_DIR, img_name)
        
        try:
            # 2. Convert Protobuf Image to OpenCV BGR
            # Extract raw data from message
            height = image_msg.height
            width = image_msg.width
            # Assuming RGB8 format from Gazebo
            frame = np.frombuffer(image_msg.data, dtype=np.uint8).reshape((height, width, 3))
            
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # 3. Save the JPG file
            cv2.imwrite(full_img_path, frame_bgr)
            
            # 4. Log to CSV
            relative_path = os.path.join("images", img_name)
            with open(CSV_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([self.last_image_time, relative_path, cmd_msg.linear.x, cmd_msg.angular.z])
                
            print(f"Saved: {img_name} | Cmd: x={cmd_msg.linear.x:.2f}, z={cmd_msg.angular.z:.2f}")

        except Exception as e:
            print(f"Error saving frame: {e}")

if __name__ == "__main__":
    try:
        collector = DataCollector()
        print("--- Recording... Press Ctrl+C to stop ---")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping collector...")