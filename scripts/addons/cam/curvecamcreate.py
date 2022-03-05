# blender CAM ops.py (c) 2022 Alain Pelletier
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


import bpy
from bpy.props import *
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from cam import utils, pack, polygon_utils_cam, simple, gcodepath, bridges, parametric, joinery, \
    curvecamtools, puzzle_joinery, involute_gear
import shapely
from shapely.geometry import Point, LineString, Polygon, MultiLineString, MultiPoint
import mathutils
import math
from Equation import Expression
import numpy as np


class CamCurveHatch(bpy.types.Operator):
    """perform hatch operation on single or multiple curves"""  # by Alain Pelletier September 2021
    bl_idname = "object.curve_hatch"
    bl_label = "CrossHatch curve"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    angle: bpy.props.FloatProperty(name="angle", default=0, min=-math.pi/2, max=math.pi/2, precision=4, subtype="ANGLE")
    distance: bpy.props.FloatProperty(name="spacing", default=0.015, min=0, max=3.0, precision=4, unit="LENGTH")
    offset: bpy.props.FloatProperty(name="Margin", default=0.001, min=-1.0, max=3.0, precision=4, unit="LENGTH")
    amount: bpy.props.IntProperty(name="amount", default=10, min=1, max=10000)
    hull: bpy.props.BoolProperty(name="Convex Hull", default=False)
    pocket_type: EnumProperty(name='Type pocket',
                              items=(('BOUNDS', 'makes a bounds rectangle', 'makes a bounding square'),
                                     ('POCKET', 'Pocket', 'makes a pocket inside a closed loop')),
                              description='Type of pocket', default='BOUNDS')

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type in ['CURVE', 'FONT']

    def execute(self, context):
        if self.hull:
            bpy.ops.object.convex_hull()
            simple.active_name('crosshatch_hull')
        from shapely import affinity
        from shapely.ops import voronoi_diagram
        shapes = utils.curveToShapely(bpy.context.active_object)
        for s in shapes.geoms:
            coords = []
            minx, miny, maxx, maxy = s.bounds
            minx -= self.offset
            miny -= self.offset
            maxx += self.offset
            maxy += self.offset

            centery = (miny + maxy) / 2
            height = maxy - miny
            width = maxx - minx
            centerx = (minx+maxx) / 2
            diagonal = math.hypot(width, height)

            simple.add_bound_rectangle(minx, miny, maxx, maxy, 'crosshatch_bound')

            amount = int(2*diagonal/self.distance) + 1

            for x in range(amount):
                distance = x * self.distance - diagonal
                coords.append(((distance, diagonal + 0.5), (distance, -diagonal - 0.5)))

            lines = MultiLineString(coords)  # create a multilinestring shapely object
            rotated = affinity.rotate(lines, self.angle, use_radians=True)  # rotate using shapely
            translated = affinity.translate(rotated, xoff=centerx, yoff=centery)  # move using shapely

            simple.make_active('crosshatch_bound')
            bounds = simple.active_to_shapely_poly()

            if self.pocket_type == 'BOUNDS':
                xing = translated.intersection(bounds)  # Shapely detects intersections with the square bounds
            else:
                xing = translated.intersection(s.buffer(self.offset))
                # Shapely detects intersections with the original curve or hull

            utils.shapelyToCurve('crosshatch_lines', xing, 0)

        # remove temporary shapes
        simple.remove_multiple('crosshatch_bound')
        simple.remove_multiple('crosshatch_hull')

        simple.select_multiple('crosshatch')
        return {'FINISHED'}


class CamCurvePlate(bpy.types.Operator):
    """perform generates rounded plate with mounting holes"""  # by Alain Pelletier Sept 2021
    bl_idname = "object.curve_plate"
    bl_label = "Sign plate"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    radius: bpy.props.FloatProperty(name="Corner Radius", default=.025, min=0, max=0.1, precision=4, unit="LENGTH")
    width: bpy.props.FloatProperty(name="Width of plate", default=0.3048, min=0, max=3.0, precision=4, unit="LENGTH")
    height: bpy.props.FloatProperty(name="Height of plate", default=0.457, min=0, max=3.0, precision=4, unit="LENGTH")
    hole_diameter: bpy.props.FloatProperty(name="Hole diameter", default=0.01, min=0, max=3.0, precision=4,
                                           unit="LENGTH")
    hole_tolerance: bpy.props.FloatProperty(name="Hole V Tolerance", default=0.005, min=0, max=3.0, precision=4,
                                            unit="LENGTH")
    hole_vdist: bpy.props.FloatProperty(name="Hole Vert distance", default=0.400, min=0, max=3.0, precision=4,
                                        unit="LENGTH")
    hole_hdist: bpy.props.FloatProperty(name="Hole horiz distance", default=0, min=0, max=3.0, precision=4,
                                        unit="LENGTH")
    hole_hamount: bpy.props.IntProperty(name="Hole horiz amount", default=1, min=0, max=50)
    resolution: bpy.props.IntProperty(name="Spline resolution", default=50, min=3, max=150)

    def execute(self, context):
        left = -self.width / 2 + self.radius
        bottom = -self.height / 2 + self.radius
        right = -left
        top = -bottom

        # create base
        bpy.ops.curve.primitive_bezier_circle_add(radius=self.radius, enter_editmode=False, align='WORLD',
                                                  location=(left, bottom, 0), scale=(1, 1, 1))
        simple.active_name("_circ_LB")
        bpy.context.object.data.resolution_u = self.resolution
        bpy.ops.curve.primitive_bezier_circle_add(radius=self.radius, enter_editmode=False, align='WORLD',
                                                  location=(right, bottom, 0), scale=(1, 1, 1))
        simple.active_name("_circ_RB")
        bpy.context.object.data.resolution_u = self.resolution
        bpy.ops.curve.primitive_bezier_circle_add(radius=self.radius, enter_editmode=False, align='WORLD',
                                                  location=(left, top, 0), scale=(1, 1, 1))
        simple.active_name("_circ_LT")
        bpy.context.object.data.resolution_u = self.resolution
        bpy.ops.curve.primitive_bezier_circle_add(radius=self.radius, enter_editmode=False, align='WORLD',
                                                  location=(right, top, 0), scale=(1, 1, 1))
        simple.active_name("_circ_RT")
        bpy.context.object.data.resolution_u = self.resolution

        simple.select_multiple("_circ")  # select the circles for the four corners
        utils.polygonConvexHull(context)  # perform hull operation on the four corner circles
        simple.active_name("plate_base")
        simple.remove_multiple("_circ")  # remove corner circles

        if self.hole_diameter > 0 or self.hole_hamount > 0:
            bpy.ops.curve.primitive_bezier_circle_add(radius=self.hole_diameter / 2, enter_editmode=False,
                                                      align='WORLD', location=(0, self.hole_tolerance / 2, 0),
                                                      scale=(1, 1, 1))
            simple.active_name("_hole_Top")
            bpy.context.object.data.resolution_u = self.resolution / 4
            if self.hole_tolerance > 0:
                bpy.ops.curve.primitive_bezier_circle_add(radius=self.hole_diameter / 2, enter_editmode=False,
                                                          align='WORLD', location=(0, -self.hole_tolerance / 2, 0),
                                                          scale=(1, 1, 1))
                simple.active_name("_hole_Bottom")
                bpy.context.object.data.resolution_u = self.resolution / 4

            simple.select_multiple("_hole")  # select everything starting with _hole and perform a convex hull on them
            utils.polygonConvexHull(context)
            simple.active_name("plate_hole")
            simple.move(y=-self.hole_vdist / 2)
            simple.duplicate(y=self.hole_vdist)

            simple.remove_multiple("_hole")  # remove temporary holes

            simple.join_multiple("plate_hole")  # join the holes together

            # horizontal holes
            if self.hole_hamount > 1:
                if self.hole_hamount % 2 != 0:
                    for x in range(int((self.hole_hamount - 1) / 2)):
                        dist = self.hole_hdist * (x + 1)  # calculate the distance from the middle
                        simple.duplicate()
                        bpy.context.object.location[0] = dist
                        simple.duplicate()
                        bpy.context.object.location[0] = -dist
                else:
                    for x in range(int(self.hole_hamount / 2)):
                        dist = self.hole_hdist * x + self.hole_hdist / 2  # calculate the distance from the middle
                        if x == 0:  # special case where the original hole only needs to move and not duplicate
                            bpy.context.object.location[0] = dist
                            simple.duplicate()
                            bpy.context.object.location[0] = -dist
                        else:
                            simple.duplicate()
                            bpy.context.object.location[0] = dist
                            simple.duplicate()
                            bpy.context.object.location[0] = -dist
                simple.join_multiple("plate_hole")  # join the holes together

            simple.select_multiple("plate_")  # select everything starting with plate_

            bpy.context.view_layer.objects.active = bpy.data.objects['plate_base']  # Make the plate base active
            utils.polygonBoolean(context, "DIFFERENCE")  # Remove holes from the base
            simple.remove_multiple("plate_")  # Remove temporary base and holes
            simple.remove_multiple("_")

        simple.active_name("plate")
        bpy.context.active_object.select_set(True)
        bpy.ops.object.curve_remove_doubles()

        return {'FINISHED'}


class CamCurveMortise(bpy.types.Operator):
    """Generates mortise along a curve"""  # by Alain Pelletier December 2021
    bl_idname = "object.curve_mortise"
    bl_label = "Mortise"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    finger_size: bpy.props.FloatProperty(name="Maximum Finger Size", default=0.015, min=0.005, max=3.0, precision=4,
                                         unit="LENGTH")
    min_finger_size: bpy.props.FloatProperty(name="Minimum Finger Size", default=0.0025, min=0.001, max=3.0,
                                             precision=4,
                                             unit="LENGTH")
    finger_tolerance: bpy.props.FloatProperty(name="Finger play room", default=0.000045, min=0, max=0.003, precision=4,
                                              unit="LENGTH")
    plate_thickness: bpy.props.FloatProperty(name="Drawer plate thickness", default=0.00477, min=0.001, max=3.0,
                                             unit="LENGTH")
    side_height: bpy.props.FloatProperty(name="side height", default=0.05, min=0.001, max=3.0, unit="LENGTH")
    flex_pocket: bpy.props.FloatProperty(name="Flex pocket", default=0.004, min=0.000, max=1.0, unit="LENGTH")
    top_bottom: bpy.props.BoolProperty(name="Side Top & bottom fingers", default=True)
    opencurve: bpy.props.BoolProperty(name="OpenCurve", default=False)
    adaptive: bpy.props.FloatProperty(name="Adaptive angle threshold", default=0.0, min=0.000, max=2, subtype="ANGLE",
                                      unit="ROTATION")
    double_adaptive: bpy.props.BoolProperty(name="Double adaptive Pockets", default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and (context.active_object.type in ['CURVE', 'FONT'])

    def execute(self, context):
        o1 = bpy.context.active_object

        bpy.context.object.data.resolution_u = 60
        bpy.ops.object.duplicate()
        obj = context.active_object
        bpy.ops.object.convert(target='MESH')
        simple.active_name("_temp_mesh")

        if self.opencurve:
            coords = []
            for v in obj.data.vertices:  # extract X,Y coordinates from the vertices data
                coords.append((v.co.x, v.co.y))
            line = LineString(coords)  # convert coordinates to shapely LineString datastructure
            simple.remove_multiple("-converted")
            utils.shapelyToCurve('-converted_curve', line, 0.0)
        shapes = utils.curveToShapely(o1)

        for s in shapes.geoms:
            if s.boundary.type == 'LineString':
                loops = [s.boundary]
            else:
                loops = s.boundary

            for ci, c in enumerate(loops):
                if self.opencurve:
                    length = line.length
                else:
                    length = c.length
                print("loop Length:", length)
                if self.opencurve:
                    loop_length = line.length
                else:
                    loop_length = c.length
                print("line Length:", loop_length)

                if self.adaptive > 0.0:
                    joinery.variable_finger(c, length, self.min_finger_size, self.finger_size, self.plate_thickness,
                                            self.finger_tolerance, self.adaptive)
                    locations = joinery.variable_finger(c, length, self.min_finger_size, self.finger_size,
                                                        self.plate_thickness, self.finger_tolerance, self.adaptive,
                                                        True, self.double_adaptive)
                    joinery.create_flex_side(loop_length, self.side_height, self.plate_thickness, self.top_bottom)
                    if self.flex_pocket > 0:
                        joinery.make_variable_flex_pocket(self.side_height, self.plate_thickness, self.flex_pocket,
                                                          locations)

                else:
                    joinery.fixed_finger(c, length, self.finger_size, self.plate_thickness, self.finger_tolerance)
                    joinery.fixed_finger(c, length, self.finger_size, self.plate_thickness, self.finger_tolerance, True)
                    joinery.create_flex_side(loop_length, self.side_height, self.plate_thickness, self.top_bottom)
                    if self.flex_pocket > 0:
                        joinery.make_flex_pocket(length, self.side_height, self.plate_thickness, self.finger_size,
                                                 self.flex_pocket)
        simple.remove_multiple('_')
        return {'FINISHED'}


class CamCurveInterlock(bpy.types.Operator):
    """Generates interlock along a curve"""  # by Alain Pelletier December 2021
    bl_idname = "object.curve_interlock"
    bl_label = "Interlock"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    finger_size: bpy.props.FloatProperty(name="Finger Size", default=0.015, min=0.005, max=3.0, precision=4,
                                         unit="LENGTH")
    finger_tolerance: bpy.props.FloatProperty(name="Finger play room", default=0.000045, min=0, max=0.003, precision=4,
                                              unit="LENGTH")
    plate_thickness: bpy.props.FloatProperty(name="Plate thickness", default=0.00477, min=0.001, max=3.0,
                                             unit="LENGTH")
    opencurve: bpy.props.BoolProperty(name="OpenCurve", default=False)
    interlock_type: EnumProperty(name='Type of interlock',
                                 items=(('TWIST', 'Twist', 'Iterlock requires 1/4 turn twist'),
                                        ('GROOVE', 'Groove', 'Simple sliding groove'),
                                        ('PUZZLE', 'Puzzle interlock', 'puzzle good for flat joints')),
                                 description='Type of interlock',
                                 default='GROOVE')
    finger_amount: bpy.props.IntProperty(name="Finger Amount", default=2, min=1, max=100)
    tangent_angle: bpy.props.FloatProperty(name="Tangent deviation", default=0.0, min=0.000, max=2, subtype="ANGLE",
                                           unit="ROTATION")
    fixed_angle: bpy.props.FloatProperty(name="fixed angle", default=0.0, min=0.000, max=2, subtype="ANGLE",
                                         unit="ROTATION")

    def execute(self, context):
        print(len(context.selected_objects), "selected object", context.selected_objects)
        if len(context.selected_objects) > 0 and (context.active_object.type in ['CURVE', 'FONT']):
            o1 = bpy.context.active_object

            bpy.context.object.data.resolution_u = 60
            simple.duplicate()
            obj = context.active_object
            bpy.ops.object.convert(target='MESH')
            simple.active_name("_temp_mesh")

            if self.opencurve:
                coords = []
                for v in obj.data.vertices:  # extract X,Y coordinates from the vertices data
                    coords.append((v.co.x, v.co.y))
                line = LineString(coords)  # convert coordinates to shapely LineString datastructure
                simple.remove_multiple("-converted")
                utils.shapelyToCurve('-converted_curve', line, 0.0)
            shapes = utils.curveToShapely(o1)

            for s in shapes.geoms:
                if s.boundary.type == 'LineString':
                    loops = [s.boundary]
                else:
                    loops = s.boundary

                for ci, c in enumerate(loops):
                    if self.opencurve:
                        length = line.length
                    else:
                        length = c.length
                    print("loop Length:", length)
                    if self.opencurve:
                        loop_length = line.length
                    else:
                        loop_length = c.length
                    print("line Length:", loop_length)

                    joinery.distributed_interlock(c, length, self.finger_size, self.plate_thickness,
                                                  self.finger_tolerance, self.finger_amount,
                                                  fixed_angle=self.fixed_angle, tangent=self.tangent_angle,
                                                  closed=not self.opencurve, type=self.interlock_type)

        else:
            location = bpy.context.scene.cursor.location
            joinery.single_interlock(self.finger_size, self.plate_thickness, self.finger_tolerance, location[0],
                                     location[1], self.fixed_angle, self.interlock_type, self.finger_amount)

            bpy.context.scene.cursor.location = location
        return {'FINISHED'}


class CamCurveDrawer(bpy.types.Operator):
    """Generates drawers"""  # by Alain Pelletier December 2021 inspired by The Drawinator
    bl_idname = "object.curve_drawer"
    bl_label = "Drawer"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    depth: bpy.props.FloatProperty(name="Drawer Depth", default=0.2, min=0, max=1.0, precision=4, unit="LENGTH")
    width: bpy.props.FloatProperty(name="Width of Drawer", default=0.125, min=0, max=3.0, precision=4, unit="LENGTH")
    height: bpy.props.FloatProperty(name="Height of drawer", default=0.07, min=0, max=3.0, precision=4, unit="LENGTH")
    finger_size: bpy.props.FloatProperty(name="Maximum Finger Size", default=0.015, min=0.005, max=3.0, precision=4,
                                         unit="LENGTH")
    finger_tolerance: bpy.props.FloatProperty(name="Finger play room", default=0.000045, min=0, max=0.003, precision=4,
                                              unit="LENGTH")
    finger_inset: bpy.props.FloatProperty(name="Finger inset", default=0.0, min=0.0, max=0.01, precision=4,
                                          unit="LENGTH")
    drawer_plate_thickness: bpy.props.FloatProperty(name="Drawer plate thickness", default=0.00477, min=0.001, max=3.0,
                                                    precision=4, unit="LENGTH")
    drawer_hole_diameter: bpy.props.FloatProperty(name="Drawer hole diameter", default=0.02, min=0.00001, max=0.5,
                                                  precision=4, unit="LENGTH")
    drawer_hole_offset: bpy.props.FloatProperty(name="Drawer hole offset", default=0.0, min=-0.5, max=0.5, precision=4,
                                                unit="LENGTH")
    overcut: bpy.props.BoolProperty(name="Add overcut", default=False)
    overcut_diameter: bpy.props.FloatProperty(name="Overcut toool Diameter", default=0.003175, min=-0.001, max=0.5,
                                              precision=4, unit="LENGTH")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'depth')
        layout.prop(self, 'width')
        layout.prop(self, 'height')
        layout.prop(self, 'finger_size')
        layout.prop(self, 'finger_tolerance')
        layout.prop(self, 'finger_inset')
        layout.prop(self, 'drawer_plate_thickness')
        layout.prop(self, 'drawer_hole_diameter')
        layout.prop(self, 'drawer_hole_offset')
        layout.prop(self, 'overcut')
        if self.overcut:
            layout.prop(self, 'overcut_diameter')

    def execute(self, context):
        height_finger_amt = int(joinery.finger_amount(self.height, self.finger_size))
        height_finger = (self.height + 0.0004) / height_finger_amt
        width_finger_amt = int(joinery.finger_amount(self.width, self.finger_size))
        width_finger = (self.width - self.finger_size) / width_finger_amt

        # create base
        joinery.create_base_plate(self.height, self.width, self.depth)
        bpy.context.object.data.resolution_u = 64
        bpy.context.scene.cursor.location = (0, 0, 0)

        joinery.vertical_finger(height_finger, self.drawer_plate_thickness, self.finger_tolerance, height_finger_amt)

        joinery.horizontal_finger(width_finger, self.drawer_plate_thickness, self.finger_tolerance,
                                  width_finger_amt * 2)
        simple.make_active('_wfb')

        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

        #   make drawer back
        finger_pair = joinery.finger_pair("_vfa", self.width - self.drawer_plate_thickness - self.finger_inset * 2, 0)
        simple.make_active('_wfa')
        fronth = bpy.context.active_object
        simple.make_active('_back')
        finger_pair.select_set(True)
        fronth.select_set(True)
        bpy.ops.object.curve_boolean(boolean_type='DIFFERENCE')
        simple.remove_multiple("_finger_pair")
        simple.active_name("drawer_back")
        simple.remove_doubles()
        simple.add_overcut(self.overcut_diameter, self.overcut)

        #   make drawer front
        bpy.ops.curve.primitive_bezier_circle_add(radius=self.drawer_hole_diameter / 2, enter_editmode=False,
                                                  align='WORLD', location=(0, self.height + self.drawer_hole_offset, 0),
                                                  scale=(1, 1, 1))
        simple.active_name("_circ")
        front_hole = bpy.context.active_object
        simple.make_active('drawer_back')
        front_hole.select_set(True)
        bpy.ops.object.curve_boolean(boolean_type='DIFFERENCE')
        simple.active_name("drawer_front")
        simple.remove_doubles()
        simple.add_overcut(self.overcut_diameter, self.overcut)

        #   place back and front side by side
        simple.make_active('drawer_front')
        bpy.ops.transform.transform(mode='TRANSLATION', value=(0.0, 2 * self.height, 0.0, 0.0))
        simple.make_active('drawer_back')

        bpy.ops.transform.transform(mode='TRANSLATION', value=(self.width + 0.01, 2 * self.height, 0.0, 0.0))
        #   make side

        finger_pair = joinery.finger_pair("_vfb", self.depth - self.drawer_plate_thickness, 0)
        simple.make_active('_side')
        finger_pair.select_set(True)
        fronth.select_set(True)
        bpy.ops.object.curve_boolean(boolean_type='DIFFERENCE')
        simple.active_name("drawer_side")
        simple.remove_doubles()
        simple.add_overcut(self.overcut_diameter, self.overcut)
        simple.remove_multiple('_finger_pair')

        #   make bottom
        simple.make_active("_wfb")
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
                                      TRANSFORM_OT_translate={"value": (0, -self.drawer_plate_thickness / 2, 0.0)})
        simple.active_name("_wfb0")
        joinery.finger_pair("_wfb0", 0, self.depth - self.drawer_plate_thickness)
        simple.active_name('_bot_fingers')

        simple.difference('_bot', '_bottom')
        simple.rotate(math.pi/2)

        joinery.finger_pair("_wfb0", 0, self.width - self.drawer_plate_thickness - self.finger_inset * 2)
        simple.active_name('_bot_fingers')
        simple.difference('_bot', '_bottom')

        simple.active_name("drawer_bottom")

        simple.remove_doubles()
        simple.add_overcut(self.overcut_diameter, self.overcut)

        # cleanup all temp polygons
        simple.remove_multiple("_")

        #   move side and bottom to location
        simple.make_active("drawer_side")
        bpy.ops.transform.transform(mode='TRANSLATION',
                                    value=(self.depth / 2 + 3 * self.width / 2 + 0.02, 2 * self.height, 0.0, 0.0))

        simple.make_active("drawer_bottom")
        bpy.ops.transform.transform(mode='TRANSLATION',
                                    value=(self.depth / 2 + 3 * self.width / 2 + 0.02, self.width / 2, 0.0, 0.0))

        simple.select_multiple('drawer')
        return {'FINISHED'}


class CamCurvePuzzle(bpy.types.Operator):
    """Generates Puzzle joints and interlocks"""  # by Alain Pelletier December 2021
    bl_idname = "object.curve_puzzle"
    bl_label = "Puzzle joints"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    diameter: bpy.props.FloatProperty(name="tool diameter", default=0.003175, min=0.001, max=3.0, precision=4,
                                      unit="LENGTH")
    finger_tolerance: bpy.props.FloatProperty(name="Finger play room", default=0.00005, min=0, max=0.003, precision=4,
                                              unit="LENGTH")
    finger_amount: bpy.props.IntProperty(name="Finger Amount", default=1, min=0, max=100)
    stem_size: bpy.props.IntProperty(name="size of the stem", default=2, min=1, max=200)
    width: bpy.props.FloatProperty(name="Width", default=0.100, min=0.005, max=3.0, precision=4,
                                   unit="LENGTH")
    height: bpy.props.FloatProperty(name="height or thickness", default=0.025, min=0.005, max=3.0, precision=4,
                                    unit="LENGTH")

    angle: bpy.props.FloatProperty(name="angle A", default=math.pi/4, min=-10, max=10, subtype="ANGLE",
                                   unit="ROTATION")
    angleb: bpy.props.FloatProperty(name="angle B", default=math.pi/4, min=-10, max=10, subtype="ANGLE",
                                    unit="ROTATION")

    radius: bpy.props.FloatProperty(name="Arc Radius", default=0.025, min=0.005, max=5, precision=4,
                                    unit="LENGTH")

    interlock_type: EnumProperty(name='Type of shape',
                                 items=(('JOINT', 'Joint', 'Puzzle Joint interlock'),
                                        ('BAR', 'Bar', 'Bar interlock'),
                                        ('ARC', 'Arc', 'Arc interlock'),
                                        ('MULTIANGLE', 'Multi angle', 'Multi angle joint'),
                                        ('CURVEBAR', 'Arc Bar', 'Arc Bar interlock'),
                                        ('CURVEBARCURVE', 'Arc Bar Arc', 'Arc Bar Arc interlock'),
                                        ('CURVET', 'T curve', 'T curve interlock'),
                                        ('T', 'T Bar', 'T Bar interlock'),
                                        ('CORNER', 'Corner Bar', 'Corner Bar interlock'),
                                        ('TILE', 'Tile', 'Tile interlock'),
                                        ('OPENCURVE', 'Open Curve', 'Corner Bar interlock')),
                                 description='Type of interlock',
                                 default='CURVET')
    gender: EnumProperty(name='Type gender',
                         items=(('MF', 'Male-Receptacle', 'Male and receptacle'),
                                ('F', 'Receptacle only', 'Receptacle'),
                                ('M', 'Male only', 'Male')),
                         description='Type of interlock',
                         default='MF')
    base_gender: EnumProperty(name='Base gender',
                              items=(('MF', 'Male - Receptacle', 'Male - Receptacle'),
                                     ('F', 'Receptacle', 'Receptacle'),
                                     ('M', 'Male', 'Male')),
                              description='Type of interlock',
                              default='M')
    multiangle_gender: EnumProperty(name='Multiangle gender',
                                    items=(('MMF', 'Male Male Receptacle', 'M M F'),
                                           ('MFF', 'Male Receptacle Receptacle', 'M F F')),
                                    description='Type of interlock',
                                    default='MFF')

    mitre: bpy.props.BoolProperty(name="Add Mitres", default=False)

    twist_lock: bpy.props.BoolProperty(name="Add TwistLock", default=False)
    twist_thick: bpy.props.FloatProperty(name="Twist Thickness", default=0.0047, min=0.001, max=3.0, precision=4,
                                         unit="LENGTH")
    twist_percent: bpy.props.FloatProperty(name="Twist neck", default=0.3, min=0.1, max=0.9, precision=4)
    twist_keep: bpy.props.BoolProperty(name="keep Twist holes", default=False)
    twist_line: bpy.props.BoolProperty(name="Add Twist to bar", default=False)
    twist_line_amount: bpy.props.IntProperty(name="amount of separators", default=2, min=1, max=600)
    twist_separator: bpy.props.BoolProperty(name="Add Twist separator", default=False)
    twist_separator_amount: bpy.props.IntProperty(name="amount of separators", default=2, min=2, max=600)
    twist_separator_spacing: bpy.props.FloatProperty(name="Separator spacing", default=0.025, min=-0.004, max=1.0,
                                                     precision=4, unit="LENGTH")
    twist_separator_edge_distance: bpy.props.FloatProperty(name="Separator edge distance", default=0.01, min=0.0005,
                                                           max=0.1, precision=4, unit="LENGTH")
    tile_x_amount: bpy.props.IntProperty(name="amount of x fingers", default=2, min=1, max=600)
    tile_y_amount: bpy.props.IntProperty(name="amount of y fingers", default=2, min=1, max=600)
    interlock_amount: bpy.props.IntProperty(name="Interlock amount on curve", default=2, min=0, max=200)
    overcut: bpy.props.BoolProperty(name="Add overcut", default=False)
    overcut_diameter: bpy.props.FloatProperty(name="Overcut toool Diameter", default=0.003175, min=-0.001, max=0.5,
                                              precision=4, unit="LENGTH")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'interlock_type')
        layout.label(text='Puzzle Joint Definition')
        layout.prop(self, 'stem_size')
        layout.prop(self, 'diameter')
        layout.prop(self, 'finger_tolerance')
        if self.interlock_type == 'TILE':
            layout.prop(self, 'tile_x_amount')
            layout.prop(self, 'tile_y_amount')
        else:
            layout.prop(self, 'finger_amount')
        if self.interlock_type != 'JOINT' and self.interlock_type != 'TILE':
            layout.prop(self, 'twist_lock')
            if self.twist_lock:
                layout.prop(self, 'twist_thick')
                layout.prop(self, 'twist_percent')
                layout.prop(self, 'twist_keep')
                layout.prop(self, 'twist_line')
                if self.twist_line:
                    layout.prop(self, 'twist_line_amount')
                layout.prop(self, 'twist_separator')
                if self.twist_separator:
                    layout.prop(self, 'twist_separator_amount')
                    layout.prop(self, 'twist_separator_spacing')
                    layout.prop(self, 'twist_separator_edge_distance')

                if self.interlock_type == 'OPENCURVE':
                    layout.prop(self, 'interlock_amount')
            layout.separator()
            layout.prop(self, 'height')

        if self.interlock_type == 'BAR':
            layout.prop(self, 'mitre')

        if self.interlock_type in ["ARC", "CURVEBARCURVE", "CURVEBAR", "MULTIANGLE", 'CURVET']  \
                or (self.interlock_type == 'BAR' and self.mitre):
            if self.interlock_type == 'MULTIANGLE':
                layout.prop(self, 'multiangle_gender')
            elif self.interlock_type != 'CURVET':
                layout.prop(self, 'gender')
            if not self.mitre:
                layout.prop(self, 'radius')
            layout.prop(self, 'angle')
            if self.interlock_type == 'CURVEBARCURVE' or self.mitre:
                layout.prop(self, 'angleb')

        if self.interlock_type in ['BAR', 'CURVEBARCURVE', 'CURVEBAR', "T", 'CORNER', 'CURVET']:
            layout.prop(self, 'gender')
            if self.interlock_type in ['T', 'CURVET']:
                layout.prop(self, 'base_gender')
            if self.interlock_type == 'CURVEBARCURVE':
                layout.label(text="Width includes 2 radius and thickness")
            layout.prop(self, 'width')
        if self.interlock_type != 'TILE':
            layout.prop(self, 'overcut')
        if self.overcut:
            layout.prop(self, 'overcut_diameter')

    def execute(self, context):
        curve_detected = False
        print(len(context.selected_objects), "selected object", context.selected_objects)
        if len(context.selected_objects) > 0 and context.active_object.type == 'CURVE':
            curve_detected = True
            # bpy.context.object.data.resolution_u = 60
            simple.duplicate()
            bpy.ops.object.transform_apply(location=True)
            obj = context.active_object
            bpy.ops.object.convert(target='MESH')
            bpy.context.active_object.name = "_tempmesh"

            coords = []
            for v in obj.data.vertices:  # extract X,Y coordinates from the vertices data
                coords.append((v.co.x, v.co.y))
            simple.remove_multiple('_tmp')
            line = LineString(coords)  # convert coordinates to shapely LineString datastructure
            simple.remove_multiple("_")

        if self.interlock_type == 'FINGER':
            puzzle_joinery.finger(self.diameter, self.finger_tolerance, stem=self.stem_size)
            simple.rename('_puzzle', 'receptacle')
            puzzle_joinery.finger(self.diameter, 0, stem=self.stem_size)
            simple.rename('_puzzle', 'finger')

        if self.interlock_type == 'JOINT':
            if self.finger_amount == 0:    # cannot be 0 in joints
                self.finger_amount = 1
            puzzle_joinery.fingers(self.diameter, self.finger_tolerance, self.finger_amount, stem=self.stem_size)

        if self.interlock_type == 'BAR':
            if not self.mitre:
                puzzle_joinery.bar(self.width, self.height, self.diameter, self.finger_tolerance, self.finger_amount,
                                   stem=self.stem_size, twist=self.twist_lock, tneck=self.twist_percent,
                                   tthick=self.twist_thick, twist_keep=self.twist_keep,
                                   twist_line=self.twist_line, twist_line_amount=self.twist_line_amount,
                                   which=self.gender)
            else:
                puzzle_joinery.mitre(self.width,  self.height, self.angle, self.angleb, self.diameter,
                                     self.finger_tolerance, self.finger_amount, stem=self.stem_size,
                                     twist=self.twist_lock, tneck=self.twist_percent,
                                     tthick=self.twist_thick, which=self.gender)
        elif self.interlock_type == 'ARC':
            puzzle_joinery.arc(self.radius, self.height, self.angle, self.diameter,
                               self.finger_tolerance, self.finger_amount,
                               stem=self.stem_size, twist=self.twist_lock, tneck=self.twist_percent,
                               tthick=self.twist_thick, which=self.gender)
        elif self.interlock_type == 'CURVEBARCURVE':
            puzzle_joinery.arcbararc(self.width, self.radius, self.height, self.angle, self.angleb, self.diameter,
                                     self.finger_tolerance, self.finger_amount,
                                     stem=self.stem_size, twist=self.twist_lock, tneck=self.twist_percent,
                                     tthick=self.twist_thick, twist_keep=self.twist_keep,
                                     twist_line=self.twist_line, twist_line_amount=self.twist_line_amount,
                                     which=self.gender)

        elif self.interlock_type == 'CURVEBAR':
            puzzle_joinery.arcbar(self.width, self.radius, self.height, self.angle, self.diameter,
                                  self.finger_tolerance, self.finger_amount,
                                  stem=self.stem_size, twist=self.twist_lock, tneck=self.twist_percent,
                                  tthick=self.twist_thick, twist_keep=self.twist_keep,
                                  twist_line=self.twist_line, twist_line_amount=self.twist_line_amount,
                                  which=self.gender)

        elif self.interlock_type == 'MULTIANGLE':
            puzzle_joinery.multiangle(self.radius, self.height, math.pi/3, self.diameter, self.finger_tolerance,
                                      self.finger_amount,
                                      stem=self.stem_size, twist=self.twist_lock, tneck=self.twist_percent,
                                      tthick=self.twist_thick,
                                      combination=self.multiangle_gender)

        elif self.interlock_type == 'T':
            puzzle_joinery.t(self.width, self.height, self.diameter, self.finger_tolerance, self.finger_amount,
                             stem=self.stem_size, twist=self.twist_lock, tneck=self.twist_percent,
                             tthick=self.twist_thick, combination=self.gender, base_gender=self.base_gender)

        elif self.interlock_type == 'CURVET':
            puzzle_joinery.curved_t(self.width, self.height, self.radius, self.diameter, self.finger_tolerance,
                                    self.finger_amount,
                                    stem=self.stem_size, twist=self.twist_lock, tneck=self.twist_percent,
                                    tthick=self.twist_thick, combination=self.gender, base_gender=self.base_gender)

        elif self.interlock_type == 'CORNER':
            puzzle_joinery.t(self.width, self.height, self.diameter, self.finger_tolerance, self.finger_amount,
                             stem=self.stem_size, twist=self.twist_lock, tneck=self.twist_percent,
                             tthick=self.twist_thick, combination=self.gender,
                             base_gender=self.base_gender, corner=True)

        elif self.interlock_type == 'TILE':
            puzzle_joinery.tile(self.diameter, self.finger_tolerance, self.tile_x_amount, self.tile_y_amount,
                             stem=self.stem_size)

        elif self.interlock_type == 'OPENCURVE' and curve_detected:
            puzzle_joinery.open_curve(line, self.height, self.diameter, self.finger_tolerance, self.finger_amount,
                                      stem=self.stem_size, twist=self.twist_lock, t_neck=self.twist_percent,
                                      t_thick=self.twist_thick, which=self.gender, twist_amount=self.interlock_amount,
                                      twist_keep=self.twist_keep)

        simple.remove_doubles()
        simple.add_overcut(self.overcut_diameter, self.overcut)

        if self.twist_lock and self.twist_separator:
            joinery.interlock_twist_separator(self.height, self.twist_thick, self.twist_separator_amount,
                                              self.twist_separator_spacing, self.twist_separator_edge_distance,
                                              finger_play=self.finger_tolerance,
                                              percentage=self.twist_percent)
            simple.remove_doubles()
            simple.add_overcut(self.overcut_diameter, self.overcut)
        return {'FINISHED'}


class CamCurveGear(bpy.types.Operator):
    """Generates involute Gears // version 1.1 by Leemon Baird, 2011, Leemon@Leemon.com
    http://www.thingiverse.com/thing:5505"""  # ported by Alain Pelletier January 2022

    bl_idname = "object.curve_gear"
    bl_label = "Gears"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    tooth_spacing: bpy.props.FloatProperty(name="distance per tooth", default=0.010, min=0.001, max=1.0, precision=4,
                                           unit="LENGTH")
    tooth_amount: bpy.props.IntProperty(name="Amount of teeth", default=7, min=4)

    spoke_amount: bpy.props.IntProperty(name="Amount of spokes", default=4, min=0)

    hole_diameter: bpy.props.FloatProperty(name="Hole diameter", default=0.003175, min=0, max=3.0, precision=4,
                                           unit="LENGTH")
    rim_size: bpy.props.FloatProperty(name="Rim size", default=0.003175, min=0, max=3.0, precision=4,
                                           unit="LENGTH")
    hub_diameter: bpy.props.FloatProperty(name="Hub diameter", default=0.005, min=0, max=3.0, precision=4,
                                           unit="LENGTH")
    pressure_angle: bpy.props.FloatProperty(name="Pressure Angle", default=math.radians(20), min=0.001, max=math.pi/2,
                                            precision=4,
                                            subtype="ANGLE",
                                            unit="ROTATION")
    clearance: bpy.props.FloatProperty(name="Clearance", default=0.00, min=0, max=0.1, precision=4,
                                       unit="LENGTH")
    backlash: bpy.props.FloatProperty(name="Backlash", default=0.0, min=0.0, max=0.1, precision=4,
                                      unit="LENGTH")
    rack_height: bpy.props.FloatProperty(name="Rack Height", default=0.012, min=0.001, max=1, precision=4,
                                      unit="LENGTH")
    rack_tooth_per_hole: bpy.props.IntProperty(name="teeth per mounting hole", default=7, min=2)
    gear_type: EnumProperty(name='Type of gear',
                            items=(('PINION', 'Pinion', 'circular gear'),
                                   ('RACK', 'Rack', 'Straight Rack')),
                            description='Type of gear',
                            default='PINION')

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'gear_type')
        layout.prop(self, 'tooth_spacing')
        layout.prop(self, 'tooth_amount')
        layout.prop(self, 'hole_diameter')
        layout.prop(self, 'pressure_angle')
        layout.prop(self, 'backlash')
        if self.gear_type == 'PINION':
            layout.prop(self, 'clearance')
            layout.prop(self, 'spoke_amount')
            layout.prop(self, 'rim_size')
            layout.prop(self, 'hub_diameter')
        elif self.gear_type == 'RACK':
            layout.prop(self, 'rack_height')
            layout.prop(self, 'rack_tooth_per_hole')

    def execute(self, context):
        if self.gear_type == 'PINION':
            involute_gear.gear(mm_per_tooth=self.tooth_spacing, number_of_teeth=self.tooth_amount,
                               hole_diameter=self.hole_diameter, pressure_angle=self.pressure_angle,
                               clearance=self.clearance, backlash=self.backlash,
                               rim_size=self.rim_size, hub_diameter=self.hub_diameter, spokes=self.spoke_amount)
        elif self.gear_type == 'RACK':
            involute_gear.rack(mm_per_tooth=self.tooth_spacing, number_of_teeth=self.tooth_amount,
                               pressure_angle=self.pressure_angle, height=self.rack_height,
                               backlash=self.backlash,
                               tooth_per_hole=self.rack_tooth_per_hole,
                               hole_diameter=self.hole_diameter)

        return {'FINISHED'}
