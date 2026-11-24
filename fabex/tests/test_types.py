from unittest import TestCase

import bpy

from .utils import (
    activate_engine,
    install_extension,
    zip_extension,
)


class FabexTypeTest(TestCase):
    """Test that a  operation can be added."""

    @classmethod
    def setUpClass(self):
        zip_extension()
        install_extension()
        activate_engine(self)

    def test_ui_types(self):
        """Check if UI classes exist"""
        ui_classes = [
            "CAM_CUTTER_MT_presets",
            "CAM_OPERATION_MT_presets",
            "CAM_MACHINE_MT_presets",
            "CAM_UL_operations",
            "CAM_UL_chains",
            "TOPBAR_MT_import_gcode",
            "VIEW3D_MT_PIE_CAM",
            "VIEW3D_MT_PIE_Operation",
            "VIEW3D_MT_PIE_Chains",
            "VIEW3D_MT_PIE_PackSliceRelief",
            "VIEW3D_MT_tools_add",
        ]
        for cls in ui_classes:
            self.assertTrue(
                hasattr(bpy.types, cls),
                msg=f"{cls} could not be found.",
            )

    def test_scene_props(self):
        """Check if Property classes exist"""
        prop_classes = [
            "cam_operations",
            "cam_active_chain",
            "cam_active_operation",
            "cam_chains",
            "gcode_output_type",
            "cam_machine",
            "cam_material",
            "cam_text",
            "interface",
            "cam_names",
            # Machine Presets
            "avidcnc",
            "carbide3d",
            "cnc4all",
            "inventables",
            "millright",
            "onefinity",
            "ooznest",
            "sienci",
            "user_machine",
            # Cutter Presets
            "idcwoodcraft",
            "cadence",
            "user_cutter",
            # Operation Presets
            "finishing",
            "roughing",
            "user_operation",
            "operation_preset",
        ]
        for cls in prop_classes:
            self.assertTrue(
                hasattr(bpy.context.scene, cls),
                msg=f"{cls} could not be found.",
            )

    def test_operator_types(self):
        """Check if Operator classes exist"""
        op_classes = [
            # Object
            bpy.ops.object.curve_boolean.idname(),
            bpy.ops.object.convex_hull.idname(),
            bpy.ops.object.curve_intarsion.idname(),
            bpy.ops.object.curve_overcuts.idname(),
            bpy.ops.object.curve_overcuts_b.idname(),
            bpy.ops.object.silhouette.idname(),
            bpy.ops.object.silhouette_offset.idname(),
            bpy.ops.object.curve_remove_doubles.idname(),
            bpy.ops.object.mesh_get_pockets.idname(),
            bpy.ops.object.cam_pack_objects.idname(),
            bpy.ops.object.cam_slice_objects.idname(),
            bpy.ops.object.calculate_cam_path.idname(),
            bpy.ops.object.cam_simulate.idname(),
            bpy.ops.object.material_cam_position.idname(),
            bpy.ops.object.calculate_cam_paths_chain.idname(),
            bpy.ops.object.cam_export_paths_chain.idname(),
            bpy.ops.object.cam_simulate_chain.idname(),
            bpy.ops.object.curve_plate.idname(),
            bpy.ops.object.curve_drawer.idname(),
            bpy.ops.object.curve_mortise.idname(),
            bpy.ops.object.curve_interlock.idname(),
            bpy.ops.object.curve_puzzle.idname(),
            bpy.ops.object.sine.idname(),
            bpy.ops.object.lissajous.idname(),
            bpy.ops.object.hypotrochoid.idname(),
            bpy.ops.object.customcurve.idname(),
            bpy.ops.object.curve_hatch.idname(),
            bpy.ops.object.curve_gear.idname(),
            bpy.ops.object.curve_flat_cone.idname(),
            # Render
            bpy.ops.render.cam_preset_operation_add.idname(),
            bpy.ops.render.cam_preset_machine_add.idname(),
            bpy.ops.render.cam_preset_cutter_add.idname(),
            # Scene
            bpy.ops.scene.calculate_bas_relief.idname(),
            bpy.ops.scene.cam_chain_add.idname(),
            bpy.ops.scene.cam_chain_remove.idname(),
            bpy.ops.scene.cam_chain_operation_add.idname(),
            bpy.ops.scene.cam_chain_operation_remove.idname(),
            bpy.ops.scene.cam_operation_add.idname(),
            bpy.ops.scene.cam_operation_copy.idname(),
            bpy.ops.scene.cam_operation_remove.idname(),
            bpy.ops.scene.cam_operation_move.idname(),
            bpy.ops.scene.cam_bridges_add.idname(),
        ]
        for cls in op_classes:
            self.assertTrue(
                hasattr(bpy.types, cls),
                msg=f"{cls} could not be found.",
            )
