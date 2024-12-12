"""Fabex 'legacy_ui.py' © 2012 Vilem Novak

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

from ..gcode_import_parser import import_gcode


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
    bl_label = "[ Curve Tools ]"
    # bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        # if not context.scene.render.engine == "FABEX_RENDER":
        #     return
        # else:
        layout = self.layout
        layout.scale_y = 1.2
        # header, panel = layout.panel("curve_tools")
        # header.label(text="Curve Tools", icon="CURVE_DATA")
        # if panel:
        col = layout.column()
        col.operator("object.curve_boolean", icon="MOD_BOOLEAN")
        col.operator("object.convex_hull", icon="MOD_SOLIDIFY")
        col.operator("object.curve_intarsion", icon="OUTLINER_DATA_META")
        column = col.column(align=True)
        column.operator("object.curve_overcuts", icon="CON_SIZELIKE")
        column.operator("object.curve_overcuts_b", icon="CON_SIZELIKE")
        column = col.column(align=True)
        column.operator("object.silhouete", icon="USER", text="Object Silhouette")
        column.operator("object.silhouete_offset", icon="COMMUNITY", text="Silhouette Offset")
        col.operator(
            "object.curve_remove_doubles", icon="FORCE_CHARGE", text="Remove Curve Doubles"
        )
        col.operator("object.mesh_get_pockets", icon="HOLDOUT_ON", text="Get Pocket Surfaces")

        column = col.column(align=True)
        column.operator(
            "object.cam_pack_objects", icon="STICKY_UVS_LOC", text="Pack Curves on Sheet"
        )
        column.operator("object.cam_slice_objects", icon="ALIGN_FLUSH", text="Slice Model to Sheet")

        col.operator("scene.calculate_bas_relief", icon="RNDCURVE", text="Bas Relief")


class VIEW3D_PT_tools_create(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "[ Curve Creators ]"
    # bl_option = "DEFAULT_CLOSED"
    # bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        # if not context.scene.render.engine == "FABEX_RENDER":
        #     return
        # else:
        layout = self.layout
        layout.scale_y = 1.2
        # header, panel = layout.panel("curve_tools")
        # header.label(text="Curve Creators", icon="FCURVE")
        # if panel:
        col = layout.column(align=True)
        col.operator("object.curve_plate", icon="META_PLANE")
        col.operator("object.curve_drawer", icon="CON_SAMEVOL")
        col.operator("object.curve_mortise", icon="CHECKBOX_DEHLT")
        col.operator("object.curve_interlock", icon="REMOVE")
        col.operator("object.curve_puzzle", icon="HAND")
        col.operator("object.sine", icon="FORCE_HARMONIC")
        col.operator("object.lissajous", icon="VIEW_ORTHO")
        col.operator("object.hypotrochoid", icon="SHADING_WIRE", text="Hypotrochoid Figure")
        col.operator("object.customcurve", icon="IPO_BOUNCE")
        col.operator("object.curve_hatch", icon="OUTLINER_DATA_LIGHTPROBE")
        col.operator("object.curve_gear", icon="PREFERENCES")
        col.operator("object.curve_flat_cone", icon="MESH_CONE")


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

    split_layers: BoolProperty(
        name="Split Layers",
        description="Save every layer as single Objects in Collection",
        default=False,
    )
    subdivide: BoolProperty(
        name="Subdivide",
        description="Only Subdivide gcode segments that are bigger than 'Segment length' ",
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

    def execute(self, context):
        print(self.filepath)
        context.gcode_output_type = self.output
        return import_gcode(
            context,
            self.filepath,
            self.output,
            self.split_layers,
            self.subdivide,
            self.max_segment_size,
        )
