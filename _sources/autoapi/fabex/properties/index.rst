fabex.properties
================

.. py:module:: fabex.properties

.. autoapi-nested-parse::

   Fabex 'properties.__init__.py' © 2012 Vilem Novak

   Import Properties, Register and Unregister Classes



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/fabex/properties/chain_props/index
   /autoapi/fabex/properties/info_props/index
   /autoapi/fabex/properties/interface_props/index
   /autoapi/fabex/properties/machine_props/index
   /autoapi/fabex/properties/material_props/index
   /autoapi/fabex/properties/movement_props/index
   /autoapi/fabex/properties/operation_props/index
   /autoapi/fabex/properties/optimisation_props/index


Attributes
----------

.. autoapisummary::

   fabex.properties.classes


Classes
-------

.. autoapisummary::

   fabex.properties.CAM_CHAIN_Properties
   fabex.properties.CAM_OP_REFERENCE_Properties
   fabex.properties.CAM_INFO_Properties
   fabex.properties.CAM_INTERFACE_Properties
   fabex.properties.CAM_MACHINE_Properties
   fabex.properties.CAM_MATERIAL_Properties
   fabex.properties.CAM_MOVEMENT_Properties
   fabex.properties.CAM_OPTIMISATION_Properties


Functions
---------

.. autoapisummary::

   fabex.properties.draw_interface
   fabex.properties.update_operation
   fabex.properties.register
   fabex.properties.unregister


Package Contents
----------------

.. py:class:: CAM_CHAIN_Properties

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: index
      :type:  IntProperty(name='Index', description='Index in the hard-defined camChains', default=-1)


   .. py:attribute:: active_operation
      :type:  IntProperty(name='Active Operation', description='Active operation in chain', default=-1)


   .. py:attribute:: name
      :type:  StringProperty(name='Chain Name', default='Chain')


   .. py:attribute:: filename
      :type:  StringProperty(name='File Name', default='Chain')


   .. py:attribute:: valid
      :type:  BoolProperty(name='Valid', description='True if whole Chain is OK for calculation', default=True)


   .. py:attribute:: invalid_reason
      :type:  StringProperty(name='Chain Error', default='', update=chain_valid)


   .. py:attribute:: computing
      :type:  BoolProperty(name='Computing Right Now', description='', default=False)


   .. py:attribute:: operations
      :type:  CollectionProperty(type=CAM_OP_REFERENCE_Properties)


.. py:class:: CAM_OP_REFERENCE_Properties

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: name
      :type:  StringProperty(name='Operation Name', default='Operation')


   .. py:attribute:: computing
      :value: False



.. py:class:: CAM_INFO_Properties

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: warnings
      :type:  StringProperty(name='Warnings', description='Warnings', default='', update=update_operation)


   .. py:attribute:: chipload
      :type:  FloatProperty(name='Chipload', description='Calculated chipload', default=0.0, unit='LENGTH', precision=CHIPLOAD_PRECISION)


   .. py:attribute:: chipload_per_tooth
      :type:  StringProperty(name='Chipload per Tooth', description='The chipload divided by the number of teeth', default='')


   .. py:attribute:: duration
      :type:  FloatProperty(name='Estimated Time', default=0.01, min=0.0, max=MAX_OPERATION_TIME, precision=PRECISION, unit='TIME')


.. py:class:: CAM_INTERFACE_Properties

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: level
      :type:  EnumProperty(name='Interface', description='Choose visible options', items=[('0', 'Basic', 'Only show essential options', '', 0), ('1', 'Advanced', 'Show advanced options', '', 1), ('2', 'Complete', 'Show all options', '', 2), ('3', 'Experimental', 'Show experimental options', 'EXPERIMENTAL', 3)], default='0', update=update_interface)


   .. py:attribute:: shading
      :type:  EnumProperty(name='Shading', description='Choose viewport shading preset', items=[('DEFAULT', 'Default', 'Standard viewport shading'), ('DELUXE', 'Deluxe', 'Cavity, Curvature, Depth of Field, Shadows & Object Colors'), ('CLEAN_DEFAULT', 'Clean Default', 'Standard viewport shading with no overlays'), ('CLEAN_DELUXE', 'Clean Deluxe', 'Deluxe shading with no overlays'), ('PREVIEW', 'Preview', 'HDRI Lighting Preview')], default='DEFAULT', update=update_shading)


   .. py:attribute:: layout
      :type:  EnumProperty(name='Layout', description='Presets for all panel locations', items=[('CLASSIC', 'Classic', 'Properties Area holds most panels, Tools holds the rest'), ('MODERN', 'Modern', 'Properties holds Main panels, Sidebar holds Operation panels, Tools holds Tools'), ('USER', 'User', 'Define your own locations for panels')], default='MODERN', update=update_layout)


   .. py:attribute:: main_location
      :type:  EnumProperty(name='Main Panels', description='Location for Chains, Operations, Material, Machine, Pack, Slice Panels', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='PROPERTIES', update=update_user_layout)


   .. py:attribute:: operation_location
      :type:  EnumProperty(name='Operation Panels', description='Location for Setup, Area, Cutter, Feedrate, Optimisation, Movement, G-code', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='SIDEBAR', update=update_user_layout)


   .. py:attribute:: tools_location
      :type:  EnumProperty(name='Tools Panels', description='Location for Curve Tools, Curve Creators, Info', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='TOOLS', update=update_user_layout)


.. py:function:: draw_interface(self, context)

.. py:class:: CAM_MACHINE_Properties

   Bases: :py:obj:`bpy.types.PropertyGroup`


   stores all data for machines


   .. py:attribute:: post_processor
      :type:  EnumProperty(name='Post Processor', items=(('ISO', 'Iso', 'Exports standardized gcode ISO 6983 (RS-274)'), ('MACH3', 'Mach3', 'Default mach3'), ('EMC', 'LinuxCNC - EMC2', 'Linux based CNC control software - formally EMC2'), ('FADAL', 'Fadal', 'Fadal VMC'), ('GRBL', 'grbl', 'Optimized gcode for grbl firmware on Arduino with cnc shield'), ('HEIDENHAIN', 'Heidenhain', 'Heidenhain'), ('HEIDENHAIN530', 'Heidenhain530', 'Heidenhain530'), ('TNC151', 'Heidenhain TNC151', 'Post Processor for the Heidenhain TNC151 machine'), ('SIEGKX1', 'Sieg KX1', 'Sieg KX1'), ('HM50', 'Hafco HM-50', 'Hafco HM-50'), ('CENTROID', 'Centroid M40', 'Centroid M40'), ('ANILAM', 'Anilam Crusader M', 'Anilam Crusader M'), ('GRAVOS', 'Gravos', 'Gravos'), ('WIN-PC', 'WinPC-NC', 'German CNC by Burkhard Lewetz'), ('SHOPBOT MTC', 'ShopBot MTC', 'ShopBot MTC'), ('LYNX_OTTER_O', 'Lynx Otter o', 'Lynx Otter o')), description='Post Processor', default='MACH3')


   .. py:attribute:: use_position_definitions
      :type:  BoolProperty(name='Use Position Definitions', description='Define own positions for op start, toolchange, ending position', default=False)


   .. py:attribute:: starting_position
      :type:  FloatVectorProperty(name='Start Position', default=(0, 0, 0), unit='LENGTH', precision=PRECISION, subtype='XYZ', update=update_machine)


   .. py:attribute:: mtc_position
      :type:  FloatVectorProperty(name='MTC Position', default=(0, 0, 0), unit='LENGTH', precision=PRECISION, subtype='XYZ', update=update_machine)


   .. py:attribute:: ending_position
      :type:  FloatVectorProperty(name='End Position', default=(0, 0, 0), unit='LENGTH', precision=PRECISION, subtype='XYZ', update=update_machine)


   .. py:attribute:: working_area
      :type:  FloatVectorProperty(name='Work Area', default=(0.5, 0.5, 0.1), unit='LENGTH', precision=PRECISION, subtype='XYZ', update=update_machine)


   .. py:attribute:: feedrate_min
      :type:  FloatProperty(name='Feedrate Minimum /min', default=0.0, min=1e-05, max=320000, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: feedrate_max
      :type:  FloatProperty(name='Feedrate Maximum /min', default=2, min=1e-05, max=320000, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: feedrate_default
      :type:  FloatProperty(name='Feedrate Default /min', default=1.5, min=1e-05, max=320000, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: hourly_rate
      :type:  FloatProperty(name='Price per Hour', default=100, min=0.005, precision=2)


   .. py:attribute:: spindle_min
      :type:  FloatProperty(name='Spindle Speed Minimum RPM', default=5000, min=1e-05, max=320000, precision=1)


   .. py:attribute:: spindle_max
      :type:  FloatProperty(name='Spindle Speed Maximum RPM', default=30000, min=1e-05, max=320000, precision=1)


   .. py:attribute:: spindle_default
      :type:  FloatProperty(name='Spindle Speed Default RPM', default=15000, min=1e-05, max=320000, precision=1)


   .. py:attribute:: spindle_start_time
      :type:  FloatProperty(name='Spindle Start Delay Seconds', description='Wait for the spindle to start spinning before starting the feeds , in seconds', default=0, min=0.0, max=320000, precision=1)


   .. py:attribute:: spindle_slow_start_enable
      :type:  BoolProperty(name='Spindle Slow Start Enable', description='Enable gradual spindle speed ramping from minimum to target speed', default=False)


   .. py:attribute:: spindle_slow_start_steps
      :type:  IntProperty(name='Slow Start Steps', description='Number of intermediate speed steps when ramping from minimum to target spindle speed. More steps = smoother acceleration', default=8, min=2, max=20)


   .. py:attribute:: spindle_slow_start_skip_threshold
      :type:  FloatProperty(name='Skip Threshold (RPM)', description='If target speed is within this RPM of the minimum speed, skip slow start and go directly to target', default=500, min=0, max=5000, precision=0)


   .. py:attribute:: spindle_slow_start_total_time
      :type:  FloatProperty(name='Total Ramp Time (seconds)', description='Total time in seconds to ramp from minimum to target speed, distributed equally across all steps', default=2.0, min=0.1, max=10.0, precision=1)


   .. py:attribute:: axis_4
      :type:  BoolProperty(name='4th Axis', description='Machine has 4th axis', default=0)


   .. py:attribute:: axis_5
      :type:  BoolProperty(name='5th Axis', description='Machine has 5th axis', default=0)


   .. py:attribute:: eval_splitting
      :type:  BoolProperty(name='Split Files', description='Split gcode file with large number of operations', default=True)


   .. py:attribute:: split_limit
      :type:  IntProperty(name='Operations per File', description='Split files with larger number of operations than this', min=1000, max=20000000, default=800000)


   .. py:attribute:: collet_size
      :type:  FloatProperty(name='Collet Size', description='Collet size for collision detection', default=33, min=1e-05, max=320000, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: output_block_numbers
      :type:  BoolProperty(name='Output Block Numbers', description='Output block numbers ie N10 at start of line', default=False)


   .. py:attribute:: start_block_number
      :type:  IntProperty(name='Start Block Number', description='The starting block number ie 10', default=10)


   .. py:attribute:: block_number_increment
      :type:  IntProperty(name='Block Number Increment', description='How much the block number should increment for the next line', default=10)


   .. py:attribute:: output_tool_definitions
      :type:  BoolProperty(name='Output Tool Definitions', description='Output tool definitions', default=True)


   .. py:attribute:: output_tool_change
      :type:  BoolProperty(name='Output Tool Change Commands', description='Output tool change commands ie: Tn M06', default=True)


   .. py:attribute:: output_G43_on_tool_change
      :type:  BoolProperty(name='Output G43 on Tool Change', description='Output G43 on tool change line', default=False)


.. py:class:: CAM_MATERIAL_Properties

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: estimate_from_model
      :type:  BoolProperty(name='Estimate Cut Area from Model', description='Estimate cut area based on model geometry', default=True, update=update_material)


   .. py:attribute:: radius_around_model
      :type:  FloatProperty(name='Radius Around Model', description='Increase cut area around the model on X and Y by this amount', default=0.0, unit='LENGTH', precision=PRECISION, update=update_material)


   .. py:attribute:: center_x
      :type:  BoolProperty(name='Center on X Axis', description='Position model centered on X', default=False, update=update_material)


   .. py:attribute:: center_y
      :type:  BoolProperty(name='Center on Y Axis', description='Position model centered on Y', default=False, update=update_material)


   .. py:attribute:: z_position
      :type:  EnumProperty(name='Z Placement', items=(('ABOVE', 'Above', 'Place object vertically above the XY plane'), ('BELOW', 'Below', 'Place object vertically below the XY plane'), ('CENTERED', 'Centered', 'Place object vertically centered on the XY plane')), description='Position below Zero', default='BELOW', update=update_material)


   .. py:attribute:: origin
      :type:  FloatVectorProperty(name='Material Origin', default=(0, 0, 0), unit='LENGTH', precision=PRECISION, subtype='XYZ', update=update_material)


   .. py:attribute:: size
      :type:  FloatVectorProperty(name='Material Size', default=(0.2, 0.2, 0.1), min=0, unit='LENGTH', precision=PRECISION, subtype='XYZ', update=update_material)


.. py:class:: CAM_MOVEMENT_Properties

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: type
      :type:  EnumProperty(name='Movement Type', items=(('CONVENTIONAL', 'Conventional (Up)', 'Cutter rotates against the direction of the feed'), ('CLIMB', 'Climb (Down)', 'Cutter rotates with the direction of the feed'), ('MEANDER', 'Meander (Zig Zag)', 'Cutting is done both with and against the rotation of the spindle')), description='movement type', default='CLIMB', update=update_operation)


   .. py:attribute:: insideout
      :type:  EnumProperty(name='Direction', items=(('INSIDEOUT', 'Inside out', 'a'), ('OUTSIDEIN', 'Outside in', 'a')), description='Approach to the piece', default='INSIDEOUT', update=update_operation)


   .. py:attribute:: spindle_rotation
      :type:  EnumProperty(name='Spindle Rotation', items=(('CW', 'Clockwise', 'a'), ('CCW', 'Counter clockwise', 'a')), description='Spindle rotation direction', default='CW', update=update_operation)


   .. py:attribute:: free_height
      :type:  FloatProperty(name='Safe Height', description='Height where the machine can freely move without hitting the workpiece', default=0.01, min=0.0, max=32, precision=PRECISION, unit='LENGTH', update=update_operation)


   .. py:attribute:: useG64
      :type:  BoolProperty(name='G64 Trajectory', description='Use only if your machine supports G64 code. LinuxCNC and Mach3 do', default=False, update=update_operation)


   .. py:attribute:: G64
      :type:  FloatProperty(name='Path Control Mode with Optional Tolerance', default=0.0001, min=0.0, max=0.005, precision=PRECISION, unit='LENGTH', update=update_operation)


   .. py:attribute:: parallel_step_back
      :type:  BoolProperty(name='Parallel Step Back', description='For roughing and finishing in one pass: mills material in climb mode, then steps back and goes between 2 last chunks back', default=False, update=update_operation)


   .. py:attribute:: helix_enter
      :type:  BoolProperty(name='Helix Enter - EXPERIMENTAL', description='Enter material in helix', default=False, update=update_operation)


   .. py:attribute:: ramp_in_angle
      :type:  FloatProperty(name='Ramp-in Angle', default=pi / 6, min=0, max=pi * 0.4999, precision=1, step=500, subtype='ANGLE', unit='ROTATION', update=update_operation)


   .. py:attribute:: helix_diameter
      :type:  FloatProperty(name='Helix Diameter - % of Cutter Diameter', default=90, min=10, max=100, precision=1, subtype='PERCENTAGE', update=update_operation)


   .. py:attribute:: ramp
      :type:  BoolProperty(name='Ramp-in - EXPERIMENTAL', description='Ramps down the whole contour, so the cutline looks like helix', default=False, update=update_operation)


   .. py:attribute:: zig_zag_ramp
      :type:  BoolProperty(name='Zigzag_ramp - EXPERIMENTAL', description='Ramps down the whole contour, so the cutline looks like zigzag_', default=False, update=update_operation)


   .. py:attribute:: ramp_out
      :type:  BoolProperty(name='Ramp-out - EXPERIMENTAL', description='Ramp out to not leave mark on surface', default=False, update=update_operation)


   .. py:attribute:: ramp_out_angle
      :type:  FloatProperty(name='Ramp-out Angle', default=pi / 6, min=0, max=pi * 0.4999, precision=1, step=500, subtype='ANGLE', unit='ROTATION', update=update_operation)


   .. py:attribute:: retract_tangential
      :type:  BoolProperty(name='Retract Tangential - EXPERIMENTAL', description='Retract from material in circular motion', default=False, update=update_operation)


   .. py:attribute:: retract_radius
      :type:  FloatProperty(name='Retract Arc Radius', default=0.001, min=1e-06, max=100, precision=PRECISION, unit='LENGTH', update=update_operation)


   .. py:attribute:: retract_height
      :type:  FloatProperty(name='Retract Arc Height', default=0.001, min=0.0, max=100, precision=PRECISION, unit='LENGTH', update=update_operation)


   .. py:attribute:: stay_low
      :type:  BoolProperty(name='Stay Low if Possible', default=True, update=update_operation)


   .. py:attribute:: merge_distance
      :type:  FloatProperty(name='Merge Distance - EXPERIMENTAL', default=0.0, min=0.0, max=0.1, precision=PRECISION, unit='LENGTH', update=update_operation)


   .. py:attribute:: protect_vertical
      :type:  BoolProperty(name='Protect Vertical', description='The path goes only vertically next to steep areas', default=True, update=update_operation)


   .. py:attribute:: protect_vertical_limit
      :type:  FloatProperty(name='Verticality Limit', description='What angle is already considered vertical', default=pi / 45, min=0, max=pi * 0.5, precision=0, step=100, subtype='ANGLE', unit='ROTATION', update=update_operation)


.. py:class:: CAM_OPTIMISATION_Properties

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: optimize
      :type:  BoolProperty(name='Reduce Path Points', description='Reduce path points', default=True, update=update_operation)


   .. py:attribute:: optimize_threshold
      :type:  FloatProperty(name='Reduction Threshold in μm', default=0.2, min=1e-09, max=1000, precision=20, update=update_operation)


   .. py:attribute:: use_exact
      :type:  BoolProperty(name='Use Exact Mode', description='Exact mode allows greater precision, but is slower with complex meshes', default=True, update=update_exact_mode)


   .. py:attribute:: imgres_limit
      :type:  IntProperty(name='Maximum Resolution in Megapixels', default=16, min=1, max=512, description='Limits total memory usage and prevents crashes. Increase it if you know what are doing', update=update_zbuffer_image)


   .. py:attribute:: pixsize
      :type:  FloatProperty(name='Sampling Raster Detail', default=0.0001, min=1e-05, max=0.1, precision=PRECISION, unit='LENGTH', update=update_zbuffer_image)


   .. py:attribute:: use_opencamlib
      :type:  BoolProperty(name='Use OpenCAMLib', description='Use OpenCAMLib to sample paths or get waterline shape', default=False, update=update_opencamlib)


   .. py:attribute:: exact_subdivide_edges
      :type:  BoolProperty(name='Auto Subdivide Long Edges', description='This can avoid some collision issues when importing CAD models', default=False, update=update_exact_mode)


   .. py:attribute:: circle_detail
      :type:  IntProperty(name='Detail of Circles Used for Curve Offsets', default=64, min=12, max=512, update=update_operation)


   .. py:attribute:: simulation_detail
      :type:  FloatProperty(name='Simulation Sampling Raster Detail', default=0.0002, min=1e-05, max=0.01, precision=PRECISION, unit='LENGTH', update=update_operation)


.. py:function:: update_operation(self, context)

   Update the CAM operation based on the current context.

   This function retrieves the active CAM operation from the Blender
   context and updates it using the `updateRest` function. It accesses the
   active operation from the scene's CAM operations and passes the
   current context to the updating function.

   :param context: The context in which the operation is being updated.


.. py:data:: classes

.. py:function:: register()

.. py:function:: unregister()

