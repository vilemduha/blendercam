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

import subprocess, os, threading
from cam import utils, pack, polygon_utils_cam, simple,gcodepath,bridges,parametric
import cam 
import shapely
import mathutils
import math
from Equation import Expression

# boolean operations for curve objects
class CamCurveBoolean(bpy.types.Operator):
    """perform Boolean operation on two or more curves"""
    bl_idname = "object.curve_boolean"
    bl_label = "Curve Boolean"
    bl_options = {'REGISTER', 'UNDO'}

    boolean_type: EnumProperty(name='type',
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


# intarsion or joints
class CamCurveIntarsion(bpy.types.Operator):
    """makes curve cuttable both inside and outside, for intarsion and joints"""
    bl_idname = "object.curve_intarsion"
    bl_label = "Intarsion"
    bl_options = {'REGISTER', 'UNDO'}

    diameter: bpy.props.FloatProperty(name="cutter diameter", default=.001, min=0, max=100, precision=4, unit="LENGTH")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and (context.active_object.type in ['CURVE', 'FONT'])

    def execute(self, context):
        utils.silhoueteOffset(context, -self.diameter / 2)
        o1 = bpy.context.active_object

        utils.silhoueteOffset(context, self.diameter)
        o2 = bpy.context.active_object
        utils.silhoueteOffset(context, -self.diameter / 2)
        o3 = bpy.context.active_object
        o1.select_set(state=True)
        o2.select_set(state=True)
        o3.select_set(state=False)
        bpy.ops.object.delete(use_global=False)
        o3.select_set(state=True)
        return {'FINISHED'}


# intarsion or joints
class CamCurveOvercuts(bpy.types.Operator):
    """Adds overcuts for slots"""
    bl_idname = "object.curve_overcuts"
    bl_label = "Add Overcuts"
    bl_options = {'REGISTER', 'UNDO'}

    diameter: bpy.props.FloatProperty(name="diameter", default=.003, min=0, max=100, precision=4, unit="LENGTH")
    threshold: bpy.props.FloatProperty(name="threshold", default=math.pi / 2 * .99, min=-3.14, max=3.14, precision=4,
                                        subtype="ANGLE", unit="ROTATION")
    do_outer: bpy.props.BoolProperty(name="Outer polygons", default=True)
    invert: bpy.props.BoolProperty(name="Invert", default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and (context.active_object.type in ['CURVE', 'FONT'])

    def execute(self, context):
        # utils.silhoueteOffset(context,-self.diameter)
        o1 = bpy.context.active_object
        shapes = utils.curveToShapely(o1)
        negative_overcuts = []
        positive_overcuts = []
        diameter = self.diameter * 1.001
        for s in shapes:
            s = shapely.geometry.polygon.orient(s, 1)
            if s.boundary.type == 'LineString':
                loops = [s.boundary]  # s=shapely.geometry.asMultiLineString(s)
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
                            # if ci==0:
                            #	sign=-1
                            # else:
                            #	sign=1

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
                                    negative_overcuts.apppend(shape)
                                else:
                                    positive_overcuts.append(shape)

                            print(a)

        # for c in s.boundary:
        negative_overcuts = shapely.ops.unary_union(negative_overcuts)
        positive_overcuts = shapely.ops.unary_union(positive_overcuts)
        # shapes.extend(overcuts)
        fs = shapely.ops.unary_union(shapes)
        fs = fs.union(positive_overcuts)
        fs = fs.difference(negative_overcuts)
        o = utils.shapelyToCurve(o1.name + '_overcuts', fs, o1.location.z)
        # o=utils.shapelyToCurve('overcuts',overcuts,0)
        return {'FINISHED'}


# Overcut type B
class CamCurveOvercutsB(bpy.types.Operator):
    """Adds overcuts for slots"""
    bl_idname = "object.curve_overcuts_b"
    bl_label = "Add Overcuts-B"
    bl_options = {'REGISTER', 'UNDO'}

    diameter: bpy.props.FloatProperty(name="Tool diameter", default=.003,
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
        diameter = self.diameter * 1.001
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
            if abs(a) < math.pi / 2:
                shape = utils.Circle(radius, 64)
                shape = shapely.affinity.translate(shape, pos.x, pos.y)
            else:  # elongate overcut circle to make sure tool bit can fit into slot
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
            s = shapely.geometry.polygon.orient(s, 1)
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
                        # print(cornerCnt, len(insideCorners))
                        # process all of the inside corners
                        for i, corner in enumerate(insideCorners):
                            pos, v1, v2, a, idx = corner
                            # figure out which side of the corner to do overcut
                            # if prev corner is outside corner
                            # calc index distance between current corner and prev
                            prevCorner = getCorner(i, -1)
                            # print('first:', i, idx, prevCorner[IDX])
                            if getCornerDelta(prevCorner[IDX], idx) == 1:
                                # make sure there is an outside corner
                                # print(getCornerDelta(getCorner(i, -2)[IDX], idx))
                                if getCornerDelta(getCorner(i, -2)[IDX], idx) > 2:
                                    setOtherEdge(v1, v2, a)
                                    # print('first won')
                                    continue

                            nextCorner = getCorner(i, 1)
                            # print('second:', i, idx, nextCorner[IDX])
                            if getCornerDelta(idx, nextCorner[IDX]) == 1:
                                # make sure there is an outside corner
                                # print(getCornerDelta(idx, getCorner(i, 2)[IDX]))
                                if getCornerDelta(idx, getCorner(i, 2)[IDX]) > 2:
                                    # print('second won')
                                    setOtherEdge(-v2, -v1, a)
                                    continue

                            # print('third')
                            if getCornerDelta(prevCorner[IDX], idx) == 3:
                                # check if they share the same edge
                                a1 = v1.angle_signed(prevCorner[V2]) * 180.0 / math.pi
                                # print('third won', a1)
                                if a1 < -135 or a1 > 135:
                                    setOtherEdge(-v2, -v1, a)
                                    continue

                            # print('fourth')
                            if getCornerDelta(idx, nextCorner[IDX]) == 3:
                                # check if they share the same edge
                                a1 = v2.angle_signed(nextCorner[V1]) * 180.0 / math.pi
                                # print('fourth won', a1)
                                if a1 < -135 or a1 > 135:
                                    setOtherEdge(v1, v2, a)
                                    continue

                            # print('***No Win***')
                            # the default if no other rules pass
                            setCenterOffset(a)

        negative_overcuts = shapely.ops.unary_union(negative_overcuts)
        positive_overcuts = shapely.ops.unary_union(positive_overcuts)
        fs = shapely.ops.unary_union(shapes)
        fs = fs.union(positive_overcuts)
        fs = fs.difference(negative_overcuts)
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
                    #n = mw @ face.normal
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
    bl_options = {'REGISTER', 'UNDO'}

    offset: bpy.props.FloatProperty(name="offset", default=.003, min=-100, max=100, precision=4, unit="LENGTH")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and (
                    context.active_object.type == 'CURVE' or context.active_object.type == 'FONT' or context.active_object.type == 'MESH')

    def execute(self, context):  # this is almost same as getobjectoutline, just without the need of operation data
        utils.silhoueteOffset(context, self.offset)
        return {'FINISHED'}


# Finds object silhouette, usefull for meshes, since with curves it's not needed.
class CamObjectSilhouete(bpy.types.Operator):
    """Object silhouete """
    bl_idname = "object.silhouete"
    bl_label = "Object silhouete"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
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
        

class CamSineCurve(bpy.types.Operator):
    """Object silhouete """
    bl_idname = "object.sine"
    bl_label = "Create Sine"
    bl_options = {'REGISTER', 'UNDO'}


#    zstring: StringProperty(name="Z equation", description="Equation for z=F(u,v)", default="0.05*sin(2*pi*4*t)" )
    axis: bpy.props.EnumProperty(name="displacement axis",items=(('XY', 'Y to displace X axis', 'Y constant; X sine displacement'),('YX', 'X to displace Y axis', 'X constant; Y sine displacement'),('ZX', 'X to displace Z axis', 'X constant; Y sine displacement'),('ZY', 'Y to displace Z axis', 'X constant; Y sine displacement')))
    amplitude: bpy.props.FloatProperty(name="Amplitude", default=.01, min=0, max=10, precision=4, unit="LENGTH")
    period: bpy.props.FloatProperty(name="Period", default=.5, min=0.001, max=100, precision=4, unit="LENGTH")
    shift: bpy.props.FloatProperty(name="phase shift", default=0, min=-360, max=360, precision=4, unit="ROTATION")
    offset: bpy.props.FloatProperty(name="offset", default=0, min=-1.0, max=1, precision=4, unit="LENGTH")
    iteration: bpy.props.IntProperty(name="iteration", default=100, min=50, max=2000)
    maxt: bpy.props.FloatProperty(name="Wave ends at x", default=0.5, min=-3.0, max=3, precision=4, unit="LENGTH")
    mint: bpy.props.FloatProperty(name="Wave starts at x", default=0, min=-3.0, max=3, precision=4, unit="LENGTH")

   
    def execute(self, context):  
        
        #z=Asin(B(x+C))+D

        zstring=str(round(self.offset,6)) + "+" + str(round(self.amplitude,6)) +"*sin((2*pi/" + str(round(self.period,6)) +")*(t+"+str(round(self.shift,6))+"))"
        print(zstring)
        e=Expression(zstring,["t"])  #make equation from string
        
        #build function to be passed to create parametric curve ()
        def f(t, offset: float = 0.0):
           if self.axis == "XY":
               c = (e(t),t,0)
           elif self.axis == "YX":        
               c = (t,e(t),0)
           elif self.axis == "ZX":        
               c = (t,0,e(t))               
           elif self.axis == "ZY":        
               c = (0,t,e(t))               
           return c
            
        parametric.create_parametric_curve(f, offset=0.0, min=self.mint, max=self.maxt, use_cubic=True, iterations=self.iteration)        
        
        return {'FINISHED'}

class CamLissajousCurve(bpy.types.Operator):
    """Object silhouete """
    bl_idname = "object.lissajous"
    bl_label = "Create Lissajous figure"
    bl_options = {'REGISTER', 'UNDO'}



    amplitude_A: bpy.props.FloatProperty(name="Amplitude A", default=.1, min=0, max=100, precision=4, unit="LENGTH")
    amplitude_B: bpy.props.FloatProperty(name="Amplitude B", default=.1, min=0, max=100, precision=4, unit="LENGTH")
    period_A: bpy.props.FloatProperty(name="Period A", default=1.1, min=0.001, max=100, precision=4, unit="LENGTH")
    period_B: bpy.props.FloatProperty(name="Period B", default=1.0, min=0.001, max=100, precision=4, unit="LENGTH")
    shift: bpy.props.FloatProperty(name="phase shift", default=0, min=-360, max=360, precision=4, unit="ROTATION")

    iteration: bpy.props.IntProperty(name="iteration", default=500, min=50, max=10000)
    maxt: bpy.props.FloatProperty(name="Wave ends at x", default=11, min=-3.0, max=1000000, precision=4, unit="LENGTH")
    mint: bpy.props.FloatProperty(name="Wave starts at x", default=0, min=-10.0, max=3, precision=4, unit="LENGTH")

   
    def execute(self, context):  
        
        #x=Asin(at+delta ),y=Bsin(bt)

        xstring=str(round(self.amplitude_A,6)) +"*sin((2*pi/" + str(round(self.period_A,6)) +")*(t+"+str(round(self.shift,6))+"))"
        ystring=str(round(self.amplitude_B,6)) +"*sin((2*pi/" + str(round(self.period_B,6)) +")*(t))"
        print("x= "+str(xstring))
        print("y= "+str(ystring))
        x=Expression(xstring,["t"])  #make equation from string
        y=Expression(ystring,["t"])  #make equation from string
        
        #build function to be passed to create parametric curve ()
        def f(t, offset: float = 0.0):
           c = (x(t),y(t),0)
           return c
            
        parametric.create_parametric_curve(f, offset=0.0, min=self.mint, max=self.maxt, use_cubic=True, iterations=self.iteration)        
        
        return {'FINISHED'}

