"""Fabex 'curve_cam_tools.py' © 2012 Vilem Novak, 2021 Alain Pelletier

Operators that perform various functions on existing curves.
"""

from math import pi, tan

import shapely
from shapely.geometry import (
    LineString,
    MultiLineString,
)

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
)
from bpy.types import Operator
from mathutils import Vector

from ..cam_chunk import (
    curve_to_shapely,
    polygon_boolean,
    polygon_convex_hull,
    silhouette_offset,
    get_object_silhouette,
)

from ..utilities.geom_utils import circle
from ..utilities.shapely_utils import (
    shapely_to_curve,
)
from ..utilities.simple_utils import (
    remove_multiple,
    join_multiple,
)


# boolean operations for curve objects
class CamCurveBoolean(Operator):
    """Perform Boolean Operation on Two or More Curves"""

    bl_idname = "object.curve_boolean"
    bl_label = "Curve Boolean"
    bl_options = {"REGISTER", "UNDO"}

    boolean_type: EnumProperty(
        name="Type",
        items=(
            ("UNION", "Union", ""),
            ("DIFFERENCE", "Difference", ""),
            ("INTERSECT", "Intersect", ""),
        ),
        description="Boolean type",
        default="UNION",
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type in ["CURVE", "FONT"]

    def execute(self, context):
        if len(context.selected_objects) > 1:
            polygon_boolean(context, self.boolean_type)
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, "at least 2 curves must be selected")
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CamCurveConvexHull(Operator):
    """Perform Hull Operation on Single or Multiple Curves"""  # by Alain Pelletier april 2021

    bl_idname = "object.convex_hull"
    bl_label = "Convex Hull"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type in ["CURVE", "FONT"]

    def execute(self, context):
        polygon_convex_hull(context)
        return {"FINISHED"}


# intarsion or joints
class CamCurveIntarsion(Operator):
    """Makes Curve Cuttable Both Inside and Outside, for Intarsion and Joints"""

    bl_idname = "object.curve_intarsion"
    bl_label = "Intarsion"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    diameter: FloatProperty(
        name="Cutter Diameter",
        default=0.001,
        min=0,
        max=0.025,
        precision=4,
        unit="LENGTH",
    )
    tolerance: FloatProperty(
        name="Cutout Tolerance",
        default=0.0001,
        min=0,
        max=0.005,
        precision=4,
        unit="LENGTH",
    )
    backlight: FloatProperty(
        name="Backlight Seat",
        default=0.000,
        min=0,
        max=0.010,
        precision=4,
        unit="LENGTH",
    )
    perimeter_cut: FloatProperty(
        name="Perimeter Cut Offset",
        default=0.000,
        min=0,
        max=0.100,
        precision=4,
        unit="LENGTH",
    )
    base_thickness: FloatProperty(
        name="Base Material Thickness",
        default=0.000,
        min=0,
        max=0.100,
        precision=4,
        unit="LENGTH",
    )
    intarsion_thickness: FloatProperty(
        name="Intarsion Material Thickness",
        default=0.000,
        min=0,
        max=0.100,
        precision=4,
        unit="LENGTH",
    )
    backlight_depth_from_top: FloatProperty(
        name="Backlight Well Depth",
        default=0.000,
        min=0,
        max=0.100,
        precision=4,
        unit="LENGTH",
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and (
            context.active_object.type in ["CURVE", "FONT"]
        )

    def execute(self, context):
        selected = context.selected_objects  # save original selected items

        remove_multiple("intarsion_")

        for ob in selected:
            ob.select_set(True)  # select original curves

        #  Perimeter cut largen then intarsion pocket externally, optional

        # make the diameter 5% larger and compensate for backlight
        diam = self.diameter * 1.05 + self.backlight * 2
        silhouette_offset(context, -diam / 2)

        o1 = bpy.context.active_object
        silhouette_offset(context, diam)
        o2 = bpy.context.active_object
        silhouette_offset(context, -diam / 2)
        o3 = bpy.context.active_object
        o1.select_set(True)
        o2.select_set(True)
        o3.select_set(False)
        # delete o1 and o2 temporary working curves
        bpy.ops.object.delete(use_global=False)
        o3.name = "intarsion_pocket"  # this is the pocket for intarsion
        bpy.context.object.location[2] = -self.intarsion_thickness

        if self.perimeter_cut > 0.0:
            silhouette_offset(context, self.perimeter_cut)
            bpy.context.active_object.name = "intarsion_perimeter"
            bpy.context.object.location[2] = -self.base_thickness
            bpy.ops.object.select_all(action="DESELECT")  # deselect new curve

        o3.select_set(True)
        context.view_layer.objects.active = o3
        #   intarsion profile is the inside piece of the intarsion
        # make smaller curve for material profile
        silhouette_offset(context, -self.tolerance / 2)
        bpy.context.object.location[2] = self.intarsion_thickness
        o4 = bpy.context.active_object
        bpy.context.active_object.name = "intarsion_profil"
        o4.select_set(False)

        if self.backlight > 0.0:  # Make a smaller curve for backlighting purposes
            silhouette_offset(context, (-self.tolerance / 2) - self.backlight)
            bpy.context.active_object.name = "intarsion_backlight"
            bpy.context.object.location[2] = (
                -self.backlight_depth_from_top - self.intarsion_thickness
            )
            o4.select_set(True)
        o3.select_set(True)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# intarsion or joints
class CamCurveSimpleOvercuts(Operator):
    """Adds Simple Fillets / Overcuts for Slots"""

    bl_idname = "object.curve_overcuts"
    bl_label = "Simple Fillet Overcuts"
    bl_options = {"REGISTER", "UNDO"}

    diameter: FloatProperty(
        name="Diameter",
        default=0.003175,
        min=0,
        max=100,
        precision=4,
        unit="LENGTH",
    )
    threshold: FloatProperty(
        name="Threshold",
        default=pi / 2 * 0.99,
        min=-3.14,
        max=3.14,
        precision=4,
        step=500,
        subtype="ANGLE",
        unit="ROTATION",
    )
    do_outer: BoolProperty(
        name="Outer Polygons",
        default=True,
    )
    invert: BoolProperty(
        name="Invert",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and (
            context.active_object.type in ["CURVE", "FONT"]
        )

    def execute(self, context):
        bpy.ops.object.curve_remove_doubles()
        o1 = bpy.context.active_object
        shapes = curve_to_shapely(o1)
        negative_overcuts = []
        positive_overcuts = []
        diameter = self.diameter * 1.001
        for s in shapes.geoms:
            s = shapely.geometry.polygon.orient(s, 1)
            if s.boundary.geom_type == "LineString":
                loops = MultiLineString([s.boundary])
            else:
                loops = s.boundary

            for ci, c in enumerate(loops.geoms):
                if ci > 0 or self.do_outer:
                    for i, co in enumerate(c.coords):
                        i1 = i - 1
                        if i1 == -1:
                            i1 = -2
                        i2 = i + 1
                        if i2 == len(c.coords):
                            i2 = 0

                        v1 = Vector(co) - Vector(c.coords[i1])
                        v1 = v1.xy  # Vector((v1.x,v1.y,0))
                        v2 = Vector(c.coords[i2]) - Vector(co)
                        v2 = v2.xy  # v2 = Vector((v2.x,v2.y,0))
                        if not v1.length == 0 and not v2.length == 0:
                            a = v1.angle_signed(v2)
                            sign = 1

                            if self.invert:  # and ci>0:
                                sign *= -1
                            if (sign < 0 and a < -self.threshold) or (
                                sign > 0 and a > self.threshold
                            ):
                                p = Vector((co[0], co[1]))
                                v1.normalize()
                                v2.normalize()
                                v = v1 - v2
                                v.normalize()
                                p = p - v * diameter / 2
                                if abs(a) < pi / 2:
                                    shape = circle(diameter / 2, 64)
                                    shape = shapely.affinity.translate(shape, p.x, p.y)
                                else:
                                    l = tan(a / 2) * diameter / 2
                                    p1 = p - sign * v * l
                                    l = shapely.geometry.LineString((p, p1))
                                    shape = l.buffer(diameter / 2, resolution=64)

                                if sign > 0:
                                    negative_overcuts.append(shape)
                                else:
                                    positive_overcuts.append(shape)

        negative_overcuts = shapely.ops.unary_union(negative_overcuts)
        positive_overcuts = shapely.ops.unary_union(positive_overcuts)

        fs = shapely.ops.unary_union(shapes)
        fs = fs.union(positive_overcuts)
        fs = fs.difference(negative_overcuts)
        shapely_to_curve(o1.name + "_overcuts", fs, o1.location.z)

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# Overcut type B
class CamCurveBoneFilletOvercuts(Operator):
    """Adds Dogbone, T-bone Fillets / Overcuts for Slots"""

    bl_idname = "object.curve_overcuts_b"
    bl_label = "Bone Fillet Overcuts"
    bl_options = {"REGISTER", "UNDO"}

    diameter: FloatProperty(
        name="Tool Diameter",
        default=0.003175,
        description="Tool bit diameter used in cut operation",
        min=0,
        max=100,
        precision=4,
        unit="LENGTH",
    )
    style: EnumProperty(
        name="Style",
        items=(
            ("OPEDGE", "opposite edge", "place corner overcuts on opposite edges"),
            ("DOGBONE", "Dog-bone / Corner Point", "place overcuts at center of corners"),
            ("TBONE", "T-bone", "place corner overcuts on the same edge"),
        ),
        default="DOGBONE",
        description="style of overcut to use",
    )
    threshold: FloatProperty(
        name="Max Inside Angle",
        default=pi / 2,
        min=-3.14,
        max=3.14,
        description="The maximum angle to be considered as an inside corner",
        precision=4,
        step=500,
        subtype="ANGLE",
        unit="ROTATION",
    )
    do_outer: BoolProperty(
        name="Include Outer Curve",
        description="Include the outer curve if there are curves inside",
        default=True,
    )
    do_invert: BoolProperty(
        name="Invert",
        description="invert overcut operation on all curves",
        default=True,
    )
    other_edge: BoolProperty(
        name="Other Edge",
        description="change to the other edge for the overcut to be on",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "CURVE"

    def execute(self, context):
        bpy.ops.object.curve_remove_doubles()
        o1 = bpy.context.active_object
        shapes = curve_to_shapely(o1)
        negative_overcuts = []
        positive_overcuts = []
        # count all the corners including inside and out
        cornerCnt = 0
        # a list of tuples for defining the inside corner
        # tuple is: (pos, v1, v2, angle, allCorners list index)
        insideCorners = []
        diameter = self.diameter * 1.002  # make bit size slightly larger to allow cutter
        radius = diameter / 2
        anglethreshold = pi - self.threshold
        centerv = Vector((0, 0))
        extendedv = Vector((0, 0))
        pos = Vector((0, 0))
        sign = -1 if self.do_invert else 1
        isTBone = self.style == "TBONE"
        # indexes in insideCorner tuple
        POS, V1, V2, A, IDX = range(5)

        def add_overcut(a):
            nonlocal pos, centerv, radius, extendedv, sign, negative_overcuts, positive_overcuts
            # move the overcut shape center position 1 radius in direction v
            pos -= centerv * radius
            print("abs(a)", abs(a))
            if abs(a) <= pi / 2 + 0.0001:
                print("<=pi/2")
                shape = circle(radius, 64)
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

        def set_other_edge(v1, v2, a):
            nonlocal centerv, extendedv
            if self.other_edge:
                centerv = v1
                extendedv = v2
            else:
                centerv = -v2
                extendedv = -v1
            add_overcut(a)

        def set_center_offset(a):
            nonlocal centerv, extendedv, sign
            centerv = v1 - v2
            centerv.normalize()
            extendedv = centerv * tan(a / 2) * -sign
            add_overcut(a)

        def get_corner(idx, offset):
            nonlocal insideCorners
            idx += offset
            if idx >= len(insideCorners):
                idx -= len(insideCorners)
            return insideCorners[idx]

        def get_corner_delta(curidx, nextidx):
            nonlocal cornerCnt
            delta = nextidx - curidx
            if delta < 0:
                delta += cornerCnt
            return delta

        for s in shapes.geoms:
            # ensure the shape is counterclockwise
            s = shapely.geometry.polygon.orient(s, 1)

            if s.boundary.geom_type == "LineString":
                from shapely import MultiLineString

                loops = MultiLineString([s.boundary])
            else:
                loops = s.boundary

            outercurve = self.do_outer or len(loops.geoms) == 1
            for ci, c in enumerate(loops.geoms):
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

                        v1 = Vector(co).xy - Vector(c.coords[i1]).xy
                        v2 = Vector(c.coords[i2]).xy - Vector(co).xy

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
                                pos = Vector((co[0], co[1]))
                                v1.normalize()
                                v2.normalize()
                                # figure out which direction vector to use
                                # v is the main direction vector to move the overcut shape along
                                # ev is the direction vector used to elongate the overcut shape
                                if self.style != "DOGBONE":
                                    # t-bone and opposite edge styles get treated nearly the same
                                    if isTBone:
                                        cornerCnt += 1
                                        # insideCorner tuplet: (pos, v1, v2, angle, corner index)
                                        insideCorners.append((pos, v1, v2, a, cornerCnt - 1))
                                        # processing of corners for T-Bone are done after all points are processed
                                        continue

                                    set_other_edge(v1, v2, a)

                                else:  # DOGBONE style
                                    set_center_offset(a)

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
                            prevCorner = get_corner(i, -1)
                            print("first:", i, idx, prevCorner[IDX])
                            if get_corner_delta(prevCorner[IDX], idx) == 1:
                                # make sure there is an outside corner
                                print(get_corner_delta(get_corner(i, -2)[IDX], idx))
                                if get_corner_delta(get_corner(i, -2)[IDX], idx) > 2:
                                    set_other_edge(v1, v2, a)
                                    print("first won")
                                    continue

                            nextCorner = get_corner(i, 1)
                            print("second:", i, idx, nextCorner[IDX])
                            if get_corner_delta(idx, nextCorner[IDX]) == 1:
                                # make sure there is an outside corner
                                print(get_corner_delta(idx, get_corner(i, 2)[IDX]))
                                if get_corner_delta(idx, get_corner(i, 2)[IDX]) > 2:
                                    print("second won")
                                    set_other_edge(-v2, -v1, a)
                                    continue

                            print("third")
                            if get_corner_delta(prevCorner[IDX], idx) == 3:
                                # check if they share the same edge
                                a1 = v1.angle_signed(prevCorner[V2]) * 180.0 / pi
                                print("third won", a1)
                                if a1 < -135 or a1 > 135:
                                    set_other_edge(-v2, -v1, a)
                                    continue

                            print("fourth")
                            if get_corner_delta(idx, nextCorner[IDX]) == 3:
                                # check if they share the same edge
                                a1 = v2.angle_signed(nextCorner[V1]) * 180.0 / pi
                                print("fourth won", a1)
                                if a1 < -135 or a1 > 135:
                                    set_other_edge(v1, v2, a)
                                    continue

                            print("***No Win***")
                            # the default if no other rules pass
                            set_center_offset(a)

        negative_overcuts = shapely.ops.unary_union(negative_overcuts)
        positive_overcuts = shapely.ops.unary_union(positive_overcuts)
        fs = shapely.ops.unary_union(shapes)
        fs = fs.union(positive_overcuts)
        fs = fs.difference(negative_overcuts)

        shapely_to_curve(o1.name + "_overcuts", fs, o1.location.z)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CamCurveRemoveDoubles(Operator):
    """Remove Duplicate Points from the Selected Curve"""

    bl_idname = "object.curve_remove_doubles"
    bl_label = "Remove Curve Doubles"
    bl_options = {"REGISTER", "UNDO"}

    merge_distance: FloatProperty(
        name="Merge distance",
        default=0.0001,
        min=0,
        max=0.01,
    )

    keep_bezier: BoolProperty(
        name="Keep bezier",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and (context.active_object.type == "CURVE")

    def execute(self, context):
        obj = bpy.context.selected_objects
        for ob in obj:
            if ob.type == "CURVE":
                if self.keep_bezier:
                    if ob.data.splines and ob.data.splines[0].type == "BEZIER":
                        bpy.ops.curvetools.operatorsplinesremoveshort()
                        bpy.context.view_layer.objects.active = ob
                        ob.data.resolution_u = 64
                        if bpy.context.mode == "OBJECT":
                            bpy.ops.object.editmode_toggle()
                        bpy.ops.curve.select_all()
                        bpy.ops.curve.remove_double(distance=self.merge_distance)
                        bpy.ops.object.editmode_toggle()
                else:
                    self.merge_distance = 0
                    if bpy.context.mode == "EDIT_CURVE":
                        bpy.ops.object.editmode_toggle()
                    bpy.ops.object.convert(target="MESH")
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.select_all(action="SELECT")
                    bpy.ops.mesh.remove_doubles(threshold=self.merge_distance)
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.object.convert(target="CURVE")

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        if obj.type == "CURVE":
            if obj.data.splines and obj.data.splines[0].type == "BEZIER":
                layout.prop(self, "keep_bezier", text="Keep Bezier")
        layout.prop(self, "merge_distance", text="Merge Distance")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CamMeshGetPockets(Operator):
    """Detect Pockets in a Mesh and Extract Them as Curves"""

    bl_idname = "object.mesh_get_pockets"
    bl_label = "Get Pocket Surfaces"
    bl_options = {"REGISTER", "UNDO"}

    threshold: FloatProperty(
        name="Horizontal Threshold",
        description="How horizontal the surface must be for a pocket: "
        "1.0 perfectly flat, 0.0 is any orientation",
        default=0.99,
        min=0,
        max=1.0,
        precision=4,
    )
    z_limit: FloatProperty(
        name="Z Limit",
        description="Maximum z height considered for pocket operation, " "default is 0.0",
        default=0.0,
        min=-1000.0,
        max=1000.0,
        precision=4,
        unit="LENGTH",
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and (context.active_object.type == "MESH")

    def execute(self, context):
        obs = bpy.context.selected_objects
        s = bpy.context.scene
        cobs = []
        for ob in obs:
            if ob.type == "MESH":
                pockets = {}
                mw = ob.matrix_world
                mesh = ob.data
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="FACE")
                bpy.ops.mesh.select_all(action="DESELECT")
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
                        if z < self.z_limit:
                            if pockets.get(z) is None:
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

                    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="EDGE")
                    bpy.ops.mesh.region_to_loop()
                    bpy.ops.mesh.separate(type="SELECTED")

                    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="FACE")
                    bpy.ops.object.editmode_toggle()
                    ao.select_set(state=False)
                    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
                    cobs.append(bpy.context.selected_objects[0])
                    bpy.ops.object.convert(target="CURVE")
                    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")

                    bpy.context.selected_objects[0].select_set(False)
                    ao.select_set(state=True)
                    bpy.context.view_layer.objects.active = ao
            # bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')

            # turn off selection of all objects in 3d view
            bpy.ops.object.select_all(action="DESELECT")
            # make new curves more visible by making them selected in the 3d view
            # This also allows the active object to still work with the operator
            # if the user decides to change the horizontal threshold property
            col = bpy.data.collections.new("multi level pocket ")
            s.collection.children.link(col)
            for obj in cobs:
                col.objects.link(obj)

        return {"FINISHED"}


# this operator finds the silhouette of objects(meshes, curves just get converted) and offsets it.
class CamOffsetSilhouete(Operator):
    """Offset Object Silhouette"""

    bl_idname = "object.silhouette_offset"
    bl_label = "Silhouette & Offset"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    offset: FloatProperty(
        name="Offset",
        default=0.003,
        min=-100,
        max=100,
        precision=4,
        unit="LENGTH",
    )
    mitre_limit: FloatProperty(
        name="Mitre Limit",
        default=2,
        min=0.00000001,
        max=20,
        precision=4,
        unit="LENGTH",
    )
    style: EnumProperty(
        name="Corner Type",
        items=(("1", "Round", ""), ("2", "Mitre", ""), ("3", "Bevel", "")),
    )
    caps: EnumProperty(
        name="Cap Type",
        items=(("round", "Round", ""), ("square", "Square", ""), ("flat", "Flat", "")),
    )
    align: EnumProperty(
        name="Alignment",
        items=(("worldxy", "World XY", ""), ("bottom", "Base Bottom", ""), ("top", "Base Top", "")),
    )
    open_type: EnumProperty(
        name="Curve Type",
        items=(
            ("dilate", "Dilate open curve", ""),
            ("leaveopen", "Leave curve open", ""),
            ("closecurve", "Close curve", ""),
        ),
        default="closecurve",
    )

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type in ["CURVE", "FONT", "MESH"]
            and context.mode == "OBJECT"
        )

    def is_straight(self, geom):
        assert geom.geom_type == "LineString", geom.geom_type
        length = geom.length
        start_pt = geom.interpolate(0)
        end_pt = geom.interpolate(1, normalized=True)
        straight_dist = start_pt.distance(end_pt)
        if straight_dist == 0.0:
            if length == 0.0:
                return True
            return False
        elif length / straight_dist == 1:
            return True
        else:
            return False

    # this is almost same as getobjectoutline, just without the need of operation data
    def execute(self, context):
        # bpy.ops.object.curve_remove_doubles()
        ob = context.active_object
        if ob.type == "FONT":
            bpy.context.object.data.resolution_u = 64
        if ob.type == "CURVE":
            if ob.data.splines and ob.data.splines[0].type == "BEZIER":
                bpy.context.object.data.resolution_u = 64
                bpy.ops.object.curve_remove_doubles(merge_distance=0.0001, keep_bezier=True)
            else:
                bpy.ops.object.curve_remove_doubles()

        bpy.ops.object.duplicate()
        obj = context.active_object
        if context.active_object.type != "MESH":
            obj.data.dimensions = "3D"
        bpy.ops.object.transform_apply(
            location=True, rotation=True, scale=True
        )  # apply all transforms
        bpy.ops.object.convert(target="MESH")
        bpy.context.active_object.name = "temp_mesh"

        # get the Z align point from the base
        if self.align == "top":
            point = max(
                [
                    (bpy.context.object.matrix_world @ v.co).z
                    for v in bpy.context.object.data.vertices
                ]
            )
        elif self.align == "bottom":
            point = min(
                [
                    (bpy.context.object.matrix_world @ v.co).z
                    for v in bpy.context.object.data.vertices
                ]
            )
        else:
            point = 0

        # extract X,Y coordinates from the vertices data and put them into a LineString object
        coords = []
        for v in obj.data.vertices:
            coords.append((v.co.x, v.co.y))
        remove_multiple("temp_mesh")  # delete temporary mesh
        remove_multiple("dilation")  # delete old dilation objects

        # convert coordinates to shapely LineString datastructure
        line = LineString(coords)

        # if curve is a straight segment, change offset type to dilate
        if self.is_straight(line) and self.open_type != "leaveopen":
            self.open_type = "dilate"

        # make the dilate or open curve offset
        if (self.open_type != "closecurve") and ob.type == "CURVE":
            print("line length=", round(line.length * 1000), "mm")

            if self.style == "3":
                style = "bevel"
            elif self.style == "2":
                style = "mitre"
            else:
                style = "round"

            if self.open_type == "leaveopen":
                new_shape = shapely.offset_curve(
                    line, self.offset, join_style=style
                )  # use shapely to expand without closing the curve
                name = "Offset: " + "%.2f" % round(self.offset * 1000) + "mm - " + ob.name
            else:
                new_shape = line.buffer(
                    self.offset,
                    cap_style=self.caps,
                    resolution=16,
                    join_style=style,
                    mitre_limit=self.mitre_limit,
                )  # use shapely to expand, closing the curve
                name = "Dilation: " + "%.2f" % round(self.offset * 1000) + "mm - " + ob.name

            # create the actual offset object based on the Shapely offset
            shapely_to_curve(name, new_shape, 0, self.open_type != "leaveopen")

            # position the object according to the calculated point
            bpy.context.object.location.z = point

        # if curve is not a straight line and neither dilate or leave open are selected, create a normal offset
        else:
            bpy.context.view_layer.objects.active = ob
            silhouette_offset(context, self.offset, int(self.style), self.mitre_limit)
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "offset", text="Offset")
        layout.prop(self, "open_type", text="Type")
        layout.prop(self, "style", text="Corner")
        if self.style == "2":
            layout.prop(self, "mitrelimit", text="Mitre Limit")
        if self.open_type == "dilate":
            layout.prop(self, "caps", text="Cap")
        if self.open_type != "closecurve":
            layout.prop(self, "align", text="Align")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    # Finds object silhouette, usefull for meshes, since with curves it's not needed.


class CamObjectSilhouette(Operator):
    """Create Object Silhouette"""

    bl_idname = "object.silhouette"
    bl_label = "Object Silhouette"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and (
            context.active_object.type == "FONT" or context.active_object.type == "MESH"
        )

    # this is almost same as getobjectoutline, just without the need of operation data
    def execute(self, context):
        ob = bpy.context.active_object
        self.silh = get_object_silhouette("OBJECTS", objects=bpy.context.selected_objects)
        bpy.context.scene.cursor.location = (0, 0, 0)

        for smp in self.silh.geoms:
            shapely_to_curve(ob.name + "_silhouette", smp, 0)

        join_multiple(ob.name + "_silhouette")
        bpy.context.scene.cursor.location = ob.location
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        bpy.ops.object.curve_remove_doubles()
        return {"FINISHED"}
