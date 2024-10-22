"""CMC CAM 'op_properties.py'

'CAM Operation Setup' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .buttons_panel import CAMButtonsPanel


class CAM_OPERATION_PROPERTIES_Panel(CAMButtonsPanel, Panel):
    """CAM Operation Properties Panel"""
    bl_label = "CAM Operation Setup"
    bl_idname = "WORLD_PT_CAM_OPERATION"
    panel_interface_level = 0

    prop_level = {
        'draw_cutter_engagement': 0,
        'draw_machine_axis': 2,
        'draw_strategy': 0,
        'draw_enable_A_B_axis': 1,
        'draw_cutout_options': 0,
        'draw_waterline_options': 0,
        'draw_medial_axis_options': 0,
        'draw_drill_options': 0,
        'draw_pocket_options': 0,
        'draw_default_options': 0,
        'draw_bridges_options': 1,
        'draw_skin': 1,
        'draw_array': 1,
        'draw_cutout_type': 0,
        'draw_overshoot': 1,
        'draw_startpoint': 1,
        'draw_lead_in_out': 3,
        'draw_outlines': 2,
        'draw_merge': 2
    }

    # Displays percentage of the cutter which is engaged with the material
    # Displays a warning for engagements greater than 50%
    def draw_cutter_engagement(self):
        if not self.has_correct_level():
            return

        if self.op.cutter_type in ['BALLCONE']:
            engagement = round(100 * self.op.dist_between_paths / self.op.ball_radius, 1)
        else:
            engagement = round(100 * self.op.dist_between_paths / self.op.cutter_diameter, 1)

        if engagement > 50:
            self.layout.label(text="Warning: High Cutter Engagement")

        self.layout.label(text=f"Cutter Engagement: {engagement}%")

    def draw_machine_axis(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'machine_axes')

    def draw_strategy(self):
        if not self.has_correct_level():
            return
        if self.op.machine_axes == '4':
            self.layout.prop(self.op, 'strategy4axis')
            if self.op.strategy4axis == 'INDEXED':
                self.layout.prop(self.op, 'strategy')
            self.layout.prop(self.op, 'rotary_axis_1')
        elif self.op.machine_axes == '5':
            self.layout.prop(self.op, 'strategy5axis')
            if self.op.strategy5axis == 'INDEXED':
                self.layout.prop(self.op, 'strategy')
            self.layout.prop(self.op, 'rotary_axis_1')
            self.layout.prop(self.op, 'rotary_axis_2')
        else:
            self.layout.prop(self.op, 'strategy')

    def draw_enable_A_B_axis(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'enable_A')
        if self.op.enable_A:
            self.layout.prop(self.op, 'rotation_A')
            self.layout.prop(self.op, 'A_along_x')
            if self.op.A_along_x:
                self.layout.label(text='A || X - B || Y')
            else:
                self.layout.label(text='A || Y - B ||X')

        self.layout.prop(self.op, 'enable_B')
        if self.op.enable_B:
            self.layout.prop(self.op, 'rotation_B')

    def draw_cutout_type(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'cut_type')
        
    def draw_overshoot(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'straight')

    def draw_startpoint(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'profile_start')

    def draw_lead_in_out(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'lead_in')
        self.layout.prop(self.op, 'lead_out')

    def draw_outlines(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'outlines_count')
        if self.op.outlines_count > 1:
            self.layout.prop(self.op, 'dist_between_paths')
            self.draw_cutter_engagement()
            self.layout.prop(self.op.movement, 'insideout')

    def draw_merge(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'dont_merge')

    def draw_cutout_options(self):
        if not self.has_correct_level():
            return
        if self.op.strategy in ['CUTOUT']:
            self.draw_cutout_type()
            if self.op.cut_type in ['OUTSIDE', 'INSIDE']:
                self.draw_overshoot()
            self.draw_startpoint()
            self.draw_lead_in_out()

        if self.op.strategy in ['CUTOUT', 'CURVE']:
            self.draw_enable_A_B_axis()
            self.draw_outlines()
            self.draw_merge()

    def draw_waterline_options(self):
        if not self.has_correct_level():
            return
        if self.op.strategy in ['WATERLINE']:
            self.layout.label(text="Ocl Doesn't Support Fill Areas")
            if not self.op.optimisation.use_opencamlib:
                self.layout.prop(self.op, 'slice_detail')
                self.layout.prop(self.op, 'waterline_fill')
                if self.op.waterline_fill:
                    self.layout.prop(self.op, 'dist_between_paths')
                    self.layout.prop(self.op, 'waterline_project')
            self.layout.label(text="Waterline Needs a Skin Margin")

    def draw_carve_options(self):
        if not self.has_correct_level():
            return
        if self.op.strategy in ['CARVE']:
            self.layout.prop(self.op, 'carve_depth')
            self.layout.prop(self.op, 'dist_along_paths')

    def draw_medial_axis_options(self):
        if not self.has_correct_level():
            return
        if self.op.strategy in ['MEDIAL_AXIS']:
            self.layout.prop(self.op, 'medial_axis_threshold')
            self.layout.prop(self.op, 'medial_axis_subdivision')
            self.layout.prop(self.op, 'add_pocket_for_medial')
            self.layout.prop(self.op, 'add_mesh_for_medial')

    def draw_drill_options(self):
        if not self.has_correct_level():
            return
        if self.op.strategy in ['DRILL']:
            self.layout.prop(self.op, 'drill_type')
            self.draw_enable_A_B_axis()

    def draw_pocket_options(self):
        if not self.has_correct_level():
            return
        if self.op.strategy in ['POCKET']:
            self.draw_overshoot()
            self.layout.prop(self.op, 'pocketType')
            if self.op.pocketType == 'PARALLEL':
                self.layout.label(text="Warning:Parallel pocket Experimental", icon='ERROR')
                self.layout.prop(self.op, 'parallelPocketCrosshatch')
                self.layout.prop(self.op, 'parallelPocketContour')
                self.layout.prop(self.op, 'parallelPocketAngle')
            else:
                self.layout.prop(self.op, 'pocket_option')
                self.layout.prop(self.op, 'pocketToCurve')
            self.layout.prop(self.op, 'dist_between_paths')
            self.draw_cutter_engagement()
            self.draw_enable_A_B_axis()

    def draw_default_options(self):
        if not self.has_correct_level():
            return
        if self.op.strategy not in ['CUTOUT', 'CURVE', 'WATERLINE', 'CARVE', 'MEDIAL_AXIS', 'DRILL', 'POCKET']:
            self.layout.prop(self.op, 'dist_between_paths')
            self.draw_cutter_engagement()
            self.layout.prop(self.op, 'dist_along_paths')
            if self.op.strategy in ['PARALLEL', 'CROSS']:
                self.layout.prop(self.op, 'parallel_angle')
                self.draw_enable_A_B_axis()
            self.layout.prop(self.op, 'inverse')

    def draw_bridges_options(self):
        if not self.has_correct_level():
            return
        if self.op.strategy not in ['POCKET', 'DRILL', 'CURVE', 'MEDIAL_AXIS']:
            self.layout.prop(self.op, 'use_bridges')
            if self.op.use_bridges:
                self.layout.prop(self.op, 'bridges_width')
                self.layout.prop(self.op, 'bridges_height')
                self.layout.prop_search(self.op, "bridges_collection_name", bpy.data, "collections")
                self.layout.prop(self.op, 'use_bridge_modifiers')
            self.layout.operator("scene.cam_bridges_add", text="Autogenerate Bridges / Tabs")

    def draw_skin(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'skin')

    def draw_array(self):
        if not self.has_correct_level():
            return
        if self.op.machine_axes == '3':
            self.layout.prop(self.op, 'array')
            if self.op.array:
                self.layout.prop(self.op, 'array_x_count')
                self.layout.prop(self.op, 'array_x_distance')
                self.layout.prop(self.op, 'array_y_count')
                self.layout.prop(self.op, 'array_y_distance')

    def draw(self, context):
        self.context = context

        self.draw_machine_axis()
        self.draw_strategy()

        self.draw_cutout_options()
        self.draw_waterline_options()
        self.draw_carve_options()
        self.draw_medial_axis_options()
        self.draw_drill_options()
        self.draw_pocket_options()
        self.draw_default_options()

        self.draw_bridges_options()
        self.draw_skin()
        self.draw_array()
