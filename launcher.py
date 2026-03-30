import sys
import time
from gz.transport13 import Node
from gz.msgs10 import twist_pb2

# Force Python to see Gazebo libraries
sys.path.append('/usr/lib/python3/dist-packages')

def launch_drone():
    node = Node()
    # Explicitly referencing the Protobuf class
    pub = node.advertise(twist_pb2.Twist, '/model/drone/cmd_vel')
    
    print("🚀 Launcher Armed: Pressurizing Tube...")
    time.sleep(3) # Countdown for your screen capture
    
    print("🔥 EJECT!")
    launch_cmd = twist_pb2.Twist()
    launch_cmd.linear.x = 15.0  # High exit velocity
    launch_cmd.linear.z = 0.5   # Upward lift
    
    # Send the impulse for 0.4 seconds
    start_time = time.time()
    while time.time() - start_time < 0.4:
        pub.publish(launch_cmd)
        time.sleep(0.01)

    print("✨ TUBE CLEAR. Handing over to Auto-Pilot...")
    
    # Send a stabilizing command
    stop_cmd = twist_pb2.Twist()
    stop_cmd.linear.x = 1.0
    pub.publish(stop_cmd)

if __name__ == "__main__":
    try:
        launch_drone()
    except KeyboardInterrupt:
        print('\nLaunch Aborted.')