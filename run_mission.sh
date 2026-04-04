#!/bin/bash

echo "🚀 Starting Drone Thesis Mission Control (OFFICE ENV)..."

# 0. KILL GHOSTS: Ensuring no old Gazebo or Python instances are hanging
sudo pkill -9 -f "gz|python3"
sleep 2

# 1. Start Gazebo in the background
echo "📦 Launching Office World..."
gz sim test_world.world -r & 

GAZEBO_PID=$!
sleep 8 

# 2. Start the Data Collector
# We start this BEFORE the launch so we record the exit from the tube
echo "📸 Starting Data Collection (Office)..."
python3 collect_data.py &
COLLECTOR_PID=$!
sleep 2

# 3. RUN THE LAUNCHER (Blocking)
# Removed the '&' - the script will wait for launcher.py to finish 
# clearing the tube before moving to the next line.
echo "🔥 INITIALIZING TUBE LAUNCH..."
python3 launcher.py

# 4. START THE AUTO-PILOT (Handover)
# Now that the tube is clear, the brain takes over.
echo "🤖 Engaging Auto-Pilot..."
python3 auto_pilot.py &
PILOT_PID=$!

echo "------------------------------------------------"
echo "Office Mission is live. Press Ctrl+C to stop."
echo "------------------------------------------------"

# CLEANUP TRAP: Swapped PILOT_PID into the trap
trap "echo 'Stopping...'; kill $GAZEBO_PID $COLLECTOR_PID $PILOT_PID; exit" INT

wait