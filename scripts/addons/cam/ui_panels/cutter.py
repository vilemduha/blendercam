import bpy
from bpy.types import Panel

from .buttons_panel import CAMButtonsPanel


class CAM_CUTTER_Panel(CAMButtonsPanel, Panel):
    """CAM Cutter Panel"""
    bl_label = "CAM Cutter"
    bl_idname = "WORLD_PT_CAM_CUTTER"
    panel_interface_level = 0

    prop_level = {
        'draw_cutter_preset_menu': 1,
        'draw_cutter_id': 2,
        'draw_cutter_type': 0,
        'draw_ball_radius': 0,
        'draw_bull_radius': 0,
        'draw_cylcone_diameter': 0,
        'draw_cutter_tip_angle': 0,
        'draw_laser': 0,
        'draw_plasma': 0,
        'draw_custom': 0,
        'draw_cutter_diameter': 0,
        'draw_cutter_flutes': 1,
        'draw_cutter_description': 1,
        'draw_engagement': 0
    }

    def draw_cutter_preset_menu(self):
        if not self.has_correct_level():
            return
        row = self.layout.row(align=True)
        row.menu("CAM_CUTTER_MT_presets", text=bpy.types.CAM_CUTTER_MT_presets.bl_label)
        row.operator("render.cam_preset_cutter_add", text="", icon='ADD')
        row.operator("render.cam_preset_cutter_add", text="", icon='REMOVE').remove_active = True

    def draw_cutter_id(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'cutter_id')

    def draw_cutter_type(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'cutter_type')

    def draw_ball_radius(self):
        if not self.has_correct_level():
            return
        if self.op.cutter_type in ['BALLCONE']:
            self.layout.prop(self.op, 'ball_radius')

    def draw_bull_radius(self):
        if not self.has_correct_level():
            return
        if self.op.cutter_type in ['BULLNOSE']:
            self.layout.prop(self.op, 'bull_corner_radius')

    def draw_cylcone_diameter(self):
        if not self.has_correct_level():
            return
        if self.op.cutter_type in ['CYLCONE']:
            self.layout.prop(self.op, 'cylcone_diameter')

    def draw_cutter_tip_angle(self):
        if not self.has_correct_level():
            return
        if self.op.cutter_type in ['VCARVE', 'BALLCONE', 'BULLNOSE', 'CYLCONE']:
            self.layout.prop(self.op, 'cutter_tip_angle')

    def draw_laser(self):
        if not self.has_correct_level():
            return
        if self.op.cutter_type in ['LASER']:
            self.layout.prop(self.op, 'Laser_on')
            self.layout.prop(self.op, 'Laser_off')
            self.layout.prop(self.op, 'Laser_cmd')
            self.layout.prop(self.op, 'Laser_delay')

    def draw_plasma(self):
        if not self.has_correct_level():
            return
        if self.op.cutter_type in ['PLASMA']:
            self.layout.prop(self.op, 'Plasma_on')
            self.layout.prop(self.op, 'Plasma_off')
            self.layout.prop(self.op, 'Plasma_delay')
            self.layout.prop(self.op, 'Plasma_dwell')
            self.layout.prop(self.op, 'lead_in')
            self.layout.prop(self.op, 'lead_out')

    def draw_custom(self):
        if not self.has_correct_level():
            return
        if self.op.cutter_type in ['CUSTOM']:
            if self.op.optimisation.use_exact:
                self.layout.label(
                    text='Warning - only Convex Shapes Are Supported. ', icon='COLOR_RED')
                self.layout.label(text='If Your Custom Cutter Is Concave,')
                self.layout.label(text='Switch Exact Mode Off.')
            self.layout.prop_search(self.op, "cutter_object_name", bpy.data, "objects")

    def draw_cutter_diameter(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'cutter_diameter')

    def draw_cutter_flutes(self):
        if not self.has_correct_level():
            return
        if self.op.cutter_type not in ['LASER', 'PLASMA']:
            self.layout.prop(self.op, 'cutter_flutes')

    def draw_cutter_description(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'cutter_description')

    def draw_engagement(self):
        if not self.has_correct_level():
            return
        if self.op.cutter_type in ['LASER', 'PLASMA']:
            return
        if self.op.strategy in ['CUTOUT']:
            return

        if self.op.cutter_type in ['BALLCONE']:
            engagement = round(100 * self.op.dist_between_paths / self.op.ball_radius, 1)
        else:
            engagement = round(100 * self.op.dist_between_paths / self.op.cutter_diameter, 1)

        self.layout.label(text=f"Cutter Engagement: {engagement}%")

        if engagement > 50:
            self.layout.label(text="WARNING: CUTTER ENGAGEMENT > 50%")

    def draw(self, context):
        self.context = context

        self.draw_cutter_preset_menu()
        self.draw_cutter_id()
        self.draw_cutter_type()
        self.draw_ball_radius()
        self.draw_bull_radius()
        self.draw_cylcone_diameter()
        self.draw_cutter_tip_angle()
        self.draw_laser()
        self.draw_plasma()
        self.draw_custom()
        self.draw_cutter_diameter()
        self.draw_cutter_flutes()
        self.draw_cutter_description()
        self.draw_engagement()
