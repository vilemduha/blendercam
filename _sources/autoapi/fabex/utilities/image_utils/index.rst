fabex.utilities.image_utils
===========================

.. py:module:: fabex.utilities.image_utils

.. autoapi-nested-parse::

   Fabex 'image_utils.py' © 2012 Vilem Novak

   Functions to render, save, convert and analyze image data.



Functions
---------

.. autoapisummary::

   fabex.utilities.image_utils.numpy_save
   fabex.utilities.image_utils.get_circle
   fabex.utilities.image_utils.get_circle_binary
   fabex.utilities.image_utils.numpy_to_image
   fabex.utilities.image_utils.image_to_numpy
   fabex.utilities.image_utils._offset_inner_loop
   fabex.utilities.image_utils.offset_area
   fabex.utilities.image_utils.dilate_array
   fabex.utilities.image_utils.crazy_path
   fabex.utilities.image_utils.build_stroke
   fabex.utilities.image_utils.test_stroke
   fabex.utilities.image_utils.apply_stroke
   fabex.utilities.image_utils.test_stroke_binary
   fabex.utilities.image_utils.get_sample_image
   fabex.utilities.image_utils.get_resolution
   fabex.utilities.image_utils._backup_render_settings
   fabex.utilities.image_utils._restore_render_settings
   fabex.utilities.image_utils.render_sample_image
   fabex.utilities.image_utils.prepare_area
   fabex.utilities.image_utils.get_cutter_array


Module Contents
---------------

.. py:function:: numpy_save(a, iname)

   Save a NumPy array as an image file in OpenEXR format.

   This function converts a NumPy array into an image and saves it using
   Blender's rendering capabilities. It sets the image format to OpenEXR
   with black and white color mode and a color depth of 32 bits. The image
   is saved to the specified filename.

   :param a: The NumPy array to be converted and saved as an image.
   :type a: numpy.ndarray
   :param iname: The file path where the image will be saved.
   :type iname: str


.. py:function:: get_circle(r, z)

   Generate a 2D array representing a circle.

   This function creates a 2D NumPy array filled with a specified value for
   points that fall within a circle of a given radius. The circle is
   centered in the array, and the function uses the Euclidean distance to
   determine which points are inside the circle. The resulting array has
   dimensions that are twice the radius, ensuring that the entire circle
   fits within the array.

   :param r: The radius of the circle.
   :type r: int
   :param z: The value to fill the points inside the circle.
   :type z: float

   :returns: A 2D array where points inside the circle are filled
             with the value `z`, and points outside are filled with -10.
   :rtype: numpy.ndarray


.. py:function:: get_circle_binary(r)

   Generate a binary representation of a circle in a 2D grid.

   This function creates a 2D boolean array where the elements inside a
   circle of radius `r` are set to `True`, and the elements outside the
   circle are set to `False`. The circle is centered in the middle of the
   array, which has dimensions of (2*r, 2*r). The function iterates over
   each point in the grid and checks if it lies within the specified
   radius.

   :param r: The radius of the circle.
   :type r: int

   :returns: A 2D boolean array representing the circle.
   :rtype: numpy.ndarray


.. py:function:: numpy_to_image(a: numpy.ndarray, iname: str) -> bpy.types.Image

   Convert a NumPy array to a Blender image.

   This function takes a NumPy array and converts it into a Blender image.
   It first checks if an image with the specified name and dimensions
   already exists in Blender. If it does not exist, a new image is created
   with the specified name and dimensions. The pixel data from the NumPy
   array is then reshaped and assigned to the image's pixel buffer.

   :param a: A 2D NumPy array representing the image data.
   :type a: numpy.ndarray
   :param iname: The name to assign to the created or found image.
   :type iname: str

   :returns: The Blender image object that was created or found.
   :rtype: bpy.types.Image


.. py:function:: image_to_numpy(i)

   Convert a Blender image to a NumPy array.

   This function takes a Blender image object and converts its pixel data
   into a NumPy array. It retrieves the pixel data, reshapes it, and swaps
   the axes to match the expected format for further processing. The
   function also measures the time taken for the conversion and prints it
   to the console.

   :param i: A Blender image object containing pixel data.
   :type i: Image

   :returns: A 2D NumPy array representing the image pixels.
   :rtype: numpy.ndarray


.. py:function:: _offset_inner_loop(y1, y2, cutterArrayNan, cwidth, sourceArray, width, height, comparearea)

   Offset the inner loop for processing a specified area in a 2D array.

   This function iterates over a specified range of rows and columns in a
   2D array, calculating the maximum value from a source array combined
   with a cutter array for each position in the defined area. The results
   are stored in the comparearea array, which is updated with the maximum
   values found.

   :param y1: The starting index for the row iteration.
   :type y1: int
   :param y2: The ending index for the row iteration.
   :type y2: int
   :param cutterArrayNan: A 2D array used for modifying the source array.
   :type cutterArrayNan: numpy.ndarray
   :param cwidth: The width of the area to consider for the maximum calculation.
   :type cwidth: int
   :param sourceArray: The source 2D array from which maximum values are derived.
   :type sourceArray: numpy.ndarray
   :param width: The width of the source array.
   :type width: int
   :param height: The height of the source array.
   :type height: int
   :param comparearea: A 2D array where the calculated maximum values are stored.
   :type comparearea: numpy.ndarray

   :returns:

             This function modifies the comparearea in place and does not return a
                 value.
   :rtype: None


.. py:function:: offset_area(o, samples)
   :async:


   Offsets the whole image with the cutter and skin offsets.

   This function modifies the offset image based on the provided cutter and
   skin offsets. It calculates the dimensions of the source and cutter
   arrays, initializes an offset image, and processes the image in
   segments. The function handles the inversion of the source array if
   specified and updates the offset image accordingly. Progress is reported
   asynchronously during processing.

   :param o: An object containing properties such as `update_offset_image_tag`,
             `min`, `max`, `inverse`, and `offset_image`.
   :param samples: A 2D array representing the source image data.
   :type samples: numpy.ndarray

   :returns: The updated offset image after applying the cutter and skin offsets.
   :rtype: numpy.ndarray


.. py:function:: dilate_array(ar, cycles)

   Dilate a binary array using a specified number of cycles.

   This function performs a dilation operation on a 2D binary array. For
   each cycle, it updates the array by applying a logical OR operation
   between the current array and its neighboring elements. The dilation
   effect expands the boundaries of the foreground (True) pixels in the
   binary array.

   :param ar: A 2D binary array (numpy array) where
              dilation will be applied.
   :type ar: numpy.ndarray
   :param cycles: The number of dilation cycles to perform.
   :type cycles: int

   :returns:

             The function modifies the input array in place and does not
                 return a value.
   :rtype: None


.. py:function:: crazy_path(o)
   :async:


   Execute a greedy adaptive algorithm for path planning.

   This function prepares an area based on the provided object `o`,
   calculates the dimensions of the area, and initializes a mill image and
   cutter array. The dimensions are determined by the maximum and minimum
   coordinates of the object, adjusted by the simulation detail and border
   width. The function is currently a stub and requires further
   implementation.

   :param o: An object containing properties such as max, min, optimisation, and
             borderwidth.
   :type o: object

   :returns: This function does not return a value.
   :rtype: None


.. py:function:: build_stroke(start, end, cutterArray)

   Build a stroke array based on start and end points.

   This function generates a 2D stroke array that represents a stroke from
   a starting point to an ending point. It calculates the length of the
   stroke and creates a grid that is filled based on the positions defined
   by the start and end coordinates. The function uses a cutter array to
   determine how the stroke interacts with the grid.

   :param start: A tuple representing the starting coordinates (x, y, z).
   :type start: tuple
   :param end: A tuple representing the ending coordinates (x, y, z).
   :type end: tuple
   :param cutterArray: An object that contains size information used to modify
                       the stroke array.

   :returns:

             A 2D array representing the stroke, filled with
                 calculated values based on the input parameters.
   :rtype: numpy.ndarray


.. py:function:: test_stroke()

.. py:function:: apply_stroke()

.. py:function:: test_stroke_binary(img, stroke)

.. py:function:: get_sample_image(s, sarray, minz)

   Get a sample image value from a 2D array based on given coordinates.

   This function retrieves a value from a 2D array by performing bilinear
   interpolation based on the provided coordinates. It checks if the
   coordinates are within the bounds of the array and calculates the
   interpolated value accordingly. If the coordinates are out of bounds, it
   returns -10.

   :param s: A tuple containing the x and y coordinates (float).
   :type s: tuple
   :param sarray: A 2D array from which to sample the image values.
   :type sarray: numpy.ndarray
   :param minz: A minimum threshold value (not used in the current implementation).
   :type minz: float

   :returns:

             The interpolated value from the 2D array, or -10 if the coordinates are
                 out of bounds.
   :rtype: float


.. py:function:: get_resolution(o)

   Calculate the resolution based on the dimensions of an object.

   This function computes the resolution in both x and y directions by
   determining the width and height of the object, adjusting for pixel size
   and border width. The resolution is calculated by dividing the
   dimensions by the pixel size and adding twice the border width to each
   dimension.

   :param o: An object with attributes `max`, `min`, `optimisation`,
             and `borderwidth`. The `max` and `min` attributes should
             have `x` and `y` properties representing the coordinates,
             while `optimisation` should have a `pixsize` attribute.
   :type o: object

   :returns:

             This function does not return a value; it performs calculations
                 to determine resolution.
   :rtype: None


.. py:function:: _backup_render_settings(pairs)

   Backup the render settings of Blender objects.

   This function iterates over a list of pairs consisting of owners and
   their corresponding structure names. It retrieves the properties of each
   structure and stores them in a backup list. If the structure is a
   Blender object, it saves all its properties that do not start with an
   underscore. For simple values, it directly appends them to the
   properties list. This is useful for preserving render settings that
   Blender does not allow direct access to during rendering.

   :param pairs: A list of tuples where each tuple contains an owner and a structure
                 name.
   :type pairs: list

   :returns:

             A list containing the backed-up properties of the specified Blender
                 objects.
   :rtype: list


.. py:function:: _restore_render_settings(pairs, properties)

   Restore render settings for a given owner and structure.

   This function takes pairs of owners and structure names along with their
   corresponding properties. It iterates through these pairs, retrieves the
   appropriate object from the owner using the structure name, and sets the
   properties on the object. If the object is an instance of
   `bpy.types.bpy_struct`, it updates its attributes; otherwise, it
   directly sets the value on the owner.

   :param pairs: A list of tuples where each tuple contains an owner and a structure
                 name.
   :type pairs: list
   :param properties: A list of dictionaries containing property names and their corresponding
                      values.
   :type properties: list


.. py:function:: render_sample_image(o)

   Render a sample image based on the provided object settings.

   This function generates a Z-buffer image for a given object by either
   rendering it from scratch or loading an existing image from the cache.
   It handles different geometry sources and applies various settings to
   ensure the image is rendered correctly. The function also manages backup
   and restoration of render settings to maintain the scene's integrity
   during the rendering process.

   :param o: An object containing various properties and settings
   :type o: object

   :returns: The generated or loaded Z-buffer image as a NumPy array.
   :rtype: numpy.ndarray


.. py:function:: prepare_area(o)
   :async:


   Prepare the area for rendering by processing the offset image.

   This function handles the preparation of the area by rendering a sample
   image and managing the offset image based on the provided options. It
   checks if the offset image needs to be updated and loads it if
   necessary. If the inverse option is set, it adjusts the samples
   accordingly before calling the offsetArea function. Finally, it saves
   the processed offset image.

   :param o: An object containing various properties and methods
             required for preparing the area, including flags for
             updating the offset image and rendering options.
   :type o: object


.. py:function:: get_cutter_array(operation, pixsize)

   Generate a cutter array based on the specified operation and pixel size.

   This function calculates a 2D array representing the cutter shape based
   on the cutter type defined in the operation object. The cutter can be of
   various types such as 'END', 'BALL', 'VCARVE', 'CYLCONE', 'BALLCONE', or
   'CUSTOM'. The function uses geometric calculations to fill the array
   with appropriate values based on the cutter's dimensions and properties.

   :param operation: An object containing properties of the cutter, including
                     cutter type, diameter, tip angle, and other relevant parameters.
   :type operation: object
   :param pixsize: The size of each pixel in the generated cutter array.
   :type pixsize: float

   :returns: A 2D array filled with values representing the cutter shape.
   :rtype: numpy.ndarray


