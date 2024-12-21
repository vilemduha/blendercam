"""Fabex 'gcode_import_op.py' © 2012 Vilem Novak

Panels displayed in the 3D Viewport - Curve Tools, Creators and Import G-code
"""

from bpy_extras.io_utils import ImportHelper
from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty,
)
from bpy.types import (
    Operator,
)

from ..gcode_import_parser import import_gcode


class WM_OT_gcode_import(Operator, ImportHelper):
    """Import G-code, Travel Lines Don't Get Drawn"""

    # important since its how bpy.ops.import_test.some_data is constructed
    bl_idname = "wm.gcode_import"
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
        context.scene.gcode_output_type = self.output
        return import_gcode(
            self,
            context,
            filepath=self.filepath,
        )
