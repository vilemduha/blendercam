# blender CAM ops.py (c) 2012 Vilem Novak
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# blender operators definitions are in this file. They mostly call the functions from utils.py


import bpy
from bpy.props import *
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from cam import utils, pack, polygon_utils_cam, simple, gcodepath, bridges, parametric, gcodeimportparser, joinery, curvecamtools
import shapely
from shapely.geometry import Point, LineString, Polygon
import mathutils
import math
from Equation import Expression
import numpy as np


class CamCurveHatch(bpy.types.Operator):
    """perform hatch operation on single or multiple curves"""  # by Alain Pelletier September 2021
    bl_idname = "object.curve_hatch"
    bl_label = "Hatch curve"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    angle: bpy.props.FloatProperty(name="angle", default=0, min=0, max=360, precision=4, subtype="ANGLE")
    distance: bpy.props.FloatProperty(name="spacing", default=0.001, min=0, max=3.0, precision=4, unit="LENGTH")
    cross: bpy.props.BoolProperty(name="Cross hatch", default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type in ['CURVE', 'FONT']

    def execute(self, context):
        utils.polygonHatch(self.distance, self.angle, self.cross)
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
    hole_tolerence: bpy.props.FloatProperty(name="Hole V Tolerance", default=0.005, min=0, max=3.0, precision=4,
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
        bpy.context.active_object.name = "_circ_LB"
        bpy.context.object.data.resolution_u = self.resolution
        bpy.ops.curve.primitive_bezier_circle_add(radius=self.radius, enter_editmode=False, align='WORLD',
                                                  location=(right, bottom, 0), scale=(1, 1, 1))
        bpy.context.active_object.name = "_circ_RB"
        bpy.context.object.data.resolution_u = self.resolution
        bpy.ops.curve.primitive_bezier_circle_add(radius=self.radius, enter_editmode=False, align='WORLD',
                                                  location=(left, top, 0), scale=(1, 1, 1))
        bpy.context.active_object.name = "_circ_LT"
        bpy.context.object.data.resolution_u = self.resolution
        bpy.ops.curve.primitive_bezier_circle_add(radius=self.radius, enter_editmode=False, align='WORLD',
                                                  location=(right, top, 0), scale=(1, 1, 1))
        bpy.context.active_object.name = "_circ_RT"
        bpy.context.object.data.resolution_u = self.resolution

        simple.selectMultiple("_circ")  # select the circles for the four corners
        utils.polygonConvexHull(context)  # perform hull operation on the four corner circles
        bpy.context.active_object.name = "plate_base"
        simple.removeMultiple("_circ")  # remove corner circles

        if self.hole_diameter > 0 or self.hole_hamount > 0:
            bpy.ops.curve.primitive_bezier_circle_add(radius=self.hole_diameter / 2, enter_editmode=False,
                                                      align='WORLD', location=(0, self.hole_tolerence / 2, 0),
                                                      scale=(1, 1, 1))
            bpy.context.active_object.name = "_hole_Top"
            bpy.context.object.data.resolution_u = self.resolution / 4
            if self.hole_tolerence > 0:
                bpy.ops.curve.primitive_bezier_circle_add(radius=self.hole_diameter / 2, enter_editmode=False,
                                                          align='WORLD', location=(0, -self.hole_tolerence / 2, 0),
                                                          scale=(1, 1, 1))
                bpy.context.active_object.name = "_hole_Bottom"
                bpy.context.object.data.resolution_u = self.resolution / 4

            simple.selectMultiple("_hole")  # select everything starting with _hole and perform a convex hull on them
            utils.polygonConvexHull(context)
            bpy.context.active_object.name = "plate_hole"
            bpy.context.object.location[1] = -self.hole_vdist / 2
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
                                          TRANSFORM_OT_translate={"value": (0, self.hole_vdist, 0)})
            simple.removeMultiple("_hole")  # remove temporary holes

            simple.joinMultiple("plate_hole")  # join the holes together

            # horizontal holes
            if self.hole_hamount > 1:
                if self.hole_hamount % 2 != 0:
                    for x in range(int((self.hole_hamount - 1) / 2)):
                        dist = self.hole_hdist * (x + 1)  # calculate the distance from the middle
                        bpy.ops.object.duplicate()
                        bpy.context.object.location[0] = dist
                        bpy.ops.object.duplicate()
                        bpy.context.object.location[0] = -dist
                else:
                    for x in range(int(self.hole_hamount / 2)):
                        dist = self.hole_hdist * x + self.hole_hdist / 2  # calculate the distance from the middle
                        if x == 0:  # special case where the original hole only needs to move and not duplicate
                            bpy.context.object.location[0] = dist
                            bpy.ops.object.duplicate()
                            bpy.context.object.location[0] = -dist
                        else:
                            bpy.ops.object.duplicate()
                            bpy.context.object.location[0] = dist
                            bpy.ops.object.duplicate()
                            bpy.context.object.location[0] = -dist
                simple.joinMultiple("plate_hole")  # join the holes together

            simple.selectMultiple("plate_")  # select everything starting with plate_

            bpy.context.view_layer.objects.active = bpy.data.objects['plate_base']  # Make the plate base active
            utils.polygonBoolean(context, "DIFFERENCE")  # Remove holes from the base
            simple.removeMultiple("plate_")  # Remove temporary base and holes

        bpy.context.active_object.name = "plate"
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
        bpy.context.active_object.name = "_temp_mesh"

        if self.opencurve:
            coords = []
            for v in obj.data.vertices:  # extract X,Y coordinates from the vertices data
                coords.append((v.co.x, v.co.y))
            line = LineString(coords)  # convert coordinates to shapely LineString datastructure
            simple.removeMultiple("-converted")
            utils.shapelyToCurve('-converted_curve', line, 0.0)
        shapes = utils.curveToShapely(o1)

        for s in shapes:
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
    finger_tolerence: bpy.props.FloatProperty(name="Finger play room", default=0.000045, min=0, max=0.003, precision=4,
                                              unit="LENGTH")
    finger_inset: bpy.props.FloatProperty(name="Finger inset", default=0.0, min=0.0, max=0.01, precision=4,
                                          unit="LENGTH")
    drawer_plate_thickness: bpy.props.FloatProperty(name="Drawer plate thickness", default=0.00477, min=0.001, max=3.0,
                                                    precision=4, unit="LENGTH")
    drawer_hole_diameter: bpy.props.FloatProperty(name="Drawer hole diameter", default=0.02, min=0.00001, max=0.5,
                                                  precision=4, unit="LENGTH")
    drawer_hole_offset: bpy.props.FloatProperty(name="Drawer hole offset", default=0.0, min=-0.5, max=0.5, precision=4,
                                                unit="LENGTH")

    def execute(self, context):
        height_finger_amt = int(joinery.finger_amount(self.height, self.finger_size))
        height_finger = (self.height + 0.0004) / height_finger_amt
        width_finger_amt = int(joinery.finger_amount(self.width, self.finger_size))
        width_finger = (self.width - self.finger_size) / width_finger_amt

        # create base
        joinery.create_base_plate(self.height, self.width, self.depth)
        bpy.context.object.data.resolution_u = 64
        bpy.context.scene.cursor.location = (0, 0, 0)

        joinery.vertical_finger(height_finger, self.drawer_plate_thickness, self.finger_tolerence, height_finger_amt)

        joinery.horizontal_finger(width_finger, self.drawer_plate_thickness, self.finger_tolerence,
                                  width_finger_amt * 2)
        simple.makeActive('_wfb')

        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

        #   make drawer back
        finger_pair = joinery.finger_pair("_vfa", self.width - self.drawer_plate_thickness - self.finger_inset * 2, 0)
        simple.makeActive('_wfa')
        fronth = bpy.context.active_object
        simple.makeActive('_back')
        finger_pair.select_set(True)
        fronth.select_set(True)
        bpy.ops.object.curve_boolean(boolean_type='DIFFERENCE')
        simple.removeMultiple("_finger_pair")
        bpy.context.active_object.name = "drawer_back"
        bpy.ops.object.curve_remove_doubles()

        #   make drawer front
        bpy.ops.curve.primitive_bezier_circle_add(radius=self.drawer_hole_diameter / 2, enter_editmode=False,
                                                  align='WORLD', location=(0, self.height + self.drawer_hole_offset, 0),
                                                  scale=(1, 1, 1))
        bpy.context.active_object.name = "_circ"
        front_hole = bpy.context.active_object
        simple.makeActive('drawer_back')
        front_hole.select_set(True)
        bpy.ops.object.curve_boolean(boolean_type='DIFFERENCE')
        bpy.context.active_object.name = "drawer_front"
        bpy.ops.object.curve_remove_doubles()

        #   place back and front side by side
        simple.makeActive('drawer_front')
        bpy.ops.transform.transform(mode='TRANSLATION', value=(0.0, 2 * self.height, 0.0, 0.0))
        simple.makeActive('drawer_back')

        bpy.ops.transform.transform(mode='TRANSLATION', value=(self.width + 0.01, 2 * self.height, 0.0, 0.0))
        #   make side

        finger_pair = joinery.finger_pair("_vfb", self.depth - self.drawer_plate_thickness, 0)
        simple.makeActive('_side')
        finger_pair.select_set(True)
        fronth.select_set(True)
        bpy.ops.object.curve_boolean(boolean_type='DIFFERENCE')
        bpy.context.active_object.name = "drawer_side"
        bpy.ops.object.curve_remove_doubles()
        simple.removeMultiple('_finger_pair')

        #   make bottom
        simple.makeActive("_wfb")
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
                                      TRANSFORM_OT_translate={"value": (0, -self.drawer_plate_thickness / 2, 0.0)})

        bpy.context.active_object.name = "_wfb0"
        finger_pair = joinery.finger_pair("_wfb0", 0, self.depth - self.drawer_plate_thickness)

        simple.makeActive('_bottom')
        finger_pair.select_set(True)
        bpy.ops.object.curve_boolean(boolean_type='DIFFERENCE')

        bpy.context.active_object.name = "_bottom2"
        simple.makeActive('_bottom2')
        bpy.context.object.rotation_euler[2] = math.pi / 2

        finger_pair = joinery.finger_pair("_wfb0", 0, self.width - self.drawer_plate_thickness - self.finger_inset * 2)

        simple.makeActive('_bottom2')
        finger_pair.select_set(True)
        bpy.ops.object.curve_boolean(boolean_type='DIFFERENCE')
        bpy.context.active_object.name = "drawer_bottom"

        # cleanup all temp polygons
        simple.removeMultiple("_")

        #   move side and bottom to location
        simple.makeActive("drawer_side")
        bpy.ops.object.curve_remove_doubles()
        bpy.ops.transform.transform(mode='TRANSLATION',
                                    value=(self.depth / 2 + 3 * self.width / 2 + 0.02, 2 * self.height, 0.0, 0.0))

        simple.makeActive("drawer_bottom")
        bpy.ops.transform.transform(mode='TRANSLATION',
                                    value=(self.depth / 2 + 3 * self.width / 2 + 0.02, self.width / 2, 0.0, 0.0))
        bpy.ops.object.curve_remove_doubles()

        return {'FINISHED'}
