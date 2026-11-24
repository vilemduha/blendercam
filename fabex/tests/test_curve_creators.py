from unittest import TestCase

import bpy

from .utils import (
    activate_dependencies,
    install_extension,
    zip_extension,
)


class CurveCreatorsTest(TestCase):
    """Test the Curve Creator Operators

    Starts by activating addon dependencies, zipping and installing
    the Extension once, then reading the default blend file before
    each test. The tests add the curves from Curve Creators, check
    that an object with the correct name and point count has been
    added and will fail if the name or point count are incorrect,
    or if an error occurs during execution.
    """

    @classmethod
    def setUpClass(self):
        activate_dependencies(self)
        zip_extension()
        install_extension()

    def setUp(self):
        bpy.ops.wm.read_homefile()

    def test_sign_plate(self):
        bpy.ops.object.curve_plate()
        name = "plate"
        objects = bpy.data.objects
        self.assertIn(name, objects)
        points = len(objects[name].data.splines[0].points)
        self.assertEqual(points, 48)

    def test_drawer(self):
        bpy.ops.object.curve_drawer()
        self.drawers = [
            "drawer_back",
            "drawer_bottom",
            "drawer_front",
            "drawer_side",
        ]
        objects = bpy.data.objects
        for drawer in self.drawers:
            self.assertIn(drawer, objects)
        points = len(bpy.context.object.data.splines[0].points)
        self.assertEqual(points, 116)

    def test_mortise(self):
        bpy.ops.object.curve_interlock()
        bpy.ops.object.curve_mortise()
        name = "mortise"
        objects = bpy.data.objects
        self.assertIn(name, objects)
        points = len(objects[name].data.splines[0].points)
        self.assertEqual(points, 4)

    def test_interlock(self):
        bpy.ops.object.curve_interlock()
        name = "_groove"
        objects = bpy.data.objects
        self.assertIn(name, objects)
        points = len(objects[name].data.splines[0].points)
        self.assertEqual(points, 4)

    def test_puzzle_joints(self):
        bpy.ops.object.curve_puzzle()
        name = "curved_t"
        objects = bpy.data.objects
        self.assertIn(name, objects)
        points = len(objects[name].data.splines[0].points)
        self.assertEqual(points, 3212)

    def test_sine(self):
        bpy.ops.object.sine()
        name = "Periodic Wave"
        objects = bpy.data.objects
        self.assertIn(name, objects)
        points = len(objects[name].data.splines[0].bezier_points)
        self.assertEqual(points, 101)

    def test_lissajous(self):
        bpy.ops.wm.read_homefile()
        bpy.ops.object.lissajous()
        name = "Lissajous"
        objects = bpy.data.objects
        self.assertIn(name, objects)
        points = len(objects[name].data.splines[0].bezier_points)
        self.assertEqual(points, 501)

    def test_hypotrochoid(self):
        bpy.ops.object.hypotrochoid()
        name = "Hypotrochoid"
        objects = bpy.data.objects
        self.assertIn(name, objects)
        points = len(objects[name].data.splines[0].bezier_points)
        self.assertEqual(points, 1131)

    def test_custom(self):
        bpy.ops.object.customcurve()
        name = "Custom"
        objects = bpy.data.objects
        self.assertIn(name, objects)
        points = len(objects[name].data.splines[0].bezier_points)
        self.assertEqual(points, 101)

    def test_crosshatch(self):
        bpy.ops.curve.primitive_bezier_circle_add()
        bpy.ops.object.curve_hatch()
        name = "BézierCircle_crosshatch"
        objects = bpy.data.objects
        self.assertIn(name, objects)
        points = len(objects[name].data.splines[0].points)
        self.assertEqual(points, 2)

    def test_gear(self):
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()
        bpy.ops.object.curve_gear()
        self.assertTrue([obj.name.startswith("gear") for obj in bpy.data.objects])
        points = len(bpy.context.object.data.splines[0].points)
        self.assertEqual(points, 356)

    def test_flat_cone(self):
        bpy.ops.object.curve_flat_cone()
        name = "flat_cone"
        objects = bpy.data.objects
        self.assertIn(name, objects)
        points = len(objects[name].data.splines[0].points)
        self.assertEqual(points, 807)
