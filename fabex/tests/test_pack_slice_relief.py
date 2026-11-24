from unittest import TestCase

import bpy

from .utils import (
    activate_dependencies,
    install_extension,
)


class BasReliefTest(TestCase):
    """Test that a Bas Relief Mesh can be added."""

    @classmethod
    def setUpClass(self):
        activate_dependencies(self)
        install_extension()

    def setUp(self):
        bpy.ops.wm.read_homefile()

    def test_bas_relief(self):
        bpy.context.scene.render.compositor_device = "CPU"
        bpy.ops.scene.calculate_bas_relief()
        self.assertIn("BasReliefMesh", bpy.data.objects)

    def test_pack_curves(self):
        bpy.ops.curve.primitive_bezier_circle_add(radius=0.01)
        bpy.ops.object.cam_pack_objects()
        self.assertIn("test", bpy.data.objects)

    def test_slice_object(self):
        bpy.ops.object.cam_slice_objects(slice_distance=0.1)
        self.assertTrue([obj.name.startswith("slice") for obj in bpy.data.objects])
