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
CURRENT_ENV  = "warehouse"  # Toggle to "office" as needed

SAVE_DIR = os.path.join(PROJECT_ROOT, DATASET_NAME, CURRENT_ENV)
IMAGE_DIR = os.path.join(SAVE_DIR, "images")
CSV_FILE  = os.path.join(SAVE_DIR, "commands.csv")

class DataCollector:
    def __init__(self):
        self.setup_directories()
        self.node = Node()
        self.last_image = None
        self.last_image_time = 0
        
        # --- TOPIC AUTO-DETECTION ---
        # UPDATED: Looking for '/camera' based on your 'gz topic -l' output
        all_topics = self.node.topic_list()
        
        # Find camera topic (checking for 'camera' instead of 'image')
        cam_topic = next((t for t in all_topics if 'camera' in t), "/camera")
        
        # Find velocity topic
        cmd_topic = next((t for t in all_topics if 'cmd_vel' in t), "/model/drone/cmd_vel")
        
        print(f"📡 Subscribing to Camera: {cam_topic}")
        print(f"🕹️ Subscribing to Teleop: {cmd_topic}")

        # Adding 'gz.msgs.Image' and 'gz.msgs.Twist' to prevent DESCRIPTOR errors
        self.node.subscribe(Image, cam_topic, self.image_callback, 'gz.msgs.Image')
        self.node.subscribe(Twist, cmd_topic, self.cmd_callback, 'gz.msgs.Twist')

    def setup_directories(self):
        if not os.path.exists(PROJECT_ROOT):
            print(f"❌ ERROR: {PROJECT_ROOT} not found. Check D: drive.")
            sys.exit(1)
        
        # Ensure folders exist
        os.makedirs(IMAGE_DIR, exist_ok=True)
        
        if not os.path.isfile(CSV_FILE):
            with open(CSV_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "image_path", "linear_x", "angular_z"])

    def image_callback(self, msg):
        self.last_image = msg
        # Handle timestamp conversion from Gazebo header
        self.last_image_time = msg.header.stamp.sec + (msg.header.stamp.nsec * 1e-9)

    def cmd_callback(self, msg):
        if self.last_image is None: 
            return
            
        cmd_time = msg.header.stamp.sec + (msg.header.stamp.nsec * 1e-9)
        time_diff = abs(self.last_image_time - cmd_time)
        
        # Sync: Match camera frame to command within 100ms
        if time_diff < 0.1:
            self.save_pair(self.last_image, msg)

    def save_pair(self, image_msg, cmd_msg):
        # Create a timestamp-based filename
        ts_ms = int(self.last_image_time * 1000)
        img_name = f"frame_{ts_ms}.jpg"
        full_path = os.path.join(IMAGE_DIR, img_name)
        
        try:
            # Convert Gazebo bytes to NumPy array and then to OpenCV format
            # image_msg.data is the raw byte string
            frame = np.frombuffer(image_msg.data, dtype=np.uint8)
            
            # Reshape based on message width/height (assuming RGB 3-channel)
            frame = frame.reshape((image_msg.height, image_msg.width, 3))
            
            # Save as BGR for OpenCV
            cv2.imwrite(full_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            
            # Append to CSV
            with open(CSV_FILE, 'a', newline='') as f:
                csv.writer(f).writerow([
                    self.last_image_time, 
                    os.path.join("images", img_name), 
                    cmd_msg.linear.x, 
                    cmd_msg.angular.z
                ])
            print(f"✅ Saved {img_name} | x:{cmd_msg.linear.x:.2f} z:{cmd_msg.angular.z:.2f}")
            
        except Exception as e:
            print(f"⚠️ Save Error: {e}")

if __name__ == "__main__":
    try:
        collector = DataCollector()
        print("--- RECORDING IN PROGRESS ---")
        while True: 
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n--- STOPPED ---")