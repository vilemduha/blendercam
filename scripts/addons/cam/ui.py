# blender CAM ui.py (c) 2012 Vilem Novak
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

import sys
import bpy
from bpy.types import UIList, Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import (StringProperty,
                       BoolProperty,
                       PointerProperty,
                       FloatProperty,
                       )

from bpy.types import (Panel, Menu, Operator, PropertyGroup, )

from cam import gcodeimportparser, simple
from cam.simple import *

from cam.ui_panels.buttons_panel  import CAMButtonsPanel
from cam.ui_panels.interface      import *
from cam.ui_panels.info           import *
from cam.ui_panels.operations     import *
from cam.ui_panels.cutter         import *
from cam.ui_panels.machine        import *
from cam.ui_panels.material       import *
from cam.ui_panels.chains         import *
from cam.ui_panels.op_properties  import *
from cam.ui_panels.movement       import *
from cam.ui_panels.feedrate       import *
from cam.ui_panels.optimisation   import *
from cam.ui_panels.area           import *
from cam.ui_panels.gcode          import *
from cam.ui_panels.pack           import *
from cam.ui_panels.slice          import *


class CAM_UL_orientations(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            layout.label(text=item.name, translate=False, icon_value=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)




# panel containing all tools

class VIEW3D_PT_tools_curvetools(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
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


class VIEW3D_PT_tools_create(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_label = "Curve CAM Creators"
    bl_option = 'DEFAULT_CLOSED'

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


class CustomPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_label = "Import Gcode"
    bl_idname = "OBJECT_PT_importgcode"

    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT',
                                'EDIT_MESH'}  # with this poll addon is visibly even when no object is selected

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        isettings = scene.cam_import_gcode
        layout.prop(isettings, 'output')
        layout.prop(isettings, "split_layers")

        layout.prop(isettings, "subdivide")
        col = layout.column(align=True)
        col = col.row(align=True)
        col.split()
        col.label(text="Segment length")

        col.prop(isettings, "max_segment_size")
        col.enabled = isettings.subdivide
        col.separator()

        col = layout.column()
        col.scale_y = 2.0
        col.operator("wm.gcode_import")


class WM_OT_gcode_import(Operator, ImportHelper):
    """Import Gcode, travel lines don't get drawn"""
    bl_idname = "wm.gcode_import"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Gcode"

    # ImportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        print(self.filepath)
        return gcodeimportparser.import_gcode(context, self.filepath)
