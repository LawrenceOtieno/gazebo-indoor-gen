#!/bin/bash

echo "🚀 Starting Drone Thesis Mission Control (OFFICE ENV)..."

# 0. KILL GHOSTS: Ensuring no old Gazebo or Python instances are hanging
sudo pkill -9 -f "gz|python3"
sleep 2

# 1. Start Gazebo in the background
# Make sure test_world.world is in your current directory or GZ_SIM_RESOURCE_PATH
echo "📦 Launching Office World..."
gz sim test_world.world -r & 

GAZEBO_PID=$!
sleep 8 # Offices usually have more meshes (chairs/desks), give it extra time to load

# 2. Start the Data Collector
echo "📸 Starting Data Collection (Office)..."
python3 collect_data.py &
COLLECTOR_PID=$!
sleep 2

# 3. Start the Auto-Pilot
echo "🤖 Engaging Auto-Pilot..."
python3 auto_pilot.py &
PILOT_PID=$!
sleep 2

# 4. Run the Launcher
echo "🔥 INITIALIZING TUBE LAUNCH..."
python3 launcher.py

echo "------------------------------------------------"
echo "Office Mission is live. Press Ctrl+C to stop."
echo "------------------------------------------------"

# CLEANUP TRAP: This kills everything when you press Ctrl+C
trap "echo 'Stopping...'; kill $GAZEBO_PID $COLLECTOR_PID $PILOT_PID; exit" INT

wait