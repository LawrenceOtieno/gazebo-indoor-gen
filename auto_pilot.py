import sys
import time
import numpy as np

# Force Python to see Gazebo libraries
sys.path.append('/usr/lib/python3/dist-packages')

from gz.transport13 import Node
from gz.msgs10.laserscan_pb2 import LaserScan
from gz.msgs10.twist_pb2 import Twist

class AutoPilot:
    def __init__(self):
        self.node = Node()
        self.pub = self.node.advertise("/model/drone/cmd_vel", Twist)
        
        # Subscribing to the Lidar topic
        lidar_topic = "/model/drone/device/lidar/scan"
        self.node.subscribe(LaserScan, lidar_topic, self.lidar_callback)
        
        # UPDATED FOR HIGH-SPEED NAVIGATION (2.5 m/s)
        self.target_linear_vel = 2.5   # Target cruise speed (m/s)
        self.turn_sensitivity = 3.0    # Increased to handle sharper turns at speed
        self.safety_distance = 3.5     # Increased look-ahead distance for 2.5m/s velocity
        
        print(f"🤖 Auto-Pilot Active on {lidar_topic}")
        print(f"⚙️  Settings: Cruise Speed={self.target_linear_vel}, Safety Gap={self.safety_distance}m")

    def lidar_callback(self, msg):
        # Handle potential empty or malformed lidar messages
        if not msg.ranges:
            return

        ranges = np.array(msg.ranges)
        
        # 1. Split Lidar into 3 sectors: Left, Center (Front), Right
        # Center is roughly indices 150 to 210 for a 360-sample scan
        center_idx = len(ranges) // 2
        front_sector = ranges[center_idx-30 : center_idx+30]
        left_sector  = ranges[center_idx+31 : center_idx+90]
        right_sector = ranges[center_idx-90 : center_idx-31]

        # 2. Find minimum distance in the front
        min_front = np.min(front_sector)
        
        drive_cmd = Twist()

        if min_front < self.safety_distance:
            # OBSTACLE DETECTED: Swerve aggressively
            # Drop to a safe speed while maneuvering
            drive_cmd.linear.x = 0.8  
            
            # Decide direction based on which side has more clear space
            if np.mean(left_sector) > np.mean(right_sector):
                drive_cmd.angular.z = self.turn_sensitivity   # Turn Left
            else:
                drive_cmd.angular.z = -self.turn_sensitivity  # Turn Right
                
            print(f"🚨 AVOIDING OBSTACLE! Dist: {min_front:.2f}m | Swerving at speed...")
        else:
            # PATH CLEAR: Full cruise speed ahead
            drive_cmd.linear.x = self.target_linear_vel
            drive_cmd.angular.z = 0.0
            
        # Publish the command
        self.pub.publish(drive_cmd)

if __name__ == "__main__":
    pilot = AutoPilot()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n--- PILOT SHUTDOWN ---")