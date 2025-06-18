"""Fabex 'curve_cam_create.py' © 2021, 2022 Alain Pelletier

Operators to create a number of predefined curve objects.
"""

from math import degrees, hypot, pi, radians

from shapely import affinity
from shapely.geometry import (
    LineString,
    MultiLineString,
    box,
)

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
)
from bpy.types import Operator

from .. import (
    involute_gear,
    joinery,
    puzzle_joinery,
)
from ..cam_chunk import (
    curve_to_shapely,
    polygon_boolean,
    polygon_convex_hull,
)

from ..utilities.simple_utils import (
    remove_multiple,
    select_multiple,
    join_multiple,
    make_active,
    deselect,
    active_name,
    remove_doubles,
    rename,
    duplicate,
    add_overcut,
    move,
    difference,
    union,
    rotate,
)
from ..utilities.shapely_utils import (
    shapely_to_curve,
)


def generate_crosshatch(context, angle, distance, offset, pocket_shape, join, ob=None):
    """Execute the crosshatch generation process based on the provided context.

    Args:
        context (bpy.context): The Blender context containing the active object.
        angle (float): The angle for rotating the crosshatch pattern.
        distance (float): The distance between crosshatch lines.
        offset (float): The offset for the bounds or hull.
        pocket_shape (str): Determines whether to use bounds, hull, or pocket.

    Returns:
        shapely.geometry.MultiLineString: The resulting intersection geometry of the crosshatch.
    """
    if ob is None:
        ob = context.active_object
    else:
        bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    if ob.data.splines and ob.data.splines[0].type == "BEZIER":
        bpy.ops.object.curve_remove_doubles(merge_distance=0.0001, keep_bezier=True)
    else:
        bpy.ops.object.curve_remove_doubles()

    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="MEDIAN")
    depth = ob.location[2]

    shapes = curve_to_shapely(ob)

    if pocket_shape == "HULL":
        shapes = shapes.convex_hull

    coords = []
    minx, miny, maxx, maxy = shapes.bounds
    minx -= offset
    miny -= offset
    maxx += offset
    maxy += offset
    centery = (miny + maxy) / 2
    length = maxy - miny
    width = maxx - minx
    centerx = (minx + maxx) / 2
    diagonal = hypot(width, length)

    bound_rectangle = box(minx, miny, maxx, maxy)
    amount = int(2 * diagonal / distance) + 1

    for x in range(amount):
        distance_val = x * distance - diagonal
        coords.append(((distance_val, diagonal + 0.5), (distance_val, -diagonal - 0.5)))

    # Create a multilinestring shapely object
    lines = MultiLineString(coords)
    rotated = affinity.rotate(lines, angle, use_radians=True)  # Rotate using shapely
    rotated_minx, rotated_miny, rotated_maxx, rotated_maxy = rotated.bounds
    rotated_centerx = (rotated_minx + rotated_maxx) / 2
    rotated_centery = (rotated_miny + rotated_maxy) / 2
    x_offset = centerx - rotated_centerx
    y_offset = centery - rotated_centery
    translated = affinity.translate(
        rotated, xoff=x_offset, yoff=y_offset, zoff=depth
    )  # Move using shapely

    bounds = bound_rectangle

    if pocket_shape == "BOUNDS":
        xing = translated.intersection(bounds)  # Intersection with bounding box
    else:
        xing = translated.intersection(
            shapes.buffer(offset, join_style=join)
        )  # Intersection with shapes or hull

    # Return the intersection result
    return xing


class CamCurveHatch(Operator):
    """Perform Hatch Operation on Single or Multiple Curves"""  # by Alain Pelletier September 2021

    bl_idname = "object.curve_hatch"
    bl_label = "CrossHatch Curve"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    angle: FloatProperty(
        default=0,
        min=-pi / 2,
        max=pi / 2,
        precision=4,
        subtype="ANGLE",
    )
    distance: FloatProperty(
        default=0.003,
        min=0.0001,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    offset: FloatProperty(
        default=0,
        min=-1.0,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    pocket_shape: EnumProperty(
        name="Pocket Shape",
        items=(
            ("BOUNDS", "Bounds Rectangle", "Uses a bounding rectangle"),
            ("HULL", "Convex Hull", "Uses a convex hull"),
            ("POCKET", "Pocket", "Uses the pocket shape"),
        ),
        description="Type of pocket shape",
        default="POCKET",
    )
    contour: BoolProperty(
        name="Contour Curve",
        default=False,
    )

    xhatch: BoolProperty(
        name="Crosshatch #",
        default=False,
    )

    contour_separate: BoolProperty(
        name="Contour Separate",
        default=False,
    )

    straight: BoolProperty(
        name="Overshoot Style",
        description="Use overshoot cutout instead of conventional rounded",
        default=True,
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type in ["CURVE", "FONT"]

    def draw(self, context):
        """Draw the layout properties for the given context."""
        layout = self.layout
        layout.prop(self, "angle")
        layout.prop(self, "distance")
        layout.prop(self, "offset")
        layout.prop(self, "pocket_shape")
        layout.prop(self, "xhatch")
        if self.pocket_shape == "POCKET":
            layout.prop(self, "straight")
            layout.prop(self, "contour")
            if self.contour:
                layout.prop(self, "contour_separate")

    def execute(self, context):
        if self.straight:
            join = 2
        else:
            join = 1
        ob = context.active_object
        obname = ob.name
        ob.select_set(True)
        remove_multiple("crosshatch")
        depth = ob.location[2]
        xingOffset = self.offset

        if self.contour:
            xingOffset = self.offset - self.distance / 2  #  contour does not touch the crosshatch
        xing = generate_crosshatch(
            context,
            self.angle,
            self.distance,
            xingOffset,
            self.pocket_shape,
            join,
        )
        shapely_to_curve("crosshatch_lines", xing, depth)

        if self.xhatch:
            make_active(obname)
            xingra = generate_crosshatch(
                context,
                self.angle + pi / 2,
                self.distance,
                xingOffset,
                self.pocket_shape,
                join,
            )
            shapely_to_curve("crosshatch_lines_ra", xingra, depth)

        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="MEDIAN")
        join_multiple("crosshatch")
        if self.contour:
            deselect()
            bpy.context.view_layer.objects.active = ob
            ob.select_set(True)
            bpy.ops.object.silhouette_offset(offset=self.offset)
            if self.contour_separate:
                active_name("contour_hatch")
                deselect()
            else:
                active_name("crosshatch_contour")
                join_multiple("crosshatch")
                remove_doubles()
        else:
            join_multiple("crosshatch")
            remove_doubles()
        return {"FINISHED"}


class CamCurvePlate(Operator):
    """Generates Rounded Plate with Mounting Holes"""  # by Alain Pelletier Sept 2021

    bl_idname = "object.curve_plate"
    bl_label = "Sign Plate"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    radius: FloatProperty(
        name="Corner Radius",
        default=0.025,
        min=0,
        max=0.1,
        precision=4,
        unit="LENGTH",
    )
    width: FloatProperty(
        name="Width of Plate",
        default=0.3048,
        min=0,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    height: FloatProperty(
        name="Height of Plate",
        default=0.457,
        min=0,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    hole_diameter: FloatProperty(
        name="Hole Diameter",
        default=0.01,
        min=0,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    hole_tolerance: FloatProperty(
        name="Hole V Tolerance",
        default=0.005,
        min=0,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    hole_vdist: FloatProperty(
        name="Hole Vert Distance",
        default=0.400,
        min=0,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    hole_hdist: FloatProperty(
        name="Hole Horiz Distance",
        default=0,
        min=0,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    hole_hamount: IntProperty(
        name="Hole Horiz Amount",
        default=1,
        min=0,
        max=50,
    )
    resolution: IntProperty(
        name="Spline Resolution",
        default=50,
        min=3,
        max=150,
    )
    plate_type: EnumProperty(
        name="Type Plate",
        items=(
            ("ROUNDED", "Rounded corner", "Makes a rounded corner plate"),
            ("COVE", "Cove corner", "Makes a plate with circles cut in each corner "),
            ("BEVEL", "Bevel corner", "Makes a plate with beveled corners "),
            ("OVAL", "Elipse", "Makes an oval plate"),
        ),
        description="Type of Plate",
        default="ROUNDED",
    )

    def draw(self, context):
        """Draw the UI layout for plate properties.

        This method creates a user interface layout for configuring various
        properties of a plate, including its type, dimensions, hole
        specifications, and resolution. It dynamically adds properties to the
        layout based on the selected plate type, allowing users to input
        relevant parameters.

        Args:
            context: The context in which the UI is being drawn.
        """

        layout = self.layout
        layout.prop(self, "plate_type")
        layout.prop(self, "width")
        layout.prop(self, "height")
        layout.prop(self, "hole_diameter")
        layout.prop(self, "hole_tolerance")
        layout.prop(self, "hole_vdist")
        layout.prop(self, "hole_hdist")
        layout.prop(self, "hole_hamount")
        layout.prop(self, "resolution")

        if self.plate_type in ["ROUNDED", "COVE", "BEVEL"]:
            layout.prop(self, "radius")

    def execute(self, context):
        """Execute the creation of a plate based on specified parameters.

        This function generates a plate shape in Blender based on the defined
        attributes such as width, height, radius, and plate type. It supports
        different plate types including rounded, oval, cove, and bevel. The
        function also handles the creation of holes in the plate if specified.
        It utilizes Blender's curve operations to create the geometry and
        applies various transformations to achieve the desired shape.

        Args:
            context (bpy.context): The Blender context in which the operation is performed.

        Returns:
            dict: A dictionary indicating the result of the operation, typically
                {'FINISHED'} if successful.
        """

        left = -self.width / 2 + self.radius
        bottom = -self.height / 2 + self.radius
        right = -left
        top = -bottom

        if self.plate_type == "ROUNDED":
            # create base
            bpy.ops.curve.primitive_bezier_circle_add(
                radius=self.radius,
                enter_editmode=False,
                align="WORLD",
                location=(left, bottom, 0),
                scale=(1, 1, 1),
            )
            active_name("_circ_LB")
            bpy.context.object.data.resolution_u = self.resolution
            bpy.ops.curve.primitive_bezier_circle_add(
                radius=self.radius,
                enter_editmode=False,
                align="WORLD",
                location=(right, bottom, 0),
                scale=(1, 1, 1),
            )
            active_name("_circ_RB")
            bpy.context.object.data.resolution_u = self.resolution
            bpy.ops.curve.primitive_bezier_circle_add(
                radius=self.radius,
                enter_editmode=False,
                align="WORLD",
                location=(left, top, 0),
                scale=(1, 1, 1),
            )
            active_name("_circ_LT")
            bpy.context.object.data.resolution_u = self.resolution
            bpy.ops.curve.primitive_bezier_circle_add(
                radius=self.radius,
                enter_editmode=False,
                align="WORLD",
                location=(right, top, 0),
                scale=(1, 1, 1),
            )
            active_name("_circ_RT")
            bpy.context.object.data.resolution_u = self.resolution

            # select the circles for the four corners
            select_multiple("_circ")
            # perform hull operation on the four corner circles
            polygon_convex_hull(context)
            active_name("plate_base")
            remove_multiple("_circ")  # remove corner circles

        elif self.plate_type == "OVAL":
            bpy.ops.curve.simple(
                align="WORLD",
                location=(0, 0, 0),
                rotation=(0, 0, 0),
                Simple_Type="Ellipse",
                Simple_a=self.width / 2,
                Simple_b=self.height / 2,
                use_cyclic_u=True,
                edit_mode=False,
            )
            bpy.context.object.data.resolution_u = self.resolution
            active_name("plate_base")

        elif self.plate_type == "COVE":
            bpy.ops.curve.primitive_bezier_circle_add(
                radius=self.radius,
                enter_editmode=False,
                align="WORLD",
                location=(left - self.radius, bottom - self.radius, 0),
                scale=(1, 1, 1),
            )
            active_name("_circ_LB")
            bpy.context.object.data.resolution_u = self.resolution
            bpy.ops.curve.primitive_bezier_circle_add(
                radius=self.radius,
                enter_editmode=False,
                align="WORLD",
                location=(right + self.radius, bottom - self.radius, 0),
                scale=(1, 1, 1),
            )
            active_name("_circ_RB")
            bpy.context.object.data.resolution_u = self.resolution
            bpy.ops.curve.primitive_bezier_circle_add(
                radius=self.radius,
                enter_editmode=False,
                align="WORLD",
                location=(left - self.radius, top + self.radius, 0),
                scale=(1, 1, 1),
            )
            active_name("_circ_LT")
            bpy.context.object.data.resolution_u = self.resolution
            bpy.ops.curve.primitive_bezier_circle_add(
                radius=self.radius,
                enter_editmode=False,
                align="WORLD",
                location=(right + self.radius, top + self.radius, 0),
                scale=(1, 1, 1),
            )
            active_name("_circ_RT")
            bpy.context.object.data.resolution_u = self.resolution

            join_multiple("_circ")

            bpy.ops.curve.simple(
                align="WORLD",
                Simple_Type="Rectangle",
                Simple_width=self.width,
                Simple_length=self.height,
                outputType="POLY",
                use_cyclic_u=True,
                edit_mode=False,
            )
            active_name("_base")

            difference("_", "_base")
            rename("_base", "plate_base")

        elif self.plate_type == "BEVEL":
            bpy.ops.curve.simple(
                align="WORLD",
                Simple_Type="Rectangle",
                Simple_width=self.radius * 2,
                Simple_length=self.radius * 2,
                location=(left - self.radius, bottom - self.radius, 0),
                rotation=(0, 0, 0.785398),
                outputType="POLY",
                use_cyclic_u=True,
                edit_mode=False,
            )
            active_name("_bev_LB")
            bpy.context.object.data.resolution_u = self.resolution
            bpy.ops.curve.simple(
                align="WORLD",
                Simple_Type="Rectangle",
                Simple_width=self.radius * 2,
                Simple_length=self.radius * 2,
                location=(right + self.radius, bottom - self.radius, 0),
                rotation=(0, 0, 0.785398),
                outputType="POLY",
                use_cyclic_u=True,
                edit_mode=False,
            )
            active_name("_bev_RB")
            bpy.context.object.data.resolution_u = self.resolution
            bpy.ops.curve.simple(
                align="WORLD",
                Simple_Type="Rectangle",
                Simple_width=self.radius * 2,
                Simple_length=self.radius * 2,
                location=(left - self.radius, top + self.radius, 0),
                rotation=(0, 0, 0.785398),
                outputType="POLY",
                use_cyclic_u=True,
                edit_mode=False,
            )

            active_name("_bev_LT")
            bpy.context.object.data.resolution_u = self.resolution

            bpy.ops.curve.simple(
                align="WORLD",
                Simple_Type="Rectangle",
                Simple_width=self.radius * 2,
                Simple_length=self.radius * 2,
                location=(right + self.radius, top + self.radius, 0),
                rotation=(0, 0, 0.785398),
                outputType="POLY",
                use_cyclic_u=True,
                edit_mode=False,
            )

            active_name("_bev_RT")
            bpy.context.object.data.resolution_u = self.resolution

            join_multiple("_bev")

            bpy.ops.curve.simple(
                align="WORLD",
                Simple_Type="Rectangle",
                Simple_width=self.width,
                Simple_length=self.height,
                outputType="POLY",
                use_cyclic_u=True,
                edit_mode=False,
            )
            active_name("_base")

            difference("_", "_base")
            rename("_base", "plate_base")

        if self.hole_diameter > 0 or self.hole_hamount > 0:
            bpy.ops.curve.primitive_bezier_circle_add(
                radius=self.hole_diameter / 2,
                enter_editmode=False,
                align="WORLD",
                location=(0, self.hole_tolerance / 2, 0),
                scale=(1, 1, 1),
            )
            active_name("_hole_Top")
            bpy.context.object.data.resolution_u = int(self.resolution / 4)
            if self.hole_tolerance > 0:
                bpy.ops.curve.primitive_bezier_circle_add(
                    radius=self.hole_diameter / 2,
                    enter_editmode=False,
                    align="WORLD",
                    location=(0, -self.hole_tolerance / 2, 0),
                    scale=(1, 1, 1),
                )
                active_name("_hole_Bottom")
                bpy.context.object.data.resolution_u = int(self.resolution / 4)

            # select everything starting with _hole and perform a convex hull on them
            select_multiple("_hole")
            polygon_convex_hull(context)
            active_name("plate_hole")
            move(y=-self.hole_vdist / 2)
            duplicate(y=self.hole_vdist)

            remove_multiple("_hole")  # remove temporary holes

            join_multiple("plate_hole")  # join the holes together

            # horizontal holes
            if self.hole_hamount > 1:
                if self.hole_hamount % 2 != 0:
                    for x in range(int((self.hole_hamount - 1) / 2)):
                        # calculate the distance from the middle
                        dist = self.hole_hdist * (x + 1)
                        duplicate()
                        bpy.context.object.location[0] = dist
                        duplicate()
                        bpy.context.object.location[0] = -dist
                else:
                    for x in range(int(self.hole_hamount / 2)):
                        dist = (
                            self.hole_hdist * x + self.hole_hdist / 2
                        )  # calculate the distance from the middle
                        if (
                            x == 0
                        ):  # special case where the original hole only needs to move and not duplicate
                            bpy.context.object.location[0] = dist
                            duplicate()
                            bpy.context.object.location[0] = -dist
                        else:
                            duplicate()
                            bpy.context.object.location[0] = dist
                            duplicate()
                            bpy.context.object.location[0] = -dist
                join_multiple("plate_hole")  # join the holes together

            # select everything starting with plate_
            select_multiple("plate_")

            # Make the plate base active
            bpy.context.view_layer.objects.active = bpy.data.objects["plate_base"]
            # Remove holes from the base
            polygon_boolean(context, "DIFFERENCE")
            remove_multiple("plate_")  # Remove temporary base and holes
            remove_multiple("_")

        active_name("plate")
        bpy.context.active_object.select_set(True)
        bpy.ops.object.curve_remove_doubles()

        return {"FINISHED"}


class CamCurveFlatCone(Operator):
    """Generates Cone from Flat Stock"""  # by Alain Pelletier Sept 2021

    bl_idname = "object.curve_flat_cone"
    bl_label = "Cone Flat Calculator"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    small_d: FloatProperty(
        name="Small Diameter",
        default=0.025,
        min=0.0001,
        max=0.1,
        precision=4,
        unit="LENGTH",
    )
    large_d: FloatProperty(
        name="Large Diameter",
        default=0.3048,
        min=0.0001,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    height: FloatProperty(
        name="Height of Cone",
        default=0.457,
        min=0.0001,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    tab: FloatProperty(
        name="Tab Witdh",
        default=0.01,
        min=0,
        max=0.100,
        precision=4,
        unit="LENGTH",
    )
    intake: FloatProperty(
        name="Intake Diameter",
        default=0,
        min=0,
        max=0.200,
        precision=4,
        unit="LENGTH",
    )
    intake_skew: FloatProperty(
        name="Intake Skew",
        default=1,
        min=0.1,
        max=4,
    )
    resolution: IntProperty(
        name="Resolution",
        default=12,
        min=5,
        max=200,
    )

    def execute(self, context):
        """Execute the construction of a geometric shape in Blender.

        This method performs a series of operations to create a geometric shape
        based on specified dimensions and parameters. It calculates various
        dimensions needed for the shape, including height and angles, and then
        uses Blender's operations to create segments, rectangles, and ellipses.
        The function also handles the positioning and rotation of these shapes
        within the 3D space of Blender.

        Args:
            context: The context in which the operation is executed, typically containing
                information about the current
                scene and active objects in Blender.

        Returns:
            dict: A dictionary indicating the completion status of the operation,
                typically {'FINISHED'}.
        """

        y = self.small_d / 2
        z = self.large_d / 2
        x = self.height
        h = x * y / (z - y)
        a = hypot(h, y)
        ab = hypot(x + h, z)
        b = ab - a
        angle = pi * 2 * y / a

        # create base
        bpy.ops.curve.simple(
            Simple_Type="Segment",
            Simple_a=ab,
            Simple_b=a,
            Simple_endangle=degrees(angle),
            use_cyclic_u=True,
            edit_mode=False,
        )

        active_name("_segment")

        bpy.ops.curve.simple(
            align="WORLD",
            location=(a + b / 2, -self.tab / 2, 0),
            rotation=(0, 0, 0),
            Simple_Type="Rectangle",
            Simple_width=b - 0.0050,
            Simple_length=self.tab,
            use_cyclic_u=True,
            edit_mode=False,
            shape="3D",
        )

        active_name("_segment")
        if self.intake > 0:
            bpy.ops.curve.simple(
                align="WORLD",
                location=(0, 0, 0),
                rotation=(0, 0, 0),
                Simple_Type="Ellipse",
                Simple_a=self.intake,
                Simple_b=self.intake * self.intake_skew,
                use_cyclic_u=True,
                edit_mode=False,
                shape="3D",
            )
            move(x=ab - 3 * self.intake / 2)
            rotate(angle / 2)

        bpy.context.object.data.resolution_u = self.resolution

        union("_segment")

        active_name("flat_cone")

        return {"FINISHED"}


class CamCurveMortise(Operator):
    """Generates Mortise Along a Curve"""  # by Alain Pelletier December 2021

    bl_idname = "object.curve_mortise"
    bl_label = "Mortise"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    finger_size: BoolProperty(
        name="Kurf Bending only",
        default=False,
    )
    finger_size: FloatProperty(
        name="Maximum Finger Size",
        default=0.015,
        min=0.005,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    min_finger_size: FloatProperty(
        name="Minimum Finger Size",
        default=0.0025,
        min=0.001,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    finger_tolerance: FloatProperty(
        name="Finger Play Room",
        default=0.000045,
        min=0,
        max=0.003,
        precision=4,
        unit="LENGTH",
    )
    plate_thickness: FloatProperty(
        name="Drawer Plate Thickness",
        default=0.00477,
        min=0.001,
        max=3.0,
        unit="LENGTH",
    )
    side_height: FloatProperty(
        name="Side Height",
        default=0.05,
        min=0.001,
        max=3.0,
        unit="LENGTH",
    )
    flex_pocket: FloatProperty(
        name="Flex Pocket",
        default=0.004,
        min=0.000,
        max=1.0,
        unit="LENGTH",
    )
    top_bottom: BoolProperty(
        name="Side Top & Bottom Fingers",
        default=True,
    )
    opencurve: BoolProperty(
        name="OpenCurve",
        default=False,
    )
    adaptive: FloatProperty(
        name="Adaptive Angle Threshold",
        default=0.0,
        min=0.000,
        max=2,
        step=100,
        subtype="ANGLE",
        unit="ROTATION",
    )
    double_adaptive: BoolProperty(
        name="Double Adaptive Pockets",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and (
            context.active_object.type in ["CURVE", "FONT"]
        )

    def execute(self, context):
        """Execute the joinery process based on the provided context.

        This function performs a series of operations to duplicate the active
        object, convert it to a mesh, and then process its geometry to create
        joinery features. It extracts vertex coordinates, converts them into a
        LineString data structure, and applies either variable or fixed finger
        joinery based on the specified parameters. The function also handles the
        creation of flexible sides and pockets if required.

        Args:
            context (bpy.context): The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the completion status of the operation.
        """

        o1 = bpy.context.active_object

        bpy.context.object.data.resolution_u = 60
        bpy.ops.object.duplicate()
        obj = context.active_object
        bpy.ops.object.convert(target="MESH")
        active_name("_temp_mesh")

        if self.opencurve:
            coords = []
            for v in obj.data.vertices:  # extract X,Y coordinates from the vertices data
                coords.append((v.co.x, v.co.y))
            # convert coordinates to shapely LineString datastructure
            line = LineString(coords)
            remove_multiple("-converted")
            shapely_to_curve("-converted_curve", line, 0.0)
        shapes = curve_to_shapely(o1)

        for s in shapes.geoms:
            if s.boundary.geom_type == "LineString":
                loops = [s.boundary]
            else:
                loops = s.boundary

            for ci, c in enumerate(loops):
                if self.opencurve:
                    length = line.length
                else:
                    length = c.length
                print("Loop Length:", length)
                if self.opencurve:
                    loop_length = line.length
                else:
                    loop_length = c.length
                print("Line Length:", loop_length)

                if self.adaptive > 0.0:
                    joinery.variable_finger(
                        c,
                        length,
                        self.min_finger_size,
                        self.finger_size,
                        self.plate_thickness,
                        self.finger_tolerance,
                        self.adaptive,
                    )
                    locations = joinery.variable_finger(
                        c,
                        length,
                        self.min_finger_size,
                        self.finger_size,
                        self.plate_thickness,
                        self.finger_tolerance,
                        self.adaptive,
                        True,
                        self.double_adaptive,
                    )
                    joinery.create_flex_side(
                        loop_length, self.side_height, self.plate_thickness, self.top_bottom
                    )
                    if self.flex_pocket > 0:
                        joinery.make_variable_flex_pocket(
                            self.side_height, self.plate_thickness, self.flex_pocket, locations
                        )

                else:
                    joinery.fixed_finger(
                        c, length, self.finger_size, self.plate_thickness, self.finger_tolerance
                    )
                    joinery.fixed_finger(
                        c,
                        length,
                        self.finger_size,
                        self.plate_thickness,
                        self.finger_tolerance,
                        True,
                    )
                    joinery.create_flex_side(
                        loop_length, self.side_height, self.plate_thickness, self.top_bottom
                    )
                    if self.flex_pocket > 0:
                        joinery.make_flex_pocket(
                            length,
                            self.side_height,
                            self.plate_thickness,
                            self.finger_size,
                            self.flex_pocket,
                        )
        remove_multiple("_")
        return {"FINISHED"}


class CamCurveInterlock(Operator):
    """Generates Interlock Along a Curve"""  # by Alain Pelletier December 2021

    bl_idname = "object.curve_interlock"
    bl_label = "Interlock"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    finger_size: FloatProperty(
        name="Finger Size",
        default=0.015,
        min=0.005,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    finger_tolerance: FloatProperty(
        name="Finger Play Room",
        default=0.000045,
        min=0,
        max=0.003,
        precision=4,
        unit="LENGTH",
    )
    plate_thickness: FloatProperty(
        name="Plate Thickness",
        default=0.00477,
        min=0.001,
        max=3.0,
        unit="LENGTH",
    )
    opencurve: BoolProperty(
        name="OpenCurve",
        default=False,
    )
    interlock_type: EnumProperty(
        name="Type of Interlock",
        items=(
            ("TWIST", "Twist", "Interlock requires 1/4 turn twist"),
            ("GROOVE", "Groove", "Simple sliding groove"),
            ("PUZZLE", "Puzzle Interlock", "Puzzle good for flat joints"),
        ),
        description="Type of interlock",
        default="GROOVE",
    )
    finger_amount: IntProperty(
        name="Finger Amount",
        default=2,
        min=1,
        max=100,
    )
    tangent_angle: FloatProperty(
        name="Tangent Deviation",
        default=0.0,
        min=0.000,
        max=2,
        step=100,
        subtype="ANGLE",
        unit="ROTATION",
    )
    fixed_angle: FloatProperty(
        name="Fixed Angle",
        default=0.0,
        min=0.000,
        max=2,
        step=100,
        subtype="ANGLE",
        unit="ROTATION",
    )

    def execute(self, context):
        """Execute the joinery operation based on the selected objects in the
        context.

        This function checks the selected objects in the provided context and
        performs different operations depending on the type of the active
        object. If the active object is a curve or font and there are selected
        objects, it duplicates the object, converts it to a mesh, and processes
        its vertices to create a LineString representation. The function then
        calculates lengths and applies distributed interlock joinery based on
        the specified parameters. If no valid objects are selected, it defaults
        to a single interlock operation at the cursor's location.

        Args:
            context (bpy.context): The context containing selected objects and active object.

        Returns:
            dict: A dictionary indicating the operation's completion status.
        """

        print(len(context.selected_objects), "selected object", context.selected_objects)
        if len(context.selected_objects) > 0 and (context.active_object.type in ["CURVE", "FONT"]):
            o1 = bpy.context.active_object

            bpy.context.object.data.resolution_u = 60
            duplicate()
            obj = context.active_object
            bpy.ops.object.convert(target="MESH")
            active_name("_temp_mesh")

            if self.opencurve:
                coords = []
                for v in obj.data.vertices:  # extract X,Y coordinates from the vertices data
                    coords.append((v.co.x, v.co.y))
                # convert coordinates to shapely LineString datastructure
                line = LineString(coords)
                remove_multiple("-converted")
                shapely_to_curve("-converted_curve", line, 0.0)
            shapes = curve_to_shapely(o1)

            for s in shapes.geoms:
                if s.boundary.type == "LineString":
                    loops = [s.boundary]
                else:
                    loops = s.boundary

                for ci, c in enumerate(loops):
                    if self.opencurve:
                        length = line.length
                    else:
                        length = c.length
                    print("Loop Length:", length)
                    if self.opencurve:
                        loop_length = line.length
                    else:
                        loop_length = c.length
                    print("Line Length:", loop_length)

                    joinery.distributed_interlock(
                        c,
                        length,
                        self.finger_size,
                        self.plate_thickness,
                        self.finger_tolerance,
                        self.finger_amount,
                        fixed_angle=self.fixed_angle,
                        tangent=self.tangent_angle,
                        closed=not self.opencurve,
                        type=self.interlock_type,
                    )

        else:
            location = bpy.context.scene.cursor.location
            joinery.single_interlock(
                self.finger_size,
                self.plate_thickness,
                self.finger_tolerance,
                location[0],
                location[1],
                self.fixed_angle,
                self.interlock_type,
                self.finger_amount,
            )

            bpy.context.scene.cursor.location = location
        return {"FINISHED"}


class CamCurveDrawer(Operator):
    """Generates Drawers"""  # by Alain Pelletier December 2021 inspired by The Drawinator

    bl_idname = "object.curve_drawer"
    bl_label = "Drawer"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    depth: FloatProperty(
        name="Drawer Depth",
        default=0.2,
        min=0,
        max=1.0,
        precision=4,
        unit="LENGTH",
    )
    width: FloatProperty(
        name="Drawer Width",
        default=0.125,
        min=0,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    height: FloatProperty(
        name="Drawer Height",
        default=0.07,
        min=0,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    finger_size: FloatProperty(
        name="Maximum Finger Size",
        default=0.015,
        min=0.005,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    finger_tolerance: FloatProperty(
        name="Finger Play Room",
        default=0.000045,
        min=0,
        max=0.003,
        precision=4,
        unit="LENGTH",
    )
    finger_inset: FloatProperty(
        name="Finger Inset",
        default=0.0,
        min=0.0,
        max=0.01,
        precision=4,
        unit="LENGTH",
    )
    drawer_plate_thickness: FloatProperty(
        name="Drawer Plate Thickness",
        default=0.00477,
        min=0.001,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    drawer_hole_diameter: FloatProperty(
        name="Drawer Hole Diameter",
        default=0.02,
        min=0.00001,
        max=0.5,
        precision=4,
        unit="LENGTH",
    )
    drawer_hole_offset: FloatProperty(
        name="Drawer Hole Offset",
        default=0.0,
        min=-0.5,
        max=0.5,
        precision=4,
        unit="LENGTH",
    )
    overcut: BoolProperty(
        name="Add Overcut",
        default=False,
    )
    overcut_diameter: FloatProperty(
        name="Overcut Tool Diameter",
        default=0.003175,
        min=-0.001,
        max=0.5,
        precision=4,
        unit="LENGTH",
    )

    def draw(self, context):
        """Draw the user interface properties for the object.

        This method is responsible for rendering the layout of various
        properties related to the object's dimensions and specifications. It
        adds properties such as depth, width, height, finger size, finger
        tolerance, finger inset, drawer plate thickness, drawer hole diameter,
        drawer hole offset, and overcut diameter to the layout. The overcut
        diameter property is only added if the overcut option is enabled.

        Args:
            context: The context in which the drawing occurs, typically containing
                information about the current state and environment.
        """

        layout = self.layout
        layout.prop(self, "depth")
        layout.prop(self, "width")
        layout.prop(self, "height")
        layout.prop(self, "finger_size")
        layout.prop(self, "finger_tolerance")
        layout.prop(self, "finger_inset")
        layout.prop(self, "drawer_plate_thickness")
        layout.prop(self, "drawer_hole_diameter")
        layout.prop(self, "drawer_hole_offset")
        layout.prop(self, "overcut")
        if self.overcut:
            layout.prop(self, "overcut_diameter")

    def execute(self, context):
        """Execute the drawer creation process in Blender.

        This method orchestrates the creation of a drawer by calculating the
        necessary dimensions for the finger joints, creating the base plate, and
        generating the drawer components such as the back, front, sides, and
        bottom. It utilizes various helper functions to perform operations like
        boolean differences and transformations to achieve the desired geometry.
        The method also handles the placement of the drawer components in the 3D
        space.

        Args:
            context (bpy.context): The Blender context that provides access to the current scene and
                objects.

        Returns:
            dict: A dictionary indicating the completion status of the operation,
                typically {'FINISHED'}.
        """

        height_finger_amt = int(joinery.finger_amount(self.height, self.finger_size))
        height_finger = (self.height + 0.0004) / height_finger_amt
        width_finger_amt = int(joinery.finger_amount(self.width, self.finger_size))
        width_finger = (self.width - self.finger_size) / width_finger_amt

        # create base
        joinery.create_base_plate(self.height, self.width, self.depth)
        bpy.context.object.data.resolution_u = 64
        bpy.context.scene.cursor.location = (0, 0, 0)

        joinery.vertical_finger(
            height_finger, self.drawer_plate_thickness, self.finger_tolerance, height_finger_amt
        )

        joinery.horizontal_finger(
            width_finger, self.drawer_plate_thickness, self.finger_tolerance, width_finger_amt * 2
        )
        make_active("_wfb")

        bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")

        #   make drawer back
        finger_pair = joinery.finger_pair(
            "_vfa", self.width - self.drawer_plate_thickness - self.finger_inset * 2, 0
        )
        make_active("_wfa")
        fronth = bpy.context.active_object
        make_active("_back")
        finger_pair.select_set(True)
        fronth.select_set(True)
        bpy.ops.object.curve_boolean(boolean_type="DIFFERENCE")
        remove_multiple("_finger_pair")
        active_name("drawer_back")
        remove_doubles()
        add_overcut(self.overcut_diameter, self.overcut)

        #   make drawer front
        bpy.ops.curve.primitive_bezier_circle_add(
            radius=self.drawer_hole_diameter / 2,
            enter_editmode=False,
            align="WORLD",
            location=(0, self.height + self.drawer_hole_offset, 0),
            scale=(1, 1, 1),
        )
        active_name("_circ")
        front_hole = bpy.context.active_object
        make_active("drawer_back")
        front_hole.select_set(True)
        bpy.ops.object.curve_boolean(boolean_type="DIFFERENCE")
        active_name("drawer_front")
        remove_doubles()
        add_overcut(self.overcut_diameter, self.overcut)

        #   place back and front side by side
        make_active("drawer_front")
        bpy.ops.transform.transform(mode="TRANSLATION", value=(0.0, 2 * self.height, 0.0, 0.0))
        make_active("drawer_back")

        bpy.ops.transform.transform(
            mode="TRANSLATION", value=(self.width + 0.01, 2 * self.height, 0.0, 0.0)
        )
        #   make side

        finger_pair = joinery.finger_pair("_vfb", self.depth - self.drawer_plate_thickness, 0)
        make_active("_side")
        finger_pair.select_set(True)
        fronth.select_set(True)
        bpy.ops.object.curve_boolean(boolean_type="DIFFERENCE")
        active_name("drawer_side")
        remove_doubles()
        add_overcut(self.overcut_diameter, self.overcut)
        remove_multiple("_finger_pair")

        #   make bottom
        make_active("_wfb")
        bpy.ops.object.duplicate_move(
            OBJECT_OT_duplicate={"linked": False, "mode": "TRANSLATION"},
            TRANSFORM_OT_translate={"value": (0, -self.drawer_plate_thickness / 2, 0.0)},
        )
        active_name("_wfb0")
        joinery.finger_pair("_wfb0", 0, self.depth - self.drawer_plate_thickness)
        active_name("_bot_fingers")

        difference("_bot", "_bottom")
        rotate(pi / 2)

        joinery.finger_pair(
            "_wfb0", 0, self.width - self.drawer_plate_thickness - self.finger_inset * 2
        )
        active_name("_bot_fingers")
        difference("_bot", "_bottom")

        active_name("drawer_bottom")

        remove_doubles()
        add_overcut(self.overcut_diameter, self.overcut)

        # cleanup all temp polygons
        remove_multiple("_")

        #   move side and bottom to location
        make_active("drawer_side")
        bpy.ops.transform.transform(
            mode="TRANSLATION",
            value=(self.depth / 2 + 3 * self.width / 2 + 0.02, 2 * self.height, 0.0, 0.0),
        )

        make_active("drawer_bottom")
        bpy.ops.transform.transform(
            mode="TRANSLATION",
            value=(self.depth / 2 + 3 * self.width / 2 + 0.02, self.width / 2, 0.0, 0.0),
        )

        select_multiple("drawer")
        return {"FINISHED"}


class CamCurvePuzzle(Operator):
    """Generates Puzzle Joints and Interlocks"""  # by Alain Pelletier December 2021

    bl_idname = "object.curve_puzzle"
    bl_label = "Puzzle Joints"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    diameter: FloatProperty(
        name="Tool Diameter",
        default=0.003175,
        min=0.001,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    finger_tolerance: FloatProperty(
        name="Finger Play Room",
        default=0.00005,
        min=0,
        max=0.003,
        precision=4,
        unit="LENGTH",
    )
    finger_amount: IntProperty(
        name="Finger Amount",
        default=1,
        min=0,
        max=100,
    )
    stem_size: IntProperty(
        name="Size of the Stem",
        default=2,
        min=1,
        max=200,
    )
    width: FloatProperty(
        name="Width",
        default=0.100,
        min=0.005,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    height: FloatProperty(
        name="Height or Thickness",
        default=0.025,
        min=0.005,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )

    angle: FloatProperty(
        name="Angle A",
        default=pi / 4,
        min=-10,
        max=10,
        step=500,
        subtype="ANGLE",
        unit="ROTATION",
    )
    angleb: FloatProperty(
        name="Angle B",
        default=pi / 4,
        min=-10,
        max=10,
        step=500,
        subtype="ANGLE",
        unit="ROTATION",
    )

    radius: FloatProperty(
        name="Arc Radius",
        default=0.025,
        min=0.005,
        max=5,
        precision=4,
        unit="LENGTH",
    )

    interlock_type: EnumProperty(
        name="Type of Shape",
        items=(
            ("JOINT", "Joint", "Puzzle Joint interlock"),
            ("BAR", "Bar", "Bar interlock"),
            ("ARC", "Arc", "Arc interlock"),
            ("MULTIANGLE", "Multi angle", "Multi angle joint"),
            ("CURVEBAR", "Arc Bar", "Arc Bar interlock"),
            ("CURVEBARCURVE", "Arc Bar Arc", "Arc Bar Arc interlock"),
            ("CURVET", "T curve", "T curve interlock"),
            ("T", "T Bar", "T Bar interlock"),
            ("CORNER", "Corner Bar", "Corner Bar interlock"),
            ("TILE", "Tile", "Tile interlock"),
            ("OPENCURVE", "Open Curve", "Corner Bar interlock"),
        ),
        description="Type of interlock",
        default="CURVET",
    )
    gender: EnumProperty(
        name="Type Gender",
        items=(
            ("MF", "Male-Receptacle", "Male and receptacle"),
            ("F", "Receptacle only", "Receptacle"),
            ("M", "Male only", "Male"),
        ),
        description="Type of interlock",
        default="MF",
    )
    base_gender: EnumProperty(
        name="Base Gender",
        items=(
            ("MF", "Male - Receptacle", "Male - Receptacle"),
            ("F", "Receptacle", "Receptacle"),
            ("M", "Male", "Male"),
        ),
        description="Type of interlock",
        default="M",
    )
    multiangle_gender: EnumProperty(
        name="Multiangle Gender",
        items=(
            ("MMF", "Male Male Receptacle", "M M F"),
            ("MFF", "Male Receptacle Receptacle", "M F F"),
        ),
        description="Type of interlock",
        default="MFF",
    )

    mitre: BoolProperty(
        name="Add Mitres",
        default=False,
    )

    twist_lock: BoolProperty(
        name="Add TwistLock",
        default=False,
    )
    twist_thick: FloatProperty(
        name="Twist Thickness",
        default=0.0047,
        min=0.001,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    twist_percent: FloatProperty(
        name="Twist Neck",
        default=0.3,
        min=0.1,
        max=0.9,
        precision=4,
    )
    twist_keep: BoolProperty(
        name="Keep Twist Holes",
        default=False,
    )
    twist_line: BoolProperty(
        name="Add Twist to Bar",
        default=False,
    )
    twist_line_amount: IntProperty(
        name="Amount of Separators",
        default=2,
        min=1,
        max=600,
    )
    twist_separator: BoolProperty(
        name="Add Twist Separator",
        default=False,
    )
    twist_separator_amount: IntProperty(
        name="Amount of Separators",
        default=2,
        min=2,
        max=600,
    )
    twist_separator_spacing: FloatProperty(
        name="Separator Spacing",
        default=0.025,
        min=-0.004,
        max=1.0,
        precision=4,
        unit="LENGTH",
    )
    twist_separator_edge_distance: FloatProperty(
        name="Separator Edge Distance",
        default=0.01,
        min=0.0005,
        max=0.1,
        precision=4,
        unit="LENGTH",
    )
    tile_x_amount: IntProperty(
        name="Amount of X Fingers",
        default=2,
        min=1,
        max=600,
    )
    tile_y_amount: IntProperty(
        name="Amount of Y Fingers",
        default=2,
        min=1,
        max=600,
    )
    interlock_amount: IntProperty(
        name="Interlock Amount on Curve",
        default=2,
        min=0,
        max=200,
    )
    overcut: BoolProperty(
        name="Add Overcut",
        default=False,
    )
    overcut_diameter: FloatProperty(
        name="Overcut Tool Diameter",
        default=0.003175,
        min=-0.001,
        max=0.5,
        precision=4,
        unit="LENGTH",
    )

    def draw(self, context):
        """Draws the user interface layout for interlock type properties.

        This method is responsible for creating and displaying the layout of
        various properties related to different interlock types in the user
        interface. It dynamically adjusts the layout based on the selected
        interlock type, allowing users to input relevant parameters such as
        dimensions, tolerances, and other characteristics specific to the chosen
        interlock type.

        Args:
            context: The context in which the layout is being drawn, typically
                provided by the user interface framework.

        Returns:
            None: This method does not return any value; it modifies the layout
                directly.
        """

        layout = self.layout
        layout.prop(self, "interlock_type")
        layout.label(text="Puzzle Joint Definition")
        layout.prop(self, "stem_size")
        layout.prop(self, "diameter")
        layout.prop(self, "finger_tolerance")
        if self.interlock_type == "TILE":
            layout.prop(self, "tile_x_amount")
            layout.prop(self, "tile_y_amount")
        else:
            layout.prop(self, "finger_amount")
        if self.interlock_type != "JOINT" and self.interlock_type != "TILE":
            layout.prop(self, "twist_lock")
            if self.twist_lock:
                layout.prop(self, "twist_thick")
                layout.prop(self, "twist_percent")
                layout.prop(self, "twist_keep")
                layout.prop(self, "twist_line")
                if self.twist_line:
                    layout.prop(self, "twist_line_amount")
                layout.prop(self, "twist_separator")
                if self.twist_separator:
                    layout.prop(self, "twist_separator_amount")
                    layout.prop(self, "twist_separator_spacing")
                    layout.prop(self, "twist_separator_edge_distance")

                if self.interlock_type == "OPENCURVE":
                    layout.prop(self, "interlock_amount")
            layout.separator()
            layout.prop(self, "height")

        if self.interlock_type == "BAR":
            layout.prop(self, "mitre")

        if self.interlock_type in ["ARC", "CURVEBARCURVE", "CURVEBAR", "MULTIANGLE", "CURVET"] or (
            self.interlock_type == "BAR" and self.mitre
        ):
            if self.interlock_type == "MULTIANGLE":
                layout.prop(self, "multiangle_gender")
            elif self.interlock_type != "CURVET":
                layout.prop(self, "gender")
            if not self.mitre:
                layout.prop(self, "radius")
            layout.prop(self, "angle")
            if self.interlock_type == "CURVEBARCURVE" or self.mitre:
                layout.prop(self, "angleb")

        if self.interlock_type in ["BAR", "CURVEBARCURVE", "CURVEBAR", "T", "CORNER", "CURVET"]:
            layout.prop(self, "gender")
            if self.interlock_type in ["T", "CURVET"]:
                layout.prop(self, "base_gender")
            if self.interlock_type == "CURVEBARCURVE":
                layout.label(text="Width includes 2 radius and thickness")
            layout.prop(self, "width")
        if self.interlock_type != "TILE":
            layout.prop(self, "overcut")
        if self.overcut:
            layout.prop(self, "overcut_diameter")

    def execute(self, context):
        """Execute the puzzle joinery process based on the provided context.

        This method processes the selected objects in the given context to
        perform various types of puzzle joinery operations. It first checks if
        there are any selected objects and if the active object is a curve. If
        so, it duplicates the object, applies transformations, and converts it
        to a mesh. The method then extracts vertex coordinates and performs
        different joinery operations based on the specified interlock type.
        Supported interlock types include 'FINGER', 'JOINT', 'BAR', 'ARC',
        'CURVEBARCURVE', 'CURVEBAR', 'MULTIANGLE', 'T', 'CURVET', 'CORNER',
        'TILE', and 'OPENCURVE'.

        Args:
            context (Context): The context containing selected objects and the active object.

        Returns:
            dict: A dictionary indicating the completion status of the operation.
        """

        curve_detected = False
        print(len(context.selected_objects), "selected object", context.selected_objects)
        if len(context.selected_objects) > 0 and context.active_object.type == "CURVE":
            curve_detected = True
            # bpy.context.object.data.resolution_u = 60
            duplicate()
            bpy.ops.object.transform_apply(location=True)
            obj = context.active_object
            bpy.ops.object.convert(target="MESH")
            bpy.context.active_object.name = "_tempmesh"

            coords = []
            for v in obj.data.vertices:  # extract X,Y coordinates from the vertices data
                coords.append((v.co.x, v.co.y))
            remove_multiple("_tmp")
            # convert coordinates to shapely LineString datastructure
            line = LineString(coords)
            remove_multiple("_")

        if self.interlock_type == "FINGER":
            puzzle_joinery.finger(self.diameter, self.finger_tolerance, stem=self.stem_size)
            rename("_puzzle", "receptacle")
            puzzle_joinery.finger(self.diameter, 0, stem=self.stem_size)
            rename("_puzzle", "finger")

        if self.interlock_type == "JOINT":
            if self.finger_amount == 0:  # cannot be 0 in joints
                self.finger_amount = 1
            puzzle_joinery.fingers(
                self.diameter, self.finger_tolerance, self.finger_amount, stem=self.stem_size
            )

        if self.interlock_type == "BAR":
            if not self.mitre:
                puzzle_joinery.bar(
                    self.width,
                    self.height,
                    self.diameter,
                    self.finger_tolerance,
                    self.finger_amount,
                    stem=self.stem_size,
                    twist=self.twist_lock,
                    tneck=self.twist_percent,
                    tthick=self.twist_thick,
                    twist_keep=self.twist_keep,
                    twist_line=self.twist_line,
                    twist_line_amount=self.twist_line_amount,
                    which=self.gender,
                )
            else:
                puzzle_joinery.mitre(
                    self.width,
                    self.height,
                    self.angle,
                    self.angleb,
                    self.diameter,
                    self.finger_tolerance,
                    self.finger_amount,
                    stem=self.stem_size,
                    twist=self.twist_lock,
                    tneck=self.twist_percent,
                    tthick=self.twist_thick,
                    which=self.gender,
                )
        elif self.interlock_type == "ARC":
            puzzle_joinery.arc(
                self.radius,
                self.height,
                self.angle,
                self.diameter,
                self.finger_tolerance,
                self.finger_amount,
                stem=self.stem_size,
                twist=self.twist_lock,
                tneck=self.twist_percent,
                tthick=self.twist_thick,
                which=self.gender,
            )
        elif self.interlock_type == "CURVEBARCURVE":
            puzzle_joinery.arc_bar_arc(
                self.width,
                self.radius,
                self.height,
                self.angle,
                self.angleb,
                self.diameter,
                self.finger_tolerance,
                self.finger_amount,
                stem=self.stem_size,
                twist=self.twist_lock,
                tneck=self.twist_percent,
                tthick=self.twist_thick,
                twist_keep=self.twist_keep,
                twist_line=self.twist_line,
                twist_line_amount=self.twist_line_amount,
                which=self.gender,
            )

        elif self.interlock_type == "CURVEBAR":
            puzzle_joinery.arc_bar(
                self.width,
                self.radius,
                self.height,
                self.angle,
                self.diameter,
                self.finger_tolerance,
                self.finger_amount,
                stem=self.stem_size,
                twist=self.twist_lock,
                tneck=self.twist_percent,
                tthick=self.twist_thick,
                twist_keep=self.twist_keep,
                twist_line=self.twist_line,
                twist_line_amount=self.twist_line_amount,
                which=self.gender,
            )

        elif self.interlock_type == "MULTIANGLE":
            puzzle_joinery.multiangle(
                self.radius,
                self.height,
                pi / 3,
                self.diameter,
                self.finger_tolerance,
                self.finger_amount,
                stem=self.stem_size,
                twist=self.twist_lock,
                tneck=self.twist_percent,
                tthick=self.twist_thick,
                combination=self.multiangle_gender,
            )

        elif self.interlock_type == "T":
            puzzle_joinery.t(
                self.width,
                self.height,
                self.diameter,
                self.finger_tolerance,
                self.finger_amount,
                stem=self.stem_size,
                twist=self.twist_lock,
                tneck=self.twist_percent,
                tthick=self.twist_thick,
                combination=self.gender,
                base_gender=self.base_gender,
            )

        elif self.interlock_type == "CURVET":
            puzzle_joinery.curved_t(
                self.width,
                self.height,
                self.radius,
                self.diameter,
                self.finger_tolerance,
                self.finger_amount,
                stem=self.stem_size,
                twist=self.twist_lock,
                tneck=self.twist_percent,
                tthick=self.twist_thick,
                combination=self.gender,
                base_gender=self.base_gender,
            )

        elif self.interlock_type == "CORNER":
            puzzle_joinery.t(
                self.width,
                self.height,
                self.diameter,
                self.finger_tolerance,
                self.finger_amount,
                stem=self.stem_size,
                twist=self.twist_lock,
                tneck=self.twist_percent,
                tthick=self.twist_thick,
                combination=self.gender,
                base_gender=self.base_gender,
                corner=True,
            )

        elif self.interlock_type == "TILE":
            puzzle_joinery.tile(
                self.diameter,
                self.finger_tolerance,
                self.tile_x_amount,
                self.tile_y_amount,
                stem=self.stem_size,
            )

        elif self.interlock_type == "OPENCURVE" and curve_detected:
            puzzle_joinery.open_curve(
                line,
                self.height,
                self.diameter,
                self.finger_tolerance,
                self.finger_amount,
                stem=self.stem_size,
                twist=self.twist_lock,
                t_neck=self.twist_percent,
                t_thick=self.twist_thick,
                which=self.gender,
                twist_amount=self.interlock_amount,
                twist_keep=self.twist_keep,
            )

        remove_doubles()
        add_overcut(self.overcut_diameter, self.overcut)

        if self.twist_lock and self.twist_separator:
            joinery.interlock_twist_separator(
                self.height,
                self.twist_thick,
                self.twist_separator_amount,
                self.twist_separator_spacing,
                self.twist_separator_edge_distance,
                finger_play=self.finger_tolerance,
                percentage=self.twist_percent,
            )
            remove_doubles()
            add_overcut(self.overcut_diameter, self.overcut)
        return {"FINISHED"}


class CamCurveGear(Operator):
    """Generates Involute Gears"""

    # // version 1.1 by Leemon Baird, 2011, Leemon@Leemon.com
    # http://www.thingiverse.com/thing:5505
    # # ported by Alain Pelletier January 2022

    bl_idname = "object.curve_gear"
    bl_label = "Gears"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    tooth_spacing: FloatProperty(
        name="Distance per Tooth",
        default=0.010,
        min=0.01,
        max=1.0,
        precision=4,
        unit="LENGTH",
    )

    tooth_amount: IntProperty(
        name="Amount of Teeth",
        default=7,
        min=6,  # min=4,
        max=32,
    )

    spoke_amount: IntProperty(
        name="Amount of Spokes",
        default=4,
        min=0,
    )

    hole_diameter: FloatProperty(
        name="Hole Diameter",
        default=0.003175,
        min=0.00001,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    rim_size: FloatProperty(
        name="Rim Size",
        default=0.003175,
        min=0,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    hub_diameter: FloatProperty(
        name="Hub Diameter",
        default=0.005,
        min=0,
        max=3.0,
        precision=4,
        unit="LENGTH",
    )
    pressure_angle: FloatProperty(
        name="Pressure Angle",
        default=radians(20),
        min=0.001,
        max=pi / 2,
        precision=4,
        step=100,
        subtype="ANGLE",
        unit="ROTATION",
    )
    clearance: FloatProperty(
        name="Clearance",
        default=0.00,
        min=0,
        max=0.1,
        precision=4,
        unit="LENGTH",
    )
    backlash: FloatProperty(
        name="Backlash",
        default=0.0,
        min=0.0,
        max=0.1,
        precision=4,
        unit="LENGTH",
    )
    rack_height: FloatProperty(
        name="Rack Height",
        default=0.012,
        min=0.001,
        max=1,
        precision=4,
        unit="LENGTH",
    )
    rack_tooth_per_hole: IntProperty(
        name="Teeth per Mounting Hole",
        default=7,
        min=2,
    )
    gear_type: EnumProperty(
        name="Type of Gear",
        items=(("PINION", "Pinion", "Circular Gear"), ("RACK", "Rack", "Straight Rack")),
        description="Type of gear",
        default="PINION",
    )

    def draw(self, context):
        """Draw the user interface properties for gear settings.

        This method sets up the layout for various gear parameters based on the
        selected gear type. It dynamically adds properties to the layout for
        different gear types, allowing users to input specific values for gear
        design. The properties include gear type, tooth spacing, tooth amount,
        hole diameter, pressure angle, and backlash. Additional properties are
        displayed if the gear type is 'PINION' or 'RACK'.

        Args:
            context: The context in which the layout is being drawn.
        """

        layout = self.layout
        layout.prop(self, "gear_type")
        layout.prop(self, "tooth_spacing")
        layout.prop(self, "tooth_amount")
        layout.prop(self, "hole_diameter")
        layout.prop(self, "pressure_angle")
        layout.prop(self, "backlash")
        if self.gear_type == "PINION":
            layout.prop(self, "clearance")
            layout.prop(self, "spoke_amount")
            layout.prop(self, "rim_size")
            layout.prop(self, "hub_diameter")
        elif self.gear_type == "RACK":
            layout.prop(self, "rack_height")
            layout.prop(self, "rack_tooth_per_hole")

    def execute(self, context):
        """Execute the gear generation process based on the specified gear type.

        This method checks the type of gear to be generated (either 'PINION' or
        'RACK') and calls the appropriate function from the `involute_gear`
        module to create the gear or rack with the specified parameters. The
        parameters include tooth spacing, number of teeth, hole diameter,
        pressure angle, clearance, backlash, rim size, hub diameter, and spoke
        amount for pinion gears, and additional parameters for rack gears.

        Args:
            context: The context in which the execution is taking place.

        Returns:
            dict: A dictionary indicating that the operation has finished with a key
                'FINISHED'.
        """

        if self.gear_type == "PINION":
            involute_gear.gear(
                mm_per_tooth=self.tooth_spacing,
                number_of_teeth=self.tooth_amount,
                hole_diameter=self.hole_diameter,
                pressure_angle=self.pressure_angle,
                clearance=self.clearance,
                backlash=self.backlash,
                rim_size=self.rim_size,
                hub_diameter=self.hub_diameter,
                spokes=self.spoke_amount,
            )
        elif self.gear_type == "RACK":
            involute_gear.rack(
                mm_per_tooth=self.tooth_spacing,
                number_of_teeth=self.tooth_amount,
                pressure_angle=self.pressure_angle,
                height=self.rack_height,
                backlash=self.backlash,
                tooth_per_hole=self.rack_tooth_per_hole,
                hole_diameter=self.hole_diameter,
            )

        return {"FINISHED"}
