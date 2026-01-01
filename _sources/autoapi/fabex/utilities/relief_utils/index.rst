fabex.utilities.relief_utils
============================

.. py:module:: fabex.utilities.relief_utils

.. autoapi-nested-parse::

   Fabex 'bas_relief.py'

   Module to allow the creation of reliefs from Images or View Layers.
   (https://en.wikipedia.org/wiki/Relief#Bas-relief_or_low_relief)



Exceptions
----------

.. autoapisummary::

   fabex.utilities.relief_utils.ReliefError


Functions
---------

.. autoapisummary::

   fabex.utilities.relief_utils.copy_compbuf_data
   fabex.utilities.relief_utils.restrict_buffer
   fabex.utilities.relief_utils.prolongate
   fabex.utilities.relief_utils.idx
   fabex.utilities.relief_utils.smooth
   fabex.utilities.relief_utils.calculate_defect
   fabex.utilities.relief_utils.add_correction
   fabex.utilities.relief_utils.solve_pde_multigrid
   fabex.utilities.relief_utils.asolve
   fabex.utilities.relief_utils.atimes
   fabex.utilities.relief_utils.snrm
   fabex.utilities.relief_utils.linear_bcg
   fabex.utilities.relief_utils.tonemap
   fabex.utilities.relief_utils.vert
   fabex.utilities.relief_utils.build_mesh
   fabex.utilities.relief_utils.render_scene
   fabex.utilities.relief_utils.problem_areas
   fabex.utilities.relief_utils.relief


Module Contents
---------------

.. py:exception:: ReliefError

   Bases: :py:obj:`Exception`


   Common base class for all non-exit exceptions.


.. py:function:: copy_compbuf_data(inbuf, outbuf)

.. py:function:: restrict_buffer(inbuf, outbuf)

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


.. py:function:: linear_bcg(n, b, x, itol, tol, itmax, iter, err, rows, cols, planar)

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


.. py:function:: build_mesh(mesh_z, br)

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


.. py:function:: render_scene(width, height, bit_diameter, passes_per_radius, make_nodes, view_layer)

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


.. py:function:: problem_areas(br)

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


