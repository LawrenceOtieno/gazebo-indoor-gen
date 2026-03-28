import collections
import collections.abc
import os
from unittest.mock import patch  # <--- Added the missing import here

# 1. Fix Python 3.12 compatibility
collections.Iterable = collections.abc.Iterable

# 2. Mock Linux paths for Windows
def mocked_listdir(path):
    if path in ['/usr/share', '/opt/ros', '/etc/gazebo']: return []
    return os.listdir(path)

# 3. Run the Test
with patch('os.listdir', side_effect=mocked_listdir):
    try:
        from pcg_gazebo.generators import WorldGenerator
        
        # Initialize the generator
        world_gen = WorldGenerator()
        
        # Create a simple "Box" model in the world
        # Corrected size syntax: size=[1, 1, 1]
        world_gen.add_asset('test_box', size=[1, 1, 1], mass=1)
        
        # Export the world to the current directory
        world_gen.export_world(output_dir=os.getcwd(), filename="test_world")
        
        print("\n" + "="*40)
        print(f"SUCCESS! World generated at: {os.path.join(os.getcwd(), 'test_world.world')}")
        print("="*40)
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
