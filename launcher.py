import os
import time

def launch_drone():
    print("🚀 Launcher Armed: Pressurizing Tube...")
    time.sleep(1) 
    
    print("🔥 EJECTING AT 15m/s!")
    # VELOCITY BOOST: 15m/s Forward
    os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 15.0, z: 0.3}"')
    
    # PULSE DURATION: Reduced to 0.3s because 15m/s is very fast
    time.sleep(0.3)
    
    print("✨ TUBE CLEAR. Handing over to Pilot...")
    # BRAKING: Drop to your new 2.5m/s cruise speed
    os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 2.5, z: 0.0}"')

if __name__ == "__main__":
    launch_drone()