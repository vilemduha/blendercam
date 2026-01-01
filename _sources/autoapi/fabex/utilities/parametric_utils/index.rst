fabex.utilities.parametric_utils
================================

.. py:module:: fabex.utilities.parametric_utils

.. autoapi-nested-parse::

   Fabex 'parametric.py' © 2019 Devon (Gorialis) R

   MIT License

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

   Summary:
   Create a Blender curve from a 3D parametric function.
   This allows for a 3D plot to be made of the function, which can be converted into a mesh.

   I have documented the inner workings here, but if you're not interested and just want to
   suit this to your own function, scroll down to the bottom and edit the `f(t)` function and
   the iteration count to your liking.

   This code has been checked to work on Blender 2.92.



Functions
---------

.. autoapisummary::

   fabex.utilities.parametric_utils.derive_bezier_handles
   fabex.utilities.parametric_utils.create_parametric_curve
   fabex.utilities.parametric_utils.make_edge_loops


Module Contents
---------------

.. py:function:: derive_bezier_handles(a, b, c, d, tb, tc)

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


.. py:function:: create_parametric_curve(function, *args, min: float = 0.0, max: float = 1.0, use_cubic: bool = True, iterations: int = 8, resolution_u: int = 10, **kwargs)

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


.. py:function:: make_edge_loops(*objects)

   Turns a set of Curve objects into meshes, creates vertex groups,
   and merges them into a set of edge loops.

   :param *objects:
       Positional arguments for each object to be converted and merged.


