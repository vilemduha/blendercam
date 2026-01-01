fabex.operators.curve_create_ops
================================

.. py:module:: fabex.operators.curve_create_ops

.. autoapi-nested-parse::

   Fabex 'curve_cam_create.py' © 2021, 2022 Alain Pelletier

   Operators to create a number of predefined curve objects.



Classes
-------

.. autoapisummary::

   fabex.operators.curve_create_ops.CamCurveHatch
   fabex.operators.curve_create_ops.CamCurvePlate
   fabex.operators.curve_create_ops.CamCurveFlatCone
   fabex.operators.curve_create_ops.CamCurveMortise
   fabex.operators.curve_create_ops.CamCurveInterlock
   fabex.operators.curve_create_ops.CamCurveDrawer
   fabex.operators.curve_create_ops.CamCurvePuzzle
   fabex.operators.curve_create_ops.CamCurveGear


Functions
---------

.. autoapisummary::

   fabex.operators.curve_create_ops.generate_crosshatch


Module Contents
---------------

.. py:function:: generate_crosshatch(context, angle, distance, offset, pocket_shape, join, ob=None)

   Execute the crosshatch generation process based on the provided context.

   :param context: The Blender context containing the active object.
   :type context: bpy.context
   :param angle: The angle for rotating the crosshatch pattern.
   :type angle: float
   :param distance: The distance between crosshatch lines.
   :type distance: float
   :param offset: The offset for the bounds or hull.
   :type offset: float
   :param pocket_shape: Determines whether to use bounds, hull, or pocket.
   :type pocket_shape: str

   :returns: The resulting intersection geometry of the crosshatch.
   :rtype: shapely.geometry.MultiLineString


.. py:class:: CamCurveHatch

   Bases: :py:obj:`bpy.types.Operator`


   Perform Hatch Operation on Single or Multiple Curves


   .. py:attribute:: bl_idname
      :value: 'object.curve_hatch'



   .. py:attribute:: bl_label
      :value: 'CrossHatch Curve'



   .. py:attribute:: bl_options


   .. py:attribute:: angle
      :type:  FloatProperty(default=0, min=-pi / 2, max=pi / 2, precision=4, subtype='ANGLE')


   .. py:attribute:: distance
      :type:  FloatProperty(default=0.003, min=0.0001, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: offset
      :type:  FloatProperty(default=0, min=-1.0, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: pocket_shape
      :type:  EnumProperty(name='Pocket Shape', items=(('BOUNDS', 'Bounds Rectangle', 'Uses a bounding rectangle'), ('HULL', 'Convex Hull', 'Uses a convex hull'), ('POCKET', 'Pocket', 'Uses the pocket shape')), description='Type of pocket shape', default='POCKET')


   .. py:attribute:: contour
      :type:  BoolProperty(name='Contour Curve', default=False)


   .. py:attribute:: xhatch
      :type:  BoolProperty(name='Crosshatch #', default=False)


   .. py:attribute:: contour_separate
      :type:  BoolProperty(name='Contour Separate', default=False)


   .. py:attribute:: straight
      :type:  BoolProperty(name='Overshoot Style', description='Use overshoot cutout instead of conventional rounded', default=True)


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: draw(context)

      Draw the layout properties for the given context.



   .. py:method:: execute(context)


.. py:class:: CamCurvePlate

   Bases: :py:obj:`bpy.types.Operator`


   Generates Rounded Plate with Mounting Holes


   .. py:attribute:: bl_idname
      :value: 'object.curve_plate'



   .. py:attribute:: bl_label
      :value: 'Sign Plate'



   .. py:attribute:: bl_options


   .. py:attribute:: radius
      :type:  FloatProperty(name='Corner Radius', default=0.025, min=0, max=0.1, precision=4, unit='LENGTH')


   .. py:attribute:: width
      :type:  FloatProperty(name='Width of Plate', default=0.3048, min=0, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: height
      :type:  FloatProperty(name='Height of Plate', default=0.457, min=0, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: hole_diameter
      :type:  FloatProperty(name='Hole Diameter', default=0.01, min=0, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: hole_tolerance
      :type:  FloatProperty(name='Hole V Tolerance', default=0.005, min=0, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: hole_vdist
      :type:  FloatProperty(name='Hole Vert Distance', default=0.4, min=0, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: hole_hdist
      :type:  FloatProperty(name='Hole Horiz Distance', default=0, min=0, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: hole_hamount
      :type:  IntProperty(name='Hole Horiz Amount', default=1, min=0, max=50)


   .. py:attribute:: resolution
      :type:  IntProperty(name='Spline Resolution', default=50, min=3, max=150)


   .. py:attribute:: plate_type
      :type:  EnumProperty(name='Type Plate', items=(('ROUNDED', 'Rounded corner', 'Makes a rounded corner plate'), ('COVE', 'Cove corner', 'Makes a plate with circles cut in each corner '), ('BEVEL', 'Bevel corner', 'Makes a plate with beveled corners '), ('OVAL', 'Elipse', 'Makes an oval plate')), description='Type of Plate', default='ROUNDED')


   .. py:method:: draw(context)

      Draw the UI layout for plate properties.

      This method creates a user interface layout for configuring various
      properties of a plate, including its type, dimensions, hole
      specifications, and resolution. It dynamically adds properties to the
      layout based on the selected plate type, allowing users to input
      relevant parameters.

      :param context: The context in which the UI is being drawn.



   .. py:method:: execute(context)

      Execute the creation of a plate based on specified parameters.

      This function generates a plate shape in Blender based on the defined
      attributes such as width, height, radius, and plate type. It supports
      different plate types including rounded, oval, cove, and bevel. The
      function also handles the creation of holes in the plate if specified.
      It utilizes Blender's curve operations to create the geometry and
      applies various transformations to achieve the desired shape.

      :param context: The Blender context in which the operation is performed.
      :type context: bpy.context

      :returns:

                A dictionary indicating the result of the operation, typically
                    {'FINISHED'} if successful.
      :rtype: dict



.. py:class:: CamCurveFlatCone

   Bases: :py:obj:`bpy.types.Operator`


   Generates Cone from Flat Stock


   .. py:attribute:: bl_idname
      :value: 'object.curve_flat_cone'



   .. py:attribute:: bl_label
      :value: 'Cone Flat Calculator'



   .. py:attribute:: bl_options


   .. py:attribute:: small_d
      :type:  FloatProperty(name='Small Diameter', default=0.025, min=0.0001, max=0.1, precision=4, unit='LENGTH')


   .. py:attribute:: large_d
      :type:  FloatProperty(name='Large Diameter', default=0.3048, min=0.0001, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: height
      :type:  FloatProperty(name='Height of Cone', default=0.457, min=0.0001, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: tab
      :type:  FloatProperty(name='Tab Witdh', default=0.01, min=0, max=0.1, precision=4, unit='LENGTH')


   .. py:attribute:: intake
      :type:  FloatProperty(name='Intake Diameter', default=0, min=0, max=0.2, precision=4, unit='LENGTH')


   .. py:attribute:: intake_skew
      :type:  FloatProperty(name='Intake Skew', default=1, min=0.1, max=4)


   .. py:attribute:: resolution
      :type:  IntProperty(name='Resolution', default=12, min=5, max=200)


   .. py:method:: execute(context)

      Execute the construction of a geometric shape in Blender.

      This method performs a series of operations to create a geometric shape
      based on specified dimensions and parameters. It calculates various
      dimensions needed for the shape, including height and angles, and then
      uses Blender's operations to create segments, rectangles, and ellipses.
      The function also handles the positioning and rotation of these shapes
      within the 3D space of Blender.

      :param context: The context in which the operation is executed, typically containing
                      information about the current
                      scene and active objects in Blender.

      :returns:

                A dictionary indicating the completion status of the operation,
                    typically {'FINISHED'}.
      :rtype: dict



.. py:class:: CamCurveMortise

   Bases: :py:obj:`bpy.types.Operator`


   Generates Mortise Along a Curve


   .. py:attribute:: bl_idname
      :value: 'object.curve_mortise'



   .. py:attribute:: bl_label
      :value: 'Mortise'



   .. py:attribute:: bl_options


   .. py:attribute:: finger_size
      :type:  BoolProperty(name='Kurf Bending only', default=False)


   .. py:attribute:: min_finger_size
      :type:  FloatProperty(name='Minimum Finger Size', default=0.0025, min=0.001, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: finger_tolerance
      :type:  FloatProperty(name='Finger Play Room', default=4.5e-05, min=0, max=0.003, precision=4, unit='LENGTH')


   .. py:attribute:: plate_thickness
      :type:  FloatProperty(name='Drawer Plate Thickness', default=0.00477, min=0.001, max=3.0, unit='LENGTH')


   .. py:attribute:: side_height
      :type:  FloatProperty(name='Side Height', default=0.05, min=0.001, max=3.0, unit='LENGTH')


   .. py:attribute:: flex_pocket
      :type:  FloatProperty(name='Flex Pocket', default=0.004, min=0.0, max=1.0, unit='LENGTH')


   .. py:attribute:: top_bottom
      :type:  BoolProperty(name='Side Top & Bottom Fingers', default=True)


   .. py:attribute:: opencurve
      :type:  BoolProperty(name='OpenCurve', default=False)


   .. py:attribute:: adaptive
      :type:  FloatProperty(name='Adaptive Angle Threshold', default=0.0, min=0.0, max=2, step=100, subtype='ANGLE', unit='ROTATION')


   .. py:attribute:: double_adaptive
      :type:  BoolProperty(name='Double Adaptive Pockets', default=False)


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the joinery process based on the provided context.

      This function performs a series of operations to duplicate the active
      object, convert it to a mesh, and then process its geometry to create
      joinery features. It extracts vertex coordinates, converts them into a
      LineString data structure, and applies either variable or fixed finger
      joinery based on the specified parameters. The function also handles the
      creation of flexible sides and pockets if required.

      :param context: The context in which the operation is executed.
      :type context: bpy.context

      :returns: A dictionary indicating the completion status of the operation.
      :rtype: dict



.. py:class:: CamCurveInterlock

   Bases: :py:obj:`bpy.types.Operator`


   Generates Interlock Along a Curve


   .. py:attribute:: bl_idname
      :value: 'object.curve_interlock'



   .. py:attribute:: bl_label
      :value: 'Interlock'



   .. py:attribute:: bl_options


   .. py:attribute:: finger_size
      :type:  FloatProperty(name='Finger Size', default=0.015, min=0.005, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: finger_tolerance
      :type:  FloatProperty(name='Finger Play Room', default=4.5e-05, min=0, max=0.003, precision=4, unit='LENGTH')


   .. py:attribute:: plate_thickness
      :type:  FloatProperty(name='Plate Thickness', default=0.00477, min=0.001, max=3.0, unit='LENGTH')


   .. py:attribute:: opencurve
      :type:  BoolProperty(name='OpenCurve', default=False)


   .. py:attribute:: interlock_type
      :type:  EnumProperty(name='Type of Interlock', items=(('TWIST', 'Twist', 'Interlock requires 1/4 turn twist'), ('GROOVE', 'Groove', 'Simple sliding groove'), ('PUZZLE', 'Puzzle Interlock', 'Puzzle good for flat joints')), description='Type of interlock', default='GROOVE')


   .. py:attribute:: finger_amount
      :type:  IntProperty(name='Finger Amount', default=2, min=1, max=100)


   .. py:attribute:: tangent_angle
      :type:  FloatProperty(name='Tangent Deviation', default=0.0, min=0.0, max=2, step=100, subtype='ANGLE', unit='ROTATION')


   .. py:attribute:: fixed_angle
      :type:  FloatProperty(name='Fixed Angle', default=0.0, min=0.0, max=2, step=100, subtype='ANGLE', unit='ROTATION')


   .. py:method:: execute(context)

      Execute the joinery operation based on the selected objects in the
      context.

      This function checks the selected objects in the provided context and
      performs different operations depending on the type of the active
      object. If the active object is a curve or font and there are selected
      objects, it duplicates the object, converts it to a mesh, and processes
      its vertices to create a LineString representation. The function then
      calculates lengths and applies distributed interlock joinery based on
      the specified parameters. If no valid objects are selected, it defaults
      to a single interlock operation at the cursor's location.

      :param context: The context containing selected objects and active object.
      :type context: bpy.context

      :returns: A dictionary indicating the operation's completion status.
      :rtype: dict



.. py:class:: CamCurveDrawer

   Bases: :py:obj:`bpy.types.Operator`


   Generates Drawers


   .. py:attribute:: bl_idname
      :value: 'object.curve_drawer'



   .. py:attribute:: bl_label
      :value: 'Drawer'



   .. py:attribute:: bl_options


   .. py:attribute:: depth
      :type:  FloatProperty(name='Drawer Depth', default=0.2, min=0, max=1.0, precision=4, unit='LENGTH')


   .. py:attribute:: width
      :type:  FloatProperty(name='Drawer Width', default=0.125, min=0, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: height
      :type:  FloatProperty(name='Drawer Height', default=0.07, min=0, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: finger_size
      :type:  FloatProperty(name='Maximum Finger Size', default=0.015, min=0.005, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: finger_tolerance
      :type:  FloatProperty(name='Finger Play Room', default=4.5e-05, min=0, max=0.003, precision=4, unit='LENGTH')


   .. py:attribute:: finger_inset
      :type:  FloatProperty(name='Finger Inset', default=0.0, min=0.0, max=0.01, precision=4, unit='LENGTH')


   .. py:attribute:: drawer_plate_thickness
      :type:  FloatProperty(name='Drawer Plate Thickness', default=0.00477, min=0.001, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: drawer_hole_diameter
      :type:  FloatProperty(name='Drawer Hole Diameter', default=0.02, min=1e-05, max=0.5, precision=4, unit='LENGTH')


   .. py:attribute:: drawer_hole_offset
      :type:  FloatProperty(name='Drawer Hole Offset', default=0.0, min=-0.5, max=0.5, precision=4, unit='LENGTH')


   .. py:attribute:: overcut
      :type:  BoolProperty(name='Add Overcut', default=False)


   .. py:attribute:: overcut_diameter
      :type:  FloatProperty(name='Overcut Tool Diameter', default=0.003175, min=-0.001, max=0.5, precision=4, unit='LENGTH')


   .. py:method:: draw(context)

      Draw the user interface properties for the object.

      This method is responsible for rendering the layout of various
      properties related to the object's dimensions and specifications. It
      adds properties such as depth, width, height, finger size, finger
      tolerance, finger inset, drawer plate thickness, drawer hole diameter,
      drawer hole offset, and overcut diameter to the layout. The overcut
      diameter property is only added if the overcut option is enabled.

      :param context: The context in which the drawing occurs, typically containing
                      information about the current state and environment.



   .. py:method:: execute(context)

      Execute the drawer creation process in Blender.

      This method orchestrates the creation of a drawer by calculating the
      necessary dimensions for the finger joints, creating the base plate, and
      generating the drawer components such as the back, front, sides, and
      bottom. It utilizes various helper functions to perform operations like
      boolean differences and transformations to achieve the desired geometry.
      The method also handles the placement of the drawer components in the 3D
      space.

      :param context: The Blender context that provides access to the current scene and
                      objects.
      :type context: bpy.context

      :returns:

                A dictionary indicating the completion status of the operation,
                    typically {'FINISHED'}.
      :rtype: dict



.. py:class:: CamCurvePuzzle

   Bases: :py:obj:`bpy.types.Operator`


   Generates Puzzle Joints and Interlocks


   .. py:attribute:: bl_idname
      :value: 'object.curve_puzzle'



   .. py:attribute:: bl_label
      :value: 'Puzzle Joints'



   .. py:attribute:: bl_options


   .. py:attribute:: diameter
      :type:  FloatProperty(name='Tool Diameter', default=0.003175, min=0.001, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: finger_tolerance
      :type:  FloatProperty(name='Finger Play Room', default=5e-05, min=0, max=0.003, precision=4, unit='LENGTH')


   .. py:attribute:: finger_amount
      :type:  IntProperty(name='Finger Amount', default=1, min=0, max=100)


   .. py:attribute:: stem_size
      :type:  IntProperty(name='Size of the Stem', default=2, min=1, max=200)


   .. py:attribute:: width
      :type:  FloatProperty(name='Width', default=0.1, min=0.005, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: height
      :type:  FloatProperty(name='Height or Thickness', default=0.025, min=0.005, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: angle
      :type:  FloatProperty(name='Angle A', default=pi / 4, min=-10, max=10, step=500, subtype='ANGLE', unit='ROTATION')


   .. py:attribute:: angleb
      :type:  FloatProperty(name='Angle B', default=pi / 4, min=-10, max=10, step=500, subtype='ANGLE', unit='ROTATION')


   .. py:attribute:: radius
      :type:  FloatProperty(name='Arc Radius', default=0.025, min=0.005, max=5, precision=4, unit='LENGTH')


   .. py:attribute:: interlock_type
      :type:  EnumProperty(name='Type of Shape', items=(('JOINT', 'Joint', 'Puzzle Joint interlock'), ('BAR', 'Bar', 'Bar interlock'), ('ARC', 'Arc', 'Arc interlock'), ('MULTIANGLE', 'Multi angle', 'Multi angle joint'), ('CURVEBAR', 'Arc Bar', 'Arc Bar interlock'), ('CURVEBARCURVE', 'Arc Bar Arc', 'Arc Bar Arc interlock'), ('CURVET', 'T curve', 'T curve interlock'), ('T', 'T Bar', 'T Bar interlock'), ('CORNER', 'Corner Bar', 'Corner Bar interlock'), ('TILE', 'Tile', 'Tile interlock'), ('OPENCURVE', 'Open Curve', 'Corner Bar interlock')), description='Type of interlock', default='CURVET')


   .. py:attribute:: gender
      :type:  EnumProperty(name='Type Gender', items=(('MF', 'Male-Receptacle', 'Male and receptacle'), ('F', 'Receptacle only', 'Receptacle'), ('M', 'Male only', 'Male')), description='Type of interlock', default='MF')


   .. py:attribute:: base_gender
      :type:  EnumProperty(name='Base Gender', items=(('MF', 'Male - Receptacle', 'Male - Receptacle'), ('F', 'Receptacle', 'Receptacle'), ('M', 'Male', 'Male')), description='Type of interlock', default='M')


   .. py:attribute:: multiangle_gender
      :type:  EnumProperty(name='Multiangle Gender', items=(('MMF', 'Male Male Receptacle', 'M M F'), ('MFF', 'Male Receptacle Receptacle', 'M F F')), description='Type of interlock', default='MFF')


   .. py:attribute:: mitre
      :type:  BoolProperty(name='Add Mitres', default=False)


   .. py:attribute:: twist_lock
      :type:  BoolProperty(name='Add TwistLock', default=False)


   .. py:attribute:: twist_thick
      :type:  FloatProperty(name='Twist Thickness', default=0.0047, min=0.001, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: twist_percent
      :type:  FloatProperty(name='Twist Neck', default=0.3, min=0.1, max=0.9, precision=4)


   .. py:attribute:: twist_keep
      :type:  BoolProperty(name='Keep Twist Holes', default=False)


   .. py:attribute:: twist_line
      :type:  BoolProperty(name='Add Twist to Bar', default=False)


   .. py:attribute:: twist_line_amount
      :type:  IntProperty(name='Amount of Separators', default=2, min=1, max=600)


   .. py:attribute:: twist_separator
      :type:  BoolProperty(name='Add Twist Separator', default=False)


   .. py:attribute:: twist_separator_amount
      :type:  IntProperty(name='Amount of Separators', default=2, min=2, max=600)


   .. py:attribute:: twist_separator_spacing
      :type:  FloatProperty(name='Separator Spacing', default=0.025, min=-0.004, max=1.0, precision=4, unit='LENGTH')


   .. py:attribute:: twist_separator_edge_distance
      :type:  FloatProperty(name='Separator Edge Distance', default=0.01, min=0.0005, max=0.1, precision=4, unit='LENGTH')


   .. py:attribute:: tile_x_amount
      :type:  IntProperty(name='Amount of X Fingers', default=2, min=1, max=600)


   .. py:attribute:: tile_y_amount
      :type:  IntProperty(name='Amount of Y Fingers', default=2, min=1, max=600)


   .. py:attribute:: interlock_amount
      :type:  IntProperty(name='Interlock Amount on Curve', default=2, min=0, max=200)


   .. py:attribute:: overcut
      :type:  BoolProperty(name='Add Overcut', default=False)


   .. py:attribute:: overcut_diameter
      :type:  FloatProperty(name='Overcut Tool Diameter', default=0.003175, min=-0.001, max=0.5, precision=4, unit='LENGTH')


   .. py:method:: draw(context)

      Draws the user interface layout for interlock type properties.

      This method is responsible for creating and displaying the layout of
      various properties related to different interlock types in the user
      interface. It dynamically adjusts the layout based on the selected
      interlock type, allowing users to input relevant parameters such as
      dimensions, tolerances, and other characteristics specific to the chosen
      interlock type.

      :param context: The context in which the layout is being drawn, typically
                      provided by the user interface framework.

      :returns:

                This method does not return any value; it modifies the layout
                    directly.
      :rtype: None



   .. py:method:: execute(context)

      Execute the puzzle joinery process based on the provided context.

      This method processes the selected objects in the given context to
      perform various types of puzzle joinery operations. It first checks if
      there are any selected objects and if the active object is a curve. If
      so, it duplicates the object, applies transformations, and converts it
      to a mesh. The method then extracts vertex coordinates and performs
      different joinery operations based on the specified interlock type.
      Supported interlock types include 'FINGER', 'JOINT', 'BAR', 'ARC',
      'CURVEBARCURVE', 'CURVEBAR', 'MULTIANGLE', 'T', 'CURVET', 'CORNER',
      'TILE', and 'OPENCURVE'.

      :param context: The context containing selected objects and the active object.
      :type context: Context

      :returns: A dictionary indicating the completion status of the operation.
      :rtype: dict



.. py:class:: CamCurveGear

   Bases: :py:obj:`bpy.types.Operator`


   Generates Involute Gears


   .. py:attribute:: bl_idname
      :value: 'object.curve_gear'



   .. py:attribute:: bl_label
      :value: 'Gears'



   .. py:attribute:: bl_options


   .. py:attribute:: tooth_spacing
      :type:  FloatProperty(name='Distance per Tooth', default=0.01, min=0.01, max=1.0, precision=4, unit='LENGTH')


   .. py:attribute:: tooth_amount
      :type:  IntProperty(name='Amount of Teeth', default=7, min=6, max=32)


   .. py:attribute:: spoke_amount
      :type:  IntProperty(name='Amount of Spokes', default=4, min=0)


   .. py:attribute:: hole_diameter
      :type:  FloatProperty(name='Hole Diameter', default=0.003175, min=1e-05, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: rim_size
      :type:  FloatProperty(name='Rim Size', default=0.003175, min=0, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: hub_diameter
      :type:  FloatProperty(name='Hub Diameter', default=0.005, min=0, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: pressure_angle
      :type:  FloatProperty(name='Pressure Angle', default=radians(20), min=0.001, max=pi / 2, precision=4, step=100, subtype='ANGLE', unit='ROTATION')


   .. py:attribute:: clearance
      :type:  FloatProperty(name='Clearance', default=0.0, min=0, max=0.1, precision=4, unit='LENGTH')


   .. py:attribute:: backlash
      :type:  FloatProperty(name='Backlash', default=0.0, min=0.0, max=0.1, precision=4, unit='LENGTH')


   .. py:attribute:: rack_height
      :type:  FloatProperty(name='Rack Height', default=0.012, min=0.001, max=1, precision=4, unit='LENGTH')


   .. py:attribute:: rack_tooth_per_hole
      :type:  IntProperty(name='Teeth per Mounting Hole', default=7, min=2)


   .. py:attribute:: gear_type
      :type:  EnumProperty(name='Type of Gear', items=(('PINION', 'Pinion', 'Circular Gear'), ('RACK', 'Rack', 'Straight Rack')), description='Type of gear', default='PINION')


   .. py:method:: draw(context)

      Draw the user interface properties for gear settings.

      This method sets up the layout for various gear parameters based on the
      selected gear type. It dynamically adds properties to the layout for
      different gear types, allowing users to input specific values for gear
      design. The properties include gear type, tooth spacing, tooth amount,
      hole diameter, pressure angle, and backlash. Additional properties are
      displayed if the gear type is 'PINION' or 'RACK'.

      :param context: The context in which the layout is being drawn.



   .. py:method:: execute(context)

      Execute the gear generation process based on the specified gear type.

      This method checks the type of gear to be generated (either 'PINION' or
      'RACK') and calls the appropriate function from the `involute_gear`
      module to create the gear or rack with the specified parameters. The
      parameters include tooth spacing, number of teeth, hole diameter,
      pressure angle, clearance, backlash, rim size, hub diameter, and spoke
      amount for pinion gears, and additional parameters for rack gears.

      :param context: The context in which the execution is taking place.

      :returns:

                A dictionary indicating that the operation has finished with a key
                    'FINISHED'.
      :rtype: dict



