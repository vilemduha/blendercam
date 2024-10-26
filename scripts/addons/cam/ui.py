"""Fabex 'ui.py' © 2012 Vilem Novak

Panels displayed in the 3D Viewport - Curve Tools, Creators and Import G-code
"""

from bpy_extras.io_utils import ImportHelper
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    StringProperty,
)
from bpy.types import (
    Panel,
    Operator,
    UIList,
    PropertyGroup,
)

from .gcodeimportparser import import_gcode


class CAM_UL_orientations(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {"DEFAULT", "COMPACT"}:

            layout.label(text=item.name, translate=False, icon_value=icon)
        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


# panel containing all tools


class VIEW3D_PT_tools_curvetools(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Curve CAM Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.curve_boolean")
        layout.operator("object.convex_hull")
        layout.operator("object.curve_intarsion")
        layout.operator("object.curve_overcuts")
        layout.operator("object.curve_overcuts_b")
        layout.operator("object.silhouete")
        layout.operator("object.silhouete_offset")
        layout.operator("object.curve_remove_doubles")
        layout.operator("object.mesh_get_pockets")


class VIEW3D_PT_tools_create(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Curve CAM Creators"
    bl_option = "DEFAULT_CLOSED"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.curve_plate")
        layout.operator("object.curve_drawer")
        layout.operator("object.curve_mortise")
        layout.operator("object.curve_interlock")
        layout.operator("object.curve_puzzle")
        layout.operator("object.sine")
        layout.operator("object.lissajous")
        layout.operator("object.hypotrochoid")
        layout.operator("object.customcurve")
        layout.operator("object.curve_hatch")
        layout.operator("object.curve_gear")
        layout.operator("object.curve_flat_cone")


# Gcode import panel---------------------------------------------------------------
# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------


class CustomPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Import G-code"
    bl_idname = "OBJECT_PT_importgcode"

    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.mode in {
            "OBJECT",
            "EDIT_MESH",
        }  # with this poll addon is visibly even when no object is selected

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        isettings = scene.cam_import_gcode
        layout.prop(isettings, "output")
        layout.prop(isettings, "split_layers")

        layout.prop(isettings, "subdivide")
        col = layout.column(align=True)
        col = col.row(align=True)
        col.split()
        col.label(text="Segment Length")

        col.prop(isettings, "max_segment_size")
        col.enabled = isettings.subdivide
        col.separator()

        col = layout.column()
        col.scale_y = 2.0
        col.operator("wm.gcode_import")


class WM_OT_gcode_import(Operator, ImportHelper):
    """Import G-code, Travel Lines Don't Get Drawn"""

    bl_idname = (
        "wm.gcode_import"  # important since its how bpy.ops.import_test.some_data is constructed
    )
    bl_label = "Import G-code"

    # ImportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob: StringProperty(
        default="*.*",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        print(self.filepath)
        return import_gcode(context, self.filepath)


class import_settings(PropertyGroup):
    split_layers: BoolProperty(
        name="Split Layers",
        description="Save every layer as single Objects in Collection",
        default=False,
    )
    subdivide: BoolProperty(
        name="Subdivide",
        description="Only Subdivide gcode segments that are " "bigger than 'Segment length' ",
        default=False,
    )
    output: EnumProperty(
        name="Output Type",
        items=(
            ("mesh", "Mesh", "Make a mesh output"),
            ("curve", "Curve", "Make curve output"),
        ),
        default="curve",
    )
    max_segment_size: FloatProperty(
        name="",
        description="Only Segments bigger than this value get subdivided",
        default=0.001,
        min=0.0001,
        max=1.0,
        unit="LENGTH",
    )
