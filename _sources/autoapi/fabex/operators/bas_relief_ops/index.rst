fabex.operators.bas_relief_ops
==============================

.. py:module:: fabex.operators.bas_relief_ops

.. autoapi-nested-parse::

   Fabex 'basrelief.py'

   Module to allow the creation of reliefs from Images or View Layers.
   (https://en.wikipedia.org/wiki/Relief#Bas-relief_or_low_relief)



Classes
-------

.. autoapisummary::

   fabex.operators.bas_relief_ops.DoBasRelief
   fabex.operators.bas_relief_ops.ProblemAreas


Module Contents
---------------

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



