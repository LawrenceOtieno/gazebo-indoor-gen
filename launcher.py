import sys
import time
# Force Python to see Gazebo libraries
sys.path.append('/usr/lib/python3/dist-packages')

from gz.transport13 import Node
from gz.msgs10 import twist_pb2

def launch_drone():
    node = Node()
    # Explicitly providing the Gazebo message type name 'gz.msgs.Twist'
    pub = node.advertise(twist_pb2.Twist, '/model/drone/cmd_vel', 'gz.msgs.Twist')
    
    print("🚀 Launcher Armed: Pressurizing Tube...")
    time.sleep(3)
    
    print("🔥 EJECT!")
    launch_cmd = twist_pb2.Twist()
    launch_cmd.linear.x = 15.0
    launch_cmd.linear.z = 0.5
    
    start_time = time.time()
    while time.time() - start_time < 0.4:
        pub.publish(launch_cmd)
        time.sleep(0.01)

    print("✨ TUBE CLEAR.")

if __name__ == "__main__":
    launch_drone()