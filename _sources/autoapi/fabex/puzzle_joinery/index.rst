fabex.puzzle_joinery
====================

.. py:module:: fabex.puzzle_joinery

.. autoapi-nested-parse::

   Fabex 'puzzle_joinery.py' © 2021 Alain Pelletier

   Functions to add various puzzle joints as curves.



Functions
---------

.. autoapisummary::

   fabex.puzzle_joinery.finger
   fabex.puzzle_joinery.fingers
   fabex.puzzle_joinery.twist_female
   fabex.puzzle_joinery.twist_male
   fabex.puzzle_joinery.bar
   fabex.puzzle_joinery.arc
   fabex.puzzle_joinery.arc_bar_arc
   fabex.puzzle_joinery.arc_bar
   fabex.puzzle_joinery.multiangle
   fabex.puzzle_joinery.t
   fabex.puzzle_joinery.curved_t
   fabex.puzzle_joinery.mitre
   fabex.puzzle_joinery.open_curve
   fabex.puzzle_joinery.tile


Module Contents
---------------

.. py:function:: finger(diameter, stem=2)

   Create a joint shape based on the specified diameter and stem.

   This function generates a 3D joint shape using Blender's curve
   operations. It calculates the dimensions of a rectangle and an ellipse
   based on the provided diameter and stem parameters. The function then
   creates these shapes, duplicates and mirrors them, and performs boolean
   operations to form the final joint shape. The resulting object is named
   and cleaned up to ensure no overlapping vertices remain.

   :param diameter: The diameter of the tool for joint creation.
   :type diameter: float
   :param stem: The amount of radius the stem or neck of the joint will have. Defaults
                to 2.
   :type stem: float?

   :returns: This function does not return any value.
   :rtype: None


.. py:function:: fingers(diameter, inside, amount=1, stem=1)

   Create a specified number of fingers for a joint tool.

   This function generates a set of fingers based on the provided diameter
   and tolerance values. It calculates the necessary translations for
   positioning the fingers and duplicates them if more than one is
   required. Additionally, it creates a receptacle using a silhouette
   offset from the fingers, allowing for precise joint creation.

   :param diameter: The diameter of the tool used for joint creation.
   :type diameter: float
   :param inside: The tolerance in the joint receptacle.
   :type inside: float
   :param amount: The number of fingers to create. Defaults to 1.
   :type amount: int?
   :param stem: The amount of radius the stem or neck of the joint will have. Defaults
                to 1.
   :type stem: float?


.. py:function:: twist_female(name, length, diameter, tolerance, twist, tneck, tthick, twist_keep=False)

   Add a twist lock to a receptacle.

   This function modifies the receptacle by adding a twist lock feature if
   the `twist` parameter is set to True. It performs several operations
   including interlocking the twist, rotating the object, and moving it to
   the correct position. If `twist_keep` is True, it duplicates the twist
   lock for further modifications. The function utilizes parameters such as
   length, diameter, tolerance, and thickness to accurately create the
   twist lock.

   :param name: The name of the receptacle to be modified.
   :type name: str
   :param length: The length of the receptacle.
   :type length: float
   :param diameter: The diameter of the receptacle.
   :type diameter: float
   :param tolerance: The tolerance value for the twist lock.
   :type tolerance: float
   :param twist: A flag indicating whether to add a twist lock.
   :type twist: bool
   :param tneck: The neck thickness for the twist lock.
   :type tneck: float
   :param tthick: The thickness of the twist lock.
   :type tthick: float
   :param twist_keep: A flag indicating whether to keep the twist
                      lock after duplication. Defaults to False.
   :type twist_keep: bool?


.. py:function:: twist_male(name, length, diameter, tolerance, twist, tneck, tthick, angle, twist_keep=False, x=0, y=0)

   Add a twist lock to a male connector.

   This function modifies the geometry of a male connector by adding a
   twist lock feature. It utilizes various parameters to determine the
   dimensions and positioning of the twist lock. If the `twist_keep`
   parameter is set to True, it duplicates the twist lock for further
   modifications. The function also allows for adjustments in position
   through the `x` and `y` parameters.

   :param name: The name of the connector to be modified.
   :type name: str
   :param length: The length of the connector.
   :type length: float
   :param diameter: The diameter of the connector.
   :type diameter: float
   :param tolerance: The tolerance level for the twist lock.
   :type tolerance: float
   :param twist: A flag indicating whether to add a twist lock.
   :type twist: bool
   :param tneck: The neck thickness for the twist lock.
   :type tneck: float
   :param tthick: The thickness of the twist lock.
   :type tthick: float
   :param angle: The angle at which to rotate the twist lock.
   :type angle: float
   :param twist_keep: A flag indicating whether to keep the twist lock duplicate. Defaults to
                      False.
   :type twist_keep: bool?
   :param x: The x-coordinate for positioning. Defaults to 0.
   :type x: float?
   :param y: The y-coordinate for positioning. Defaults to 0.
   :type y: float?

   :returns:

             This function modifies the state of the connector but does not return a
                 value.
   :rtype: None


.. py:function:: bar(width, thick, diameter, tolerance, amount=0, stem=1, twist=False, tneck=0.5, tthick=0.01, twist_keep=False, twist_line=False, twist_line_amount=2, which='MF')

   Create a bar with specified dimensions and joint features.

   This function generates a bar with customizable parameters such as
   width, thickness, and joint characteristics. It can automatically
   determine the number of fingers in the joint if the amount is set to
   zero. The function also supports various options for twisting and neck
   dimensions, allowing for flexible design of the bar according to the
   specified parameters. The resulting bar can be manipulated further based
   on the provided options.

   :param width: The length of the bar.
   :type width: float
   :param thick: The thickness of the bar.
   :type thick: float
   :param diameter: The diameter of the tool used for joint creation.
   :type diameter: float
   :param tolerance: The tolerance in the joint.
   :type tolerance: float
   :param amount: The number of fingers in the joint; 0 means auto-generate. Defaults to
                  0.
   :type amount: int?
   :param stem: The radius of the stem or neck of the joint. Defaults to 1.
   :type stem: float?
   :param twist: Whether to add a twist lock. Defaults to False.
   :type twist: bool?
   :param tneck: The percentage the twist neck will have compared to thickness. Defaults
                 to 0.5.
   :type tneck: float?
   :param tthick: The thickness of the twist material. Defaults to 0.01.
   :type tthick: float?
   :param twist_keep: Whether to keep the twist feature. Defaults to False.
   :type twist_keep: bool?
   :param twist_line: Whether to add a twist line. Defaults to False.
   :type twist_line: bool?
   :param twist_line_amount: The amount for the twist line. Defaults to 2.
   :type twist_line_amount: int?
   :param which: Specifies the type of joint; options are 'M', 'F', 'MF', 'MM', 'FF'.
                 Defaults to 'MF'.
   :type which: str?

   :returns:

             This function does not return a value but modifies the state of the 3D
                 model in Blender.
   :rtype: None


.. py:function:: arc(radius, thick, angle, diameter, tolerance, amount=0, stem=1, twist=False, tneck=0.5, tthick=0.01, twist_keep=False, which='MF')

   Generate an arc with specified parameters.

   This function creates a 3D arc based on the provided radius, thickness,
   angle, and other parameters. It handles the generation of fingers for
   the joint and applies twisting features if specified. The function also
   manages the orientation and positioning of the generated arc in a 3D
   space.

   :param radius: The radius of the curve.
   :type radius: float
   :param thick: The thickness of the bar.
   :type thick: float
   :param angle: The angle of the arc (must not be zero).
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
   :param twist: Whether to add a twist lock. Defaults to False.
   :type twist: bool?
   :param tneck: Percentage the twist neck will have compared to thickness. Defaults to
                 0.5.
   :type tneck: float?
   :param tthick: Thickness of the twist material. Defaults to 0.01.
   :type tthick: float?
   :param twist_keep: Whether to keep the twist. Defaults to False.
   :type twist_keep: bool?
   :param which: Specifies which joint to generate ('M', 'F', 'MF'). Defaults to 'MF'.
   :type which: str?

   :returns:

             This function does not return a value but modifies the 3D scene
                 directly.
   :rtype: None


.. py:function:: arc_bar_arc(length, radius, thick, angle, angleb, diameter, tolerance, amount=0, stem=1, twist=False, tneck=0.5, tthick=0.01, which='MF', twist_keep=False, twist_line=False, twist_line_amount=2)

   Generate an arc bar joint with specified parameters.

   This function creates a joint consisting of male and female sections
   based on the provided parameters. It adjusts the length to account for
   the radius and thickness, generates a base rectangle, and then
   constructs the male and/or female sections as specified. Additionally,
   it can create a twist lock feature if required. The function utilizes
   Blender's bpy operations to manipulate 3D objects.

   :param length: The total width of the segments including 2 * radius and thickness.
   :type length: float
   :param radius: The radius of the curve.
   :type radius: float
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
   :param amount: The number of fingers in the joint; 0 means auto-generate. Defaults to
                  0.
   :type amount: int?
   :param stem: The amount of radius the stem or neck of the joint will have. Defaults
                to 1.
   :type stem: float?
   :param twist: Whether to add a twist lock feature. Defaults to False.
   :type twist: bool?
   :param tneck: Percentage the twist neck will have compared to thickness. Defaults to
                 0.5.
   :type tneck: float?
   :param tthick: Thickness of the twist material. Defaults to 0.01.
   :type tthick: float?
   :param which: Specifies which joint to generate ('M', 'F', or 'MF'). Defaults to 'MF'.
   :type which: str?
   :param twist_keep: Whether to keep the twist after creation. Defaults to False.
   :type twist_keep: bool?
   :param twist_line: Whether to create a twist line feature. Defaults to False.
   :type twist_line: bool?
   :param twist_line_amount: Amount for the twist line feature. Defaults to 2.
   :type twist_line_amount: int?

   :returns:

             This function does not return a value but modifies the Blender scene
                 directly.
   :rtype: None


.. py:function:: arc_bar(length, radius, thick, angle, diameter, tolerance, amount=0, stem=1, twist=False, tneck=0.5, tthick=0.01, twist_keep=False, which='MF', twist_line=False, twist_line_amount=2)

   Generate an arc bar joint based on specified parameters.

   This function constructs an arc bar joint by generating male and female
   sections according to the specified parameters such as length, radius,
   thickness, and joint type. The function adjusts the length to account
   for the radius and thickness of the bar and creates the appropriate
   geometric shapes for the joint. It also includes options for twisting
   and adjusting the neck thickness of the joint.

   :param length: The total width of the segments including 2 * radius and thickness.
   :type length: float
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
   :param amount: The number of fingers in the joint; 0 means auto-generate. Defaults to
                  0.
   :type amount: int?
   :param stem: The amount of radius the stem or neck of the joint will have. Defaults
                to 1.
   :type stem: float?
   :param twist: Whether to add a twist lock. Defaults to False.
   :type twist: bool?
   :param tneck: Percentage the twist neck will have compared to thickness. Defaults to
                 0.5.
   :type tneck: float?
   :param tthick: Thickness of the twist material. Defaults to 0.01.
   :type tthick: float?
   :param twist_keep: Whether to keep the twist. Defaults to False.
   :type twist_keep: bool?
   :param which: Specifies which joint to generate ('M', 'F', 'MF'). Defaults to 'MF'.
   :type which: str?
   :param twist_line: Whether to include a twist line. Defaults to False.
   :type twist_line: bool?
   :param twist_line_amount: Amount of twist line. Defaults to 2.
   :type twist_line_amount: int?


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


