
import bpy
import math
from cam.ui_panels.buttons_panel import CAMButtonsPanel
import cam.utils
import cam.constants


class CAM_MOVEMENT_Properties(bpy.types.PropertyGroup):
    # movement parallel_step_back
    type: bpy.props.EnumProperty(name='Movement type', items=(
        ('CONVENTIONAL', 'Conventional / Up milling',
        'cutter rotates against the direction of the feed'),
        ('CLIMB', 'Climb / Down milling',
            'cutter rotates with the direction of the feed'),
        ('MEANDER', 'Meander / Zig Zag',
            'cutting is done both with and against the rotation of the spindle')),
        description='movement type', default='CLIMB', update=cam.utils.update_operation)

    insideout: bpy.props.EnumProperty(name='Direction',
        items=(('INSIDEOUT', 'Inside out', 'a'), ('OUTSIDEIN', 'Outside in', 'a')),
        description='approach to the piece', default='INSIDEOUT',
        update=cam.utils.update_operation)

    spindle_rotation: bpy.props.EnumProperty(name='Spindle rotation',
        items=(('CW', 'Clock wise', 'a'), ('CCW', 'Counter clock wise', 'a')),
        description='Spindle rotation direction', default='CW',
        update=cam.utils.update_operation)

    free_height: bpy.props.FloatProperty(name="Free movement height",
        default=0.01, min=0.0000, max=32,
        precision=cam.constants.PRECISION, unit="LENGTH",
        update=cam.utils.update_operation)

    useG64: bpy.props.BoolProperty(name="G64 trajectory",
        description='Use only if your machine supports G64 code. LinuxCNC and Mach3 do',
        default=False, update=cam.utils.update_operation)

    G64: bpy.props.FloatProperty(name="Path Control Mode with Optional Tolerance",
        default=0.0001, min=0.0000, max=0.005,
        precision=cam.constants.PRECISION, unit="LENGTH", update=cam.utils.update_operation)

    parallel_step_back: bpy.props.BoolProperty(name="Parallel step back",
        description='For roughing and finishing in one pass: mills material in climb mode, then steps back and goes between 2 last chunks back',
        default=False, update=cam.utils.update_operation)

    first_down: bpy.props.BoolProperty(name="First down",
        description="First go down on a contour, then go to the next one",
        default=False, update=cam.utils.update_operation)

    helix_enter: bpy.props.BoolProperty(name="Helix enter - EXPERIMENTAL",
        description="Enter material in helix",
        default=False, update=cam.utils.update_operation)

    ramp_in_angle: bpy.props.FloatProperty(name="Ramp in angle", default=math.pi / 6,
        min=0, max=math.pi * 0.4999,
        precision=1, subtype="ANGLE", unit="ROTATION", update=cam.utils.update_operation)

    helix_diameter: bpy.props.FloatProperty(name='Helix diameter - % of cutter diameter',
        default=90, min=10, max=100,
        precision=1, subtype='PERCENTAGE', update=cam.utils.update_operation)

    ramp: bpy.props.BoolProperty(name="Ramp in - EXPERIMENTAL",
        description="Ramps down the whole contour, so the cutline looks like helix",
        default=False, update=cam.utils.update_operation)

    ramp_out: bpy.props.BoolProperty(name="Ramp out - EXPERIMENTAL",
        description="Ramp out to not leave mark on surface", default=False,
        update=cam.utils.update_operation)

    ramp_out_angle: bpy.props.FloatProperty(name="Ramp out angle",
        default=math.pi / 6, min=0, max=math.pi * 0.4999,
        precision=1, subtype="ANGLE", unit="ROTATION", update=cam.utils.update_operation)

    retract_tangential: bpy.props.BoolProperty(name="Retract tangential - EXPERIMENTAL",
        description="Retract from material in circular motion", default=False,
        update=cam.utils.update_operation)

    retract_radius: bpy.props.FloatProperty(name='Retract arc radius',
        default=0.001, min=0.000001, max=100,
        precision=cam.constants.PRECISION, unit="LENGTH",
        update=cam.utils.update_operation)

    retract_height: bpy.props.FloatProperty(name='Retract arc height',
        default=0.001, min=0.00000, max=100,
        precision=cam.constants.PRECISION, unit="LENGTH",
        update=cam.utils.update_operation)

    stay_low: bpy.props.BoolProperty(name="Stay low if possible",
        default=True, update=cam.utils.update_operation)

    merge_dist: bpy.props.FloatProperty(name="Merge distance - EXPERIMENTAL",
        default=0.0, min=0.0000, max=0.1,
        precision=cam.constants.PRECISION, unit="LENGTH",
        update=cam.utils.update_operation)

    protect_vertical: bpy.props.BoolProperty(name="Protect vertical",
        description="The path goes only vertically next to steep areas",
        default=True,
        update=cam.utils.update_operation)

    protect_vertical_limit: bpy.props.FloatProperty(name="Verticality limit",
        description="What angle is allready considered vertical",
        default=math.pi / 45, min=0, max=math.pi * 0.5, precision=0,
        subtype="ANGLE", unit="ROTATION", update=cam.utils.update_operation)

class CAM_MOVEMENT_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM movement panel"""
    bl_label = "CAM movement"
    bl_idname = "WORLD_PT_CAM_MOVEMENT"
    panel_interface_level = 0

    prop_level = {
        'type': 1,
        'spindle_rotation': 2,
        'free_height': 0,
        'useG64': 2,
        'parallel_step_back': 1,
        'first_down': 1,
        'helix_enter': 2,
        'ramp': 1,
        'retract_tangential': 2,
        'stay_low': 1,
        'protect_vertical': 1
    }


    def draw_cut_type(self):
        if not self.has_correct_level('type'): return
        self.layout.prop(self.op.movement, 'type')
        if self.op.movement.type in ['BLOCK', 'SPIRAL', 'CIRCLES']:
            self.layout.prop(self.op.movement, 'insideout')

    def draw_spindle_rotation(self):
        if not self.has_correct_level('spindle_rotation'): return
        self.layout.prop(self.op.movement, 'spindle_rotation')

    def draw_free_height(self):
        if not self.has_correct_level('free_height'): return
        self.layout.prop(self.op.movement, 'free_height')
        if self.op.maxz > self.op.movement.free_height:
            self.layout.label(text='Depth start > Free movement')
            self.layout.label(text='POSSIBLE COLLISION')

    def draw_use_g64(self):
        if not self.has_correct_level('useG64'): return
        self.layout.prop(self.op.movement, 'useG64')
        if self.op.movement.useG64:
            self.layout.prop(self.op.movement, 'G64')

    def draw_parallel_stepback(self):
        if not self.has_correct_level('parallel_step_back'): return
        if self.op.strategy in ['PARALLEL','CROSS']:
            if not self.op.movement.ramp:
                self.layout.prop(self.op.movement, 'parallel_step_back')

    def draw_helix_enter(self):
        if not self.has_correct_level('helix_enter'): return
        if self.op.strategy in ['POCKET']:
            self.layout.prop(self.op.movement, 'helix_enter')
            if self.op.movement.helix_enter:
                self.layout.prop(self.op.movement, 'ramp_in_angle')
                self.layout.prop(self.op.movement, 'helix_diameter')

    def draw_first_down(self):
        if not self.has_correct_level('first_down'): return
        if self.op.strategy in ['CUTOUT','POCKET','MEDIAL_AXIS']:
            self.layout.prop(self.op.movement, 'first_down')

    def draw_ramp(self):
        if not self.has_correct_level('ramp'): return
        self.layout.prop(self.op.movement, 'ramp')
        if self.op.movement.ramp:
            self.layout.prop(self.op.movement, 'ramp_in_angle')
            self.layout.prop(self.op.movement, 'ramp_out')
            if self.op.movement.ramp_out:
                self.layout.prop(self.movement, 'ramp_out_angle')

    def draw_retract_tangential(self):
        if not self.has_correct_level('retract_tangential'): return
        if self.op.strategy in ['POCKET']:
            self.layout.prop(self.op.movement, 'retract_tangential')
            if self.op.movement.retract_tangential:
                self.layout.prop(self.op.movement, 'retract_radius')
                self.layout.prop(self.op.movement, 'retract_height')

    def draw_stay_low(self):
        if not self.has_correct_level('stay_low'): return
        self.layout.prop(self.op.movement, 'stay_low')
        if self.op.movement.stay_low:
            self.layout.prop(self.op.movement, 'merge_dist')

    def draw_protect_vertical(self):
        if not self.has_correct_level('protect_vertical'): return
        if self.op.cutter_type not in ['BALLCONE']:
            self.layout.prop(self.op.movement, 'protect_vertical')
            if self.op.movement.protect_vertical:
                self.layout.prop(self.op.movement, 'protect_vertical_limit')

    def draw(self, context):
        self.context = context
        scene = bpy.context.scene

        if not self.op.valid:
            return

        self.draw_cut_type()
        self.draw_spindle_rotation()
        self.draw_free_height()
        self.draw_use_g64()
        self.draw_parallel_stepback()
        self.draw_first_down()
        self.draw_ramp()
        self.draw_helix_enter()
        self.draw_retract_tangential()
        self.draw_stay_low()
        self.draw_protect_vertical()

