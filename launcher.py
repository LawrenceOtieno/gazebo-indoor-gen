import os
import time

def launch_drone():
    print("🚀 Launcher Armed: Pressurizing Tube...")
    time.sleep(1) 
    
    print("🔥 EJECT!")
    # REPEAT THE COMMAND: We send the burst 5 times rapidly 
    # to ensure the physics engine "grabs" the velocity.
    for _ in range(5):
        os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 10.0, z: 0.3}"')
        time.sleep(0.05)
    
    # PULSE DURATION: Wait for it to clear the 2.5m tube
    time.sleep(0.4)
    
    print("✨ TUBE CLEAR. Handing over...")
    # BRAKING/STABILIZING
    os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.5, z: 0.0}"')

if __name__ == "__main__":
    launch_drone()