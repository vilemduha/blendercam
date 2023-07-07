import json
import subprocess
import hashlib
import os
import unittest

class BlenderCAMTest(unittest.TestCase):
    def setUp(self):
        self.test_cases = []
        for root, dirs, files in os.walk('test_data'):
            subdir_name = os.path.basename(root)
            blend_file = None
            gcode_files = []

            for file in files:
                if file.endswith('.blend'):
                    blend_file = file
                elif file.startswith('_') and file.endswith('.gcode'):
                    gcode_files.append(file)

            if blend_file and gcode_files:
                test_case = {
                    'subdir_name': subdir_name,
                    'blend_file': blend_file,
                    'gcode_files': gcode_files
                }
                self.test_cases.append(test_case)

    @staticmethod
    def get_gcode_from_file(file):
        with open(file, 'r') as f:
            gcode = f.read()
        # Remove first line, it contains the time and date
        lines = gcode.splitlines()
        return '\n'.join(lines[1:])

    def test_operation(self):
        original_dir = os.getcwd()  # Get the original working directory
        generator_path = os.path.join(original_dir, "gcode_generator.py")

        for test_case in self.test_cases:
            os.chdir(original_dir)  # Always start at original working directory

            blend_dir = os.path.join('test_data', test_case["subdir_name"])
            os.chdir(blend_dir)

            # Run Blender in the background to generate GCode
            command = f"blender -b \"{test_case['blend_file']}\" -P \"{generator_path}\""
            subprocess.run(command, shell=True, check=True)

            for gcode_file in test_case['gcode_files']:
                generated_gcode = self.get_gcode_from_file(gcode_file[1:])
                expected_gcode  = self.get_gcode_from_file(gcode_file)

                with self.subTest(operation= f"{test_case['subdir_name']}/{gcode_file}"):
                    self.assertEqual(generated_gcode, expected_gcode)

                os.remove(gcode_file[1:])


if __name__ == '__main__':
    unittest.main()
