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
   fabex.utilities.image_utils.numpy_to_image
   fabex.utilities.image_utils.image_to_numpy
   fabex.utilities.image_utils._offset_inner_loop
   fabex.utilities.image_utils.offset_area
   fabex.utilities.image_utils.get_sample_image
   fabex.utilities.image_utils.get_resolution
   fabex.utilities.image_utils._backup_render_settings
   fabex.utilities.image_utils._restore_render_settings
   fabex.utilities.image_utils.render_sample_image
   fabex.utilities.image_utils.prepare_area
   fabex.utilities.image_utils.image_edge_search_on_line
   fabex.utilities.image_utils.get_offset_image_cavities
   fabex.utilities.image_utils.image_to_chunks


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


.. py:function:: image_edge_search_on_line(o, ar, zimage)

   Search for edges in an image using a pencil strategy.

   This function implements an edge detection algorithm that simulates a
   pencil-like movement across the image represented by a 2D array. It
   identifies white pixels and builds chunks of points based on the
   detected edges. The algorithm iteratively explores possible directions
   to find and track the edges until a specified condition is met, such as
   exhausting the available white pixels or reaching a maximum number of
   tests.

   :param o: An object containing parameters such as min, max coordinates, cutter
             diameter,
             border width, and optimisation settings.
   :type o: object
   :param ar: A 2D array representing the image where edge detection is to be
              performed.
   :type ar: np.ndarray
   :param zimage: A 2D array representing the z-coordinates corresponding to the image.
   :type zimage: np.ndarray

   :returns: A list of chunks representing the detected edges in the image.
   :rtype: list


.. py:function:: get_offset_image_cavities(o, i)

   Detects areas in the offset image which are 'cavities' due to curvature
   changes.

   This function analyzes the input image to identify regions where the
   curvature changes, indicating the presence of cavities. It computes
   vertical and horizontal differences in pixel values to detect edges and
   applies a threshold to filter out insignificant changes. The resulting
   areas are then processed to remove any chunks that do not meet the
   minimum criteria for cavity detection. The function returns a list of
   valid chunks that represent the detected cavities.

   :param o: An object containing parameters and thresholds for the detection
             process.
   :param i: A 2D array representing the image data to be analyzed.
   :type i: np.ndarray

   :returns: A list of detected chunks representing the cavities in the image.
   :rtype: list


.. py:function:: image_to_chunks(o, image, with_border=False)

   Convert an image into chunks based on detected edges.

   This function processes a given image to identify edges and convert them
   into polychunks, which are essentially collections of connected edge
   segments. It utilizes the properties of the input object `o` to
   determine the boundaries and size of the chunks. The function can
   optionally include borders in the edge detection process. The output is
   a list of chunks that represent the detected polygons in the image.

   :param o: An object containing properties such as min, max, borderwidth,
             and optimisation settings.
   :type o: object
   :param image: A 2D array representing the image to be processed,
                 expected to be in a format compatible with uint8.
   :type image: np.ndarray
   :param with_border: A flag indicating whether to include borders
                       in the edge detection. Defaults to False.
   :type with_border: bool?

   :returns:

             A list of chunks, where each chunk is represented as a collection of
                 points that outline the detected edges in the image.
   :rtype: list


