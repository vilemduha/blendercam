fabex.properties.preset_props
=============================

.. py:module:: fabex.properties.preset_props

.. autoapi-nested-parse::

   Fabex 'properties.preset_props.py' © 2012 Vilem Novak

   Preset Properties



Attributes
----------

.. autoapisummary::

   fabex.properties.preset_props.operation_presets
   fabex.properties.preset_props.operation_preset_path
   fabex.properties.preset_props.operation_presets
   fabex.properties.preset_props.finishing_operations
   fabex.properties.preset_props.roughing_operations
   fabex.properties.preset_props.operation_types
   fabex.properties.preset_props.user_operations
   fabex.properties.preset_props.finishing_presets
   fabex.properties.preset_props.roughing_presets
   fabex.properties.preset_props.user_operation_presets
   fabex.properties.preset_props.cutter_presets
   fabex.properties.preset_props.cutter_preset_path
   fabex.properties.preset_props.cutter_presets
   fabex.properties.preset_props.idcwoodcraft_cutters
   fabex.properties.preset_props.cadence_cutters
   fabex.properties.preset_props.brand_cutters
   fabex.properties.preset_props.user_cutters
   fabex.properties.preset_props.idcwoodcraft_presets
   fabex.properties.preset_props.cadence_presets
   fabex.properties.preset_props.user_cutter_presets
   fabex.properties.preset_props.machine_presets
   fabex.properties.preset_props.machine_preset_path
   fabex.properties.preset_props.machine_presets
   fabex.properties.preset_props.avidcnc_machines
   fabex.properties.preset_props.carbide3d_machines
   fabex.properties.preset_props.cnc4all_machines
   fabex.properties.preset_props.inventables_machines
   fabex.properties.preset_props.millright_machines
   fabex.properties.preset_props.onefinity_machines
   fabex.properties.preset_props.ooznest_machines
   fabex.properties.preset_props.sienci_machines
   fabex.properties.preset_props.brand_machines
   fabex.properties.preset_props.user_machines
   fabex.properties.preset_props.avidcnc_presets
   fabex.properties.preset_props.carbide3d_presets
   fabex.properties.preset_props.cnc4all_presets
   fabex.properties.preset_props.inventables_presets
   fabex.properties.preset_props.millright_presets
   fabex.properties.preset_props.onefinity_presets
   fabex.properties.preset_props.ooznest_presets
   fabex.properties.preset_props.sienci_presets
   fabex.properties.preset_props.user_machine_presets


Functions
---------

.. autoapisummary::

   fabex.properties.preset_props.operation_by_op_type
   fabex.properties.preset_props.get_operation_list
   fabex.properties.preset_props.update_operation_preset
   fabex.properties.preset_props.update_finishing
   fabex.properties.preset_props.update_roughing
   fabex.properties.preset_props.update_user_operation
   fabex.properties.preset_props.cutter_by_make
   fabex.properties.preset_props.get_cutter_list
   fabex.properties.preset_props.update_cutter_preset
   fabex.properties.preset_props.update_idcwoodcraft
   fabex.properties.preset_props.update_cadence
   fabex.properties.preset_props.update_user_cutter
   fabex.properties.preset_props.machine_by_make
   fabex.properties.preset_props.get_machine_list
   fabex.properties.preset_props.update_machine_preset
   fabex.properties.preset_props.update_avidcnc
   fabex.properties.preset_props.update_carbide3d
   fabex.properties.preset_props.update_cnc4all
   fabex.properties.preset_props.update_inventables
   fabex.properties.preset_props.update_millright
   fabex.properties.preset_props.update_onefinity
   fabex.properties.preset_props.update_ooznest
   fabex.properties.preset_props.update_sienci
   fabex.properties.preset_props.update_user_machine


Module Contents
---------------

.. py:data:: operation_presets
   :value: []


.. py:data:: operation_preset_path

.. py:data:: operation_presets

.. py:function:: operation_by_op_type(op_type)

.. py:data:: finishing_operations

.. py:data:: roughing_operations

.. py:data:: operation_types

.. py:data:: user_operations

.. py:function:: get_operation_list(op_type, op_types)

.. py:data:: finishing_presets
   :value: []


.. py:data:: roughing_presets
   :value: []


.. py:data:: user_operation_presets
   :value: []


.. py:function:: update_operation_preset(self, context)

.. py:function:: update_finishing(self, context)

.. py:function:: update_roughing(self, context)

.. py:function:: update_user_operation(self, context)

.. py:data:: cutter_presets
   :value: []


.. py:data:: cutter_preset_path

.. py:data:: cutter_presets

.. py:function:: cutter_by_make(make)

.. py:data:: idcwoodcraft_cutters

.. py:data:: cadence_cutters

.. py:data:: brand_cutters

.. py:data:: user_cutters

.. py:function:: get_cutter_list(make, models)

.. py:data:: idcwoodcraft_presets
   :value: []


.. py:data:: cadence_presets
   :value: []


.. py:data:: user_cutter_presets
   :value: []


.. py:function:: update_cutter_preset(self, context)

.. py:function:: update_idcwoodcraft(self, context)

.. py:function:: update_cadence(self, context)

.. py:function:: update_user_cutter(self, context)

.. py:data:: machine_presets
   :value: []


.. py:data:: machine_preset_path

.. py:data:: machine_presets

.. py:function:: machine_by_make(make)

.. py:data:: avidcnc_machines

.. py:data:: carbide3d_machines

.. py:data:: cnc4all_machines

.. py:data:: inventables_machines

.. py:data:: millright_machines

.. py:data:: onefinity_machines

.. py:data:: ooznest_machines

.. py:data:: sienci_machines

.. py:data:: brand_machines

.. py:data:: user_machines

.. py:function:: get_machine_list(make, models)

.. py:data:: avidcnc_presets
   :value: []


.. py:data:: carbide3d_presets
   :value: []


.. py:data:: cnc4all_presets
   :value: []


.. py:data:: inventables_presets
   :value: []


.. py:data:: millright_presets
   :value: []


.. py:data:: onefinity_presets
   :value: []


.. py:data:: ooznest_presets
   :value: []


.. py:data:: sienci_presets
   :value: []


.. py:data:: user_machine_presets
   :value: []


.. py:function:: update_machine_preset(self, context)

.. py:function:: update_avidcnc(self, context)

.. py:function:: update_carbide3d(self, context)

.. py:function:: update_cnc4all(self, context)

.. py:function:: update_inventables(self, context)

.. py:function:: update_millright(self, context)

.. py:function:: update_onefinity(self, context)

.. py:function:: update_ooznest(self, context)

.. py:function:: update_sienci(self, context)

.. py:function:: update_user_machine(self, context)

