import sys
import time
import numpy as np

sys.path.append('/usr/lib/python3/dist-packages')
from gz.transport13 import Node
from gz.msgs10.laserscan_pb2 import LaserScan
from gz.msgs10.twist_pb2 import Twist

class AutoPilot:
    def __init__(self):
        self.node = Node()
        self.pub = self.node.advertise("/model/drone/cmd_vel", Twist)
        lidar_topic = "/model/drone/device/lidar/scan"
        self.node.subscribe(LaserScan, lidar_topic, self.lidar_callback)
        
        # EXTREME SPEED SETTINGS (5.5 m/s)
        self.target_linear_vel = 5.5   
        self.turn_sensitivity = 5.0    # Extreme swerve for high speed
        self.safety_distance = 8.0     # Must see 8 meters ahead to react at 5.5m/s
        
        print(f"🏎️ RACING MODE: {self.target_linear_vel} m/s")

    def lidar_callback(self, msg):
        if not msg.ranges: return
        ranges = np.array(msg.ranges)
        
        center_idx = len(ranges) // 2
        # Wider front sector (40 samples) for better high-speed detection
        front_sector = ranges[center_idx-40 : center_idx+40]
        left_sector  = ranges[center_idx+41 : center_idx+110]
        right_sector = ranges[center_idx-110 : center_idx-41]

        min_front = np.min(front_sector)
        drive_cmd = Twist()

        if min_front < self.safety_distance:
            # OBSTACLE DETECTED: Brake to 2.0m/s while swerving hard
            drive_cmd.linear.x = 2.0  
            if np.mean(left_sector) > np.mean(right_sector):
                drive_cmd.angular.z = self.turn_sensitivity
            else:
                drive_cmd.angular.z = -self.turn_sensitivity
            print(f"🏁 HIGH-SPEED MANEUVER! Dist: {min_front:.2f}m")
        else:
            drive_cmd.linear.x = self.target_linear_vel
            drive_cmd.angular.z = 0.0
            
        self.pub.publish(drive_cmd)

if __name__ == "__main__":
    pilot = AutoPilot()
    try:
        while True: time.sleep(0.05) # Faster loop for higher speeds
    except KeyboardInterrupt:
        print("\n--- PILOT SHUTDOWN ---")