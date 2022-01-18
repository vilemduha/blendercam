# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2019 Devon (Gorialis) R

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Create a Blender curve from a 3D parametric function.
This allows for a 3D plot to be made of the function, which can be converted into a mesh.

I have documented the inner workings here, but if you're not interested and just want to
suit this to your own function, scroll down to the bottom and edit the `f(t)` function and
the iteration count to your liking.

This code has been checked to work on Blender 2.92.

"""

import math
from math import sin, cos, pi
import bmesh
import bpy
from mathutils import Vector


def derive_bezier_handles(a, b, c, d, tb, tc):
    """
    Derives bezier handles by using the start and end of the curve with 2 intermediate
    points to use for interpolation.

    :param a:
        The start point.
    :param b:
        The first mid-point, located at `tb` on the bezier segment, where 0 < `tb` < 1.
    :param c:
        The second mid-point, located at `tc` on the bezier segment, where 0 < `tc` < 1.
    :param d:
        The end point.
    :param tb:
        The position of the first point in the bezier segment.
    :param tc:
        The position of the second point in the bezier segment.
    :return:
        A tuple of the two intermediate handles, that is, the right handle of the start point
        and the left handle of the end point.
    """

    # Calculate matrix coefficients
    matrix_a = 3 * math.pow(1 - tb, 2) * tb
    matrix_b = 3 * (1 - tb) * math.pow(tb, 2)
    matrix_c = 3 * math.pow(1 - tc, 2) * tc
    matrix_d = 3 * (1 - tc) * math.pow(tc, 2)

    # Calculate the matrix determinant
    matrix_determinant = 1 / ((matrix_a * matrix_d) - (matrix_b * matrix_c))

    # Calculate the components of the target position vector
    final_b = b - (math.pow(1 - tb, 3) * a) - (math.pow(tb, 3) * d)
    final_c = c - (math.pow(1 - tc, 3) * a) - (math.pow(tc, 3) * d)

    # Multiply the inversed matrix with the position vector to get the handle points
    bezier_b = matrix_determinant * ((matrix_d * final_b) + (-matrix_b * final_c))
    bezier_c = matrix_determinant * ((-matrix_c * final_b) + (matrix_a * final_c))

    # Return the handle points
    return bezier_b, bezier_c


def create_parametric_curve(
        function,
        *args,
        min: float = 0.0,
        max: float = 1.0,
        use_cubic: bool = True,
        iterations: int = 8,
        resolution_u: int = 10,
        **kwargs):
    """
    Creates a Blender bezier curve object from a parametric function.
    This "plots" the function in 3D space from `min <= t <= max`.

    :param function:
        The function to plot as a Blender curve.

        This function should take in a float value of `t` and return a 3-item tuple or list
        of the X, Y and Z coordinates at that point:
        `function(t) -> (x, y, z)`

        `t` is plotted according to `min <= t <= max`, but if `use_cubic` is enabled, this function
        needs to be able to take values less than `min` and greater than `max`.
    :param *args:
        Additional positional arguments to be passed to the plotting function.
        These are not required.
    :param use_cubic:
        Whether or not to calculate the cubic bezier handles as to create smoother splines.
        Turning this off reduces calculation time and memory usage, but produces more jagged
        splines with sharp edges.
    :param iterations:
        The 'subdivisions' of the parametric to plot.
        Setting this higher produces more accurate curves but increases calculation time and
        memory usage.
    :param resolution_u:
        The preview surface resolution in the U direction of the bezier curve.
        Setting this to a higher value produces smoother curves in rendering, and increases the
        number of vertices the curve will get if converted into a mesh (e.g. for edge looping)
    :param **kwargs:
        Additional keyword arguments to be passed to the plotting function.
        These are not required.
    :return:
        The new Blender object.
    """

    # Create the Curve to populate with points.
    curve = bpy.data.curves.new('Parametric', type='CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 30

    # Add a new spline and give it the appropriate amount of points
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(iterations)

    if use_cubic:
        points = [
            function(((i - 3) / (3 * iterations)) * (max - min) + min, *args, **kwargs)
            for i in range((3 * (iterations + 2)) + 1)
        ]

        # Convert intermediate points into handles
        for i in range(iterations + 2):
            a = points[(3 * i)]
            b = points[(3 * i) + 1]
            c = points[(3 * i) + 2]
            d = points[(3 * i) + 3]

            bezier_bx, bezier_cx = derive_bezier_handles(a[0], b[0], c[0], d[0], 1 / 3, 2 / 3)
            bezier_by, bezier_cy = derive_bezier_handles(a[1], b[1], c[1], d[1], 1 / 3, 2 / 3)
            bezier_bz, bezier_cz = derive_bezier_handles(a[2], b[2], c[2], d[2], 1 / 3, 2 / 3)

            points[(3 * i) + 1] = (bezier_bx, bezier_by, bezier_bz)
            points[(3 * i) + 2] = (bezier_cx, bezier_cy, bezier_cz)

        # Set point coordinates and handles
        for i in range(iterations + 1):
            spline.bezier_points[i].co = points[3 * (i + 1)]

            spline.bezier_points[i].handle_left_type = 'FREE'
            spline.bezier_points[i].handle_left = Vector(points[(3 * (i + 1)) - 1])

            spline.bezier_points[i].handle_right_type = 'FREE'
            spline.bezier_points[i].handle_right = Vector(points[(3 * (i + 1)) + 1])

    else:
        points = [function(i / iterations, *args, **kwargs) for i in range(iterations + 1)]

        # Set point coordinates, disable handles
        for i in range(iterations + 1):
            spline.bezier_points[i].co = points[i]
            spline.bezier_points[i].handle_left_type = 'VECTOR'
            spline.bezier_points[i].handle_right_type = 'VECTOR'

    # Create the Blender object and link it to the scene
    curve_object = bpy.data.objects.new('Parametric', curve)
    context = bpy.context
    scene = context.scene
    link_object = scene.collection.objects.link 
    link_object(curve_object)

    # Return the new object
    return curve_object


def make_edge_loops(*objects):
    """
    Turns a set of Curve objects into meshes, creates vertex groups,
    and merges them into a set of edge loops.

    :param *objects:
        Positional arguments for each object to be converted and merged.
    """

    mesh_objects = []
    vertex_groups = []

    # Convert all curves to meshes
    for obj in objects:
        # Unlink old object
        unlink_object(obj)

        # Convert curve to a mesh
        if bpy.app.version >= (2, 80):
            new_mesh = obj.to_mesh().copy()
        else:
            new_mesh = obj.to_mesh(scene, False, 'PREVIEW')

        # Store name and matrix, then fully delete the old object
        name = obj.name
        matrix = obj.matrix_world
        bpy.data.objects.remove(obj)

        # Attach the new mesh to a new object with the old name
        new_object = bpy.data.objects.new(name, new_mesh)
        new_object.matrix_world = matrix

        # Make a new vertex group from all vertices on this mesh
        vertex_group = new_object.vertex_groups.new(name=name)
        vertex_group.add(range(len(new_mesh.vertices)), 1.0, 'ADD')

        vertex_groups.append(vertex_group)

        # Link our new object
        link_object(new_object)

        # Add it to our list
        mesh_objects.append(new_object)

    # Make a new context
    ctx = context.copy()

    # Select our objects in the context
    ctx['active_object'] = mesh_objects[0]
    ctx['selected_objects'] = mesh_objects
    if bpy.app.version >= (2, 80):
        ctx['selected_editable_objects'] = mesh_objects
    else:
        ctx['selected_editable_bases'] = [scene.object_bases[o.name] for o in mesh_objects]

    # Join them together
    bpy.ops.object.join(ctx)

