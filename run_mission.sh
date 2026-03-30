#!/bin/bash

echo "🚀 Starting Drone Thesis Mission Control..."

# 1. Start Gazebo in the background
echo "📦 Launching Gazebo Warehouse..."
gz sim warehouse.world -s -r & 
GAZEBO_PID=$!
sleep 5 # Wait for Gazebo to initialize

# 2. Start the Data Collector in a new terminal tab (or background)
echo "📸 Starting Data Collection..."
python3 collect_data.py &
COLLECTOR_PID=$!
sleep 2

# 3. Start the Auto-Pilot (Expert System)
echo "🤖 Engaging Auto-Pilot..."
python3 auto_pilot.py &
PILOT_PID=$!
sleep 2

# 4. Run the Launcher (The "Ejection" Phase)
echo "🔥 INITIALIZING TUBE LAUNCH..."
python3 launcher.py

echo "------------------------------------------------"
echo "Mission is live. Press Ctrl+C to stop all systems."
echo "------------------------------------------------"

# Keep the script running to manage the processes
wait $GAZEBO_PID $COLLECTOR_PID $PILOT_PID