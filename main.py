import collections
import collections.abc
import os
from unittest.mock import patch

# 1. Compatibility Fixes
collections.Iterable = collections.abc.Iterable
def mocked_listdir(path):
    if path in ['/usr/share', '/opt/ros', '/etc/gazebo']: return []
    return os.listdir(path)

# 2. Build the Room
with patch('os.listdir', side_effect=mocked_listdir):
    try:
        from pcg_gazebo.generators import WorldGenerator
        world_gen = WorldGenerator()

        # Define a Wall manually
        # This uses the 'tag' to identify it's a box and 'parameters' for dimensions
        world_gen.add_asset(
            tag='wall',
            description=dict(
                type='box',
                args=dict(size=[5, 0.1, 2])
            )
        )
        
        # Define the 4 positions
        wall_poses = [
            [2.5, 0, 1, 0, 0, 1.57],
            [-2.5, 0, 1, 0, 0, 1.57],
            [0, 2.5, 1, 0, 0, 0],
            [0, -2.5, 1, 0, 0, 0]
        ]

        # Add each wall to the world
        for i, pose in enumerate(wall_poses):
            world_gen.add_engine(
                tag=f'wall_engine_{i}',
                engine_name='fixed_pose',
                models=['wall'],
                poses=[pose]
            )

        # Run and Export
        world_gen.run_engines()
        world_gen.export_world(output_dir=os.getcwd(), filename="indoor_room")
        
        print("\n" + "="*40)
        print("SUCCESS! 'indoor_room.world' created.")
        print("="*40)

    except Exception as e:
        print(f"Error building room: {e}")
