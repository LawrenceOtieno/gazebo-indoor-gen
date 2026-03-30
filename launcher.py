import os
import time

def launch_drone():
    print("🚀 Launcher Armed: Pressurizing Tube...")
    time.sleep(3)
    
    print("🔥 EJECT!")
    # We use the direct CLI command to bypass the Python API bug
    # This sends 15m/s forward and 0.5m/s up
    os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 15.0, z: 0.5}"')
    
    # Keep the pressure on for half a second
    time.sleep(0.5)
    
    print("✨ TUBE CLEAR. Handing over to Auto-Pilot...")
    # Stabilize
    os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 1.0}"')

if __name__ == "__main__":
    launch_drone()