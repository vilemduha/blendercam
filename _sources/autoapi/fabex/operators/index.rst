fabex.operators
===============

.. py:module:: fabex.operators

.. autoapi-nested-parse::

   Fabex 'operators.__init__.py' © 2012 Vilem Novak

   Import Properties, Register and Unregister Classes



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/fabex/operators/async_op/index
   /autoapi/fabex/operators/bas_relief_ops/index
   /autoapi/fabex/operators/bridges_op/index
   /autoapi/fabex/operators/chain_ops/index
   /autoapi/fabex/operators/compatibility_op/index
   /autoapi/fabex/operators/curve_create_ops/index
   /autoapi/fabex/operators/curve_equation_ops/index
   /autoapi/fabex/operators/curve_tools_ops/index
   /autoapi/fabex/operators/gcode_import_op/index
   /autoapi/fabex/operators/log_ops/index
   /autoapi/fabex/operators/operation_ops/index
   /autoapi/fabex/operators/orient_op/index
   /autoapi/fabex/operators/pack_op/index
   /autoapi/fabex/operators/path_ops/index
   /autoapi/fabex/operators/position_op/index
   /autoapi/fabex/operators/preset_ops/index
   /autoapi/fabex/operators/simulation_ops/index
   /autoapi/fabex/operators/slice_op/index


Attributes
----------

.. autoapisummary::

   fabex.operators.classes


Classes
-------

.. autoapisummary::

   fabex.operators.DoBasRelief
   fabex.operators.ProblemAreas
   fabex.operators.CamBridgesAdd
   fabex.operators.CamChainAdd
   fabex.operators.CamChainOperationAdd
   fabex.operators.CamChainOperationDown
   fabex.operators.CamChainOperationRemove
   fabex.operators.CamChainOperationUp
   fabex.operators.CamChainRemove
   fabex.operators.CamCurveDrawer
   fabex.operators.CamCurveFlatCone
   fabex.operators.CamCurveGear
   fabex.operators.CamCurveHatch
   fabex.operators.CamCurveInterlock
   fabex.operators.CamCurveMortise
   fabex.operators.CamCurvePlate
   fabex.operators.CamCurvePuzzle
   fabex.operators.CamCustomCurve
   fabex.operators.CamHypotrochoidCurve
   fabex.operators.CamLissajousCurve
   fabex.operators.CamSineCurve
   fabex.operators.CamCurveBoolean
   fabex.operators.CamCurveConvexHull
   fabex.operators.CamCurveIntarsion
   fabex.operators.CamCurveSimpleOvercuts
   fabex.operators.CamCurveBoneFilletOvercuts
   fabex.operators.CamCurveRemoveDoubles
   fabex.operators.CamMeshGetPockets
   fabex.operators.CamObjectSilhouette
   fabex.operators.CamOffsetSilhouete
   fabex.operators.WM_OT_gcode_import
   fabex.operators.CamOpenLogFolder
   fabex.operators.CamPurgeLogs
   fabex.operators.CamOperationAdd
   fabex.operators.CamOperationCopy
   fabex.operators.CamOperationMove
   fabex.operators.CamOperationRemove
   fabex.operators.CamOrientationAdd
   fabex.operators.CamPackObjects
   fabex.operators.PathExport
   fabex.operators.PathExportChain
   fabex.operators.PathsAll
   fabex.operators.PathsBackground
   fabex.operators.PathsChain
   fabex.operators.KillPathsBackground
   fabex.operators.CalculatePath
   fabex.operators.CAM_MATERIAL_PositionObject
   fabex.operators.AddPresetCamCutter
   fabex.operators.AddPresetCamMachine
   fabex.operators.AddPresetCamOperation
   fabex.operators.EditUserPostProcessor
   fabex.operators.CAMSimulate
   fabex.operators.CAMSimulateChain
   fabex.operators.CamSliceObjects


Functions
---------

.. autoapisummary::

   fabex.operators.register
   fabex.operators.unregister


Package Contents
----------------

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


   .. py:attribute:: width_mm
      :type:  IntProperty(name='Desired Width in mm', default=200, min=5, max=4000)


   .. py:attribute:: height_mm
      :type:  IntProperty(name='Desired Height in mm', default=150, min=5, max=4000)


   .. py:attribute:: thickness_mm
      :type:  IntProperty(name='Thickness in mm', default=15, min=5, max=100)


   .. py:attribute:: justify_x
      :type:  EnumProperty(name='X', items=[('1', 'Left', '', 0), ('-0.5', 'Centered', '', 1), ('-1', 'Right', '', 2)], default='-1')


   .. py:attribute:: justify_y
      :type:  EnumProperty(name='Y', items=[('1', 'Bottom', '', 0), ('-0.5', 'Centered', '', 2), ('-1', 'Top', '', 1)], default='-1')


   .. py:attribute:: justify_z
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


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: invoke(context, event)


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



.. py:class:: CamBridgesAdd

   Bases: :py:obj:`bpy.types.Operator`


   Add Bridge Objects to Curve


   .. py:attribute:: bl_idname
      :value: 'scene.cam_bridges_add'



   .. py:attribute:: bl_label
      :value: 'Add Bridges / Tabs'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM operation in the given context.

      This function retrieves the active CAM operation from the current
      scene and adds automatic bridges to it. It is typically called within
      the context of a Blender operator to perform specific actions related to
      CAM operations.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the result of the operation, typically
                containing the key 'FINISHED' to signify successful completion.
      :rtype: dict



.. py:class:: CamChainAdd

   Bases: :py:obj:`bpy.types.Operator`


   Add New CAM Chain


   .. py:attribute:: bl_idname
      :value: 'scene.cam_chain_add'



   .. py:attribute:: bl_label
      :value: 'Add New CAM Chain'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM chain creation in the given context.

      This function adds a new CAM chain to the current scene in Blender.
      It updates the active CAM chain index and assigns a name and filename
      to the newly created chain. The function is intended to be called within
      a Blender operator context.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the operation's completion status,
                    specifically returning {'FINISHED'} upon successful execution.
      :rtype: dict



.. py:class:: CamChainOperationAdd

   Bases: :py:obj:`bpy.types.Operator`


   Add Operation to Chain


   .. py:attribute:: bl_idname
      :value: 'scene.cam_chain_operation_add'



   .. py:attribute:: bl_label
      :value: 'Add Operation to Chain'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute an operation in the active CAM chain.

      This function retrieves the active CAM chain from the current scene
      and adds a new operation to it. It increments the active operation index
      and assigns the name of the currently selected CAM operation to the
      newly added operation. This is typically used in the context of managing
      CAM operations in a 3D environment.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the execution status, typically {'FINISHED'}.
      :rtype: dict



.. py:class:: CamChainOperationDown

   Bases: :py:obj:`bpy.types.Operator`


   Add Operation to Chain


   .. py:attribute:: bl_idname
      :value: 'scene.cam_chain_operation_down'



   .. py:attribute:: bl_label
      :value: 'Add Operation to Chain'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the operation to move the active CAM operation in the chain.

      This function retrieves the current scene and the active CAM chain.
      It checks if the active operation can be moved down in the list of
      operations. If so, it moves the active operation one position down and
      updates the active operation index accordingly.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the result of the operation,
                    specifically {'FINISHED'} when the operation completes successfully.
      :rtype: dict



.. py:class:: CamChainOperationRemove

   Bases: :py:obj:`bpy.types.Operator`


   Remove Operation from Chain


   .. py:attribute:: bl_idname
      :value: 'scene.cam_chain_operation_remove'



   .. py:attribute:: bl_label
      :value: 'Remove Operation from Chain'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the operation to remove the active operation from the CAM
      chain.

      This method accesses the current scene and retrieves the active CAM
      chain. It then removes the currently active operation from that chain
      and adjusts the index of the active operation accordingly. If the active
      operation index becomes negative, it resets it to zero to ensure it
      remains within valid bounds.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the execution status, typically
                    containing {'FINISHED'} upon successful completion.
      :rtype: dict



.. py:class:: CamChainOperationUp

   Bases: :py:obj:`bpy.types.Operator`


   Add Operation to Chain


   .. py:attribute:: bl_idname
      :value: 'scene.cam_chain_operation_up'



   .. py:attribute:: bl_label
      :value: 'Add Operation to Chain'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the operation to move the active CAM operation in the chain.

      This function retrieves the current scene and the active CAM chain.
      If there is an active operation (i.e., its index is greater than 0), it
      moves the operation one step up in the chain by adjusting the indices
      accordingly. After moving the operation, it updates the active operation
      index to reflect the change.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the result of the operation,
                    specifically returning {'FINISHED'} upon successful execution.
      :rtype: dict



.. py:class:: CamChainRemove

   Bases: :py:obj:`bpy.types.Operator`


   Remove CAM Chain


   .. py:attribute:: bl_idname
      :value: 'scene.cam_chain_remove'



   .. py:attribute:: bl_label
      :value: 'Remove CAM Chain'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM chain removal process.

      This function removes the currently active CAM chain from the scene
      and decrements the active CAM chain index if it is greater than zero.
      It modifies the Blender context to reflect these changes.

      :param context: The context in which the function is executed.

      :returns:

                A dictionary indicating the status of the operation,
                    specifically {'FINISHED'} upon successful execution.
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



.. py:class:: CamCustomCurve

   Bases: :py:obj:`bpy.types.Operator`


   Create a Curve based on User Defined Variables


   .. py:attribute:: bl_idname
      :value: 'object.customcurve'



   .. py:attribute:: bl_label
      :value: 'Custom Curve'



   .. py:attribute:: bl_options


   .. py:attribute:: x_string
      :type:  StringProperty(name='X Equation', description='Equation x=F(t)', default='t')


   .. py:attribute:: y_string
      :type:  StringProperty(name='Y Equation', description='Equation y=F(t)', default='0')


   .. py:attribute:: z_string
      :type:  StringProperty(name='Z Equation', description='Equation z=F(t)', default='0.05*sin(2*pi*4*t)')


   .. py:attribute:: iteration
      :type:  IntProperty(name='Iteration', default=100, min=50, max=2000)


   .. py:attribute:: max_t
      :type:  FloatProperty(name='Wave Ends at X', default=0.5, min=-3.0, max=10, precision=4, unit='LENGTH')


   .. py:attribute:: min_t
      :type:  FloatProperty(name='Wave Starts at X', default=0, min=-3.0, max=3, precision=4, unit='LENGTH')


   .. py:method:: execute(context)


.. py:class:: CamHypotrochoidCurve

   Bases: :py:obj:`bpy.types.Operator`


   Create a Hypotrochoid Curve (Spirograph-type Pattern)


   .. py:attribute:: bl_idname
      :value: 'object.hypotrochoid'



   .. py:attribute:: bl_label
      :value: 'Spirograph Type Figure'



   .. py:attribute:: bl_options


   .. py:attribute:: typecurve
      :type:  EnumProperty(name='Type of Curve', items=(('hypo', 'Hypotrochoid', 'Inside ring'), ('epi', 'Epicycloid', 'Outside inner ring')))


   .. py:attribute:: R
      :type:  FloatProperty(name='Big Circle Radius', default=0.25, min=0.001, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: r
      :type:  FloatProperty(name='Small Circle Radius', default=0.18, min=0.0001, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: d
      :type:  FloatProperty(name='Distance from Center of Interior Circle', default=0.05, min=0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: dip
      :type:  FloatProperty(name='Variable Depth from Center', default=0.0, min=-100, max=100, precision=4)


   .. py:method:: execute(context)


.. py:class:: CamLissajousCurve

   Bases: :py:obj:`bpy.types.Operator`


   Create a Lissajous Curve (Knot / Weave Pattern)


   .. py:attribute:: bl_idname
      :value: 'object.lissajous'



   .. py:attribute:: bl_label
      :value: 'Lissajous Figure'



   .. py:attribute:: bl_options


   .. py:attribute:: amplitude_a
      :type:  FloatProperty(name='Amplitude A', default=0.1, min=0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: wave_a
      :type:  EnumProperty(name='Wave X', items=(('sine', 'Sine Wave', 'Sine Wave'), ('triangle', 'Triangle Wave', 'triangle wave')), default='sine')


   .. py:attribute:: amplitude_b
      :type:  FloatProperty(name='Amplitude B', default=0.1, min=0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: wave_b
      :type:  EnumProperty(name='Wave Y', items=(('sine', 'Sine Wave', 'Sine Wave'), ('triangle', 'Triangle Wave', 'triangle wave')), default='sine')


   .. py:attribute:: period_a
      :type:  FloatProperty(name='Period A', default=1.1, min=0.001, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: period_b
      :type:  FloatProperty(name='Period B', default=1.0, min=0.001, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: period_z
      :type:  FloatProperty(name='Period Z', default=1.0, min=0.001, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: amplitude_z
      :type:  FloatProperty(name='Amplitude Z', default=0.0, min=0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: shift
      :type:  FloatProperty(name='Phase Shift', default=0, min=-360, max=360, precision=4, step=100, unit='ROTATION')


   .. py:attribute:: iteration
      :type:  IntProperty(name='Iteration', default=500, min=50, max=10000)


   .. py:attribute:: max_t
      :type:  FloatProperty(name='Wave Ends at X', default=11, min=-3.0, max=1000000, precision=4, unit='LENGTH')


   .. py:attribute:: min_t
      :type:  FloatProperty(name='Wave Starts at X', default=0, min=-10.0, max=3, precision=4, unit='LENGTH')


   .. py:method:: execute(context)


.. py:class:: CamSineCurve

   Bases: :py:obj:`bpy.types.Operator`


   Create a Sine Wave Curve


   .. py:attribute:: bl_idname
      :value: 'object.sine'



   .. py:attribute:: bl_label
      :value: 'Periodic Wave'



   .. py:attribute:: bl_options


   .. py:attribute:: axis
      :type:  EnumProperty(name='Displacement Axis', items=(('XY', 'Y to displace X axis', 'Y constant; X sine displacement'), ('YX', 'X to displace Y axis', 'X constant; Y sine displacement'), ('ZX', 'X to displace Z axis', 'X constant; Y sine displacement'), ('ZY', 'Y to displace Z axis', 'X constant; Y sine displacement')), default='ZX')


   .. py:attribute:: wave
      :type:  EnumProperty(name='Wave', items=(('sine', 'Sine Wave', 'Sine Wave'), ('triangle', 'Triangle Wave', 'triangle wave'), ('cycloid', 'Cycloid', 'Sine wave rectification'), ('invcycloid', 'Inverse Cycloid', 'Sine wave rectification')), default='sine')


   .. py:attribute:: amplitude
      :type:  FloatProperty(name='Amplitude', default=0.01, min=0, max=10, precision=4, unit='LENGTH')


   .. py:attribute:: period
      :type:  FloatProperty(name='Period', default=0.5, min=0.001, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: beat_period
      :type:  FloatProperty(name='Beat Period Offset', default=0.0, min=0.0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: shift
      :type:  FloatProperty(name='Phase Shift', default=0, min=-360, max=360, precision=4, step=100, unit='ROTATION')


   .. py:attribute:: offset
      :type:  FloatProperty(name='Offset', default=0, min=-1.0, max=1, precision=4, unit='LENGTH')


   .. py:attribute:: iteration
      :type:  IntProperty(name='Iteration', default=100, min=50, max=2000)


   .. py:attribute:: max_t
      :type:  FloatProperty(name='Wave Ends at X', default=0.5, min=-3.0, max=3, precision=4, unit='LENGTH')


   .. py:attribute:: min_t
      :type:  FloatProperty(name='Wave Starts at X', default=0, min=-3.0, max=3, precision=4, unit='LENGTH')


   .. py:attribute:: wave_distance
      :type:  FloatProperty(name='Distance Between Multiple Waves', default=0.0, min=0.0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: wave_angle_offset
      :type:  FloatProperty(name='Angle Offset for Multiple Waves', default=pi / 2, min=-200 * pi, max=200 * pi, precision=4, step=100, unit='ROTATION')


   .. py:attribute:: wave_amount
      :type:  IntProperty(name='Amount of Multiple Waves', default=1, min=1, max=2000)


   .. py:method:: execute(context)


.. py:class:: CamCurveBoolean

   Bases: :py:obj:`bpy.types.Operator`


   Perform Boolean Operation on Two or More Curves


   .. py:attribute:: bl_idname
      :value: 'object.curve_boolean'



   .. py:attribute:: bl_label
      :value: 'Curve Boolean'



   .. py:attribute:: bl_options


   .. py:attribute:: boolean_type
      :type:  EnumProperty(name='Type', items=(('UNION', 'Union', ''), ('DIFFERENCE', 'Difference', ''), ('INTERSECT', 'Intersect', '')), description='Boolean type', default='UNION')


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)


   .. py:method:: invoke(context, event)


.. py:class:: CamCurveConvexHull

   Bases: :py:obj:`bpy.types.Operator`


   Perform Hull Operation on Single or Multiple Curves


   .. py:attribute:: bl_idname
      :value: 'object.convex_hull'



   .. py:attribute:: bl_label
      :value: 'Convex Hull'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)


.. py:class:: CamCurveIntarsion

   Bases: :py:obj:`bpy.types.Operator`


   Makes Curve Cuttable Both Inside and Outside, for Intarsion and Joints


   .. py:attribute:: bl_idname
      :value: 'object.curve_intarsion'



   .. py:attribute:: bl_label
      :value: 'Intarsion'



   .. py:attribute:: bl_options


   .. py:attribute:: diameter
      :type:  FloatProperty(name='Cutter Diameter', default=0.001, min=0, max=0.025, precision=4, unit='LENGTH')


   .. py:attribute:: tolerance
      :type:  FloatProperty(name='Cutout Tolerance', default=0.0001, min=0, max=0.005, precision=4, unit='LENGTH')


   .. py:attribute:: backlight
      :type:  FloatProperty(name='Backlight Seat', default=0.0, min=0, max=0.01, precision=4, unit='LENGTH')


   .. py:attribute:: perimeter_cut
      :type:  FloatProperty(name='Perimeter Cut Offset', default=0.0, min=0, max=0.1, precision=4, unit='LENGTH')


   .. py:attribute:: base_thickness
      :type:  FloatProperty(name='Base Material Thickness', default=0.0, min=0, max=0.1, precision=4, unit='LENGTH')


   .. py:attribute:: intarsion_thickness
      :type:  FloatProperty(name='Intarsion Material Thickness', default=0.0, min=0, max=0.1, precision=4, unit='LENGTH')


   .. py:attribute:: backlight_depth_from_top
      :type:  FloatProperty(name='Backlight Well Depth', default=0.0, min=0, max=0.1, precision=4, unit='LENGTH')


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)


   .. py:method:: invoke(context, event)


.. py:class:: CamCurveSimpleOvercuts

   Bases: :py:obj:`bpy.types.Operator`


   Adds Simple Fillets / Overcuts for Slots


   .. py:attribute:: bl_idname
      :value: 'object.curve_overcuts'



   .. py:attribute:: bl_label
      :value: 'Simple Fillet Overcuts'



   .. py:attribute:: bl_options


   .. py:attribute:: diameter
      :type:  FloatProperty(name='Diameter', default=0.003175, min=0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: threshold
      :type:  FloatProperty(name='Threshold', default=pi / 2 * 0.99, min=-3.14, max=3.14, precision=4, step=500, subtype='ANGLE', unit='ROTATION')


   .. py:attribute:: do_outer
      :type:  BoolProperty(name='Outer Polygons', default=True)


   .. py:attribute:: invert
      :type:  BoolProperty(name='Invert', default=False)


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)


   .. py:method:: invoke(context, event)


.. py:class:: CamCurveBoneFilletOvercuts

   Bases: :py:obj:`bpy.types.Operator`


   Adds Dogbone, T-bone Fillets / Overcuts for Slots


   .. py:attribute:: bl_idname
      :value: 'object.curve_overcuts_b'



   .. py:attribute:: bl_label
      :value: 'Bone Fillet Overcuts'



   .. py:attribute:: bl_options


   .. py:attribute:: diameter
      :type:  FloatProperty(name='Tool Diameter', default=0.003175, description='Tool bit diameter used in cut operation', min=0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: style
      :type:  EnumProperty(name='Style', items=(('OPEDGE', 'opposite edge', 'place corner overcuts on opposite edges'), ('DOGBONE', 'Dog-bone / Corner Point', 'place overcuts at center of corners'), ('TBONE', 'T-bone', 'place corner overcuts on the same edge')), default='DOGBONE', description='style of overcut to use')


   .. py:attribute:: threshold
      :type:  FloatProperty(name='Max Inside Angle', default=pi / 2, min=-3.14, max=3.14, description='The maximum angle to be considered as an inside corner', precision=4, step=500, subtype='ANGLE', unit='ROTATION')


   .. py:attribute:: do_outer
      :type:  BoolProperty(name='Include Outer Curve', description='Include the outer curve if there are curves inside', default=True)


   .. py:attribute:: do_invert
      :type:  BoolProperty(name='Invert', description='invert overcut operation on all curves', default=True)


   .. py:attribute:: other_edge
      :type:  BoolProperty(name='Other Edge', description='change to the other edge for the overcut to be on', default=False)


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)


   .. py:method:: invoke(context, event)


.. py:class:: CamCurveRemoveDoubles

   Bases: :py:obj:`bpy.types.Operator`


   Remove Duplicate Points from the Selected Curve


   .. py:attribute:: bl_idname
      :value: 'object.curve_remove_doubles'



   .. py:attribute:: bl_label
      :value: 'Remove Curve Doubles'



   .. py:attribute:: bl_options


   .. py:attribute:: merge_distance
      :type:  FloatProperty(name='Merge distance', default=0.0001, min=0, max=0.01)


   .. py:attribute:: keep_bezier
      :type:  BoolProperty(name='Keep bezier', default=False)


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)


   .. py:method:: draw(context)


   .. py:method:: invoke(context, event)


.. py:class:: CamMeshGetPockets

   Bases: :py:obj:`bpy.types.Operator`


   Detect Pockets in a Mesh and Extract Them as Curves


   .. py:attribute:: bl_idname
      :value: 'object.mesh_get_pockets'



   .. py:attribute:: bl_label
      :value: 'Get Pocket Surfaces'



   .. py:attribute:: bl_options


   .. py:attribute:: threshold
      :type:  FloatProperty(name='Horizontal Threshold', description='How horizontal the surface must be for a pocket: 1.0 perfectly flat, 0.0 is any orientation', default=0.99, min=0, max=1.0, precision=4)


   .. py:attribute:: z_limit
      :type:  FloatProperty(name='Z Limit', description='Maximum z height considered for pocket operation, default is 0.0', default=0.0, min=-1000.0, max=1000.0, precision=4, unit='LENGTH')


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)


.. py:class:: CamObjectSilhouette

   Bases: :py:obj:`bpy.types.Operator`


   Create Object Silhouette


   .. py:attribute:: bl_idname
      :value: 'object.silhouette'



   .. py:attribute:: bl_label
      :value: 'Object Silhouette'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)


.. py:class:: CamOffsetSilhouete

   Bases: :py:obj:`bpy.types.Operator`


   Offset Object Silhouette


   .. py:attribute:: bl_idname
      :value: 'object.silhouette_offset'



   .. py:attribute:: bl_label
      :value: 'Silhouette & Offset'



   .. py:attribute:: bl_options


   .. py:attribute:: offset
      :type:  FloatProperty(name='Offset', default=0.003, min=-100, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: mitre_limit
      :type:  FloatProperty(name='Mitre Limit', default=2, min=1e-08, max=20, precision=4, unit='LENGTH')


   .. py:attribute:: style
      :type:  EnumProperty(name='Corner Type', items=(('1', 'Round', ''), ('2', 'Mitre', ''), ('3', 'Bevel', '')))


   .. py:attribute:: caps
      :type:  EnumProperty(name='Cap Type', items=(('round', 'Round', ''), ('square', 'Square', ''), ('flat', 'Flat', '')))


   .. py:attribute:: align
      :type:  EnumProperty(name='Alignment', items=(('worldxy', 'World XY', ''), ('bottom', 'Base Bottom', ''), ('top', 'Base Top', '')))


   .. py:attribute:: open_type
      :type:  EnumProperty(name='Curve Type', items=(('dilate', 'Dilate open curve', ''), ('leaveopen', 'Leave curve open', ''), ('closecurve', 'Close curve', '')), default='closecurve')


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: is_straight(geom)


   .. py:method:: execute(context)


   .. py:method:: draw(context)


   .. py:method:: invoke(context, event)


.. py:class:: WM_OT_gcode_import

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`bpy_extras.io_utils.ImportHelper`


   Import G-code, Travel Lines Don't Get Drawn


   .. py:attribute:: bl_idname
      :value: 'wm.gcode_import'



   .. py:attribute:: bl_label
      :value: 'Import G-code'



   .. py:attribute:: filename_ext
      :value: '.txt'



   .. py:attribute:: filter_glob
      :type:  StringProperty(default='*.*', options={'HIDDEN'}, maxlen=255)


   .. py:attribute:: split_layers
      :type:  BoolProperty(name='Split Layers', description='Save every layer as single Objects in Collection', default=False)


   .. py:attribute:: subdivide
      :type:  BoolProperty(name='Subdivide', description="Only Subdivide gcode segments that are bigger than 'Segment length' ", default=False)


   .. py:attribute:: output
      :type:  EnumProperty(name='Output Type', items=(('mesh', 'Mesh', 'Make a mesh output'), ('curve', 'Curve', 'Make curve output')), default='curve')


   .. py:attribute:: max_segment_size
      :type:  FloatProperty(name='', description='Only Segments bigger than this value get subdivided', default=0.001, min=0.0001, max=1.0, unit='LENGTH')


   .. py:method:: execute(context)


.. py:class:: CamOpenLogFolder

   Bases: :py:obj:`bpy.types.Operator`


   Open the CAM Log Folder


   .. py:attribute:: bl_idname
      :value: 'scene.cam_open_log_folder'



   .. py:attribute:: bl_label
      :value: 'Open Log Folder'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Opens the folder where CAM logs are stored.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the operation's completion status,
                    specifically returning {'FINISHED'} upon successful execution.
      :rtype: dict



.. py:class:: CamPurgeLogs

   Bases: :py:obj:`bpy.types.Operator`


   Delete CAM Logs


   .. py:attribute:: bl_idname
      :value: 'scene.cam_purge_logs'



   .. py:attribute:: bl_label
      :value: 'Purge CAM Logs'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM log removal process.

      This function removes the files from the CAM logs folder

      :param context: The context in which the function is executed.

      :returns:

                A dictionary indicating the status of the operation,
                    specifically {'FINISHED'} upon successful execution.
      :rtype: dict



.. py:class:: CamOperationAdd

   Bases: :py:obj:`bpy.types.Operator`


   Add New CAM Operation


   .. py:attribute:: bl_idname
      :value: 'scene.cam_operation_add'



   .. py:attribute:: bl_label
      :value: 'Add New CAM Operation'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM operation based on the active object in the scene.

      This method retrieves the active object from the Blender context and
      performs operations related to CAM settings. It checks if an object
      is selected and retrieves its bounding box dimensions. If no object is
      found, it reports an error and cancels the operation. If an object is
      present, it adds a new CAM operation to the scene, sets its
      properties, and ensures that a machine area object is present.

      :param context: The context in which the operation is executed.



.. py:class:: CamOperationCopy

   Bases: :py:obj:`bpy.types.Operator`


   Copy CAM Operation


   .. py:attribute:: bl_idname
      :value: 'scene.cam_operation_copy'



   .. py:attribute:: bl_label
      :value: 'Copy Active CAM Operation'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM operation in the given context.

      This method handles the execution of CAM operations within the
      Blender scene. It first checks if there are any CAM operations
      available. If not, it returns a cancellation status. If there are
      operations, it copies the active operation, increments the active
      operation index, and updates the name and filename of the new operation.
      The function also ensures that the new operation's name is unique by
      appending a copy suffix or incrementing a numeric suffix.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the status of the operation,
                    either {'CANCELLED'} if no operations are available or
                    {'FINISHED'} if the operation was successfully executed.
      :rtype: dict



.. py:class:: CamOperationMove

   Bases: :py:obj:`bpy.types.Operator`


   Move CAM Operation


   .. py:attribute:: bl_idname
      :value: 'scene.cam_operation_move'



   .. py:attribute:: bl_label
      :value: 'Move CAM Operation in List'



   .. py:attribute:: bl_options


   .. py:attribute:: direction
      :type:  EnumProperty(name='Direction', items=(('UP', 'Up', ''), ('DOWN', 'Down', '')), description='Direction', default='DOWN')


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute a CAM operation based on the specified direction.

      This method modifies the active CAM operation in the Blender context
      based on the direction specified. If the direction is 'UP', it moves the
      active operation up in the list, provided it is not already at the top.
      Conversely, if the direction is not 'UP', it moves the active operation
      down in the list, as long as it is not at the bottom. The method updates
      the active operation index accordingly.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the operation has finished, with
                the key 'FINISHED'.
      :rtype: dict



.. py:class:: CamOperationRemove

   Bases: :py:obj:`bpy.types.Operator`


   Remove CAM Operation


   .. py:attribute:: bl_idname
      :value: 'scene.cam_operation_remove'



   .. py:attribute:: bl_label
      :value: 'Remove CAM Operation'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM operation in the given context.

      This function performs the active CAM operation by deleting the
      associated object from the scene. It checks if there are any CAM
      operations available and handles the deletion of the active operation's
      object. If the active operation is removed, it updates the active
      operation index accordingly. Additionally, it manages a dictionary that
      tracks hidden objects.

      :param context: The Blender context containing the scene and operations.
      :type context: bpy.context

      :returns:

                A dictionary indicating the result of the operation, either
                    {'CANCELLED'} if no operations are available or {'FINISHED'} if the
                    operation was successfully executed.
      :rtype: dict



.. py:class:: CamOrientationAdd

   Bases: :py:obj:`bpy.types.Operator`


   Add Orientation to CAM Operation, for Multiaxis Operations


   .. py:attribute:: bl_idname
      :value: 'scene.cam_orientation_add'



   .. py:attribute:: bl_label
      :value: 'Add Orientation'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM orientation operation in Blender.

      This function retrieves the active CAM operation from the current
      scene, creates an empty object to represent the CAM orientation, and
      adds it to a specified group. The empty object is named based on the
      operation's name and the current count of objects in the group. The size
      of the empty object is set to a predefined value for visibility.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the operation's completion status,
                    typically {'FINISHED'}.
      :rtype: dict



.. py:class:: CamPackObjects

   Bases: :py:obj:`bpy.types.Operator`


   Calculate All CAM Paths


   .. py:attribute:: bl_idname
      :value: 'object.cam_pack_objects'



   .. py:attribute:: bl_label
      :value: 'Pack Curves on Sheet'



   .. py:attribute:: bl_options


   .. py:attribute:: sheet_fill_direction
      :type:  EnumProperty(name='Fill Direction', items=(('X', 'X', 'Fills sheet in X axis direction'), ('Y', 'Y', 'Fills sheet in Y axis direction')), description='Fill direction of the packer algorithm', default='Y')


   .. py:attribute:: sheet_x
      :type:  FloatProperty(name='X Size', description='Sheet size', min=0.001, max=10, default=0.5, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: sheet_y
      :type:  FloatProperty(name='Y Size', description='Sheet size', min=0.001, max=10, default=0.5, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: distance
      :type:  FloatProperty(name='Minimum Distance', description='Minimum distance between objects(should be at least cutter diameter!)', min=0.001, max=10, default=0.01, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: tolerance
      :type:  FloatProperty(name='Placement Tolerance', description='Tolerance for placement: smaller value slower placemant', min=0.001, max=0.02, default=0.005, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: rotate
      :type:  BoolProperty(name='Enable Rotation', description='Enable rotation of elements', default=True)


   .. py:attribute:: rotate_angle
      :type:  FloatProperty(name='Placement Angle Rotation Step', description='Bigger rotation angle, faster placemant', default=0.19635 * 4, min=pi / 180, max=pi, precision=5, step=500, subtype='ANGLE', unit='ROTATION')


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: invoke(context, event)


   .. py:method:: execute(context)

      Execute the operation in the given context.

      This function sets the Blender object mode to 'OBJECT', retrieves the
      currently selected objects, and calls the `pack_curves` function from the
      `pack` module. It is typically used to finalize operations on selected
      objects in Blender.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the completion status of the operation.
      :rtype: dict



   .. py:method:: draw(context)


.. py:class:: PathExport

   Bases: :py:obj:`bpy.types.Operator`


   Export G-code. Can Be Used only when the Path Object Is Present


   .. py:attribute:: bl_idname
      :value: 'object.cam_export'



   .. py:attribute:: bl_label
      :value: 'Export Operation G-code'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)

      Execute the CAM operation and export the G-code path.

      This method retrieves the active CAM operation from the current scene
      and exports the corresponding G-code path to a specified filename. It
      prints the filename and relevant operation details to the console for
      debugging purposes. The G-code path is generated based on the CAM
      path data associated with the active operation.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the completion status of the operation,
                    typically {'FINISHED'}.
      :rtype: dict



.. py:class:: PathExportChain

   Bases: :py:obj:`bpy.types.Operator`


   Calculate a Chain and Export the G-code Together.


   .. py:attribute:: bl_idname
      :value: 'object.cam_export_paths_chain'



   .. py:attribute:: bl_label
      :value: 'Export CAM Paths in Current Chain as G-code'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:


      Check the validity of the active CAM chain in the given context.

      This method retrieves the currently active CAM chain from the scene
      context and checks its validity using the `isChainValid` function. It
      returns a boolean indicating whether the active CAM chain is valid or
      not.

      :param context: The context containing the scene and CAM chain information.
      :type context: object

      :returns: True if the active CAM chain is valid, False otherwise.
      :rtype: bool



   .. py:method:: execute(context)

      Execute the CAM path export process.

      This function retrieves the active CAM chain from the current scene
      and gathers the mesh data associated with the operations of that chain.
      It then exports the G-code path using the specified filename and the
      collected mesh data. The function is designed to be called within the
      context of a Blender operator.

      :param context: The context in which the operator is executed.
      :type context: bpy.context

      :returns:

                A dictionary indicating the completion status of the operation,
                    typically {'FINISHED'}.
      :rtype: dict



.. py:class:: PathsAll

   Bases: :py:obj:`bpy.types.Operator`


   Calculate All CAM Paths


   .. py:attribute:: bl_idname
      :value: 'object.calculate_cam_paths_all'



   .. py:attribute:: bl_label
      :value: 'Calculate All CAM Paths'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)

      Execute CAM operations in the current Blender context.

      This function iterates through the CAM operations defined in the
      current scene and executes the background calculation for each
      operation. It sets the active CAM operation index and prints the name
      of each operation being processed. This is typically used in a Blender
      add-on or script to automate CAM path calculations.

      :param context: The current Blender context.
      :type context: bpy.context

      :returns:

                A dictionary indicating the completion status of the operation,
                    typically {'FINISHED'}.
      :rtype: dict



   .. py:method:: draw(context)

      Draws the user interface elements for the operation selection.

      This method utilizes the Blender layout system to create a property
      search interface for selecting operations related to CAM
      functionalities. It links the current instance's operation property to
      the available CAM operations defined in the Blender scene.

      :param context: The context in which the drawing occurs,
      :type context: bpy.context



.. py:class:: PathsBackground

   Bases: :py:obj:`bpy.types.Operator`


   Calculate CAM Paths in Background. File Has to Be Saved Before.


   .. py:attribute:: bl_idname
      :value: 'object.calculate_cam_paths_background'



   .. py:attribute:: bl_label
      :value: 'Calculate CAM Paths in Background'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)

      Execute the CAM operation in the background.

      This method initiates a background process to perform CAM operations
      based on the current scene and active CAM operation. It sets up the
      necessary paths for the script and starts a subprocess to handle the
      CAM computations. Additionally, it manages threading to ensure that
      the main thread remains responsive while the background operation is
      executed.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the completion status of the operation.
      :rtype: dict



.. py:class:: PathsChain(*args, **kwargs)

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`fabex.operators.async_op.AsyncOperatorMixin`


   Calculate a Chain and Export the G-code Alltogether.


   .. py:attribute:: bl_idname
      :value: 'object.calculate_cam_paths_chain'



   .. py:attribute:: bl_label
      :value: 'Calculate CAM Paths in Current Chain and Export Chain G-code'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:


      Check the validity of the active CAM chain in the given context.

      This method retrieves the active CAM chain from the scene and checks
      its validity using the `isChainValid` function. It returns a boolean
      value indicating whether the CAM chain is valid or not.

      :param context: The context containing the scene and CAM chain information.
      :type context: Context

      :returns: True if the active CAM chain is valid, False otherwise.
      :rtype: bool



   .. py:method:: execute_async(context)
      :async:


      Execute asynchronous operations for CAM path calculations.

      This method sets the object mode for the Blender scene and processes a
      series of CAM operations defined in the active CAM chain. It
      reports the progress of each operation and handles any exceptions that
      may occur during the path calculation. After successful calculations, it
      exports the resulting mesh data to a specified G-code file.

      :param context: The Blender context containing scene and
      :type context: bpy.context

      :returns: A dictionary indicating the result of the operation,
                typically {'FINISHED'}.
      :rtype: dict



.. py:class:: KillPathsBackground

   Bases: :py:obj:`bpy.types.Operator`


   Remove CAM Path Processes in Background.


   .. py:attribute:: bl_idname
      :value: 'object.kill_calculate_cam_paths_background'



   .. py:attribute:: bl_label
      :value: 'Kill Background Computation of an Operation'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)

      Execute the CAM operation in the given context.

      This method retrieves the active CAM operation from the scene and
      checks if there are any ongoing processes related to CAM path
      calculations. If such processes exist and match the current operation,
      they are terminated. The method then marks the operation as not
      computing and returns a status indicating that the execution has
      finished.

      :param context: The context in which the operation is executed.

      :returns: A dictionary with a status key indicating the result of the execution.
      :rtype: dict



.. py:class:: CalculatePath(*args, **kwargs)

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`fabex.operators.async_op.AsyncOperatorMixin`


   Calculate CAM Paths


   .. py:attribute:: bl_idname
      :value: 'object.calculate_cam_path'



   .. py:attribute:: bl_label
      :value: 'Calculate CAM Paths'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:


      Check if the current CAM operation is valid.

      This method checks the active CAM operation in the given context and
      determines if it is valid. It retrieves the active operation from the
      scene's CAM operations and validates it using the `isValid` function.
      If the operation is valid, it returns True; otherwise, it returns False.

      :param context: The context containing the scene and CAM operations.
      :type context: Context

      :returns: True if the active CAM operation is valid, False otherwise.
      :rtype: bool



   .. py:method:: execute_async(context)
      :async:


      Execute an asynchronous calculation of a path.

      This method performs an asynchronous operation to calculate a path based
      on the provided context. It awaits the result of the calculation and
      prints the success status along with the return value. The return value
      can be used for further processing or analysis.

      :param context: The context in which the path calculation is to be executed.
      :type context: Any

      :returns: The result of the path calculation.
      :rtype: Any



.. py:class:: CAM_MATERIAL_PositionObject

   Bases: :py:obj:`bpy.types.Operator`


   .. py:attribute:: bl_idname
      :value: 'object.material_cam_position'



   .. py:attribute:: bl_label
      :value: 'Position Object for CAM Operation'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)


   .. py:method:: draw(context)


.. py:class:: AddPresetCamCutter

   Bases: :py:obj:`bl_operators.presets.AddPresetBase`, :py:obj:`bpy.types.Operator`


   Add a Cutter Preset


   .. py:attribute:: bl_idname
      :value: 'render.cam_preset_cutter_add'



   .. py:attribute:: bl_label
      :value: 'Add Cutter Preset'



   .. py:attribute:: preset_menu
      :value: 'CAM_CUTTER_MT_presets'



   .. py:attribute:: preset_defines
      :value: ['d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]']



   .. py:attribute:: preset_values
      :value: ['d.cutter_id', 'd.cutter_type', 'd.cutter_diameter', 'd.cutter_length', 'd.cutter_flutes',...



   .. py:attribute:: preset_subdir
      :value: 'cam_cutters'



.. py:class:: AddPresetCamMachine

   Bases: :py:obj:`bl_operators.presets.AddPresetBase`, :py:obj:`bpy.types.Operator`


   Add a Cam Machine Preset


   .. py:attribute:: bl_idname
      :value: 'render.cam_preset_machine_add'



   .. py:attribute:: bl_label
      :value: 'Add Machine Preset'



   .. py:attribute:: preset_menu
      :value: 'CAM_MACHINE_MT_presets'



   .. py:attribute:: preset_defines
      :value: ['d = bpy.context.scene.cam_machine', 's = bpy.context.scene.unit_settings']



   .. py:attribute:: preset_values
      :value: ['d.post_processor', 'd.unit_system', 'd.use_position_definitions', 'd.starting_position',...



   .. py:attribute:: preset_subdir
      :value: 'cam_machines'



.. py:class:: AddPresetCamOperation

   Bases: :py:obj:`bl_operators.presets.AddPresetBase`, :py:obj:`bpy.types.Operator`


   Add an Operation Preset


   .. py:attribute:: bl_idname
      :value: 'render.cam_preset_operation_add'



   .. py:attribute:: bl_label
      :value: 'Add Operation Preset'



   .. py:attribute:: preset_menu
      :value: 'CAM_OPERATION_MT_presets'



   .. py:attribute:: preset_defines
      :value: ['from pathlib import Path', "if '__file__' in globals(): bpy.ops.scene.cam_operation_add()",...



   .. py:attribute:: preset_values
      :value: ['o.info.duration', 'o.info.chipload', 'o.info.warnings', 'o.material.estimate_from_model',...



   .. py:attribute:: preset_subdir
      :value: 'cam_operations'



.. py:class:: EditUserPostProcessor

   Bases: :py:obj:`bpy.types.Operator`


   Edit the User Post Processor File in Blender


   .. py:attribute:: bl_idname
      :value: 'fabex.edit_user_post_processor'



   .. py:attribute:: bl_label
      :value: 'Edit User Post Processor'



   .. py:method:: execute(context)


.. py:class:: CAMSimulate(*args, **kwargs)

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`fabex.operators.async_op.AsyncOperatorMixin`


   Simulate CAM Operation
   This Is Performed by: Creating an Image, Painting Z Depth of the Brush Subtractively.
   Works only for Some Operations, Can Not Be Used for 4-5 Axis.


   .. py:attribute:: bl_idname
      :value: 'object.cam_simulate'



   .. py:attribute:: bl_label
      :value: 'CAM Simulation'



   .. py:attribute:: bl_options


   .. py:attribute:: operation
      :type:  StringProperty(name='Operation', description='Specify the operation to calculate', default='Operation')


   .. py:method:: execute_async(context)
      :async:


      Execute an asynchronous simulation operation based on the active CAM
      operation.

      This method retrieves the current scene and the active CAM operation.
      It constructs the operation name and checks if the corresponding object
      exists in the Blender data. If it does, it attempts to run the
      simulation asynchronously. If the simulation is cancelled, it returns a
      cancellation status. If the object does not exist, it reports an error
      and returns a finished status.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the status of the operation, either
                    {'CANCELLED'} or {'FINISHED'}.
      :rtype: dict



   .. py:method:: draw(context)

      Draws the user interface for selecting CAM operations.

      This method creates a layout element in the user interface that allows
      users to search and select a specific CAM operation from a list of
      available operations defined in the current scene. It utilizes the
      Blender Python API to integrate with the UI.

      :param context: The context in which the drawing occurs, typically
                      provided by Blender's UI system.



.. py:class:: CAMSimulateChain(*args, **kwargs)

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`fabex.operators.async_op.AsyncOperatorMixin`


   Simulate CAM Chain, Compared to Single Op Simulation Just Writes Into One Image and Thus Enables
   to See how Ops Work Together.


   .. py:attribute:: bl_idname
      :value: 'object.cam_simulate_chain'



   .. py:attribute:: bl_label
      :value: 'CAM Simulation'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:


      Check the validity of the active CAM chain in the scene.

      This method retrieves the currently active CAM chain from the scene's
      CAM chains and checks its validity using the `isChainValid` function.
      It returns a boolean indicating whether the active CAM chain is
      valid.

      :param context: The context containing the scene and its properties.
      :type context: object

      :returns: True if the active CAM chain is valid, False otherwise.
      :rtype: bool



   .. py:attribute:: operation
      :type:  StringProperty(name='Operation', description='Specify the operation to calculate', default='Operation')


   .. py:method:: execute_async(context)
      :async:


      Execute an asynchronous simulation for a specified CAM chain.

      This method retrieves the active CAM chain from the current Blender
      scene and determines the operations associated with that chain. It
      checks if all operations are valid and can be simulated. If valid, it
      proceeds to execute the simulation asynchronously. If any operation is
      invalid, it logs a message and returns a finished status without
      performing the

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the status of the operation, either
                operation completed successfully.
      :rtype: dict



   .. py:method:: draw(context)

      Draw the user interface for selecting CAM operations.

      This function creates a user interface element that allows the user to
      search and select a specific CAM operation from a list of available
      operations in the current scene. It utilizes the Blender Python API to
      create a property search layout.

      :param context: The context in which the drawing occurs, typically containing
                      information about the current scene and UI elements.



.. py:class:: CamSliceObjects

   Bases: :py:obj:`bpy.types.Operator`


   Slice a Mesh Object Horizontally


   .. py:attribute:: bl_idname
      :value: 'object.cam_slice_objects'



   .. py:attribute:: bl_label
      :value: 'Slice Object - Useful for Lasercut Puzzles etc'



   .. py:attribute:: bl_options


   .. py:attribute:: slice_distance
      :type:  FloatProperty(name='Slicing Distance', description='Slices distance in z, should be most often thickness of plywood sheet.', min=0.001, max=10, default=0.005, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: slice_above_0
      :type:  BoolProperty(name='Slice Above 0', description='only slice model above 0', default=False)


   .. py:attribute:: slice_3d
      :type:  BoolProperty(name='3D Slice', description='For 3D carving', default=False)


   .. py:attribute:: indexes
      :type:  BoolProperty(name='Add Indexes', description='Adds index text of layer + index', default=True)


   .. py:method:: invoke(context, event)


   .. py:method:: execute(context)

      Slice a 3D object into layers based on a specified thickness.

      This function takes a 3D object and slices it into multiple layers
      according to the specified thickness. It creates a new collection for
      the slices and optionally creates text labels for each slice if the
      indexes parameter is set. The slicing can be done in either 2D or 3D
      based on the user's selection. The function also handles the positioning
      of the slices based on the object's bounding box.

      :param ob: The 3D object to be sliced.
      :type ob: bpy.types.Object



   .. py:method:: draw(context)


.. py:data:: classes

.. py:function:: register()

.. py:function:: unregister()

