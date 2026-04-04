import os
import time

def launch_drone():
    print("🚀 Launcher Armed: Pressurizing Tube...")
    # Reduced from 3s to 1s for faster testing loops
    time.sleep(1) 
    
    print("🔥 EJECT!")
    # VELOCITY ADJUSTMENT: 
    # Changed 15.0 to 5.0. 
    # At 5m/s, the drone takes ~0.5s to clear the tube.
    # This captures ~15 high-quality frames of the exit for your dataset.
    os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 5.0, z: 0.2}"')
    
    # DURATION ADJUSTMENT:
    # We hold this for 0.7 seconds to ensure the drone is 100% clear 
    # of the tube's 2.5m length (5m/s * 0.7s = 3.5 meters traveled).
    time.sleep(0.7)
    
    print("✨ TUBE CLEAR. Handing over to Auto-Pilot...")
    
    # STABILIZATION:
    # Drop to 1.5m/s (Your cruise speed) so the transition to 
    # Auto-Pilot doesn't cause a massive physics "jerk" or crash.
    os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 1.5}"')

if __name__ == "__main__":
    launch_drone()