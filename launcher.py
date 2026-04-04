import os
import time

def launch_drone():
    print("🚀 Launcher Armed: Pressurizing Tube...")
    time.sleep(1) 
    
    print("🔥 EJECTING: 30-METER POWER LAUNCH (15m/s)...")
    # VELOCITY: 15m/s Forward, 0.6m/s Up (Ensures it stays level over 30m)
    os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 15.0, z: 0.6}"')
    
    # DURATION: 2.0 Seconds (15m/s * 2.0s = 30 meters)
    time.sleep(2.0)
    
    print("✨ 30m CLEAR. Transitioning to High-Speed Cruise (5.5m/s)...")
    # INITIAL BRAKING: Force a speed drop before autopilot takes over
    os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 5.5, z: 0.0}"')

if __name__ == "__main__":
    launch_drone()