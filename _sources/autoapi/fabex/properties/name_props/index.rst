fabex.properties.name_props
===========================

.. py:module:: fabex.properties.name_props

.. autoapi-nested-parse::

   Fabex 'name_props.py'


   All CAM related naming properties.



Attributes
----------

.. autoapisummary::

   fabex.properties.name_props.name_options


Classes
-------

.. autoapisummary::

   fabex.properties.name_props.CAM_NAME_Properties


Functions
---------

.. autoapisummary::

   fabex.properties.name_props.setup_names
   fabex.properties.name_props.build_names
   fabex.properties.name_props.get_path_name
   fabex.properties.name_props.get_operation_name
   fabex.properties.name_props.get_chain_name
   fabex.properties.name_props.get_simulation_name
   fabex.properties.name_props.get_file_name
   fabex.properties.name_props.update_name_link


Module Contents
---------------

.. py:data:: name_options
   :value: [('NONE', '(none)', 'Empty name slots will be ignored'), ('DATE', 'Date', 'The date of the gcode...


.. py:function:: setup_names()

.. py:function:: build_names(enum_dict, prefix, main_1, main_2, main_3, suffix)

.. py:function:: get_path_name(context)

.. py:function:: get_operation_name(context)

.. py:function:: get_chain_name(context)

.. py:function:: get_simulation_name(context)

.. py:function:: get_file_name(context)

.. py:function:: update_name_link(self, context)

.. py:class:: CAM_NAME_Properties

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: default_export_location
      :type:  StringProperty(name='Export Folder', description='Folder where Fabex will save exported gcode files', subtype='DIR_PATH', default='')


   .. py:attribute:: link_names
      :type:  BoolProperty(name='Link Chain/Op and File Names', description='Uses the Chain or Operation name as the gcode export File name', default=False, update=update_name_link)


   .. py:attribute:: separator
      :type:  StringProperty(name='Separator', description='Character to place between name items - prefix, main, suffix', default='_')


   .. py:attribute:: path_prefix
      :type:  StringProperty(name='Path Prefix', description="Start of CAM Path's name", default='cam_path')


   .. py:attribute:: path_main_1
      :type:  EnumProperty(name='Path Main 1', description="Middle of CAM Path's name (1/3)", items=name_options, default='OP_NAME')


   .. py:attribute:: path_main_2
      :type:  EnumProperty(name='Path Main 2', description="Middle of CAM Path's name (2/3)", items=name_options, default='NONE')


   .. py:attribute:: path_main_3
      :type:  EnumProperty(name='Path Main 3', description="Middle of CAM Path's name (3/3)", items=name_options, default='NONE')


   .. py:attribute:: path_suffix
      :type:  StringProperty(name='Path Suffix', description="End of CAM Path's name", default='')


   .. py:attribute:: path_name_full
      :type:  StringProperty(name='Path Name (full)', get=get_path_name)


   .. py:attribute:: operation_prefix
      :type:  StringProperty(name='Operation Prefix', description="Start of CAM Operation's name", default='Op')


   .. py:attribute:: operation_main_1
      :type:  EnumProperty(name='Operation Main 1', description="Middle of CAM Operation's name (1/3)", items=name_options, default='OBJECT')


   .. py:attribute:: operation_main_2
      :type:  EnumProperty(name='Operation Main 2', description="Middle of CAM Operation's name (2/3)", items=name_options, default='INDEX')


   .. py:attribute:: operation_main_3
      :type:  EnumProperty(name='Operation Main 3', description="Middle of CAM Operation's name (3/3)", items=name_options, default='NONE')


   .. py:attribute:: operation_suffix
      :type:  StringProperty(name='Operation Suffix', description="End of CAM Operation's name", default='')


   .. py:attribute:: operation_name_full
      :type:  StringProperty(name='Operation Name (full)', get=get_operation_name)


   .. py:attribute:: chain_prefix
      :type:  StringProperty(name='Chain Prefix', description="Start of CAM Chain's name", default='Chain')


   .. py:attribute:: chain_main_1
      :type:  EnumProperty(name='Chain Main 1', description="Middle of CAM Chain's name (1/3)", items=name_options, default='INDEX')


   .. py:attribute:: chain_main_2
      :type:  EnumProperty(name='Chain Main 2', description="Middle of CAM Chain's name (2/3)", items=name_options, default='NONE')


   .. py:attribute:: chain_main_3
      :type:  EnumProperty(name='Chain Main 3', description="Middle of CAM Chain's name (3/3)", items=name_options, default='NONE')


   .. py:attribute:: chain_suffix
      :type:  StringProperty(name='Chain Suffix', description="End of CAM Chain's name", default='')


   .. py:attribute:: chain_name_full
      :type:  StringProperty(name='Chain Name (full)', get=get_chain_name)


   .. py:attribute:: simulation_prefix
      :type:  StringProperty(name='Simulation Prefix', description="Start of CAM Simulation's name", default='csim')


   .. py:attribute:: simulation_main_1
      :type:  EnumProperty(name='Simulation Main 1', description="Middle of CAM Simulation's name (1/3)", items=name_options, default='OP_NAME')


   .. py:attribute:: simulation_main_2
      :type:  EnumProperty(name='Simulation Main 2', description="Middle of CAM Simulation's name (2/3)", items=name_options, default='NONE')


   .. py:attribute:: simulation_main_3
      :type:  EnumProperty(name='Simulation Main 3', description="Middle of CAM Simulation's name (3/3)", items=name_options, default='NONE')


   .. py:attribute:: simulation_suffix
      :type:  StringProperty(name='Simulation Suffix', description="End of CAM Simulation's name", default='')


   .. py:attribute:: simulation_name_full
      :type:  StringProperty(name='Simulation Name (full)', get=get_simulation_name)


   .. py:attribute:: file_prefix
      :type:  StringProperty(name='File Prefix', description="Start of CAM File's name", default='')


   .. py:attribute:: file_main_1
      :type:  EnumProperty(name='File Main 1', description="Middle of CAM File's name (1/3)", items=name_options, default='OP_NAME')


   .. py:attribute:: file_main_2
      :type:  EnumProperty(name='File Main 2', description="Middle of CAM File's name (2/3)", items=name_options, default='NONE')


   .. py:attribute:: file_main_3
      :type:  EnumProperty(name='File Main 3', description="Middle of CAM File's name (3/3)", items=name_options, default='NONE')


   .. py:attribute:: file_suffix
      :type:  StringProperty(name='File Suffix', description="End of CAM File's name", default='')


   .. py:attribute:: file_name_full
      :type:  StringProperty(name='File Name (full)', get=get_file_name)


