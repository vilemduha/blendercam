cam.basrelief
=============

.. py:module:: cam.basrelief

.. autoapi-nested-parse::

   BlenderCAM 'basrelief.py'

   Module to allow the creation of reliefs from Images or View Layers.
   (https://en.wikipedia.org/wiki/Relief#Bas-relief_or_low_relief)



Attributes
----------

.. autoapisummary::

   cam.basrelief.EPS
   cam.basrelief.PRECISION
   cam.basrelief.NUMPYALG


Exceptions
----------

.. autoapisummary::

   cam.basrelief.ReliefError


Classes
-------

.. autoapisummary::

   cam.basrelief.BasReliefsettings
   cam.basrelief.BASRELIEF_Panel
   cam.basrelief.DoBasRelief
   cam.basrelief.ProblemAreas


Functions
---------

.. autoapisummary::

   cam.basrelief.copy_compbuf_data
   cam.basrelief.restrictbuf
   cam.basrelief.prolongate
   cam.basrelief.idx
   cam.basrelief.smooth
   cam.basrelief.calculate_defect
   cam.basrelief.add_correction
   cam.basrelief.solve_pde_multigrid
   cam.basrelief.asolve
   cam.basrelief.atimes
   cam.basrelief.snrm
   cam.basrelief.linbcg
   cam.basrelief.numpysave
   cam.basrelief.numpytoimage
   cam.basrelief.imagetonumpy
   cam.basrelief.tonemap
   cam.basrelief.vert
   cam.basrelief.buildMesh
   cam.basrelief.renderScene
   cam.basrelief.problemAreas
   cam.basrelief.relief
   cam.basrelief.get_panels
   cam.basrelief.register
   cam.basrelief.unregister


Module Contents
---------------

.. py:data:: EPS
   :value: 1e-32


.. py:data:: PRECISION
   :value: 5


.. py:data:: NUMPYALG
   :value: False


.. py:function:: copy_compbuf_data(inbuf, outbuf)

.. py:function:: restrictbuf(inbuf, outbuf)

   Restrict the resolution of an input buffer to match an output buffer.

   This function scales down the input buffer `inbuf` to fit the dimensions
   of the output buffer `outbuf`. It computes the average of the
   neighboring pixels in the input buffer to create a downsampled version
   in the output buffer. The method used for downsampling can vary based on
   the dimensions of the input and output buffers, utilizing either a
   simple averaging method or a more complex numpy-based approach.

   :param inbuf: The input buffer to be downsampled, expected to be
                 a 2D array.
   :type inbuf: numpy.ndarray
   :param outbuf: The output buffer where the downsampled result will
                  be stored, also expected to be a 2D array.
   :type outbuf: numpy.ndarray

   :returns: The function modifies `outbuf` in place.
   :rtype: None


.. py:function:: prolongate(inbuf, outbuf)

   Prolongate an input buffer to a larger output buffer.

   This function takes an input buffer and enlarges it to fit the
   dimensions of the output buffer. It uses different methods to achieve
   this based on the scaling factors derived from the input and output
   dimensions. The function can handle specific cases where the scaling
   factors are exactly 0.5, as well as a general case that applies a
   bilinear interpolation technique for resizing.

   :param inbuf: The input buffer to be enlarged, expected to be a 2D array.
   :type inbuf: numpy.ndarray
   :param outbuf: The output buffer where the enlarged data will be stored,
                  expected to be a 2D array of larger dimensions than inbuf.
   :type outbuf: numpy.ndarray


.. py:function:: idx(r, c, cols)

.. py:function:: smooth(U, F, linbcgiterations, planar)

   Smooth a matrix U using a filter F at a specified level.

   This function applies a smoothing operation on the input matrix U using
   the filter F. It utilizes the linear Biconjugate Gradient method for the
   smoothing process. The number of iterations for the linear BCG method is
   specified by linbcgiterations, and the planar parameter indicates
   whether the operation is to be performed in a planar manner.

   :param U: The input matrix to be smoothed.
   :type U: numpy.ndarray
   :param F: The filter used for smoothing.
   :type F: numpy.ndarray
   :param linbcgiterations: The number of iterations for the linear BCG method.
   :type linbcgiterations: int
   :param planar: A flag indicating whether to perform the operation in a planar manner.
   :type planar: bool

   :returns: This function modifies the input matrix U in place.
   :rtype: None


.. py:function:: calculate_defect(D, U, F)

   Calculate the defect of a grid based on the input fields.

   This function computes the defect values for a grid by comparing the
   input field `F` with the values in the grid `U`. The defect is
   calculated using finite difference approximations, taking into account
   the neighboring values in the grid. The results are stored in the output
   array `D`, which is modified in place.

   :param D: A 2D array where the defect values will be stored.
   :type D: ndarray
   :param U: A 2D array representing the current state of the grid.
   :type U: ndarray
   :param F: A 2D array representing the target field to compare against.
   :type F: ndarray

   :returns:

             The function modifies the array `D` in place and does not return a
                 value.
   :rtype: None


.. py:function:: add_correction(U, C)

.. py:function:: solve_pde_multigrid(F, U, vcycleiterations, linbcgiterations, smoothiterations, mins, levels, useplanar, planar)

   Solve a partial differential equation using a multigrid method.

   This function implements a multigrid algorithm to solve a given partial
   differential equation (PDE). It operates on a grid of varying
   resolutions, applying smoothing and correction steps iteratively to
   converge towards the solution. The algorithm consists of several key
   phases: restriction of the right-hand side to coarser grids, solving on
   the coarsest grid, and then interpolating corrections back to finer
   grids. The process is repeated for a specified number of V-cycle
   iterations.

   :param F: The right-hand side of the PDE represented as a 2D array.
   :type F: numpy.ndarray
   :param U: The initial guess for the solution, which will be updated in place.
   :type U: numpy.ndarray
   :param vcycleiterations: The number of V-cycle iterations to perform.
   :type vcycleiterations: int
   :param linbcgiterations: The number of iterations for the linear solver used in smoothing.
   :type linbcgiterations: int
   :param smoothiterations: The number of smoothing iterations to apply at each level.
   :type smoothiterations: int
   :param mins: Minimum grid size (not used in the current implementation).
   :type mins: int
   :param levels: The number of levels in the multigrid hierarchy.
   :type levels: int
   :param useplanar: A flag indicating whether to use planar information during the solution
                     process.
   :type useplanar: bool
   :param planar: A 2D array indicating planar information for the grid.
   :type planar: numpy.ndarray

   :returns:

             The function modifies the input array U in place to contain the final
                 solution.
   :rtype: None

   .. note::

      The function assumes that the input arrays F and U have compatible
      shapes
      and that the planar array is appropriately defined for the problem
      context.


.. py:function:: asolve(b, x)

.. py:function:: atimes(x, res)

   Apply a discrete Laplacian operator to a 2D array.

   This function computes the discrete Laplacian of a given 2D array `x`
   and stores the result in the `res` array. The Laplacian is calculated
   using finite difference methods, which involve summing the values of
   neighboring elements and applying specific boundary conditions for the
   edges and corners of the array.

   :param x: A 2D array representing the input values.
   :type x: numpy.ndarray
   :param res: A 2D array where the result will be stored. It must have the same shape
               as `x`.
   :type res: numpy.ndarray

   :returns: The result is stored directly in the `res` array.
   :rtype: None


.. py:function:: snrm(n, sx, itol)

   Calculate the square root of the sum of squares or the maximum absolute
   value.

   This function computes a value based on the input parameters. If the
   tolerance level (itol) is less than or equal to 3, it calculates the
   square root of the sum of squares of the input array (sx). If the
   tolerance level is greater than 3, it returns the maximum absolute value
   from the input array.

   :param n: An integer parameter, though it is not used in the current
             implementation.
   :type n: int
   :param sx: A numpy array of numeric values.
   :type sx: numpy.ndarray
   :param itol: An integer that determines which calculation to perform.
   :type itol: int

   :returns:

             The square root of the sum of squares if itol <= 3, otherwise the
                 maximum absolute value.
   :rtype: float


.. py:function:: linbcg(n, b, x, itol, tol, itmax, iter, err, rows, cols, planar)

   Solve a linear system using the Biconjugate Gradient Method.

   This function implements the Biconjugate Gradient Method as described in
   Numerical Recipes in C. It iteratively refines the solution to a linear
   system of equations defined by the matrix-vector product. The method is
   particularly useful for large, sparse systems where direct methods are
   inefficient. The function takes various parameters to control the
   iteration process and convergence criteria.

   :param n: The size of the linear system.
   :type n: int
   :param b: The right-hand side vector of the linear system.
   :type b: numpy.ndarray
   :param x: The initial guess for the solution vector.
   :type x: numpy.ndarray
   :param itol: The type of norm to use for convergence checks.
   :type itol: int
   :param tol: The tolerance for convergence.
   :type tol: float
   :param itmax: The maximum number of iterations allowed.
   :type itmax: int
   :param iter: The current iteration count (should be initialized to 0).
   :type iter: int
   :param err: The error estimate (should be initialized).
   :type err: float
   :param rows: The number of rows in the matrix.
   :type rows: int
   :param cols: The number of columns in the matrix.
   :type cols: int
   :param planar: A flag indicating if the problem is planar.
   :type planar: bool

   :returns: The solution is stored in the input array `x`.
   :rtype: None


.. py:function:: numpysave(a, iname)

   Save a NumPy array as an image file in OpenEXR format.

   This function takes a NumPy array and saves it as an image file using
   Blender's rendering capabilities. It configures the image settings to
   use the OpenEXR format with black and white color mode and a color depth
   of 32 bits. The rendered image is saved to the specified filename.

   :param a: The NumPy array to be saved as an image.
   :type a: numpy.ndarray
   :param iname: The filename (including path) where the image will be saved.
   :type iname: str


.. py:function:: numpytoimage(a, iname)

   Convert a NumPy array to a Blender image.

   This function takes a NumPy array and converts it into a Blender image.
   It first checks if an image with the specified name and dimensions
   already exists in Blender. If it does, that image is used; otherwise, a
   new image is created with the specified name and dimensions. The
   function then reshapes the NumPy array to match the image format and
   assigns the pixel data to the image.

   :param a: A 2D NumPy array representing the pixel data of the image.
   :type a: numpy.ndarray
   :param iname: The name to assign to the Blender image.
   :type iname: str

   :returns:

             The Blender image created or modified with the pixel data from the NumPy
                 array.
   :rtype: bpy.types.Image


.. py:function:: imagetonumpy(i)

   Convert an image to a NumPy array.

   This function takes an image object and converts its pixel data into a
   NumPy array. It first retrieves the pixel data from the image, then
   reshapes and rearranges it to match the image's dimensions. The
   resulting array is structured such that the height and width of the
   image are preserved, and the color channels are appropriately ordered.

   :param i: An image object that contains pixel data.
   :type i: Image

   :returns: A 2D NumPy array representing the pixel data of the image.
   :rtype: numpy.ndarray

   .. note::

      The function optimizes performance by directly accessing pixel data
      instead of using slower methods.


.. py:function:: tonemap(i, exponent)

   Apply tone mapping to an image array.

   This function performs tone mapping on the input image array by first
   filtering out values that are excessively high, which may indicate that
   the depth buffer was not written correctly. It then normalizes the
   values between the minimum and maximum heights, and finally applies an
   exponentiation to adjust the brightness of the image.

   :param i: A numpy array representing the image data.
   :type i: numpy.ndarray
   :param exponent: The exponent used for adjusting the brightness
                    of the normalized image.
   :type exponent: float

   :returns: The function modifies the input array in place.
   :rtype: None


.. py:function:: vert(column, row, z, XYscaling, Zscaling)

   Create a single vertex in 3D space.

   This function calculates the 3D coordinates of a vertex based on the
   provided column and row values, as well as scaling factors for the X-Y
   and Z dimensions. The resulting coordinates are scaled accordingly to
   fit within a specified 3D space.

   :param column: The column value representing the X coordinate.
   :type column: float
   :param row: The row value representing the Y coordinate.
   :type row: float
   :param z: The Z coordinate value.
   :type z: float
   :param XYscaling: The scaling factor for the X and Y coordinates.
   :type XYscaling: float
   :param Zscaling: The scaling factor for the Z coordinate.
   :type Zscaling: float

   :returns: A tuple containing the scaled X, Y, and Z coordinates.
   :rtype: tuple


.. py:function:: buildMesh(mesh_z, br)

   Build a 3D mesh from a height map and apply transformations.

   This function constructs a 3D mesh based on the provided height map
   (mesh_z) and applies various transformations such as scaling and
   positioning based on the parameters defined in the br object. It first
   removes any existing BasReliefMesh objects from the scene, then creates
   a new mesh from the height data, and finally applies decimation if the
   specified ratio is within acceptable limits.

   :param mesh_z: A 2D array representing the height values
                  for the mesh vertices.
   :type mesh_z: numpy.ndarray
   :param br: An object containing properties for width, height,
              thickness, justification, and decimation ratio.
   :type br: object


.. py:function:: renderScene(width, height, bit_diameter, passes_per_radius, make_nodes, view_layer)

   Render a scene using Blender's Cycles engine.

   This function switches the rendering engine to Cycles, sets up the
   necessary nodes for depth rendering if specified, and configures the
   render resolution based on the provided parameters. It ensures that the
   scene is in object mode before rendering and restores the original
   rendering engine after the process is complete.

   :param width: The width of the render in pixels.
   :type width: int
   :param height: The height of the render in pixels.
   :type height: int
   :param bit_diameter: The diameter used to calculate the number of passes.
   :type bit_diameter: float
   :param passes_per_radius: The number of passes per radius for rendering.
   :type passes_per_radius: int
   :param make_nodes: A flag indicating whether to create render nodes.
   :type make_nodes: bool
   :param view_layer: The name of the view layer to be rendered.
   :type view_layer: str

   :returns: This function does not return any value.
   :rtype: None


.. py:function:: problemAreas(br)

   Process image data to identify problem areas based on silhouette
   thresholds.

   This function analyzes an image and computes gradients to detect and
   recover silhouettes based on specified parameters. It utilizes various
   settings from the provided `br` object to adjust the processing,
   including silhouette thresholds, scaling factors, and iterations for
   smoothing and recovery. The function also handles image scaling and
   applies a gradient mask if specified. The resulting data is then
   converted back into an image format for further use.

   :param br: An object containing various parameters for processing, including:
              - use_image_source (bool): Flag to determine if a specific image source
              should be used.
              - source_image_name (str): Name of the source image if
              `use_image_source` is True.
              - silhouette_threshold (float): Threshold for silhouette detection.
              - recover_silhouettes (bool): Flag to indicate if silhouettes should be
              recovered.
              - silhouette_scale (float): Scaling factor for silhouette recovery.
              - min_gridsize (int): Minimum grid size for processing.
              - smooth_iterations (int): Number of iterations for smoothing.
              - vcycle_iterations (int): Number of iterations for V-cycle processing.
              - linbcg_iterations (int): Number of iterations for linear BCG
              processing.
              - use_planar (bool): Flag to indicate if planar processing should be
              used.
              - gradient_scaling_mask_use (bool): Flag to indicate if a gradient
              scaling mask should be used.
              - gradient_scaling_mask_name (str): Name of the gradient scaling mask
              image.
              - depth_exponent (float): Exponent for depth adjustment.
              - silhouette_exponent (int): Exponent for silhouette recovery.
              - attenuation (float): Attenuation factor for processing.
   :type br: object

   :returns:

             The function does not return a value but processes the image data and
                 saves the result.
   :rtype: None


.. py:function:: relief(br)

   Process an image to enhance relief features.

   This function takes an input image and applies various processing
   techniques to enhance the relief features based on the provided
   parameters. It utilizes gradient calculations, silhouette recovery, and
   optional detail enhancement through Fourier transforms. The processed
   image is then used to build a mesh representation.

   :param br: An object containing various parameters for the relief processing,
              including:
              - use_image_source (bool): Whether to use a specified image source.
              - source_image_name (str): The name of the source image.
              - silhouette_threshold (float): Threshold for silhouette detection.
              - recover_silhouettes (bool): Flag to indicate if silhouettes should be
              recovered.
              - silhouette_scale (float): Scale factor for silhouette recovery.
              - min_gridsize (int): Minimum grid size for processing.
              - smooth_iterations (int): Number of iterations for smoothing.
              - vcycle_iterations (int): Number of iterations for V-cycle processing.
              - linbcg_iterations (int): Number of iterations for linear BCG
              processing.
              - use_planar (bool): Flag to indicate if planar processing should be
              used.
              - gradient_scaling_mask_use (bool): Flag to indicate if a gradient
              scaling mask should be used.
              - gradient_scaling_mask_name (str): Name of the gradient scaling mask
              image.
              - depth_exponent (float): Exponent for depth adjustment.
              - attenuation (float): Attenuation factor for the processing.
              - detail_enhancement_use (bool): Flag to indicate if detail enhancement
              should be applied.
              - detail_enhancement_freq (float): Frequency for detail enhancement.
              - detail_enhancement_amount (float): Amount of detail enhancement to
              apply.
   :type br: object

   :returns:

             The function processes the image and builds a mesh but does not return a
                 value.
   :rtype: None

   :raises ReliefError: If the input image is blank or invalid.


.. py:class:: BasReliefsettings

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: use_image_source
      :type:  BoolProperty(name='Use Image Source', description='', default=False)


   .. py:attribute:: source_image_name
      :type:  StringProperty(name='Image Source', description='image source')


   .. py:attribute:: view_layer_name
      :type:  StringProperty(name='View Layer Source', description='Make a bas-relief from whatever is on this view layer')


   .. py:attribute:: bit_diameter
      :type:  FloatProperty(name='Diameter of Ball End in mm', description='Diameter of bit which will be used for carving', min=0.01, max=50.0, default=3.175, precision=PRECISION)


   .. py:attribute:: pass_per_radius
      :type:  IntProperty(name='Passes per Radius', description='Amount of passes per radius\n(more passes, more mesh precision)', default=2, min=1, max=10)


   .. py:attribute:: widthmm
      :type:  IntProperty(name='Desired Width in mm', default=200, min=5, max=4000)


   .. py:attribute:: heightmm
      :type:  IntProperty(name='Desired Height in mm', default=150, min=5, max=4000)


   .. py:attribute:: thicknessmm
      :type:  IntProperty(name='Thickness in mm', default=15, min=5, max=100)


   .. py:attribute:: justifyx
      :type:  EnumProperty(name='X', items=[('1', 'Left', '', 0), ('-0.5', 'Centered', '', 1), ('-1', 'Right', '', 2)], default='-1')


   .. py:attribute:: justifyy
      :type:  EnumProperty(name='Y', items=[('1', 'Bottom', '', 0), ('-0.5', 'Centered', '', 2), ('-1', 'Top', '', 1)], default='-1')


   .. py:attribute:: justifyz
      :type:  EnumProperty(name='Z', items=[('-1', 'Below 0', '', 0), ('-0.5', 'Centered', '', 2), ('1', 'Above 0', '', 1)], default='-1')


   .. py:attribute:: depth_exponent
      :type:  FloatProperty(name='Depth Exponent', description='Initial depth map is taken to this power. Higher = sharper relief', min=0.5, max=10.0, default=1.0, precision=PRECISION)


   .. py:attribute:: silhouette_threshold
      :type:  FloatProperty(name='Silhouette Threshold', description='Silhouette threshold', min=1e-06, max=1.0, default=0.003, precision=PRECISION)


   .. py:attribute:: recover_silhouettes
      :type:  BoolProperty(name='Recover Silhouettes', description='', default=True)


   .. py:attribute:: silhouette_scale
      :type:  FloatProperty(name='Silhouette Scale', description='Silhouette scale', min=1e-06, max=5.0, default=0.3, precision=PRECISION)


   .. py:attribute:: silhouette_exponent
      :type:  IntProperty(name='Silhouette Square Exponent', description='If lower, true depth distances between objects will be more visibe in the relief', default=3, min=0, max=5)


   .. py:attribute:: attenuation
      :type:  FloatProperty(name='Gradient Attenuation', description='Gradient attenuation', min=1e-06, max=100.0, default=1.0, precision=PRECISION)


   .. py:attribute:: min_gridsize
      :type:  IntProperty(name='Minimum Grid Size', default=16, min=2, max=512)


   .. py:attribute:: smooth_iterations
      :type:  IntProperty(name='Smooth Iterations', default=1, min=1, max=64)


   .. py:attribute:: vcycle_iterations
      :type:  IntProperty(name='V-Cycle Iterations', description='Set higher for planar constraint', default=2, min=1, max=128)


   .. py:attribute:: linbcg_iterations
      :type:  IntProperty(name='LINBCG Iterations', description='Set lower for flatter relief, and when using planar constraint', default=5, min=1, max=64)


   .. py:attribute:: use_planar
      :type:  BoolProperty(name='Use Planar Constraint', description='', default=False)


   .. py:attribute:: gradient_scaling_mask_use
      :type:  BoolProperty(name='Scale Gradients with Mask', description='', default=False)


   .. py:attribute:: decimate_ratio
      :type:  FloatProperty(name='Decimate Ratio', description='Simplify the mesh using the Decimate modifier. The lower the value the more simplyfied', min=0.01, max=1.0, default=0.1, precision=PRECISION)


   .. py:attribute:: gradient_scaling_mask_name
      :type:  StringProperty(name='Scaling Mask Name', description='Mask name')


   .. py:attribute:: scale_down_before_use
      :type:  BoolProperty(name='Scale Down Image Before Processing', description='', default=False)


   .. py:attribute:: scale_down_before
      :type:  FloatProperty(name='Image Scale', description='Image scale', min=0.025, max=1.0, default=0.5, precision=PRECISION)


   .. py:attribute:: detail_enhancement_use
      :type:  BoolProperty(name='Enhance Details', description='Enhance details by frequency analysis', default=False)


   .. py:attribute:: detail_enhancement_amount
      :type:  FloatProperty(name='Amount', description='Image scale', min=0.025, max=1.0, default=0.5, precision=PRECISION)


   .. py:attribute:: advanced
      :type:  BoolProperty(name='Advanced Options', description='Show advanced options', default=True)


.. py:class:: BASRELIEF_Panel

   Bases: :py:obj:`bpy.types.Panel`


   Bas Relief Panel


   .. py:attribute:: bl_label
      :value: 'Bas Relief'



   .. py:attribute:: bl_idname
      :value: 'WORLD_PT_BASRELIEF'



   .. py:attribute:: bl_space_type
      :value: 'PROPERTIES'



   .. py:attribute:: bl_region_type
      :value: 'WINDOW'



   .. py:attribute:: bl_context
      :value: 'render'



   .. py:attribute:: COMPAT_ENGINES


   .. py:method:: poll(context)
      :classmethod:


      Check if the current render engine is compatible.

      This class method checks whether the render engine specified in the
      provided context is included in the list of compatible engines. It
      accesses the render settings from the context and verifies if the engine
      is part of the predefined compatible engines.

      :param context: The context containing the scene and render settings.
      :type context: Context

      :returns: True if the render engine is compatible, False otherwise.
      :rtype: bool



   .. py:method:: draw(context)

      Draw the user interface for the bas relief settings.

      This method constructs the layout for the bas relief settings in the
      Blender user interface. It includes various properties and options that
      allow users to configure the bas relief calculations, such as selecting
      images, adjusting parameters, and setting justification options. The
      layout is dynamically updated based on user selections, providing a
      comprehensive interface for manipulating bas relief settings.

      :param context: The context in which the UI is being drawn.
      :type context: bpy.context

      :returns: This method does not return any value; it modifies the layout
                directly.
      :rtype: None



.. py:exception:: ReliefError

   Bases: :py:obj:`Exception`


   Common base class for all non-exit exceptions.


.. py:class:: DoBasRelief

   Bases: :py:obj:`bpy.types.Operator`


   Calculate Bas Relief


   .. py:attribute:: bl_idname
      :value: 'scene.calculate_bas_relief'



   .. py:attribute:: bl_label
      :value: 'Calculate Bas Relief'



   .. py:attribute:: bl_options


   .. py:attribute:: processes
      :value: []



   .. py:method:: execute(context)

      Execute the relief rendering process based on the provided context.

      This function retrieves the scene and its associated bas relief
      settings. It checks if an image source is being used and sets the view
      layer name accordingly. The function then attempts to render the scene
      and generate the relief. If any errors occur during these processes,
      they are reported, and the operation is canceled.

      :param context: The context in which the function is executed.

      :returns: A dictionary indicating the result of the operation, either
      :rtype: dict



.. py:class:: ProblemAreas

   Bases: :py:obj:`bpy.types.Operator`


   Find Bas Relief Problem Areas


   .. py:attribute:: bl_idname
      :value: 'scene.problemareas_bas_relief'



   .. py:attribute:: bl_label
      :value: 'Problem Areas Bas Relief'



   .. py:attribute:: bl_options


   .. py:attribute:: processes
      :value: []



   .. py:method:: execute(context)

      Execute the operation related to the bas relief settings in the current
      scene.

      This method retrieves the current scene from the Blender context and
      accesses the bas relief settings. It then calls the `problemAreas`
      function to perform operations related to those settings. The method
      concludes by returning a status indicating that the operation has
      finished successfully.

      :param context: The current Blender context, which provides access
      :type context: bpy.context

      :returns: A dictionary with a status key indicating the operation result,
                specifically {'FINISHED'}.
      :rtype: dict



.. py:function:: get_panels()

   Retrieve a tuple of panel settings and related components.

   This function returns a tuple containing various components related to
   Bas Relief settings. The components include BasReliefsettings,
   BASRELIEF_Panel, DoBasRelief, and ProblemAreas, which are likely used in
   the context of a graphical user interface or a specific application
   domain.

   :returns: A tuple containing the BasReliefsettings, BASRELIEF_Panel,
             DoBasRelief, and ProblemAreas components.
   :rtype: tuple


.. py:function:: register()

   Register the necessary classes and properties for the add-on.

   This function registers all the panels defined in the add-on by
   iterating through the list of panels returned by the `get_panels()`
   function. It also adds a new property, `basreliefsettings`, to the
   `Scene` type, which is a pointer property that references the
   `BasReliefsettings` class. This setup is essential for the proper
   functioning of the add-on, allowing users to access and modify the
   settings related to bas relief.


.. py:function:: unregister()

   Unregister all panels and remove basreliefsettings from the Scene type.

   This function iterates through all registered panels and unregisters
   each one using Blender's utility functions. Additionally, it removes the
   basreliefsettings attribute from the Scene type, ensuring that any
   settings related to bas relief are no longer accessible in the current
   Blender session.


