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

from cam import utils, pack, polygon_utils_cam, simple, gcodepath, bridges, parametric, gcodeimportparser, joinery
import shapely
from shapely.geometry import Point, LineString, Polygon
import mathutils
import math
from Equation import Expression
import numpy as np


# boolean operations for curve objects
class CamCurveBoolean(bpy.types.Operator):
    """perform Boolean operation on two or more curves"""
    bl_idname = "object.curve_boolean"
    bl_label = "Curve Boolean"
    bl_options = {'REGISTER', 'UNDO'}

    boolean_type: bpy.props.EnumProperty(name='type',
                                         items=(('UNION', 'Union', ''), ('DIFFERENCE', 'Difference', ''),
                                                ('INTERSECT', 'Intersect', '')),
                                         description='boolean type',
                                         default='UNION')

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type in ['CURVE', 'FONT']

    def execute(self, context):
        if len(context.selected_objects) > 1:
            utils.polygonBoolean(context, self.boolean_type)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, 'at least 2 curves must be selected')
            return {'CANCELLED'}


class CamCurveConvexHull(bpy.types.Operator):
    """perform hull operation on single or multiple curves"""  # by Alain Pelletier april 2021
    bl_idname = "object.convex_hull"
    bl_label = "Convex Hull"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type in ['CURVE', 'FONT']

    def execute(self, context):
        utils.polygonConvexHull(context)
        return {'FINISHED'}


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
        diameter = 2 * self.radius
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

        return {'FINISHED'}


class CamCurveMortise(bpy.types.Operator):
    """Generates mortise along a curve"""  # by Alain Pelletier December 2021
    bl_idname = "object.curve_mortise"
    bl_label = "Mortise"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    finger_size: bpy.props.FloatProperty(name="Maximum Finger Size", default=0.015, min=0.005, max=3.0, precision=4,
                                         unit="LENGTH")
    finger_tolerence: bpy.props.FloatProperty(name="Finger play room", default=0.000045, min=0, max=0.003, precision=4,
                                              unit="LENGTH")
    plate_thickness: bpy.props.FloatProperty(name="Drawer plate thickness", default=0.00477, min=0.001, max=3.0,unit="LENGTH")
    side_height: bpy.props.FloatProperty(name="side height", default=0.05, min=0.001, max=3.0,unit="LENGTH")
    flex_pocket: bpy.props.FloatProperty(name="Flex pocket", default=0.004, min=0.000, max=1.0,unit="LENGTH")
    top_bottom: bpy.props.BoolProperty(name="Side Top & bottom fingers", default=True)
    opencurve: bpy.props.BoolProperty(name="OpenCurve", default=False)


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
        cp = (0, 0)

        if self.opencurve:
            coords = []
            for v in obj.data.vertices:  # extract X,Y coordinates from the vertices data
                coords.append((v.co.x, v.co.y))
            line = LineString(coords)  # convert coordinates to shapely LineString datastructure
            print("line length=", round(line.length * 1000), 'mm')

        shapes = utils.curveToShapely(o1)

        for s in shapes:
            if s.boundary.type == 'LineString':
                loops = [s.boundary]
            else:
                loops = s.boundary

            for ci, c in enumerate(loops):
                loop_length = c.length
                print("loop Length:", loop_length)
                j = 0
                distance = self.finger_size / 2
                oldp = (0, 0)
                coords = list(c.coords)
                if self.opencurve:
                    loop_length = line.length
                else:
                    loop_length = c.length
                print("line Length:", loop_length)
                for i, p in enumerate(coords):
                    if i == 0:

                        p_start = p

                    if p != p_start:
                        not_start = True
                    else:
                        not_start = False

                    pd = c.project(Point(p))
                    if not_start:
                        while distance <= pd:
                            mortise_point = c.interpolate(distance)
                            p_difference = (p[0]-oldp[0],p[1]-oldp[1])
                            joinery.mortise(self.finger_size,self.plate_thickness,self.finger_tolerence,mortise_point.x, mortise_point.y, math.atan2(p_difference[1], p_difference[0]))
                            bpy.context.active_object.name = "_mortise"
                            j += 1
                            distance = j * 2 * self.finger_size + self.finger_size/2
                    oldp = p
            simple.joinMultiple("_mort")
            bpy.context.active_object.name = "mortise"
            joinery.create_flex_side(loop_length, self.side_height, self.finger_size, self.plate_thickness, self.finger_tolerence,self.top_bottom,self.flex_pocket)
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

        #   make drawer front
        bpy.ops.curve.primitive_bezier_circle_add(radius=self.drawer_hole_diameter / 2, enter_editmode=False,
                                                  align='WORLD', location=(0, self.height + self.drawer_hole_offset, 0),
                                                  scale=(1, 1, 1))
        bpy.context.active_object.name = "_circ"
        front_hole = bpy.context.active_object
        simple.makeActive('drawer_back')
        bpy.ops.object.curve_remove_doubles()
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


# intarsion or joints
class CamCurveIntarsion(bpy.types.Operator):
    """makes curve cuttable both inside and outside, for intarsion and joints"""
    bl_idname = "object.curve_intarsion"
    bl_label = "Intarsion"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    diameter: bpy.props.FloatProperty(name="cutter diameter", default=.001, min=0, max=0.025, precision=4,
                                      unit="LENGTH")
    tolerance: bpy.props.FloatProperty(name="cutout Tolerance", default=.0001, min=0, max=0.005, precision=4,
                                       unit="LENGTH")
    backlight: bpy.props.FloatProperty(name="Backlight seat", default=0.000, min=0, max=0.010, precision=4,
                                       unit="LENGTH")
    perimeter_cut: bpy.props.FloatProperty(name="Perimeter cut offset", default=0.000, min=0, max=0.100, precision=4,
                                           unit="LENGTH")
    base_thickness: bpy.props.FloatProperty(name="Base material thickness", default=0.000, min=0, max=0.100,
                                            precision=4, unit="LENGTH")
    intarsion_thickness: bpy.props.FloatProperty(name="Intarsion material thickness", default=0.000, min=0, max=0.100,
                                                 precision=4, unit="LENGTH")
    backlight_depth_from_top: bpy.props.FloatProperty(name="Backlight well depth", default=0.000, min=0, max=0.100,
                                                      precision=4, unit="LENGTH")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and (context.active_object.type in ['CURVE', 'FONT'])

    def execute(self, context):
        selected = context.selected_objects  # save original selected items
        scene = bpy.context.scene

        simple.removeMultiple('intarsion_')

        for ob in selected: ob.select_set(True)  # select original curves

        #  Perimeter cut largen then intarsion pocket externally, optional

        diam = self.diameter * 1.05 + self.backlight * 2  # make the diameter 5% larger and compensate for backlight
        utils.silhoueteOffset(context, -diam / 2)

        o1 = bpy.context.active_object
        utils.silhoueteOffset(context, diam)
        o2 = bpy.context.active_object
        utils.silhoueteOffset(context, -diam / 2)
        o3 = bpy.context.active_object
        o1.select_set(True)
        o2.select_set(True)
        o3.select_set(False)
        bpy.ops.object.delete(use_global=False)  # delete o1 and o2 temporary working curves
        o3.name = "intarsion_pocket"  # this is the pocket for intarsion
        bpy.context.object.location[2] = -self.intarsion_thickness

        if self.perimeter_cut > 0.0:
            utils.silhoueteOffset(context, self.perimeter_cut)
            bpy.context.active_object.name = "intarsion_perimeter"
            bpy.context.object.location[2] = -self.base_thickness
            bpy.ops.object.select_all(action='DESELECT')  # deselect new curve

        o3.select_set(True)
        context.view_layer.objects.active = o3
        #   intarsion profile is the inside piece of the intarsion
        utils.silhoueteOffset(context, -self.tolerance / 2)  # make smaller curve for material profile
        bpy.context.object.location[2] = self.intarsion_thickness
        o4 = bpy.context.active_object
        bpy.context.active_object.name = "intarsion_profil"
        o4.select_set(False)

        if self.backlight > 0.0:  # Make a smaller curve for backlighting purposes
            utils.silhoueteOffset(context, (-self.tolerance / 2) - self.backlight)
            bpy.context.active_object.name = "intarsion_backlight"
            bpy.context.object.location[2] = -self.backlight_depth_from_top - self.intarsion_thickness
            o4.select_set(True)
        o3.select_set(True)
        return {'FINISHED'}


# intarsion or joints
class CamCurveOvercuts(bpy.types.Operator):
    """Adds overcuts for slots"""
    bl_idname = "object.curve_overcuts"
    bl_label = "Add Overcuts"
    bl_options = {'REGISTER', 'UNDO'}

    diameter: bpy.props.FloatProperty(name="diameter", default=.003175, min=0, max=100, precision=4, unit="LENGTH")
    threshold: bpy.props.FloatProperty(name="threshold", default=math.pi / 2 * .99, min=-3.14, max=3.14, precision=4,
                                       subtype="ANGLE", unit="ROTATION")
    do_outer: bpy.props.BoolProperty(name="Outer polygons", default=True)
    invert: bpy.props.BoolProperty(name="Invert", default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and (context.active_object.type in ['CURVE', 'FONT'])

    def execute(self, context):
        o1 = bpy.context.active_object
        shapes = utils.curveToShapely(o1)
        negative_overcuts = []
        positive_overcuts = []
        diameter = self.diameter * 1.001
        for s in shapes:
            s = shapely.geometry.polygon.orient(s, 1)
            if s.boundary.type == 'LineString':
                loops = [s.boundary]
            else:
                loops = s.boundary

            for ci, c in enumerate(loops):
                if ci > 0 or self.do_outer:
                    # c=s.boundary
                    for i, co in enumerate(c.coords):
                        i1 = i - 1
                        if i1 == -1:
                            i1 = -2
                        i2 = i + 1
                        if i2 == len(c.coords):
                            i2 = 0

                        v1 = mathutils.Vector(co) - mathutils.Vector(c.coords[i1])
                        v1 = v1.xy  # Vector((v1.x,v1.y,0))
                        v2 = mathutils.Vector(c.coords[i2]) - mathutils.Vector(co)
                        v2 = v2.xy  # v2 = Vector((v2.x,v2.y,0))
                        if not v1.length == 0 and not v2.length == 0:
                            a = v1.angle_signed(v2)
                            sign = 1

                            if self.invert:  # and ci>0:
                                sign *= -1
                            if (sign < 0 and a < -self.threshold) or (sign > 0 and a > self.threshold):
                                p = mathutils.Vector((co[0], co[1]))
                                v1.normalize()
                                v2.normalize()
                                v = v1 - v2
                                v.normalize()
                                p = p - v * diameter / 2
                                if abs(a) < math.pi / 2:
                                    shape = utils.Circle(diameter / 2, 64)
                                    shape = shapely.affinity.translate(shape, p.x, p.y)
                                else:
                                    l = math.tan(a / 2) * diameter / 2
                                    p1 = p - sign * v * l
                                    l = shapely.geometry.LineString((p, p1))
                                    shape = l.buffer(diameter / 2, resolution=64)

                                if sign > 0:
                                    negative_overcuts.append(shape)
                                else:
                                    positive_overcuts.append(shape)

                            print(a)

        negative_overcuts = shapely.ops.unary_union(negative_overcuts)
        positive_overcuts = shapely.ops.unary_union(positive_overcuts)

        fs = shapely.ops.unary_union(shapes)
        fs = fs.union(positive_overcuts)
        fs = fs.difference(negative_overcuts)
        o = utils.shapelyToCurve(o1.name + '_overcuts', fs, o1.location.z)
        return {'FINISHED'}


# Overcut type B
class CamCurveOvercutsB(bpy.types.Operator):
    """Adds overcuts for slots"""
    bl_idname = "object.curve_overcuts_b"
    bl_label = "Add Overcuts-B"
    bl_options = {'REGISTER', 'UNDO'}

    diameter: bpy.props.FloatProperty(name="Tool diameter", default=.003175,
                                      description='Tool bit diameter used in cut operation', min=0, max=100,
                                      precision=4, unit="LENGTH")
    style: bpy.props.EnumProperty(
        name="style",
        items=(('OPEDGE', 'opposite edge', 'place corner overcuts on opposite edges'),
               ('DOGBONE', 'Dog-bone / Corner Point', 'place overcuts at center of corners'),
               ('TBONE', 'T-bone', 'place corner overcuts on the same edge')),
        default='DOGBONE',
        description='style of overcut to use')
    threshold: bpy.props.FloatProperty(name="Max Inside Angle", default=math.pi / 2, min=-3.14, max=3.14,
                                       description='The maximum angle to be considered as an inside corner',
                                       precision=4, subtype="ANGLE", unit="ROTATION")
    do_outer: bpy.props.BoolProperty(name="Include outer curve",
                                     description='Include the outer curve if there are curves inside', default=True)
    do_invert: bpy.props.BoolProperty(name="Invert", description='invert overcut operation on all curves',
                                      default=True)
    otherEdge: bpy.props.BoolProperty(name="other edge",
                                      description='change to the other edge for the overcut to be on', default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'CURVE'

    def execute(self, context):
        o1 = bpy.context.active_object
        shapes = utils.curveToShapely(o1)
        negative_overcuts = []
        positive_overcuts = []
        # count all the corners including inside and out
        cornerCnt = 0
        # a list of tuples for defining the inside corner
        # tuple is: (pos, v1, v2, angle, allCorners list index)
        insideCorners = []
        diameter = self.diameter * 1.002  # make bit size slightly larger to allow cutter
        radius = diameter / 2
        anglethreshold = math.pi - self.threshold
        centerv = mathutils.Vector((0, 0))
        extendedv = mathutils.Vector((0, 0))
        pos = mathutils.Vector((0, 0))
        sign = -1 if self.do_invert else 1
        isTBone = self.style == 'TBONE'
        # indexes in insideCorner tuple
        POS, V1, V2, A, IDX = range(5)

        def addOvercut(a):
            nonlocal pos, centerv, radius, extendedv, sign, negative_overcuts, positive_overcuts
            # move the overcut shape center position 1 radius in direction v
            pos -= centerv * radius
            print("abs(a)", abs(a))
            if abs(a) <= math.pi / 2 + 0.0001:
                print("<=pi/2")
                shape = utils.Circle(radius, 64)
                shape = shapely.affinity.translate(shape, pos.x, pos.y)
            else:  # elongate overcut circle to make sure tool bit can fit into slot
                print(">pi/2")
                p1 = pos + (extendedv * radius)
                l = shapely.geometry.LineString((pos, p1))
                shape = l.buffer(radius, resolution=64)

            if sign > 0:
                negative_overcuts.append(shape)
            else:
                positive_overcuts.append(shape)

        def setOtherEdge(v1, v2, a):
            nonlocal centerv, extendedv
            if self.otherEdge:
                centerv = v1
                extendedv = v2
            else:
                centerv = -v2
                extendedv = -v1
            addOvercut(a)

        def setCenterOffset(a):
            nonlocal centerv, extendedv, sign
            centerv = v1 - v2
            centerv.normalize()
            extendedv = centerv * math.tan(a / 2) * -sign
            addOvercut(a)

        def getCorner(idx, offset):
            nonlocal insideCorners
            idx += offset
            if idx >= len(insideCorners):
                idx -= len(insideCorners)
            return insideCorners[idx]

        def getCornerDelta(curidx, nextidx):
            nonlocal cornerCnt
            delta = nextidx - curidx
            if delta < 0:
                delta += cornerCnt
            return delta

        for s in shapes:
            s = shapely.geometry.polygon.orient(s, 1)  # ensure the shape is counterclockwise
            loops = [s.boundary] if s.boundary.type == 'LineString' else s.boundary
            outercurve = self.do_outer or len(loops) == 1
            for ci, c in enumerate(loops):
                if ci > 0 or outercurve:
                    if isTBone:
                        cornerCnt = 0
                        insideCorners = []

                    for i, co in enumerate(c.coords):
                        i1 = i - 1
                        if i1 == -1:
                            i1 = -2
                        i2 = i + 1
                        if i2 == len(c.coords):
                            i2 = 0

                        v1 = mathutils.Vector(co).xy - mathutils.Vector(c.coords[i1]).xy
                        v2 = mathutils.Vector(c.coords[i2]).xy - mathutils.Vector(co).xy

                        if not v1.length == 0 and not v2.length == 0:
                            a = v1.angle_signed(v2)
                            insideCornerFound = False
                            outsideCornerFound = False
                            if a < -anglethreshold:
                                if sign < 0:
                                    insideCornerFound = True
                                else:
                                    outsideCornerFound = True
                            elif a > anglethreshold:
                                if sign > 0:
                                    insideCornerFound = True
                                else:
                                    outsideCornerFound = True

                            if insideCornerFound:
                                # an inside corner with an overcut has been found
                                # which means a new side has been found
                                pos = mathutils.Vector((co[0], co[1]))
                                v1.normalize()
                                v2.normalize()
                                # figure out which direction vector to use
                                # v is the main direction vector to move the overcut shape along
                                # ev is the direction vector used to elongate the overcut shape
                                if self.style != 'DOGBONE':
                                    # t-bone and opposite edge styles get treated nearly the same
                                    if isTBone:
                                        cornerCnt += 1
                                        # insideCorner tuplet: (pos, v1, v2, angle, corner index)
                                        insideCorners.append((pos, v1, v2, a, cornerCnt - 1))
                                        # processing of corners for T-Bone are done after all points are processed
                                        continue

                                    setOtherEdge(v1, v2, a)

                                else:  # DOGBONE style
                                    setCenterOffset(a)

                            elif isTBone and outsideCornerFound:
                                # add an outside corner to the list
                                cornerCnt += 1

                    # check if t-bone processing required
                    # if no inside corners then nothing to do
                    if isTBone and len(insideCorners) > 0:
                        print("corner count", cornerCnt, "inside corner count", len(insideCorners))
                        # process all of the inside corners
                        for i, corner in enumerate(insideCorners):
                            pos, v1, v2, a, idx = corner
                            # figure out which side of the corner to do overcut
                            # if prev corner is outside corner
                            # calc index distance between current corner and prev
                            prevCorner = getCorner(i, -1)
                            print('first:', i, idx, prevCorner[IDX])
                            if getCornerDelta(prevCorner[IDX], idx) == 1:
                                # make sure there is an outside corner
                                print(getCornerDelta(getCorner(i, -2)[IDX], idx))
                                if getCornerDelta(getCorner(i, -2)[IDX], idx) > 2:
                                    setOtherEdge(v1, v2, a)
                                    print('first won')
                                    continue

                            nextCorner = getCorner(i, 1)
                            print('second:', i, idx, nextCorner[IDX])
                            if getCornerDelta(idx, nextCorner[IDX]) == 1:
                                # make sure there is an outside corner
                                print(getCornerDelta(idx, getCorner(i, 2)[IDX]))
                                if getCornerDelta(idx, getCorner(i, 2)[IDX]) > 2:
                                    print('second won')
                                    setOtherEdge(-v2, -v1, a)
                                    continue

                            print('third')
                            if getCornerDelta(prevCorner[IDX], idx) == 3:
                                # check if they share the same edge
                                a1 = v1.angle_signed(prevCorner[V2]) * 180.0 / math.pi
                                print('third won', a1)
                                if a1 < -135 or a1 > 135:
                                    setOtherEdge(-v2, -v1, a)
                                    continue

                            print('fourth')
                            if getCornerDelta(idx, nextCorner[IDX]) == 3:
                                # check if they share the same edge
                                a1 = v2.angle_signed(nextCorner[V1]) * 180.0 / math.pi
                                print('fourth won', a1)
                                if a1 < -135 or a1 > 135:
                                    setOtherEdge(v1, v2, a)
                                    continue

                            print('***No Win***')
                            # the default if no other rules pass
                            setCenterOffset(a)

        negative_overcuts = shapely.ops.unary_union(negative_overcuts)
        positive_overcuts = shapely.ops.unary_union(positive_overcuts)
        fs = shapely.ops.unary_union(shapes)
        fs = fs.union(positive_overcuts)
        fs = fs.difference(negative_overcuts)
        #        utils.shapelyToCurve(o1.name + '_overcuts', positive_overcuts, o1.location.z)
        #        utils.shapelyToCurve(o1.name + '_overcuts', negative_overcuts, o1.location.z)
        o = utils.shapelyToCurve(o1.name + '_overcuts', fs, o1.location.z)
        return {'FINISHED'}


class CamCurveRemoveDoubles(bpy.types.Operator):
    """curve remove doubles - warning, removes beziers!"""
    bl_idname = "object.curve_remove_doubles"
    bl_label = "C-Remove doubles"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and (context.active_object.type == 'CURVE')

    def execute(self, context):
        obs = bpy.context.selected_objects
        for ob in obs:
            bpy.context.view_layer.objects.active = ob

            mode = False
            if bpy.context.mode == 'EDIT_CURVE':
                bpy.ops.object.editmode_toggle()
                mode = True
            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='TOGGLE')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.convert(target='CURVE')
            a = bpy.context.active_object
            # a.data.show_normal_face = False
            if mode:
                bpy.ops.object.editmode_toggle()

        return {'FINISHED'}


class CamMeshGetPockets(bpy.types.Operator):
    """Detect pockets in a mesh and extract them as curves"""
    bl_idname = "object.mesh_get_pockets"
    bl_label = "Get pocket surfaces"
    bl_options = {'REGISTER', 'UNDO'}

    threshold: bpy.props.FloatProperty(name="horizontal threshold",
                                       description="How horizontal the surface must be for a pocket: 1.0 perfectly flat, 0.0 is any orientation",
                                       default=.99, min=0, max=1.0, precision=4)
    zlimit: bpy.props.FloatProperty(name="z limit",
                                    description="maximum z height considered for pocket operation, default is 0.0",
                                    default=0.0, min=-1000.0, max=1000.0, precision=4, unit='LENGTH')

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and (context.active_object.type == 'MESH')

    def execute(self, context):
        obs = bpy.context.selected_objects
        s = bpy.context.scene
        cobs = []
        for ob in obs:
            if ob.type == 'MESH':
                pockets = {}
                mw = ob.matrix_world
                mesh = ob.data
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.editmode_toggle()
                i = 0
                for face in mesh.polygons:
                    # n = mw @ face.normal
                    n = face.normal.to_4d()
                    n.w = 0
                    n = (mw @ n).to_3d().normalized()
                    if n.z > self.threshold:
                        face.select = True
                        z = (mw @ mesh.vertices[face.vertices[0]].co).z
                        if z < self.zlimit:
                            if pockets.get(z) == None:
                                pockets[z] = [i]
                            else:
                                pockets[z].append(i)
                    i += 1
                print(len(pockets))
                for p in pockets:
                    print(p)
                ao = bpy.context.active_object
                i = 0
                for p in pockets:
                    print(i)
                    i += 1

                    sf = pockets[p]
                    for face in mesh.polygons:
                        face.select = False

                    for fi in sf:
                        face = mesh.polygons[fi]
                        face.select = True

                    bpy.ops.object.editmode_toggle()

                    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                    bpy.ops.mesh.region_to_loop()
                    bpy.ops.mesh.separate(type='SELECTED')

                    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
                    bpy.ops.object.editmode_toggle()
                    ao.select_set(state=False)
                    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
                    cobs.append(bpy.context.selected_objects[0])
                    bpy.ops.object.convert(target='CURVE')
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

                    bpy.context.selected_objects[0].select_set(False)
                    ao.select_set(state=True)
                    bpy.context.view_layer.objects.active = ao
            # bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')

            # turn off selection of all objects in 3d view
            bpy.ops.object.select_all(action='DESELECT')
            # make new curves more visible by making them selected in the 3d view
            # This also allows the active object to still work with the operator
            # if the user decides to change the horizontal threshold property
            col = bpy.data.collections.new('multi level pocket ')
            s.collection.children.link(col)
            for obj in cobs:
                col.objects.link(obj)

        return {'FINISHED'}


# this operator finds the silhouette of objects(meshes, curves just get converted) and offsets it.
class CamOffsetSilhouete(bpy.types.Operator):
    """Curve offset operation """
    bl_idname = "object.silhouete_offset"
    bl_label = "Silhouete offset"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    offset: bpy.props.FloatProperty(name="offset", default=.003, min=-100, max=100, precision=4, unit="LENGTH")
    mitrelimit: bpy.props.FloatProperty(name="Mitre Limit", default=.003, min=0.0, max=20, precision=4, unit="LENGTH")
    style: bpy.props.EnumProperty(name="type of curve", items=(
        ('1', 'Round', ''), ('2', 'Mitre', ''), ('3', 'Bevel', '')))
    opencurve: bpy.props.BoolProperty(name="Dialate open curve", default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and (
                context.active_object.type == 'CURVE' or context.active_object.type == 'FONT' or context.active_object.type == 'MESH')

    def execute(self, context):  # this is almost same as getobjectoutline, just without the need of operation data
        ob = context.active_object
        if self.opencurve and ob.type == 'CURVE':
            bpy.ops.object.duplicate()
            obj = context.active_object
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)  # apply all transforms
            bpy.context.object.data.resolution_u = 60
            bpy.ops.object.convert(target='MESH')
            bpy.context.active_object.name = "temp_mesh"

            coords = []
            for v in obj.data.vertices:  # extract X,Y coordinates from the vertices data
                coords.append((v.co.x, v.co.y))

            simple.removeMultiple('temp_mesh')  # delete temporary mesh
            simple.removeMultiple('dilation')  # delete old dilation objects

            line = LineString(coords)  # convert coordinates to shapely LineString datastructure
            print("line length=", round(line.length * 1000), 'mm')

            dilated = line.buffer(self.offset, cap_style=1, resolution=16,
                                  mitre_limit=self.mitrelimit)  # use shapely to expand
            polygon_utils_cam.shapelyToCurve("dilation", dilated, 0)
        else:
            utils.silhoueteOffset(context, self.offset, int(self.style), self.mitrelimit)
        return {'FINISHED'}


# Finds object silhouette, usefull for meshes, since with curves it's not needed.
class CamObjectSilhouete(bpy.types.Operator):
    """Object silhouete """
    bl_idname = "object.silhouete"
    bl_label = "Object silhouete"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        #        return context.active_object is not None and (context.active_object.type == 'CURVE' or context.active_object.type == 'FONT' or context.active_object.type == 'MESH')
        return context.active_object is not None and (context.active_object.type == 'MESH')

    def execute(self, context):  # this is almost same as getobjectoutline, just without the need of operation data
        ob = bpy.context.active_object
        self.silh = utils.getObjectSilhouete('OBJECTS', objects=bpy.context.selected_objects)
        bpy.context.scene.cursor.location = (0, 0, 0)
        # smp=sgeometry.asMultiPolygon(self.silh)
        for smp in self.silh:
            polygon_utils_cam.shapelyToCurve(ob.name + '_silhouette', smp, 0)  #
        # bpy.ops.object.convert(target='CURVE')
        bpy.context.scene.cursor.location = ob.location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        return {'FINISHED'}

# ---------------------------------------------------
