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
# Changing environment to 'office' for the second phase of your thesis
CURRENT_ENV  = "office" 

SAVE_DIR = os.path.join(PROJECT_ROOT, DATASET_NAME, CURRENT_ENV)
IMAGE_DIR = os.path.join(SAVE_DIR, "images")
CSV_FILE  = os.path.join(SAVE_DIR, "commands.csv")

class DataCollector:
    def __init__(self):
        self.setup_directories()
        self.node = Node()
        self.last_image = None
        self.last_image_time = 0
        
        cam_topic = "/camera"
        cmd_topic = "/model/drone/cmd_vel"
        
        print(f"📡 Subscribing to Camera: {cam_topic}")
        print(f"🕹️ Subscribing to Teleop: {cmd_topic}")
        print(f"📂 Saving to: {SAVE_DIR}")

        self.node.subscribe(Image, cam_topic, self.image_callback)
        self.node.subscribe(Twist, cmd_topic, self.cmd_callback)

    def setup_directories(self):
        # Creates drone_dataset/office/images/ automatically
        os.makedirs(IMAGE_DIR, exist_ok=True)
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
        # Save the pair immediately when a command is received
        self.save_pair(self.last_image, msg.linear.x, msg.angular.z)

    def save_pair(self, image_msg, lx, az):
        ts_ms = int(self.last_image_time * 1000)
        img_name = f"frame_{ts_ms}.jpg"
        full_path = os.path.join(IMAGE_DIR, img_name)
        
        try:
            # 1. Robust Buffer Conversion
            frame_raw = np.frombuffer(image_msg.data, dtype=np.uint8)
            frame = frame_raw.reshape((image_msg.height, image_msg.width, 3))
            
            # 2. Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # 3. BLANK CHECK: Ignore frames that are solid gray/flat colors
            # Essential to prevent 'dataset poisoning' in your thesis model
            pixel_std = np.std(frame_bgr)

            if pixel_std < 5.0: 
                print(f"⚠️  Skipping Blank Frame: {img_name} (Standard Deviation too low: {pixel_std:.2f})")
                return

            # 4. Save the valid image
            cv2.imwrite(full_path, frame_bgr)
            
            # 5. Live Preview (Ensures you can see the Office environment in real-time)
            cv2.imshow("Drone POV - Office Collection", frame_bgr)
            cv2.waitKey(1) 
            
            # 6. Log to CSV
            with open(CSV_FILE, 'a', newline='') as f:
                csv.writer(f).writerow([
                    self.last_image_time, 
                    os.path.join("images", img_name), 
                    lx, 
                    az
                ])
            
            print(f"✅ OFFICE DATA: {img_name} | LX: {lx:.2f} | AZ: {az:.2f}")

        except Exception as e:
            print(f"❌ Error processing frame: {e}")

if __name__ == "__main__":
    try:
        collector = DataCollector()
        print("--- OFFICE RECORDING IN PROGRESS ---")
        while True: 
            time.sleep(1)
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        print("\n--- STOPPED ---")