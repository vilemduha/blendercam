from unittest import TestCase

import bpy

from .utils import (
    activate_engine,
    add_collections,
    install_extension,
    zip_extension,
)


class AddOperationTest(TestCase):
    """Test that a  operation can be added."""

    @classmethod
    def setUpClass(self):
        zip_extension()
        install_extension()
        activate_engine(self)
        bpy.ops.wm.read_homefile()
        add_collections()
        bpy.ops.scene.cam_operation_add()

        scene = bpy.context.scene
        self.operations = [operation.name for operation in scene.cam_operations]
        self.operation = scene.cam_operations[scene.cam_active_operation]

    def test_add_operation(self):
        self.assertIn("Op_Cube_1", self.operations)

    def test_available_strategies(self):
        strategies = [
            "CUTOUT",
            "POCKET",
            "DRILL",
            "PARALLEL",
            "CROSS",
            "BLOCK",
            "SPIRAL",
            "CIRCLES",
            "OUTLINEFILL",
            "CARVE",
            "WATERLINE",
            "CURVE",
            "MEDIAL_AXIS",
        ]
        for strat in strategies:
            self.operation.strategy = strat
            self.assertTrue(self.operation.strategy == strat)

    def test_calculate_path(self):
        self.operation.strategy = "CUTOUT"
        bpy.ops.object.calculate_cam_path()
        self.assertIn("cam_path_Op_Cube_1", bpy.data.objects)
