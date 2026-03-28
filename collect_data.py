import sys
import os
import time

# Force Python to see the Gazebo libraries you just found
sys.path.append('/usr/lib/python3/dist-packages')

from gz.transport13 import Node
from gz.msgs10.image_pb2 import Image
from gz.msgs10.twist_pb2 import Twist

# Configuration
DATASET_PATH = "./drone_dataset"
os.makedirs(DATASET_PATH, exist_ok=True)

class DataCollector:
    def __init__(self):
        self.node = Node()
        self.last_image = None
        self.last_image_time = 0
        
        # 1. Subscribe to the Camera
        self.node.subscribe(Image, "/model/drone/device/depth_camera/image", self.image_callback)
        
        # 2. Subscribe to the Pilot Commands
        self.node.subscribe(Twist, "/model/drone/cmd_vel", self.cmd_callback)
        
        print("Collector started. Listening for Image + Cmd pairs...")

    def image_callback(self, msg):
        self.last_image = msg
        # Convert simulation timestamp to seconds
        self.last_image_time = msg.header.stamp.sec + (msg.header.stamp.nsec * 1e-9)

    def cmd_callback(self, msg):
        if self.last_image is None:
            return

        # Get command simulation timestamp
        cmd_time = msg.header.stamp.sec + (msg.header.stamp.nsec * 1e-9)
        
        # Logic: Match if timestamps are within 0.1 seconds (100ms)
        time_diff = abs(self.last_image_time - cmd_time)
        
        if time_diff < 0.1:
            self.save_pair(self.last_image, msg, time_diff)

    def save_pair(self, image, cmd, diff):
        # This is where your imitation learning dataset is built
        timestamp = int(self.last_image_time * 1000)
        print(f"✅ Matched! Diff: {diff:.4f}s | Saving to {DATASET_PATH}/{timestamp}")
        # In the next step, we can add the actual image saving (OpenCV) logic here

if __name__ == "__main__":
    try:
        collector = DataCollector()
        print("--- Press Ctrl+C to stop collecting ---")
        while True:
            # This keeps the script from exiting
            time.sleep(1)
            # Optional: print a dot every second to show it's working
            # print(".", end="", flush=True) 
    except KeyboardInterrupt:
        print("\nStopping collector...")
    except Exception as e:
        print(f"Error: {e}")