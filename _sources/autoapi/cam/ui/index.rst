cam.ui
======

.. py:module:: cam.ui

.. autoapi-nested-parse::

   BlenderCAM 'ui.py' © 2012 Vilem Novak

   Panels displayed in the 3D Viewport - Curve Tools, Creators and Import G-code



Classes
-------

.. autoapisummary::

   cam.ui.CAM_UL_orientations
   cam.ui.VIEW3D_PT_tools_curvetools
   cam.ui.VIEW3D_PT_tools_create
   cam.ui.CustomPanel
   cam.ui.WM_OT_gcode_import
   cam.ui.import_settings


Module Contents
---------------

.. py:class:: CAM_UL_orientations

   Bases: :py:obj:`bpy.types.UIList`


   .. py:method:: draw_item(context, layout, data, item, icon, active_data, active_propname, index)


.. py:class:: VIEW3D_PT_tools_curvetools

   Bases: :py:obj:`bpy.types.Panel`


   .. py:attribute:: bl_space_type
      :value: 'VIEW_3D'



   .. py:attribute:: bl_region_type
      :value: 'TOOLS'



   .. py:attribute:: bl_context
      :value: 'objectmode'



   .. py:attribute:: bl_label
      :value: 'Curve CAM Tools'



   .. py:method:: draw(context)


.. py:class:: VIEW3D_PT_tools_create

   Bases: :py:obj:`bpy.types.Panel`


   .. py:attribute:: bl_space_type
      :value: 'VIEW_3D'



   .. py:attribute:: bl_region_type
      :value: 'TOOLS'



   .. py:attribute:: bl_context
      :value: 'objectmode'



   .. py:attribute:: bl_label
      :value: 'Curve CAM Creators'



   .. py:attribute:: bl_option
      :value: 'DEFAULT_CLOSED'



   .. py:method:: draw(context)


.. py:class:: CustomPanel

   Bases: :py:obj:`bpy.types.Panel`


   .. py:attribute:: bl_space_type
      :value: 'VIEW_3D'



   .. py:attribute:: bl_region_type
      :value: 'TOOLS'



   .. py:attribute:: bl_context
      :value: 'objectmode'



   .. py:attribute:: bl_label
      :value: 'Import G-code'



   .. py:attribute:: bl_idname
      :value: 'OBJECT_PT_importgcode'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: draw(context)


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


   .. py:method:: execute(context)


.. py:class:: import_settings

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: split_layers
      :type:  BoolProperty(name='Split Layers', description='Save every layer as single Objects in Collection', default=False)


   .. py:attribute:: subdivide
      :type:  BoolProperty(name='Subdivide', description="Only Subdivide gcode segments that are bigger than 'Segment length' ", default=False)


   .. py:attribute:: output
      :type:  EnumProperty(name='Output Type', items=(('mesh', 'Mesh', 'Make a mesh output'), ('curve', 'Curve', 'Make curve output')), default='curve')


   .. py:attribute:: max_segment_size
      :type:  FloatProperty(name='', description='Only Segments bigger than this value get subdivided', default=0.001, min=0.0001, max=1.0, unit='LENGTH')


