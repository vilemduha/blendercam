fabex.operators.curve_tools_ops
===============================

.. py:module:: fabex.operators.curve_tools_ops

.. autoapi-nested-parse::

   Fabex 'curve_cam_tools.py' © 2012 Vilem Novak, 2021 Alain Pelletier

   Operators that perform various functions on existing curves.



Classes
-------

.. autoapisummary::

   fabex.operators.curve_tools_ops.CamCurveBoolean
   fabex.operators.curve_tools_ops.CamCurveConvexHull
   fabex.operators.curve_tools_ops.CamCurveIntarsion
   fabex.operators.curve_tools_ops.CamCurveSimpleOvercuts
   fabex.operators.curve_tools_ops.CamCurveBoneFilletOvercuts
   fabex.operators.curve_tools_ops.CamCurveRemoveDoubles
   fabex.operators.curve_tools_ops.CamMeshGetPockets
   fabex.operators.curve_tools_ops.CamOffsetSilhouete
   fabex.operators.curve_tools_ops.CamObjectSilhouette


Module Contents
---------------

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


