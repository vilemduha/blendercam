fabex.joinery.arc_bar
=====================

.. py:module:: fabex.joinery.arc_bar


Functions
---------

.. autoapisummary::

   fabex.joinery.arc_bar.bar
   fabex.joinery.arc_bar.arc
   fabex.joinery.arc_bar.arc_bar_arc
   fabex.joinery.arc_bar.arc_bar


Module Contents
---------------

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


