import sys
import time
# Force Python to see Gazebo libraries
sys.path.append('/usr/lib/python3/dist-packages')

from gz.transport13 import Node
from gz.msgs10 import twist_pb2
from gz.msgs10 import laserscan_pb2

class AutoPilot:
    def __init__(self):
        self.node = Node()
        # Using the string name of the message type to avoid DESCRIPTOR errors
        self.pub = self.node.advertise(twist_pb2.Twist, '/model/drone/cmd_vel', 'gz.msgs.Twist')
        
        # Subscribe using the same explicit type naming
        self.node.subscribe(laserscan_pb2.LaserScan, '/model/drone/device/lidar/scan', self.sensor_callback, 'gz.msgs.LaserScan')
        
        print('🤖 Auto-Pilot Engaged: Flying the Warehouse...')

    def sensor_callback(self, msg):
        if not msg.ranges: return
        center_index = len(msg.ranges) // 2
        front_distance = msg.ranges[center_index]
        
        cmd = twist_pb2.Twist()
        if front_distance < 2.5:
            print(f'🚧 Obstacle at {front_distance:.2f}m! Turning...')
            cmd.linear.x = 0.2
            cmd.angular.z = 0.6
        else:
            cmd.linear.x = 0.8
            cmd.angular.z = 0.0
        self.pub.publish(cmd)

if __name__ == "__main__":
    try:
        pilot = AutoPilot()
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('\nStopping...')