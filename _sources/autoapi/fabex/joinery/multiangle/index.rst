fabex.joinery.multiangle
========================

.. py:module:: fabex.joinery.multiangle


Functions
---------

.. autoapisummary::

   fabex.joinery.multiangle.multiangle
   fabex.joinery.multiangle.t
   fabex.joinery.multiangle.curved_t
   fabex.joinery.multiangle.mitre
   fabex.joinery.multiangle.open_curve
   fabex.joinery.multiangle.tile


Module Contents
---------------

.. py:function:: multiangle(radius, thick, angle, diameter, tolerance, amount=0, stem=1, twist=False, tneck=0.5, tthick=0.01, combination='MFF')

   Generate a multi-angle joint based on specified parameters.

   This function creates a multi-angle joint by generating various
   geometric shapes using the provided parameters such as radius,
   thickness, angle, diameter, and tolerance. It utilizes Blender's
   operations to create and manipulate curves, resulting in a joint that
   can be customized with different combinations of male and female parts.
   The function also allows for automatic generation of the number of
   fingers in the joint and includes options for twisting and neck
   dimensions.

   :param radius: The radius of the curve.
   :type radius: float
   :param thick: The thickness of the bar.
   :type thick: float
   :param angle: The angle of the female part.
   :type angle: float
   :param diameter: The diameter of the tool for joint creation.
   :type diameter: float
   :param tolerance: Tolerance in the joint.
   :type tolerance: float
   :param amount: The amount of fingers in the joint; 0 means auto-generate. Defaults to
                  0.
   :type amount: int?
   :param stem: The amount of radius the stem or neck of the joint will have. Defaults
                to 1.
   :type stem: float?
   :param twist: Indicates if a twist lock addition is required. Defaults to False.
   :type twist: bool?
   :param tneck: Percentage the twist neck will have compared to thickness. Defaults to
                 0.5.
   :type tneck: float?
   :param tthick: Thickness of the twist material. Defaults to 0.01.
   :type tthick: float?
   :param combination: Specifies which joint to generate ('M', 'F', 'MF', 'MFF', 'MMF').
                       Defaults to 'MFF'.
   :type combination: str?

   :returns:

             This function does not return a value but performs operations in
                 Blender.
   :rtype: None


.. py:function:: t(length, thick, diameter, tolerance, amount=0, stem=1, twist=False, tneck=0.5, tthick=0.01, combination='MF', base_gender='M', corner=False)

   Generate a 3D model based on specified parameters.

   This function creates a 3D model by manipulating geometric shapes based
   on the provided parameters. It handles different combinations of shapes
   and orientations based on the specified gender and corner options. The
   function utilizes several helper functions to perform operations such as
   moving, duplicating, and uniting shapes to form the final model.

   :param length: The length of the model.
   :type length: float
   :param thick: The thickness of the model.
   :type thick: float
   :param diameter: The diameter of the model.
   :type diameter: float
   :param tolerance: The tolerance level for the model dimensions.
   :type tolerance: float
   :param amount: The amount of material to use. Defaults to 0.
   :type amount: int?
   :param stem: The stem value for the model. Defaults to 1.
   :type stem: int?
   :param twist: Whether to apply a twist to the model. Defaults to False.
   :type twist: bool?
   :param tneck: The neck thickness. Defaults to 0.5.
   :type tneck: float?
   :param tthick: The thickness for the neck. Defaults to 0.01.
   :type tthick: float?
   :param combination: The combination type ('MF', 'F', 'M'). Defaults to 'MF'.
   :type combination: str?
   :param base_gender: The base gender for the model ('M' or 'F'). Defaults to 'M'.
   :type base_gender: str?
   :param corner: Whether to apply corner adjustments. Defaults to False.
   :type corner: bool?

   :returns:

             This function does not return a value but modifies the 3D model
                 directly.
   :rtype: None


.. py:function:: curved_t(length, thick, radius, diameter, tolerance, amount=0, stem=1, twist=False, tneck=0.5, tthick=0.01, combination='MF', base_gender='M')

   Create a curved shape based on specified parameters.

   This function generates a 3D curved shape using the provided dimensions
   and characteristics. It utilizes the `bar` and `arc` functions to create
   the desired geometry and applies transformations such as mirroring and
   union operations to achieve the final shape. The function also allows
   for customization based on the gender specification, which influences
   the shape's design.

   :param length: The length of the bar.
   :type length: float
   :param thick: The thickness of the bar.
   :type thick: float
   :param radius: The radius of the arc.
   :type radius: float
   :param diameter: The diameter used in arc creation.
   :type diameter: float
   :param tolerance: The tolerance level for the shape.
   :type tolerance: float
   :param amount: The amount parameter for the shape generation. Defaults to 0.
   :type amount: int?
   :param stem: The stem parameter for the shape generation. Defaults to 1.
   :type stem: int?
   :param twist: A flag indicating whether to apply a twist to the shape. Defaults to
                 False.
   :type twist: bool?
   :param tneck: The neck thickness parameter. Defaults to 0.5.
   :type tneck: float?
   :param tthick: The thickness parameter for the neck. Defaults to 0.01.
   :type tthick: float?
   :param combination: The combination type for the shape. Defaults to 'MF'.
   :type combination: str?
   :param base_gender: The base gender for the shape design. Defaults to 'M'.
   :type base_gender: str?

   :returns:

             This function does not return a value but modifies the 3D model in the
                 environment.
   :rtype: None


.. py:function:: mitre(length, thick, angle, angleb, diameter, tolerance, amount=0, stem=1, twist=False, tneck=0.5, tthick=0.01, which='MF')

   Generate a mitre joint based on specified parameters.

   This function creates a 3D representation of a mitre joint using
   Blender's bpy.ops.curve.simple operations. It generates a base rectangle
   and cutout shapes, then constructs male and female sections of the joint
   based on the provided angles and dimensions. The function allows for
   customization of various parameters such as thickness, diameter,
   tolerance, and the number of fingers in the joint. The resulting joint
   can be either male, female, or a combination of both.

   :param length: The total width of the segments including 2 * radius and thickness.
   :type length: float
   :param thick: The thickness of the bar.
   :type thick: float
   :param angle: The angle of the female part.
   :type angle: float
   :param angleb: The angle of the male part.
   :type angleb: float
   :param diameter: The diameter of the tool for joint creation.
   :type diameter: float
   :param tolerance: Tolerance in the joint.
   :type tolerance: float
   :param amount: Amount of fingers in the joint; 0 means auto-generate. Defaults to 0.
   :type amount: int?
   :param stem: Amount of radius the stem or neck of the joint will have. Defaults to 1.
   :type stem: float?
   :param twist: Indicates if a twist lock addition is required. Defaults to False.
   :type twist: bool?
   :param tneck: Percentage the twist neck will have compared to thickness. Defaults to
                 0.5.
   :type tneck: float?
   :param tthick: Thickness of the twist material. Defaults to 0.01.
   :type tthick: float?
   :param which: Specifies which joint to generate ('M', 'F', 'MF'). Defaults to 'MF'.
   :type which: str?


.. py:function:: open_curve(line, thick, diameter, tolerance, amount=0, stem=1, twist=False, t_neck=0.5, t_thick=0.01, twist_amount=1, which='MF', twist_keep=False)

   Open a curve and add puzzle connectors with optional twist lock
   connectors.

   This function takes a shapely LineString and creates an open curve with
   specified parameters such as thickness, diameter, tolerance, and twist
   options. It generates puzzle connectors at the ends of the curve and can
   optionally add twist lock connectors along the curve. The function also
   handles the creation of the joint based on the provided parameters,
   ensuring that the resulting geometry meets the specified design
   requirements.

   :param line: A shapely LineString representing the path of the curve.
   :type line: LineString
   :param thick: The thickness of the bar used in the joint.
   :type thick: float
   :param diameter: The diameter of the tool for joint creation.
   :type diameter: float
   :param tolerance: The tolerance in the joint.
   :type tolerance: float
   :param amount: The number of fingers in the joint; 0 means auto-generate. Defaults to
                  0.
   :type amount: int?
   :param stem: The amount of radius the stem or neck of the joint will have. Defaults
                to 1.
   :type stem: float?
   :param twist: Whether to add twist lock connectors. Defaults to False.
   :type twist: bool?
   :param t_neck: The percentage the twist neck will have compared to thickness. Defaults
                  to 0.5.
   :type t_neck: float?
   :param t_thick: The thickness of the twist material. Defaults to 0.01.
   :type t_thick: float?
   :param twist_amount: The amount of twist distributed on the curve, not counting joint twists.
                        Defaults to 1.
   :type twist_amount: int?
   :param which: Specifies the type of joint; options include 'M', 'F', 'MF', 'MM', 'FF'.
                 Defaults to 'MF'.
   :type which: str?
   :param twist_keep: Whether to keep the twist lock connectors. Defaults to False.
   :type twist_keep: bool?

   :returns:

             This function does not return a value but modifies the geometry in the
                 Blender context.
   :rtype: None


.. py:function:: tile(diameter, tolerance, tile_x_amount, tile_y_amount, stem=1)

   Create a tile shape based on specified dimensions and parameters.

   This function calculates the dimensions of a tile based on the provided
   diameter and tolerance, as well as the number of tiles in the x and y
   directions. It constructs the tile shape by creating a base and adding
   features such as fingers for interlocking. The function also handles
   transformations such as moving, rotating, and performing boolean
   operations to achieve the desired tile geometry.

   :param diameter: The diameter of the tile.
   :type diameter: float
   :param tolerance: The tolerance to be applied to the tile dimensions.
   :type tolerance: float
   :param tile_x_amount: The number of tiles along the x-axis.
   :type tile_x_amount: int
   :param tile_y_amount: The number of tiles along the y-axis.
   :type tile_y_amount: int
   :param stem: A parameter affecting the tile's features. Defaults to 1.
   :type stem: int?

   :returns: This function does not return a value but modifies global state.
   :rtype: None


