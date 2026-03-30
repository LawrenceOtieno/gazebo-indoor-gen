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
        
        # Subscribing to the Lidar topic defined in your warehouse.world
        lidar_topic = "/model/drone/device/lidar/scan"
        self.node.subscribe(LaserScan, lidar_topic, self.lidar_callback)
        
        # AGGRESSIVE TUNING PARAMETERS
        self.target_linear_vel = 1.8   # Faster forward speed (m/s)
        self.turn_sensitivity = 2.5    # How hard it swerves (Multiplier)
        self.safety_distance = 2.2     # Distance in meters to trigger a turn
        
        print(f"🤖 Auto-Pilot Active on {lidar_topic}")
        print(f"⚙️  Settings: Speed={self.target_linear_vel}, Sensitivity={self.turn_sensitivity}")

    def lidar_callback(self, msg):
        ranges = np.array(msg.ranges)
        
        # 1. Split Lidar into 3 sectors: Left, Center (Front), Right
        # Your lidar has 360 samples (-3.14 to 3.14 radians)
        # Center is roughly indices 150 to 210
        center_idx = len(ranges) // 2
        front_sector = ranges[center_idx-30 : center_idx+30]
        left_sector  = ranges[center_idx+31 : center_idx+90]
        right_sector = ranges[center_idx-90 : center_idx-31]

        # 2. Find minimum distance in the front
        min_front = np.min(front_sector)
        
        drive_cmd = Twist()

        if min_front < self.safety_distance:
            # OBSTACLE DETECTED: Swerve aggressively
            drive_cmd.linear.x = 0.5  # Slow down while turning
            
            # Decide direction based on which side has more clear space
            if np.mean(left_sector) > np.mean(right_sector):
                drive_cmd.angular.z = self.turn_sensitivity  # Turn Left
            else:
                drive_cmd.angular.z = -self.turn_sensitivity # Turn Right
                
            print(f"🚨 AVOIDING OBSTACLE! Dist: {min_front:.2f}m | Swerving...")
        else:
            # PATH CLEAR: Full speed ahead with minor corrections
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