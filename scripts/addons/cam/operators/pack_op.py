"""Fabex 'ops.py' © 2012 Vilem Novak

Blender Operator definitions are in this file.
They mostly call the functions from 'utils.py'
"""

from math import pi
import os
import random
import time

import shapely
from shapely import geometry as sgeometry
from shapely import affinity, prepared, speedups

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    FloatProperty,
)
from bpy.types import Operator


from ..cam_chunk import curve_to_chunks
from ..constants import PRECISION
from ..pack import pack_curves

from ..utilities.chunk_utils import chunks_to_shapely
from ..utilities.shapely_utils import shapely_to_curve
from ..utilities.simple_utils import activate


class CamPackObjects(Operator):
    """Calculate All CAM Paths"""

    bl_idname = "object.cam_pack_objects"
    bl_label = "Pack Curves on Sheet"
    bl_options = {"REGISTER", "UNDO"}

    sheet_fill_direction: EnumProperty(
        name="Fill Direction",
        items=(
            ("X", "X", "Fills sheet in X axis direction"),
            ("Y", "Y", "Fills sheet in Y axis direction"),
        ),
        description="Fill direction of the packer algorithm",
        default="Y",
    )
    sheet_x: FloatProperty(
        name="X Size",
        description="Sheet size",
        min=0.001,
        max=10,
        default=0.5,
        precision=PRECISION,
        unit="LENGTH",
    )
    sheet_y: FloatProperty(
        name="Y Size",
        description="Sheet size",
        min=0.001,
        max=10,
        default=0.5,
        precision=PRECISION,
        unit="LENGTH",
    )
    distance: FloatProperty(
        name="Minimum Distance",
        description="Minimum distance between objects(should be " "at least cutter diameter!)",
        min=0.001,
        max=10,
        default=0.01,
        precision=PRECISION,
        unit="LENGTH",
    )
    tolerance: FloatProperty(
        name="Placement Tolerance",
        description="Tolerance for placement: smaller value slower placemant",
        min=0.001,
        max=0.02,
        default=0.005,
        precision=PRECISION,
        unit="LENGTH",
    )
    rotate: BoolProperty(
        name="Enable Rotation",
        description="Enable rotation of elements",
        default=True,
    )
    rotate_angle: FloatProperty(
        name="Placement Angle Rotation Step",
        description="Bigger rotation angle, faster placemant",
        default=0.19635 * 4,
        min=pi / 180,
        max=pi,
        precision=5,
        step=500,
        subtype="ANGLE",
        unit="ROTATION",
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "CURVE"

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        """Execute the operation in the given context.

        This function sets the Blender object mode to 'OBJECT', retrieves the
        currently selected objects, and calls the `pack_curves` function from the
        `pack` module. It is typically used to finalize operations on selected
        objects in Blender.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the completion status of the operation.
        """

        bpy.ops.object.mode_set(mode="OBJECT")  # force object mode
        obs = bpy.context.selected_objects
        if speedups.available:
            speedups.enable()
        t = time.time()

        sheetsizex = self.sheet_x
        sheetsizey = self.sheet_y
        direction = self.sheet_fill_direction
        distance = self.distance
        tolerance = self.tolerance
        rotate = self.rotate
        rotate_angle = self.rotate_angle

        # in this, position, rotation, and actual poly will be stored.
        polyfield = []
        for ob in bpy.context.selected_objects:
            activate(ob)
            bpy.ops.object.make_single_user(type="SELECTED_OBJECTS")
            bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
            z = ob.location.z
            bpy.ops.object.location_clear()
            bpy.ops.object.rotation_clear()

            chunks = curve_to_chunks(ob)
            npolys = chunks_to_shapely(chunks)
            # add all polys in silh to one poly
            poly = shapely.ops.unary_union(npolys)

            poly = poly.buffer(distance / 1.5, 8)
            poly = poly.simplify(0.0003)
            polyfield.append([[0, 0], 0.0, poly, ob, z])
        random.shuffle(polyfield)
        # primitive layout here:
        allpoly = prepared.prep(sgeometry.Polygon())  # main collision poly.

        shift = tolerance  # one milimeter by now.
        rotchange = rotate_angle  # in radians

        xmin, ymin, xmax, ymax = polyfield[0][2].bounds
        if direction == "X":
            mindist = -xmin
        else:
            mindist = -ymin
        i = 0
        p = polyfield[0][2]
        placedpolys = []
        rotcenter = sgeometry.Point(0, 0)
        for pf in polyfield:
            print(i)
            rot = 0
            porig = pf[2]
            placed = False
            xmin, ymin, xmax, ymax = p.bounds
            if direction == "X":
                x = mindist
                y = -ymin
            if direction == "Y":
                x = -xmin
                y = mindist

            itera = 0
            best = None
            hits = 0
            besthit = None
            while not placed:
                # swap x and y, and add to x
                # print(x,y)
                p = porig

                if rotate:
                    ptrans = affinity.rotate(p, rot, origin=rotcenter, use_radians=True)
                    ptrans = affinity.translate(ptrans, x, y)
                else:
                    ptrans = affinity.translate(p, x, y)
                xmin, ymin, xmax, ymax = ptrans.bounds
                # print(iter,p.bounds)

                if (
                    xmin > 0
                    and ymin > 0
                    and (
                        (direction == "Y" and xmax < sheetsizex)
                        or (direction == "X" and ymax < sheetsizey)
                    )
                ):
                    if not allpoly.intersects(ptrans):
                        # we do more good solutions, choose best out of them:
                        hits += 1
                        if best is None:
                            best = [x, y, rot, xmax, ymax]
                            besthit = hits
                        if direction == "X":
                            if xmax < best[3]:
                                best = [x, y, rot, xmax, ymax]
                                besthit = hits
                        elif ymax < best[4]:
                            best = [x, y, rot, xmax, ymax]
                            besthit = hits

                if hits >= 15 or (
                    itera > 20000 and hits > 0
                ):  # here was originally more, but 90% of best solutions are still 1
                    placed = True
                    pf[3].location.x = best[0]
                    pf[3].location.y = best[1]
                    pf[3].location.z = pf[4]
                    pf[3].rotation_euler.z = best[2]

                    pf[3].select_set(state=True)

                    # print(mindist)
                    mindist = mindist - 0.5 * (xmax - xmin)
                    # print(mindist)
                    # print(iter)

                    # reset polygon to best position here:
                    ptrans = affinity.rotate(porig, best[2], rotcenter, use_radians=True)
                    ptrans = affinity.translate(ptrans, best[0], best[1])

                    print(best[0], best[1], itera)
                    placedpolys.append(ptrans)
                    allpoly = prepared.prep(sgeometry.MultiPolygon(placedpolys))

                    # cleanup allpoly
                    print(itera, hits, besthit)
                if not placed:
                    if direction == "Y":
                        x += shift
                        mindist = y
                        if xmax + shift > sheetsizex:
                            x = x - xmin
                            y += shift
                    if direction == "X":
                        y += shift
                        mindist = x
                        if ymax + shift > sheetsizey:
                            y = y - ymin
                            x += shift
                    if rotate:
                        rot += rotchange
                itera += 1
            i += 1
        t = time.time() - t

        shapely_to_curve("test", sgeometry.MultiPolygon(placedpolys), 0)
        print(t)
        # layout.
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Sheet Size")
        col.prop(self, "sheet_x", text="X")
        col.prop(self, "sheet_y", text="Y")
        col.prop(self, "sheet_fill_direction")
        col = layout.column(align=True)
        col.prop(self, "distance")
        col.prop(self, "tolerance")
        header, panel = col.panel_prop(self, "rotate")
        header.label(text="Rotation")
        if panel:
            col = panel.column(align=True)
            col.prop(self, "rotate_angle", text="Placement Angle Step")
