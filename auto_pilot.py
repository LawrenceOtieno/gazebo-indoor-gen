import os
import sys
import time
import subprocess

# Force Python to see Gazebo libraries
sys.path.append('/usr/lib/python3/dist-packages')

def get_lidar_distance():
    """Gets a single Lidar reading using the Gazebo CLI"""
    try:
        # Request one message from the Lidar topic
        cmd = "gz topic -t /model/drone/device/lidar/scan -n 1"
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
        
        # Look for the 'ranges' data in the text output
        if "ranges:" in output:
            ranges_str = output.split("ranges: [")[1].split("]")[0]
            ranges = [float(x) for x in ranges_str.split(",")]
            # Return the middle ray (center of drone's view)
            return ranges[len(ranges)//2]
    except Exception:
        return 10.0 # Default to clear path if error
    return 10.0

def run_pilot():
    print('🤖 Auto-Pilot Engaged (CLI Mode): Flying the Warehouse...')
    
    while True:
        dist = get_lidar_distance()
        
        if dist < 2.5:
            print(f'🚧 Obstacle at {dist:.2f}m! Turning...')
            # Using the exact same CLI method that made the launcher work:
            os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.2}, angular: {z: 0.6}"')
        else:
            # Clear path
            os.system('gz topic -t "/model/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.8}, angular: {z: 0.0}"')
        
        time.sleep(0.1) # Check 10 times per second

if __name__ == "__main__":
    try:
        run_pilot()
    except KeyboardInterrupt:
        print('\nStopping Pilot...')