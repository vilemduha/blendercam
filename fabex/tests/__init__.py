import unittest
from pathlib import Path

import bpy

# from .test_suite import FabexGcodeTest

# Path to tests
test_path = str(Path(__file__).parent)

if __name__ == "__main__":
    # Queue and run tests
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=test_path,
        pattern="test*.py",
        top_level_dir="fabex",
    )
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

    # quit Blender after running
    bpy.ops.wm.quit_blender()
