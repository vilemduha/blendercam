"""Fabex 'image_utils.py' © 2012 Vilem Novak

Functions to render, save, convert and analyze image data.
"""

from math import (
    acos,
    ceil,
    cos,
    floor,
    pi,
    radians,
    sin,
    tan,
)
from typing import Optional
import os
import random
import time

import numpy

import bpy

try:
    import bl_ext.blender_org.simplify_curves_plus as curve_simplify
except ImportError:
    pass

from mathutils import (
    Euler,
    Vector,
)

from .async_utils import progress_async
from .chunk_utils import parent_child_distance, chunks_to_shapely
from .simple_utils import (
    progress,
    get_cache_path,
)
from .numba_utils import (
    jit,
    prange,
)


def numpy_save(a, iname):
    """Save a NumPy array as an image file in OpenEXR format.

    This function converts a NumPy array into an image and saves it using
    Blender's rendering capabilities. It sets the image format to OpenEXR
    with black and white color mode and a color depth of 32 bits. The image
    is saved to the specified filename.

    Args:
        a (numpy.ndarray): The NumPy array to be converted and saved as an image.
        iname (str): The file path where the image will be saved.
    """

    inamebase = bpy.path.basename(iname)

    i = numpy_to_image(a, inamebase)

    r = bpy.context.scene.render

    r.image_settings.file_format = "OPEN_EXR"
    r.image_settings.color_mode = "BW"
    r.image_settings.color_depth = "32"

    i.save_render(iname)


def get_circle(r, z):
    """Generate a 2D array representing a circle.

    This function creates a 2D NumPy array filled with a specified value for
    points that fall within a circle of a given radius. The circle is
    centered in the array, and the function uses the Euclidean distance to
    determine which points are inside the circle. The resulting array has
    dimensions that are twice the radius, ensuring that the entire circle
    fits within the array.

    Args:
        r (int): The radius of the circle.
        z (float): The value to fill the points inside the circle.

    Returns:
        numpy.ndarray: A 2D array where points inside the circle are filled
        with the value `z`, and points outside are filled with -10.
    """

    car = numpy.full(shape=(r * 2, r * 2), fill_value=-10, dtype=numpy.double)
    res = 2 * r
    m = r
    v = Vector((0, 0, 0))
    for a in range(0, res):
        v.x = a + 0.5 - m
        for b in range(0, res):
            v.y = b + 0.5 - m
            if v.length <= r:
                car[a, b] = z
    return car


def get_circle_binary(r):
    """Generate a binary representation of a circle in a 2D grid.

    This function creates a 2D boolean array where the elements inside a
    circle of radius `r` are set to `True`, and the elements outside the
    circle are set to `False`. The circle is centered in the middle of the
    array, which has dimensions of (2*r, 2*r). The function iterates over
    each point in the grid and checks if it lies within the specified
    radius.

    Args:
        r (int): The radius of the circle.

    Returns:
        numpy.ndarray: A 2D boolean array representing the circle.
    """

    car = numpy.full(shape=(r * 2, r * 2), fill_value=False, dtype=bool)
    res = 2 * r
    m = r
    v = Vector((0, 0, 0))
    for a in range(0, res):
        v.x = a + 0.5 - m
        for b in range(0, res):
            v.y = b + 0.5 - m
            if v.length <= r:
                car.itemset((a, b), True)
    return car


# get cutters for the z-buffer image method


def numpy_to_image(a: numpy.ndarray, iname: str) -> bpy.types.Image:
    """Convert a NumPy array to a Blender image.

    This function takes a NumPy array and converts it into a Blender image.
    It first checks if an image with the specified name and dimensions
    already exists in Blender. If it does not exist, a new image is created
    with the specified name and dimensions. The pixel data from the NumPy
    array is then reshaped and assigned to the image's pixel buffer.

    Args:
        a (numpy.ndarray): A 2D NumPy array representing the image data.
        iname (str): The name to assign to the created or found image.

    Returns:
        bpy.types.Image: The Blender image object that was created or found.
    """

    t = time.time()

    width = a.shape[0]
    height = a.shape[1]
    # Based on the Blender source code: source/blender/makesdna/DNA_ID.h. MAX_ID_NAME=64
    # is defining the maximum length of the id and we need to subtract four letters for
    # suffix as Blender seems to use the ".%03d" pattern to avoid creating duplicate ids.
    iname_59 = iname[:59]

    print(f"numpy_to_image: iname:{iname}, width:{width}, height:{height}")

    def find_image(name: str, width: int, heigh: int) -> Optional[bpy.types.Image]:
        if name in bpy.data.images:
            image = bpy.data.images[name]

            if image.size[0] == width and image.size[1] == height:
                return image

        return None

    image = find_image(iname, width, height) or find_image(iname_59, width, height)

    if image is None:
        print(f"numpy_to_image: Creating a new image:{iname_59}")
        result = bpy.ops.image.new(
            name=iname_59,
            width=width,
            height=height,
            color=(0, 0, 0, 1),
            alpha=True,
            generated_type="BLANK",
            float=True,
        )
        print(f"numpy_to_image: Image creation result:{result}")

        # If 'iname_59' id didn't exist previously, then
        # it should have been created without changing its id.
        image = bpy.data.images[iname_59]

    a = a.swapaxes(0, 1)
    a = a.reshape(width * height)
    a = a.repeat(4)
    a[3::4] = 1

    image.pixels[:] = a[:]  # this gives big speedup!

    print(f"numpy_to_image: Time:{str(time.time() - t)}")

    return image


def image_to_numpy(i):
    """Convert a Blender image to a NumPy array.

    This function takes a Blender image object and converts its pixel data
    into a NumPy array. It retrieves the pixel data, reshapes it, and swaps
    the axes to match the expected format for further processing. The
    function also measures the time taken for the conversion and prints it
    to the console.

    Args:
        i (Image): A Blender image object containing pixel data.

    Returns:
        numpy.ndarray: A 2D NumPy array representing the image pixels.
    """

    t = time.time()

    width = i.size[0]
    height = i.size[1]
    na = numpy.full(shape=(width * height * 4,), fill_value=-10, dtype=numpy.double)

    p = i.pixels[:]
    # these 2 lines are about 15% faster than na[:]=i.pixels[:].... whyyyyyyyy!!?!?!?!?!
    # Blender image data access is evil.
    na[:] = p
    na = na[::4]
    na = na.reshape(height, width)
    na = na.swapaxes(0, 1)

    print("\nTime of Image to Numpy " + str(time.time() - t))
    return na


@jit(nopython=True, parallel=True, fastmath=False, cache=True)
def _offset_inner_loop(y1, y2, cutterArrayNan, cwidth, sourceArray, width, height, comparearea):
    """Offset the inner loop for processing a specified area in a 2D array.

    This function iterates over a specified range of rows and columns in a
    2D array, calculating the maximum value from a source array combined
    with a cutter array for each position in the defined area. The results
    are stored in the comparearea array, which is updated with the maximum
    values found.

    Args:
        y1 (int): The starting index for the row iteration.
        y2 (int): The ending index for the row iteration.
        cutterArrayNan (numpy.ndarray): A 2D array used for modifying the source array.
        cwidth (int): The width of the area to consider for the maximum calculation.
        sourceArray (numpy.ndarray): The source 2D array from which maximum values are derived.
        width (int): The width of the source array.
        height (int): The height of the source array.
        comparearea (numpy.ndarray): A 2D array where the calculated maximum values are stored.

    Returns:
        None: This function modifies the comparearea in place and does not return a
            value.
    """

    for y in prange(y1, y2):
        for x in range(0, width - cwidth):
            comparearea[x, y] = numpy.nanmax(
                sourceArray[x : x + cwidth, y : y + cwidth] + cutterArrayNan
            )


async def offset_area(o, samples):
    """Offsets the whole image with the cutter and skin offsets.

    This function modifies the offset image based on the provided cutter and
    skin offsets. It calculates the dimensions of the source and cutter
    arrays, initializes an offset image, and processes the image in
    segments. The function handles the inversion of the source array if
    specified and updates the offset image accordingly. Progress is reported
    asynchronously during processing.

    Args:
        o: An object containing properties such as `update_offset_image_tag`,
            `min`, `max`, `inverse`, and `offset_image`.
        samples (numpy.ndarray): A 2D array representing the source image data.

    Returns:
        numpy.ndarray: The updated offset image after applying the cutter and skin offsets.
    """
    if o.update_offset_image_tag:
        minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z

        sourceArray = samples
        cutterArray = get_cutter_array(o, o.optimisation.pixsize)

        # progress('image size', sourceArray.shape)

        width = len(sourceArray)
        height = len(sourceArray[0])
        cwidth = len(cutterArray)
        o.offset_image = numpy.full(shape=(width, height), fill_value=-10.0, dtype=numpy.double)

        t = time.time()

        m = int(cwidth / 2.0)

        if o.inverse:
            sourceArray = -sourceArray + minz
        comparearea = o.offset_image[m : width - cwidth + m, m : height - cwidth + m]
        # i=0
        cutterArrayNan = numpy.where(
            cutterArray > -10, cutterArray, numpy.full(cutterArray.shape, numpy.nan)
        )
        for y in range(0, 10):
            y1 = (y * comparearea.shape[1]) // 10
            y2 = ((y + 1) * comparearea.shape[1]) // 10
            _offset_inner_loop(
                y1, y2, cutterArrayNan, cwidth, sourceArray, width, height, comparearea
            )
            await progress_async("Offset Depth Image", int((y2 * 100) / comparearea.shape[1]))
        o.offset_image[m : width - cwidth + m, m : height - cwidth + m] = comparearea

        print("\nOffset Image Time " + str(time.time() - t))

        o.update_offset_image_tag = False
    return o.offset_image


def dilate_array(ar, cycles):
    """Dilate a binary array using a specified number of cycles.

    This function performs a dilation operation on a 2D binary array. For
    each cycle, it updates the array by applying a logical OR operation
    between the current array and its neighboring elements. The dilation
    effect expands the boundaries of the foreground (True) pixels in the
    binary array.

    Args:
        ar (numpy.ndarray): A 2D binary array (numpy array) where
            dilation will be applied.
        cycles (int): The number of dilation cycles to perform.

    Returns:
        None: The function modifies the input array in place and does not
            return a value.
    """

    for c in range(cycles):
        ar[1:-1, :] = numpy.logical_or(ar[1:-1, :], ar[:-2, :])
        ar[:, 1:-1] = numpy.logical_or(ar[:, 1:-1], ar[:, :-2])


async def crazy_path(o):
    """Execute a greedy adaptive algorithm for path planning.

    This function prepares an area based on the provided object `o`,
    calculates the dimensions of the area, and initializes a mill image and
    cutter array. The dimensions are determined by the maximum and minimum
    coordinates of the object, adjusted by the simulation detail and border
    width. The function is currently a stub and requires further
    implementation.

    Args:
        o (object): An object containing properties such as max, min, optimisation, and
            borderwidth.

    Returns:
        None: This function does not return a value.
    """

    # TODO: try to do something with this  stuff, it's just a stub. It should be a greedy adaptive algorithm.
    #  started another thing below.
    await prepare_area(o)
    sx = o.max.x - o.min.x
    sy = o.max.y - o.min.y

    resx = ceil(sx / o.optimisation.simulation_detail) + 2 * o.borderwidth
    resy = ceil(sy / o.optimisation.simulation_detail) + 2 * o.borderwidth

    o.millimage = numpy.full(shape=(resx, resy), fill_value=0.0, dtype=numpy.float)
    # getting inverted cutter
    o.cutterArray = -get_cutter_array(o, o.optimisation.simulation_detail)


def build_stroke(start, end, cutterArray):
    """Build a stroke array based on start and end points.

    This function generates a 2D stroke array that represents a stroke from
    a starting point to an ending point. It calculates the length of the
    stroke and creates a grid that is filled based on the positions defined
    by the start and end coordinates. The function uses a cutter array to
    determine how the stroke interacts with the grid.

    Args:
        start (tuple): A tuple representing the starting coordinates (x, y, z).
        end (tuple): A tuple representing the ending coordinates (x, y, z).
        cutterArray: An object that contains size information used to modify
            the stroke array.

    Returns:
        numpy.ndarray: A 2D array representing the stroke, filled with
            calculated values based on the input parameters.
    """

    strokelength = max(abs(end[0] - start[0]), abs(end[1] - start[1]))
    size_x = abs(end[0] - start[0]) + cutterArray.size[0]
    size_y = abs(end[1] - start[1]) + cutterArray.size[0]
    r = cutterArray.size[0] / 2

    strokeArray = numpy.full(shape=(size_x, size_y), fill_value=-10.0, dtype=numpy.float)
    samplesx = numpy.round(numpy.linspace(start[0], end[0], strokelength))
    samplesy = numpy.round(numpy.linspace(start[1], end[1], strokelength))
    samplesz = numpy.round(numpy.linspace(start[2], end[2], strokelength))

    for i in range(0, len(strokelength)):
        strokeArray[
            samplesx[i] - r : samplesx[i] + r, samplesy[i] - r : samplesy[i] + r
        ] = numpy.maximum(
            strokeArray[samplesx[i] - r : samplesx[i] + r, samplesy[i] - r : samplesy[i] + r],
            cutterArray + samplesz[i],
        )
    return strokeArray


def test_stroke():
    pass


def apply_stroke():
    pass


def test_stroke_binary(img, stroke):
    pass  # buildstroke()


def get_sample_image(s, sarray, minz):
    """Get a sample image value from a 2D array based on given coordinates.

    This function retrieves a value from a 2D array by performing bilinear
    interpolation based on the provided coordinates. It checks if the
    coordinates are within the bounds of the array and calculates the
    interpolated value accordingly. If the coordinates are out of bounds, it
    returns -10.

    Args:
        s (tuple): A tuple containing the x and y coordinates (float).
        sarray (numpy.ndarray): A 2D array from which to sample the image values.
        minz (float): A minimum threshold value (not used in the current implementation).

    Returns:
        float: The interpolated value from the 2D array, or -10 if the coordinates are
            out of bounds.
    """

    x = s[0]
    y = s[1]
    if (x < 0 or x > len(sarray) - 1) or (y < 0 or y > len(sarray[0]) - 1):
        return -10
    else:
        minx = floor(x)
        maxx = minx + 1
        miny = floor(y)
        maxy = miny + 1
        s1a = sarray[minx, miny]
        s2a = sarray[maxx, miny]
        s1b = sarray[minx, maxy]
        s2b = sarray[maxx, maxy]
        # s1a = sarray.item(minx, miny)  # most optimal access to array so far
        # s2a = sarray.item(maxx, miny)
        # s1b = sarray.item(minx, maxy)
        # s2b = sarray.item(maxx, maxy)

        sa = s1a * (maxx - x) + s2a * (x - minx)
        sb = s1b * (maxx - x) + s2b * (x - minx)
        z = sa * (maxy - y) + sb * (y - miny)
        return z


def get_resolution(o):
    """Calculate the resolution based on the dimensions of an object.

    This function computes the resolution in both x and y directions by
    determining the width and height of the object, adjusting for pixel size
    and border width. The resolution is calculated by dividing the
    dimensions by the pixel size and adding twice the border width to each
    dimension.

    Args:
        o (object): An object with attributes `max`, `min`, `optimisation`,
            and `borderwidth`. The `max` and `min` attributes should
            have `x` and `y` properties representing the coordinates,
            while `optimisation` should have a `pixsize` attribute.

    Returns:
        None: This function does not return a value; it performs calculations
            to determine resolution.
    """

    sx = o.max.x - o.min.x
    sy = o.max.y - o.min.y

    resx = ceil(sx / o.optimisation.pixsize) + 2 * o.borderwidth
    resy = ceil(sy / o.optimisation.pixsize) + 2 * o.borderwidth


# this basically renders blender zbuffer and makes it accessible by saving & loading it again.
# that's because blender doesn't allow accessing pixels in render :(


def _backup_render_settings(pairs):
    """Backup the render settings of Blender objects.

    This function iterates over a list of pairs consisting of owners and
    their corresponding structure names. It retrieves the properties of each
    structure and stores them in a backup list. If the structure is a
    Blender object, it saves all its properties that do not start with an
    underscore. For simple values, it directly appends them to the
    properties list. This is useful for preserving render settings that
    Blender does not allow direct access to during rendering.

    Args:
        pairs (list): A list of tuples where each tuple contains an owner and a structure
            name.

    Returns:
        list: A list containing the backed-up properties of the specified Blender
            objects.
    """

    properties = []
    for owner, struct_name in pairs:
        obj = getattr(owner, struct_name)
        if isinstance(obj, bpy.types.bpy_struct):
            # structure, backup all properties
            obj_value = {}
            for k in dir(obj):
                if not k.startswith("_"):
                    obj_value[k] = getattr(obj, k)
            properties.append(obj_value)
        else:
            # simple value
            properties.append(obj)


def _restore_render_settings(pairs, properties):
    """Restore render settings for a given owner and structure.

    This function takes pairs of owners and structure names along with their
    corresponding properties. It iterates through these pairs, retrieves the
    appropriate object from the owner using the structure name, and sets the
    properties on the object. If the object is an instance of
    `bpy.types.bpy_struct`, it updates its attributes; otherwise, it
    directly sets the value on the owner.

    Args:
        pairs (list): A list of tuples where each tuple contains an owner and a structure
            name.
        properties (list): A list of dictionaries containing property names and their corresponding
            values.
    """

    for (owner, struct_name), obj_value in zip(pairs, properties):
        obj = getattr(owner, struct_name)
        if isinstance(obj, bpy.types.bpy_struct):
            for k, v in obj_value.items():
                setattr(obj, k, v)
        else:
            setattr(owner, struct_name, obj_value)


def render_sample_image(o):
    """Render a sample image based on the provided object settings.

    This function generates a Z-buffer image for a given object by either
    rendering it from scratch or loading an existing image from the cache.
    It handles different geometry sources and applies various settings to
    ensure the image is rendered correctly. The function also manages backup
    and restoration of render settings to maintain the scene's integrity
    during the rendering process.

    Args:
        o (object): An object containing various properties and settings

    Returns:
        numpy.ndarray: The generated or loaded Z-buffer image as a NumPy array.
    """

    t = time.time()
    progress("Getting Z-Buffer")
    # print(o.zbuffer_image)
    o.update_offset_image_tag = True
    if o.geometry_source == "OBJECT" or o.geometry_source == "COLLECTION":
        pixsize = o.optimisation.pixsize

        sx = o.max.x - o.min.x
        sy = o.max.y - o.min.y

        resx = ceil(sx / o.optimisation.pixsize) + 2 * o.borderwidth
        resy = ceil(sy / o.optimisation.pixsize) + 2 * o.borderwidth

        if (
            not o.update_z_buffer_image_tag
            and len(o.zbuffer_image) == resx
            and len(o.zbuffer_image[0]) == resy
        ):
            # if we call this accidentally in more functions, which currently happens...
            # print('has zbuffer')
            return o.zbuffer_image
        # ###setup image name
        iname = get_cache_path(o) + "_z.exr"
        if not o.update_z_buffer_image_tag:
            try:
                i = bpy.data.images.load(iname)
                if i.size[0] != resx or i.size[1] != resy:
                    print("Z Buffer Size Changed:", i.size, resx, resy)
                    o.update_z_buffer_image_tag = True

            except:
                o.update_z_buffer_image_tag = True
        if o.update_z_buffer_image_tag:
            s = bpy.context.scene
            s.use_nodes = True
            vl = bpy.context.view_layer
            n = s.node_tree
            r = s.render

            SETTINGS_TO_BACKUP = [
                (s.render, "resolution_x"),
                (s.render, "resolution_x"),
                (s.cycles, "samples"),
                (s, "camera"),
                (vl, "samples"),
                (vl.cycles, "use_denoising"),
                (s.world, "mist_settings"),
                (r, "resolution_x"),
                (r, "resolution_y"),
                (r, "resolution_percentage"),
            ]
            for ob in s.objects:
                SETTINGS_TO_BACKUP.append((ob, "hide_render"))
            backup_settings = None
            try:
                backup_settings = _backup_render_settings(SETTINGS_TO_BACKUP)
                # prepare nodes first
                r.resolution_x = resx
                r.resolution_y = resy
                # use cycles for everything because
                # it renders okay on github actions
                r.engine = "CYCLES"
                s.cycles.samples = 1
                vl.samples = 1
                vl.cycles.use_denoising = False

                n.links.clear()
                n.nodes.clear()
                node_in = n.nodes.new("CompositorNodeRLayers")
                s.view_layers[node_in.layer].use_pass_mist = True
                mist_settings = s.world.mist_settings
                s.world.mist_settings.depth = 10.0
                s.world.mist_settings.start = 0
                s.world.mist_settings.falloff = "LINEAR"
                s.world.mist_settings.height = 0
                s.world.mist_settings.intensity = 0
                node_out = n.nodes.new("CompositorNodeOutputFile")
                node_out.base_path = os.path.dirname(iname)
                node_out.format.file_format = "OPEN_EXR"
                node_out.format.color_mode = "RGB"
                node_out.format.color_depth = "32"
                node_out.file_slots.new(os.path.basename(iname))
                n.links.new(node_in.outputs[node_in.outputs.find("Mist")], node_out.inputs[-1])
                ###################

                # resize operation image
                o.offset_image = numpy.full(shape=(resx, resy), fill_value=-10, dtype=numpy.double)

                # various settings for  faster render
                r.resolution_percentage = 100

                # add a new camera settings
                bpy.ops.object.camera_add(
                    align="WORLD", enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0)
                )
                camera = bpy.context.active_object
                bpy.context.scene.camera = camera

                camera.data.type = "ORTHO"
                camera.data.ortho_scale = max(
                    resx * o.optimisation.pixsize, resy * o.optimisation.pixsize
                )
                camera.location = (o.min.x + sx / 2, o.min.y + sy / 2, 1)
                camera.rotation_euler = (0, 0, 0)
                camera.data.clip_end = 10.0
                # if not o.render_all:#removed in 0.3

                h = []

                # ob=bpy.data.objects[o.object_name]
                for ob in s.objects:
                    ob.hide_render = True
                for ob in o.objects:
                    ob.hide_render = False

                bpy.ops.render.render()

                n.nodes.remove(node_out)
                n.nodes.remove(node_in)
                camera.select_set(True)
                bpy.ops.object.delete()

                os.replace(iname + "%04d.exr" % (s.frame_current), iname)
            finally:
                if backup_settings is not None:
                    _restore_render_settings(SETTINGS_TO_BACKUP, backup_settings)
                else:
                    print("Failed to Backup Scene Settings")

            i = bpy.data.images.load(iname)
            bpy.context.scene.render.engine = "FABEX_RENDER"

        a = image_to_numpy(i)
        a = 10.0 * a
        a = 1.0 - a
        o.zbuffer_image = a
        o.update_z_buffer_image_tag = False

    else:
        i = bpy.data.images[o.source_image_name]
        if o.source_image_crop:
            sx = int(i.size[0] * o.source_image_crop_start_x / 100.0)
            ex = int(i.size[0] * o.source_image_crop_end_x / 100.0)
            sy = int(i.size[1] * o.source_image_crop_start_y / 100.0)
            ey = int(i.size[1] * o.source_image_crop_end_y / 100.0)
        else:
            sx = 0
            ex = i.size[0]
            sy = 0
            ey = i.size[1]

        # o.offset_image.resize(ex - sx + 2 * o.borderwidth, ey - sy + 2 * o.borderwidth)

        o.optimisation.pixsize = o.source_image_size_x / i.size[0]
        progress("Pixel Size in the Image Source", o.optimisation.pixsize)

        rawimage = image_to_numpy(i)
        maxa = numpy.max(rawimage)
        mina = numpy.min(rawimage)
        neg = o.source_image_scale_z < 0
        # waterline strategy needs image border to have ok ambient.
        if o.strategy == "WATERLINE":
            a = numpy.full(
                shape=(2 * o.borderwidth + i.size[0], 2 * o.borderwidth + i.size[1]),
                fill_value=1 - neg,
                dtype=numpy.float,
            )
        else:  # other operations like parallel need to reach the border
            a = numpy.full(
                shape=(2 * o.borderwidth + i.size[0], 2 * o.borderwidth + i.size[1]),
                fill_value=neg,
                dtype=numpy.float,
            )
        # 2*o.borderwidth
        a[o.borderwidth : -o.borderwidth, o.borderwidth : -o.borderwidth] = rawimage
        a = a[sx : ex + o.borderwidth * 2, sy : ey + o.borderwidth * 2]

        if o.source_image_scale_z < 0:
            # negative images place themselves under the 0 plane by inverting through scale multiplication
            # first, put the image down, se we know the image minimum is on 0
            a = a - mina
            a *= o.source_image_scale_z

        else:  # place positive images under 0 plane, this is logical
            # first, put the image down, se we know the image minimum is on 0
            a = a - mina
            a *= o.source_image_scale_z
            a -= (maxa - mina) * o.source_image_scale_z

        a += o.source_image_offset.z  # after that, image gets offset.

        o.min_z = numpy.min(a)  # TODO: I really don't know why this is here...
        o.min.z = numpy.min(a)
        print("min z ", o.min.z)
        print("max z ", o.max.z)
        print("max image ", numpy.max(a))
        print("min image ", numpy.min(a))
        o.zbuffer_image = a
    # progress('got z buffer also with conversion in:')
    progress(time.time() - t)

    # progress(a)
    o.update_z_buffer_image_tag = False
    return o.zbuffer_image


# return numpy.array([])


async def prepare_area(o):
    """Prepare the area for rendering by processing the offset image.

    This function handles the preparation of the area by rendering a sample
    image and managing the offset image based on the provided options. It
    checks if the offset image needs to be updated and loads it if
    necessary. If the inverse option is set, it adjusts the samples
    accordingly before calling the offsetArea function. Finally, it saves
    the processed offset image.

    Args:
        o (object): An object containing various properties and methods
            required for preparing the area, including flags for
            updating the offset image and rendering options.
    """

    # if not o.use_exact:
    render_sample_image(o)
    samples = o.zbuffer_image

    iname = get_cache_path(o) + "_off.exr"

    if not o.update_offset_image_tag:
        progress("Loading Offset Image")
        try:
            o.offset_image = image_to_numpy(bpy.data.images.load(iname))

        except:
            o.update_offset_image_tag = True

    if o.update_offset_image_tag:
        if o.inverse:
            samples = numpy.maximum(samples, o.min.z - 0.00001)
        await offset_area(o, samples)
        numpy_save(o.offset_image, iname)


def get_cutter_array(operation, pixsize):
    """Generate a cutter array based on the specified operation and pixel size.

    This function calculates a 2D array representing the cutter shape based
    on the cutter type defined in the operation object. The cutter can be of
    various types such as 'END', 'BALL', 'VCARVE', 'CYLCONE', 'BALLCONE', or
    'CUSTOM'. The function uses geometric calculations to fill the array
    with appropriate values based on the cutter's dimensions and properties.

    Args:
        operation (object): An object containing properties of the cutter, including
            cutter type, diameter, tip angle, and other relevant parameters.
        pixsize (float): The size of each pixel in the generated cutter array.

    Returns:
        numpy.ndarray: A 2D array filled with values representing the cutter shape.
    """

    type = operation.cutter_type
    # print('generating cutter')
    r = operation.cutter_diameter / 2 + operation.skin  # /operation.pixsize
    res = ceil((r * 2) / pixsize)
    m = res / 2.0
    car = numpy.full(shape=(res, res), fill_value=-10.0, dtype=float)

    v = Vector((0, 0, 0))
    ps = pixsize
    if type == "END":
        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps
            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps
                if v.length <= r:
                    car.itemset((a, b), 0)
    elif type == "BALL" or type == "BALLNOSE":
        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps
            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps
                if v.length <= r:
                    z = sin(acos(v.length / r)) * r - r
                    car.itemset((a, b), z)  # [a,b]=z

    elif type == "VCARVE":
        angle = operation.cutter_tip_angle
        s = tan(pi * (90 - angle / 2) / 180)  # angle in degrees
        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps
            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps
                if v.length <= r:
                    z = -v.length * s
                    car.itemset((a, b), z)
    elif type == "CYLCONE":
        angle = operation.cutter_tip_angle
        cyl_r = operation.cylcone_diameter / 2
        s = tan(pi * (90 - angle / 2) / 180)  # angle in degrees
        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps
            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps
                if v.length <= r:
                    z = -(v.length - cyl_r) * s
                    if v.length <= cyl_r:
                        z = 0
                    car.itemset((a, b), z)
    elif type == "BALLCONE":
        angle = radians(operation.cutter_tip_angle) / 2
        ball_r = operation.ball_radius
        cutter_r = operation.cutter_diameter / 2
        conedepth = (cutter_r - ball_r) / tan(angle)
        Ball_R = ball_r / cos(angle)
        D_ofset = ball_r * tan(angle)
        s = tan(pi / 2 - angle)
        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps
            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps
                if v.length <= cutter_r:
                    z = -(v.length - ball_r) * s - Ball_R + D_ofset
                    if v.length <= ball_r:
                        z = sin(acos(v.length / Ball_R)) * Ball_R - Ball_R
                    car.itemset((a, b), z)
    elif type == "CUSTOM":
        cutob = bpy.data.objects[operation.cutter_object_name]
        scale = ((cutob.dimensions.x / cutob.scale.x) / 2) / r  #
        # print(cutob.scale)
        vstart = Vector((0, 0, -10))
        vend = Vector((0, 0, 10))
        print("Sampling Custom Cutter")
        maxz = -1
        for a in range(0, res):
            vstart.x = (a + 0.5 - m) * ps * scale
            vend.x = vstart.x

            for b in range(0, res):
                vstart.y = (b + 0.5 - m) * ps * scale
                vend.y = vstart.y
                v = vend - vstart
                c = cutob.ray_cast(vstart, v, distance=1.70141e38)
                if c[3] != -1:
                    z = -c[1][2] / scale
                    # print(c)
                    if z > -9:
                        # print(z)
                        if z > maxz:
                            maxz = z
                        car.itemset((a, b), z)
        car -= maxz
    return car
