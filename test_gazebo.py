import collections
import collections.abc
import os
from unittest.mock import patch

# 1. Fix Python 3.12 compatibility
collections.Iterable = collections.abc.Iterable

# 2. Mock Linux paths for Windows
def mocked_listdir(path):
    if path in ['/usr/share', '/opt/ros', '/etc/gazebo']: return []
    return os.listdir(path)

# 3. Run the Test
with patch('os.listdir', side_effect=mocked_listdir):
    from pcg_gazebo.generators import WorldGenerator
    
    try:
        # Initialize the generator
        world_gen = WorldGenerator()
        
        # Create a simple "Box" model in the world
        world_gen.add_asset('test_box', size=[1, 1, 1], mass=1)
        world_gen.add_engine(
            tag='box_engine',
            engine_name='fixed_pose',
            models=['test_box'],
            poses=[[0, 0, 0.5, 0, 0, 0]]
        )
        
        # Generate the world
        world_gen.run_engines()
        
        # Save to your current folder
        export_path = os.path.join(os.getcwd(), "test_world.world")
        world_gen.export_world(output_dir=os.getcwd(), filename="test_world")
        
        print("\n" + "="*40)
        print(f"SUCCESS! World generated at:\n{export_path}")
        print("="*40)
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
