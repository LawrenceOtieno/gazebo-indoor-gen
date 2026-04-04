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
        
        # HIGH-SPEED TUNING (3.5 m/s)
        self.target_linear_vel = 3.5   # New Cruise Speed
        self.turn_sensitivity = 4.0    # Much sharper turns for high speed
        self.safety_distance = 5.5     # "Look-ahead" increased to 5.5 meters
        
        print(f"🤖 High-Speed Auto-Pilot: {self.target_linear_vel} m/s")

    def lidar_callback(self, msg):
        if not msg.ranges: return
        ranges = np.array(msg.ranges)
        
        center_idx = len(ranges) // 2
        front_sector = ranges[center_idx-30 : center_idx+30]
        left_sector  = ranges[center_idx+31 : center_idx+90]
        right_sector = ranges[center_idx-90 : center_idx-31]

        min_front = np.min(front_sector)
        drive_cmd = Twist()

        if min_front < self.safety_distance:
            # OBSTACLE DETECTED: Brake slightly and swerve hard
            drive_cmd.linear.x = 1.0  
            if np.mean(left_sector) > np.mean(right_sector):
                drive_cmd.angular.z = self.turn_sensitivity
            else:
                drive_cmd.angular.z = -self.turn_sensitivity
            print(f"🚨 HIGH-SPEED EVASION! Dist: {min_front:.2f}m")
        else:
            # Full 3.5 m/s Sprint
            drive_cmd.linear.x = self.target_linear_vel
            drive_cmd.angular.z = 0.0
            
        self.pub.publish(drive_cmd)

if __name__ == "__main__":
    pilot = AutoPilot()
    try:
        while True: time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n--- PILOT SHUTDOWN ---")