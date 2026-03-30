import sys
import time
from gz.transport13 import Node
# Using module imports to avoid DESCRIPTOR attribute errors
from gz.msgs10 import twist_pb2
from gz.msgs10 import laserscan_pb2

# Force Python to see Gazebo libraries
sys.path.append('/usr/lib/python3/dist-packages')

class AutoPilot:
    def __init__(self):
        self.node = Node()
        # Explicitly referencing the Protobuf class
        self.pub = self.node.advertise(twist_pb2.Twist, '/model/drone/cmd_vel')
        
        # Subscribe to Lidar
        success = self.node.subscribe(
            laserscan_pb2.LaserScan, 
            '/model/drone/device/lidar/scan', 
            self.sensor_callback
        )
        
        if success:
            print('🤖 Auto-Pilot Engaged: Flying the Warehouse...')
        else:
            print('❌ Error: Lidar subscription failed!')

    def sensor_callback(self, msg):
        if not msg.ranges:
            return
            
        # Check the middle of the Lidar scan (front of drone)
        center_index = len(msg.ranges) // 2
        front_distance = msg.ranges[center_index]
        
        cmd = twist_pb2.Twist()
        # Avoidance Logic
        if front_distance < 2.5:
            print(f'🚧 Obstacle at {front_distance:.2f}m! Turning...')
            cmd.linear.x = 0.2    # Slow down
            cmd.angular.z = 0.6   # Turn left
        else:
            cmd.linear.x = 0.8    # Cruising speed
            cmd.angular.z = 0.0   # Straight
            
        self.pub.publish(cmd)

if __name__ == "__main__":
    try:
        pilot = AutoPilot()
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('\nStopping Auto-Pilot...')