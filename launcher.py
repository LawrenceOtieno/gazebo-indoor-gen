import os
import time

def launch_drone():
    print("🚀 Launcher Armed: Pressurizing Tube...")
    time.sleep(1) 
    
    print("🔥 EJECTING AT 15m/s!")
    # VELOCITY: 15m/s Forward, 0.5m/s Up (to maintain altitude during the sprint)
    os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 15.0, z: 0.5}"')
    
    # DURATION: 1.0 Second (Drone travels 15 meters)
    time.sleep(1.0)
    
    print("✨ TUBE CLEAR. Handing over to High-Speed Auto-Pilot...")
    # BRAKING: Drop to your new 3.5m/s cruise speed
    os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 3.5, z: 0.0}"')

if __name__ == "__main__":
    launch_drone()