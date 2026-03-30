import sys
import time
from gz.transport13 import Node
from gz.msgs10.twist_pb2 import Twist

# Force Python to see Gazebo libraries
sys.path.append('/usr/lib/python3/dist-packages')

def launch_drone():
    node = Node()
    pub = node.advertise(Twist, '/model/drone/cmd_vel')
    
    print("🚀 Launcher Armed: Standing by for Tube Exit...")
    time.sleep(2)  # Countdown
    
    # 1. THE IMPULSE (High speed to simulate being shot out)
    print("🔥 LAUNCH!")
    launch_cmd = Twist()
    launch_cmd.linear.x = 12.0  # Rapid forward movement (m/s)
    launch_cmd.linear.z = 2.0   # Slight upward angle
    
    # Send the burst for 0.5 seconds
    start_time = time.time()
    while time.time() - start_time < 0.5:
        pub.publish(launch_cmd)
        time.sleep(0.01)

    # 2. THE TRANSITION (Slow down to cruising speed)
    print("✅ Clear of Tube. Handing over to Auto-Pilot...")
    coast_cmd = Twist()
    coast_cmd.linear.x = 1.0
    pub.publish(coast_cmd)

if __name__ == "__main__":
    try:
        launch_drone()
    except KeyboardInterrupt:
        pass