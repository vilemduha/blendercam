cam.preset_managers
===================

.. py:module:: cam.preset_managers

.. autoapi-nested-parse::

   BlenderCAM 'preset_managers.py'

   Operators and Menus for CAM Machine, Cutter and Operation Presets.



Classes
-------

.. autoapisummary::

   cam.preset_managers.CAM_CUTTER_MT_presets
   cam.preset_managers.CAM_MACHINE_MT_presets
   cam.preset_managers.AddPresetCamCutter
   cam.preset_managers.CAM_OPERATION_MT_presets
   cam.preset_managers.AddPresetCamOperation
   cam.preset_managers.AddPresetCamMachine


Module Contents
---------------

.. py:class:: CAM_CUTTER_MT_presets

   Bases: :py:obj:`bpy.types.Menu`


   .. py:attribute:: bl_label
      :value: 'Cutter Presets'



   .. py:attribute:: preset_subdir
      :value: 'cam_cutters'



   .. py:attribute:: preset_operator
      :value: 'script.execute_preset'



   .. py:attribute:: draw


.. py:class:: CAM_MACHINE_MT_presets

   Bases: :py:obj:`bpy.types.Menu`


   .. py:attribute:: bl_label
      :value: 'Machine Presets'



   .. py:attribute:: preset_subdir
      :value: 'cam_machines'



   .. py:attribute:: preset_operator
      :value: 'script.execute_preset'



   .. py:attribute:: draw


   .. py:method:: post_cb(context)
      :classmethod:



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



.. py:class:: CAM_OPERATION_MT_presets

   Bases: :py:obj:`bpy.types.Menu`


   .. py:attribute:: bl_label
      :value: 'Operation Presets'



   .. py:attribute:: preset_subdir
      :value: 'cam_operations'



   .. py:attribute:: preset_operator
      :value: 'script.execute_preset'



   .. py:attribute:: draw


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
      :value: ['from pathlib import Path', 'bpy.ops.scene.cam_operation_add()', 'scene = bpy.context.scene',...



   .. py:attribute:: preset_values
      :value: ['o.info.duration', 'o.info.chipload', 'o.info.warnings', 'o.material.estimate_from_model',...



   .. py:attribute:: preset_subdir
      :value: 'cam_operations'



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
      :value: ['d.post_processor', 's.system', 'd.use_position_definitions', 'd.starting_position',...



   .. py:attribute:: preset_subdir
      :value: 'cam_machines'



