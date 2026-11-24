from unittest import TestCase

import bpy

from .utils import (
    activate_engine,
    compare_gcode_files,
    delta,
    get_gcode_filepaths,
    get_gcode_from_file,
    install_extension,
    # remove_test_images,
    run_test_file,
    zip_extension,
)


class BlendFileTest(TestCase):
    """Test operations from the simple_cutout file."""

    @classmethod
    def setUpClass(self):
        zip_extension()
        install_extension()
        activate_engine(self)

    @staticmethod
    def assert_equal_points(self, paths):
        objects = bpy.data.objects
        for path in paths:
            name = path[0]
            vertices = path[1]
            self.assertIn(
                name,
                objects,
                msg=f"{path} not found!",
            )
            self.assertEqual(vertices, len(objects[name].data.vertices))

    @staticmethod
    def assert_almost_equal_gcode(self, paths, test):
        generated_files, expected_files = get_gcode_filepaths(test, paths)
        for i in range(len(paths)):
            if f"_{generated_files[i]}" == expected_files[i]:
                generated_stripped, expected_stripped = compare_gcode_files(
                    generated_files[i], expected_files[i]
                )
                for i in range(len(expected_stripped)):
                    self.assertAlmostEqual(
                        generated_stripped[i],
                        expected_stripped[i],
                        delta=delta,
                    )

    def test_simple_cutout(self):
        test = "simple_cutout"
        paths = [
            ("cam_path_Op_Cutout", 20),
            ("cam_path_Op_Cutout_Layers", 173),
        ]
        run_test_file(test)
        self.assert_equal_points(self, paths)
        self.assert_almost_equal_gcode(self, paths, test)

    def test_first_down(self):
        test = "first_down"
        paths = [
            ("cam_path_first_down", 397),
            ("cam_path_no_first_down", 451),
        ]
        run_test_file(test)
        self.assert_equal_points(self, paths)
        self.assert_almost_equal_gcode(self, paths, test)

    def test_min_depth(self):
        test = "min_depth"
        paths = [
            ("cam_path_min_depth_custom", 2573),
            ("cam_path_min_depth_material", 2573),
            ("cam_path_min_depth_object", 2573),
        ]
        run_test_file(test)
        self.assert_equal_points(self, paths)
        self.assert_almost_equal_gcode(self, paths, test)

    def test_parallel(self):
        test = "parallel"
        paths = [
            ("cam_path_Op_Parallel_Internal_Exact", 2095),
            ("cam_path_Op_Parallel_OCL", 2159),
        ]
        run_test_file(test)
        self.assert_equal_points(self, paths)
        self.assert_almost_equal_gcode(self, paths, test)
        # remove_test_images(test)

    def test_patterns(self):
        test = "patterns"
        paths = [
            ("cam_path_Block", 1392),
            ("cam_path_Circles", 248984),
            ("cam_path_Cross", 4319),
            ("cam_path_Parallel", 58249),
            ("cam_path_Spiral", 249123),
        ]
        run_test_file(test)
        self.assert_equal_points(self, paths)
        self.assert_almost_equal_gcode(self, paths, test)
        # remove_test_images(test)

    def test_ramps(self):
        test = "ramps"
        paths = [
            ("cam_path_HelixEnter", 9559),
            ("cam_path_RampIn", 177413),
            ("cam_path_RampOut", 1650),
        ]
        run_test_file(test)
        self.assert_equal_points(self, paths)
        self.assert_almost_equal_gcode(self, paths, test)

    def test_simplify(self):
        test = "simplify"
        paths = [
            ("cam_path_simplify", 1331),
        ]
        run_test_file(test)
        self.assert_equal_points(self, paths)
        self.assert_almost_equal_gcode(self, paths, test)

    def test_waterline(self):
        test = "waterline"
        paths = [
            ("cam_path_Waterline_Internal", 13897),
            ("cam_path_Waterline_Internal_Exact", 1571),
            ("cam_path_Waterline_OCL", 4777),
        ]
        run_test_file(test)
        self.assert_equal_points(self, paths)
        self.assert_almost_equal_gcode(self, paths, test)
        # remove_test_images(test)

    def test_four_axis(self):
        test = "4axistest"
        paths = [
            ("cam_path_Op_Plane_1", 67),
        ]
        run_test_file(test)
        self.assert_equal_points(self, paths)
        self.assert_almost_equal_gcode(self, paths, test)

    # Medial fails due to invalid curve

    def test_medial(self):
        test = "medial"
        paths = [
            ("cam_path_fern", 8532),
            ("cam_path_MedialPocket", 1751),
            # ("cam_path_Text_MedialPocket", 1572), # Need to re-add equivalent later
            ("cam_path_text", 4340),
        ]
        run_test_file(test)
        self.assert_equal_points(self, paths)
        self.assert_almost_equal_gcode(self, paths, test)
