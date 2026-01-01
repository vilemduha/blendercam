fabex.operators.preset_ops
==========================

.. py:module:: fabex.operators.preset_ops

.. autoapi-nested-parse::

   Fabex 'preset_managers.py'

   Operators and Menus for CAM Machine, Cutter and Operation Presets.



Classes
-------

.. autoapisummary::

   fabex.operators.preset_ops.AddPresetCamCutter
   fabex.operators.preset_ops.AddPresetCamOperation
   fabex.operators.preset_ops.AddPresetCamMachine
   fabex.operators.preset_ops.EditUserPostProcessor


Module Contents
---------------

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



.. py:class:: EditUserPostProcessor

   Bases: :py:obj:`bpy.types.Operator`


   Edit the User Post Processor File in Blender


   .. py:attribute:: bl_idname
      :value: 'fabex.edit_user_post_processor'



   .. py:attribute:: bl_label
      :value: 'Edit User Post Processor'



   .. py:method:: execute(context)


