import sys
import time
import os

sys.path.append('/usr/lib/python3/dist-packages')

from gz.transport13 import Node
from gz.msgs10.laserscan_pb2 import LaserScan
from gz.msgs10.twist_pb2 import Twist

class AutoPilot:
    def __init__(self):
        self.node = Node()
        self.pub = self.node.advertise(Twist, '/model/drone/cmd_vel')
        self.node.subscribe(LaserScan, '/model/drone/device/lidar/scan', self.sensor_callback)
        print('🤖 Auto-Pilot Engaged: Flying the Warehouse...')

    def sensor_callback(self, msg):
        if not msg.ranges: return
        center_index = len(msg.ranges) // 2
        front_distance = msg.ranges[center_index]
        cmd = Twist()
        if front_distance < 2.5:  
            print(f'🚧 Obstacle at {front_distance:.2f}m! Turning...')
            cmd.linear.x = 0.2    
            cmd.angular.z = 0.6   
        else:
            cmd.linear.x = 0.8    
            cmd.angular.z = 0.0
        self.pub.publish(cmd)

if __name__ == '__main__':
    try:
        pilot = AutoPilot()
        while True: time.sleep(0.1)
    except KeyboardInterrupt:
        print('
Stopping Auto-Pilot...')
