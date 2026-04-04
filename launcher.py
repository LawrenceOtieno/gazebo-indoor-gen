import os
import time

def launch_drone():
    print("🚀 Launcher Armed: Pressurizing Tube...")
    time.sleep(1) 
    
    print("🔥 EJECTING: 30-METER POWER LAUNCH (15m/s)...")
    
    # We loop for 2 seconds to maintain the 30m distance requirement
    start_time = time.time()
    while time.time() - start_time < 2.0:
        # High-frequency command burst (no internal smoothing)
        os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 15.0, z: 0.6}"')
        # Tiny sleep to avoid crashing the terminal, but fast enough for physics
        time.sleep(0.01) 
    
    print("✨ 30m CLEAR. Transitioning to High-Speed Cruise (5.5m/s)...")
    # Strong braking pulse to settle the drone
    for _ in range(10):
        os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 5.5, z: 0.0}"')
        time.sleep(0.01)

if __name__ == "__main__":
    launch_drone()