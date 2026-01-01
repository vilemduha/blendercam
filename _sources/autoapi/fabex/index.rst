fabex
=====

.. py:module:: fabex

.. autoapi-nested-parse::

   Fabex '__init__.py' © 2012 Vilem Novak

   Import Modules, Register and Unregister  Classes



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/fabex/bridges/index
   /autoapi/fabex/constants/index
   /autoapi/fabex/engine/index
   /autoapi/fabex/exception/index
   /autoapi/fabex/gcode/index
   /autoapi/fabex/joinery/index
   /autoapi/fabex/operators/index
   /autoapi/fabex/preferences/index
   /autoapi/fabex/properties/index
   /autoapi/fabex/simulation/index
   /autoapi/fabex/strategies/index
   /autoapi/fabex/toolpath/index
   /autoapi/fabex/utilities/index
   /autoapi/fabex/version/index


Attributes
----------

.. autoapisummary::

   fabex.classes


Classes
-------

.. autoapisummary::

   fabex.FABEX_ENGINE
   fabex.CAM_OPERATION_Properties
   fabex.CamAddonPreferences


Functions
---------

.. autoapisummary::

   fabex.get_panels
   fabex.ops_register
   fabex.ops_unregister
   fabex.props_register
   fabex.props_unregister
   fabex.on_blender_startup
   fabex.keymap_register
   fabex.keymap_unregister
   fabex.on_engine_change
   fabex.timer_update
   fabex.register
   fabex.unregister


Package Contents
----------------

.. py:class:: FABEX_ENGINE(*args, **kwargs)

   Bases: :py:obj:`bpy.types.RenderEngine`


   .. py:attribute:: bl_idname
      :value: 'FABEX_RENDER'



   .. py:attribute:: bl_label
      :value: 'Fabex CNC/CAM'



   .. py:attribute:: bl_use_eevee_viewport
      :value: True



.. py:function:: get_panels()

   Retrieve a list of panels for the Blender UI.

   This function compiles a list of UI panels that are compatible with the
   Blender rendering engine. It excludes certain predefined panels that are
   not relevant for the current context. The function checks all subclasses
   of the `bpy.types.Panel` and includes those that have the
   `COMPAT_ENGINES` attribute set to include 'BLENDER_RENDER', provided
   they are not in the exclusion list.

   :returns: A list of panel classes that are compatible with the
             Blender rendering engine, excluding specified panels.
   :rtype: list


.. py:function:: ops_register()

.. py:function:: ops_unregister()

.. py:function:: props_register()

.. py:function:: props_unregister()

.. py:class:: CAM_OPERATION_Properties

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: material
      :type:  PointerProperty(type=CAM_MATERIAL_Properties)


   .. py:attribute:: info
      :type:  PointerProperty(type=CAM_INFO_Properties)


   .. py:attribute:: optimisation
      :type:  PointerProperty(type=CAM_OPTIMISATION_Properties)


   .. py:attribute:: movement
      :type:  PointerProperty(type=CAM_MOVEMENT_Properties)


   .. py:attribute:: name
      :type:  StringProperty(name='Operation Name', default='Operation', update=update_rest)


   .. py:attribute:: filename
      :type:  StringProperty(name='File Name', default='Operation', update=update_rest)


   .. py:attribute:: link_operation_file_names
      :type:  BoolProperty(name='Link Operation & File Name', description='Auto-assign the Operation Name to the Operation Gcode File', default=False)


   .. py:attribute:: auto_export
      :type:  BoolProperty(name='Auto Export', description='Export files immediately after path calculation', default=True)


   .. py:attribute:: remove_redundant_points
      :type:  BoolProperty(name='Simplify G-code', description='Remove redundant points sharing the same angle as the start vector', default=False)


   .. py:attribute:: simplify_tolerance
      :type:  IntProperty(name='Tolerance', description='lower number means more precise', default=50, min=1, max=1000)


   .. py:attribute:: hide_all_others
      :type:  BoolProperty(name='Hide All Others', description='Hide all other tool paths except toolpath associated with selected CAM operation', default=False)


   .. py:attribute:: parent_path_to_object
      :type:  BoolProperty(name='Parent Path to Object', description='Parent generated CAM path to source object', default=False)


   .. py:attribute:: object_name
      :type:  StringProperty(name='Object', description='Object handled by this operation', update=update_operation_valid)


   .. py:attribute:: collection_name
      :type:  StringProperty(name='Collection', description='Object collection handled by this operation', update=update_operation_valid)


   .. py:attribute:: curve_source
      :type:  StringProperty(name='Curve Source', description='Curve which will be sampled along the 3D object', update=operation_valid)


   .. py:attribute:: curve_target
      :type:  StringProperty(name='Curve Target', description='Curve which will serve as attractor for the cutter when the cutter follows the curve', update=operation_valid)


   .. py:attribute:: source_image_name
      :type:  StringProperty(name='Image Source', description='image source', update=operation_valid)


   .. py:attribute:: geometry_source
      :type:  EnumProperty(name='Data Source', items=(('OBJECT', 'Object', 'a', 'OBJECT_DATA', 0), ('COLLECTION', 'Collection', 'a', 'OUTLINER_COLLECTION', 1), ('IMAGE', 'Image', 'a', 'OUTLINER_OB_IMAGE', 2)), description='Geometry source', default='OBJECT', update=update_operation_valid)


   .. py:attribute:: machine_axes
      :type:  EnumProperty(name='Number of Axes', items=(('3', '3 axis', 'a', 'EMPTY_DATA', 0), ('4', '4 axis - EXPERIMENTAL', 'a', 'EXPERIMENTAL', 1), ('5', '5 axis - EXPERIMENTAL', 'a', 'EXPERIMENTAL', 2)), description='How many axes will be used for the operation', default='3', update=update_strategy)


   .. py:attribute:: strategy
      :type:  EnumProperty(name='Strategy', items=get_strategy_list, description='Strategy', update=update_strategy)


   .. py:attribute:: strategy_4_axis
      :type:  EnumProperty(name='4 Axis Strategy', items=(('PARALLELR', 'Parallel around 1st rotary axis', 'Parallel lines around first rotary axis'), ('PARALLEL', 'Parallel along 1st rotary axis', 'Parallel lines along first rotary axis'), ('HELIX', 'Helix around 1st rotary axis', 'Helix around rotary axis'), ('INDEXED', 'Indexed 3-axis', 'all 3 axis strategies, just applied to the 4th axis'), ('CROSS', 'Cross', 'Cross paths')), description='#Strategy', default='PARALLEL', update=update_strategy)


   .. py:attribute:: strategy_5_axis
      :type:  EnumProperty(name='Strategy', items=(('INDEXED', 'Indexed 3-axis', 'All 3 axis strategies, just rotated by 4+5th axes'), ), description='5 axis Strategy', default='INDEXED', update=update_strategy)


   .. py:attribute:: rotary_axis_1
      :type:  EnumProperty(name='Rotary Axis', items=(('X', 'X', ''), ('Y', 'Y', ''), ('Z', 'Z', '')), description='Around which axis rotates the first rotary axis', default='X', update=update_strategy)


   .. py:attribute:: rotary_axis_2
      :type:  EnumProperty(name='Rotary Axis 2', items=(('X', 'X', ''), ('Y', 'Y', ''), ('Z', 'Z', '')), description='Around which axis rotates the second rotary axis', default='Z', update=update_strategy)


   .. py:attribute:: skin
      :type:  FloatProperty(name='Skin', description='Material to leave when roughing ', min=0.0, max=1.0, default=0.0, precision=PRECISION, unit='LENGTH', update=update_offset_image)


   .. py:attribute:: inverse
      :type:  BoolProperty(name='Inverse Milling', description='Male to female model conversion', default=False, update=update_offset_image)


   .. py:attribute:: array
      :type:  BoolProperty(name='Use Array', description='Create a repetitive array for producing the same thing many times', default=False, update=update_rest)


   .. py:attribute:: array_x_count
      :type:  IntProperty(name='X Count', description='X count', default=1, min=1, max=32000, update=update_rest)


   .. py:attribute:: array_y_count
      :type:  IntProperty(name='Y Count', description='Y count', default=1, min=1, max=32000, update=update_rest)


   .. py:attribute:: array_x_distance
      :type:  FloatProperty(name='X Distance', description='Distance between operation origins', min=1e-05, max=1.0, default=0.01, precision=PRECISION, unit='LENGTH', update=update_rest)


   .. py:attribute:: array_y_distance
      :type:  FloatProperty(name='Y Distance', description='Distance between operation origins', min=1e-05, max=1.0, default=0.01, precision=PRECISION, unit='LENGTH', update=update_rest)


   .. py:attribute:: pocket_option
      :type:  EnumProperty(name='Start Position', items=(('INSIDE', 'Inside', 'a'), ('OUTSIDE', 'Outside', 'a')), description='Pocket starting position', default='INSIDE', update=update_rest)


   .. py:attribute:: pocket_type
      :type:  EnumProperty(name='pocket type', items=(('PERIMETER', 'Perimeter', 'a', '', 0), ('PARALLEL', 'Parallel', 'a', 'EXPERIMENTAL', 1)), description='Type of pocket', default='PERIMETER', update=update_rest)


   .. py:attribute:: parallel_pocket_angle
      :type:  FloatProperty(name='Parallel Pocket Angle', description='Angle for parallel pocket', min=-180, max=180.0, default=45.0, precision=PRECISION, update=update_rest)


   .. py:attribute:: parallel_pocket_crosshatch
      :type:  BoolProperty(name='Crosshatch #', description='Crosshatch X finish', default=False, update=update_rest)


   .. py:attribute:: parallel_pocket_contour
      :type:  BoolProperty(name='Contour Finish', description='Contour path finish', default=False, update=update_rest)


   .. py:attribute:: pocket_to_curve
      :type:  BoolProperty(name='Pocket to Curve', description='Generates a curve instead of a path', default=False, update=update_rest)


   .. py:attribute:: cut_type
      :type:  EnumProperty(name='Cut', items=(('OUTSIDE', 'Outside', 'a'), ('INSIDE', 'Inside', 'a'), ('ONLINE', 'On Line', 'a')), description='Type of cutter used', default='OUTSIDE', update=update_rest)


   .. py:attribute:: outlines_count
      :type:  IntProperty(name='Outlines Count', description='Outlines count', default=1, min=1, max=32, update=update_cutout)


   .. py:attribute:: straight
      :type:  BoolProperty(name='Overshoot Style', description='Use overshoot cutout instead of conventional rounded', default=True, update=update_rest)


   .. py:attribute:: cutter_type
      :type:  EnumProperty(name='Cutter', items=(('END', 'End', 'End - Flat cutter'), ('BALLNOSE', 'Ballnose', 'Ballnose cutter'), ('BULLNOSE', 'Bullnose', 'Bullnose cutter ***placeholder **'), ('VCARVE', 'V-carve', 'V-carve cutter'), ('BALLCONE', 'Ballcone', 'Ball with a Cone for Parallel - X'), ('CYLCONE', 'Cylinder cone', 'Cylinder End with a Cone for Parallel - X'), ('LASER', 'Laser', 'Laser cutter'), ('PLASMA', 'Plasma', 'Plasma cutter'), ('CUSTOM', 'Custom-EXPERIMENTAL', 'Modelled cutter - not well tested yet.')), description='Type of cutter used', default='END', update=update_Z_buffer_image)


   .. py:attribute:: cutter_object_name
      :type:  StringProperty(name='Cutter Object', description='Object used as custom cutter for this operation', update=update_Z_buffer_image)


   .. py:attribute:: cutter_id
      :type:  IntProperty(name='Tool Number', description='For machines which support tool change based on tool id', min=0, max=10000, default=1, update=update_rest)


   .. py:attribute:: cutter_diameter
      :type:  FloatProperty(name='Cutter Diameter', description='Cutter diameter = 2x cutter radius', min=1e-06, max=10, default=0.003, precision=PRECISION, unit='LENGTH', update=update_offset_image)


   .. py:attribute:: cylcone_diameter
      :type:  FloatProperty(name='Bottom Diameter', description='Bottom diameter', min=1e-06, max=10, default=0.003, precision=PRECISION, unit='LENGTH', update=update_offset_image)


   .. py:attribute:: cutter_length
      :type:  FloatProperty(name='#Cutter Length', description='#not supported#Cutter length', min=0.0, max=100.0, default=25.0, precision=PRECISION, unit='LENGTH', update=update_offset_image)


   .. py:attribute:: cutter_flutes
      :type:  IntProperty(name='Cutter Flutes', description='Cutter flutes', min=1, max=20, default=2, update=update_chipload)


   .. py:attribute:: cutter_tip_angle
      :type:  FloatProperty(name='Cutter V-carve Angle', description='Cutter V-carve angle', default=60.0, min=0.0, max=180.0, precision=PRECISION, step=500, update=update_offset_image)


   .. py:attribute:: ball_radius
      :type:  FloatProperty(name='Ball Radius', description='Radius of', min=0.0, max=0.035, default=0.001, unit='LENGTH', precision=PRECISION, update=update_offset_image)


   .. py:attribute:: bull_corner_radius
      :type:  FloatProperty(name='Bull Corner Radius', description='Radius tool bit corner', min=0.0, max=0.035, default=0.005, unit='LENGTH', precision=PRECISION, update=update_offset_image)


   .. py:attribute:: cutter_description
      :type:  StringProperty(name='Tool Description', default='', update=update_offset_image)


   .. py:attribute:: laser_on
      :type:  StringProperty(name='Laser ON String', default='M68 E0 Q100')


   .. py:attribute:: laser_off
      :type:  StringProperty(name='Laser OFF String', default='M68 E0 Q0')


   .. py:attribute:: laser_cmd
      :type:  StringProperty(name='Laser Command', default='M68 E0 Q')


   .. py:attribute:: laser_delay
      :type:  FloatProperty(name='Laser ON Delay', description='Time after fast move to turn on laser and let machine stabilize', default=0.2)


   .. py:attribute:: plasma_on
      :type:  StringProperty(name='Plasma ON String', default='M03')


   .. py:attribute:: plasma_off
      :type:  StringProperty(name='Plasma OFF String', default='M05')


   .. py:attribute:: plasma_delay
      :type:  FloatProperty(name='Plasma ON Delay', description='Time after fast move to turn on Plasma and let machine stabilize', default=0.1)


   .. py:attribute:: plasma_dwell
      :type:  FloatProperty(name='Plasma Dwell Time', description='Time to dwell and warm up the torch', default=0.0)


   .. py:attribute:: distance_between_paths
      :type:  FloatProperty(name='Distance Between Toolpaths', description='Distance Between / Overlap of Toolpaths - Linked to Cutter Diameter', default=0.001, min=1e-05, max=32, precision=PRECISION, unit='LENGTH', update=update_rest)


   .. py:attribute:: distance_along_paths
      :type:  FloatProperty(name='Distance Along Toolpaths', description='Toolpath Resolution - Details Smaller than this Size Will not be Captured', default=0.0002, min=1e-05, max=32, precision=PRECISION, unit='LENGTH', update=update_rest)


   .. py:attribute:: parallel_angle
      :type:  FloatProperty(name='Angle of Paths', default=0, min=-360, max=360, precision=0, step=500, subtype='ANGLE', unit='ROTATION', update=update_rest)


   .. py:attribute:: old_rotation_a
      :type:  FloatProperty(name='A Axis Angle', description='old value of Rotate A axis\nto specified angle', default=0, min=-360, max=360, precision=0, subtype='ANGLE', unit='ROTATION', update=update_rest)


   .. py:attribute:: old_rotation_b
      :type:  FloatProperty(name='A Axis Angle', description='old value of Rotate A axis\nto specified angle', default=0, min=-360, max=360, precision=0, subtype='ANGLE', unit='ROTATION', update=update_rest)


   .. py:attribute:: rotation_a
      :type:  FloatProperty(name='A Axis Angle', description='Rotate A axis\nto specified angle', default=0, min=-360, max=360, precision=0, step=500, subtype='ANGLE', unit='ROTATION', update=update_rotation)


   .. py:attribute:: enable_a_axis
      :type:  BoolProperty(name='Enable A Axis', description='Rotate A axis', default=False, update=update_rotation)


   .. py:attribute:: a_along_x
      :type:  BoolProperty(name='A Along X ', description='A Parallel to X', default=True, update=update_rest)


   .. py:attribute:: rotation_b
      :type:  FloatProperty(name='B Axis Angle', description='Rotate B axis\nto specified angle', default=0, min=-360, max=360, precision=0, step=500, subtype='ANGLE', unit='ROTATION', update=update_rotation)


   .. py:attribute:: enable_b_axis
      :type:  BoolProperty(name='Enable B Axis', description='Rotate B axis', default=False, update=update_rotation)


   .. py:attribute:: carve_depth
      :type:  FloatProperty(name='Carve Depth', default=0.001, min=-0.1, max=32, precision=PRECISION, unit='LENGTH', update=update_rest)


   .. py:attribute:: drill_type
      :type:  EnumProperty(name='Holes On', items=(('MIDDLE_SYMETRIC', 'Middle of Symmetric Curves', 'a'), ('MIDDLE_ALL', 'Middle of All Curve Parts', 'a'), ('ALL_POINTS', 'All Points in Curve', 'a')), description='Strategy to detect holes to drill', default='MIDDLE_SYMETRIC', update=update_rest)


   .. py:attribute:: slice_detail
      :type:  FloatProperty(name='Distance Between Slices', default=0.001, min=1e-05, max=32, precision=PRECISION, unit='LENGTH', update=update_rest)


   .. py:attribute:: waterline_fill
      :type:  BoolProperty(name='Fill Areas Between Slices', description='Fill areas between slices in waterline mode', default=True, update=update_rest)


   .. py:attribute:: waterline_project
      :type:  BoolProperty(name='Project Paths - Not Recomended', description='Project paths in areas between slices', default=True, update=update_rest)


   .. py:attribute:: use_layers
      :type:  BoolProperty(name='Use Layers', description='Use layers for roughing', default=True, update=update_rest)


   .. py:attribute:: stepdown
      :type:  FloatProperty(name='', description='Layer height', default=0.01, min=1e-05, max=32, precision=PRECISION, unit='LENGTH', update=update_rest)


   .. py:attribute:: lead_in
      :type:  FloatProperty(name='Lead-in Radius', description='Lead in radius for torch or laser to turn off', min=0.0, max=1, default=0.0, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: lead_out
      :type:  FloatProperty(name='Lead-out Radius', description='Lead out radius for torch or laser to turn off', min=0.0, max=1, default=0.0, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: profile_start
      :type:  IntProperty(name='Start Point', description='Start point offset', min=0, default=0, update=update_rest)


   .. py:attribute:: min_z
      :type:  FloatProperty(name='Operation Depth End', default=-0.01, min=-3, max=3, precision=PRECISION, unit='LENGTH', update=update_rest)


   .. py:attribute:: min_z_from
      :type:  EnumProperty(name='Max Depth From', description='Set maximum operation depth', items=(('OBJECT', 'Object', 'Set max operation depth from Object'), ('MATERIAL', 'Material', 'Set max operation depth from Material'), ('CUSTOM', 'Custom', 'Custom max depth')), default='OBJECT', update=update_rest)


   .. py:attribute:: start_type
      :type:  EnumProperty(name='Start Type', items=(('ZLEVEL', 'Z level', 'Starts on a given Z level'), ('OPERATIONRESULT', 'Rest Milling', 'For rest milling, operations have to be put in chain for this to work well.')), description='Starting depth', default='ZLEVEL', update=update_strategy)


   .. py:attribute:: max_z
      :type:  FloatProperty(name='Operation Depth Start', description='operation starting depth', default=0, min=-3, max=10, precision=PRECISION, unit='LENGTH', update=update_rest)


   .. py:attribute:: first_down
      :type:  BoolProperty(name='First Down', description='First go down on a contour, then go to the next one', default=False, update=update_operation)


   .. py:attribute:: source_image_scale_z
      :type:  FloatProperty(name='Image Source Depth Scale', default=0.01, min=-1, max=1, precision=PRECISION, unit='LENGTH', update=update_Z_buffer_image)


   .. py:attribute:: source_image_size_x
      :type:  FloatProperty(name='Image Source X Size', default=0.1, min=-10, max=10, precision=PRECISION, unit='LENGTH', update=update_Z_buffer_image)


   .. py:attribute:: source_image_size_y
      :type:  FloatProperty(name='Image Source Y Size', default=0.1, min=-10, max=10, precision=PRECISION, unit='LENGTH', update=update_image_size_y)


   .. py:attribute:: source_image_offset
      :type:  FloatVectorProperty(name='Image Offset', default=(0, 0, 0), unit='LENGTH', precision=PRECISION, subtype='XYZ', update=update_Z_buffer_image)


   .. py:attribute:: source_image_crop
      :type:  BoolProperty(name='Crop Source Image', description='Crop source image - the position of the sub-rectangle is relative to the whole image, so it can be used for e.g. finishing just a part of an image', default=False, update=update_Z_buffer_image)


   .. py:attribute:: source_image_crop_start_x
      :type:  FloatProperty(name='Crop Start X', default=0, min=0, max=100, precision=PRECISION, subtype='PERCENTAGE', update=update_Z_buffer_image)


   .. py:attribute:: source_image_crop_start_y
      :type:  FloatProperty(name='Crop Start Y', default=0, min=0, max=100, precision=PRECISION, subtype='PERCENTAGE', update=update_Z_buffer_image)


   .. py:attribute:: source_image_crop_end_x
      :type:  FloatProperty(name='Crop End X', default=100, min=0, max=100, precision=PRECISION, subtype='PERCENTAGE', update=update_Z_buffer_image)


   .. py:attribute:: source_image_crop_end_y
      :type:  FloatProperty(name='Crop End Y', default=100, min=0, max=100, precision=PRECISION, subtype='PERCENTAGE', update=update_Z_buffer_image)


   .. py:attribute:: ambient_behaviour
      :type:  EnumProperty(name='Ambient', items=(('ALL', 'All', 'a'), ('AROUND', 'Around', 'a')), description='Handling ambient surfaces', default='ALL', update=update_Z_buffer_image)


   .. py:attribute:: ambient_radius
      :type:  FloatProperty(name='Ambient Radius', description='Radius around the part which will be milled if ambient is set to Around', min=0.0, max=100.0, default=0.01, precision=PRECISION, unit='LENGTH', update=update_rest)


   .. py:attribute:: use_limit_curve
      :type:  BoolProperty(name='Use Limit Curve', description='A curve limits the operation area', default=False, update=update_rest)


   .. py:attribute:: ambient_cutter_restrict
      :type:  BoolProperty(name='Cutter Stays in Ambient Limits', description="Cutter doesn't get out from ambient limits otherwise goes on the border exactly", default=True, update=update_rest)


   .. py:attribute:: limit_curve
      :type:  StringProperty(name='Limit Curve', description='Curve used to limit the area of the operation', update=update_rest)


   .. py:attribute:: feedrate
      :type:  FloatProperty(name='Feedrate', description='Feedrate in units per minute', min=5e-05, max=50.0, default=1.0, precision=PRECISION, unit='LENGTH', update=update_chipload)


   .. py:attribute:: plunge_feedrate
      :type:  FloatProperty(name='Plunge Speed', description='% of feedrate', min=0.1, max=100.0, default=50.0, precision=1, subtype='PERCENTAGE', update=update_rest)


   .. py:attribute:: plunge_angle
      :type:  FloatProperty(name='Plunge Angle', description='What angle is already considered to plunge', default=pi / 6, min=0, max=pi * 0.5, precision=0, step=500, subtype='ANGLE', unit='ROTATION', update=update_rest)


   .. py:attribute:: spindle_rpm
      :type:  FloatProperty(name='Spindle RPM', description='Spindle speed ', min=0, max=60000, default=12000, update=update_chipload)


   .. py:attribute:: do_simulation_feedrate
      :type:  BoolProperty(name='Adjust Feedrates with Simulation EXPERIMENTAL', description='Adjust feedrates with simulation', default=False, update=update_rest)


   .. py:attribute:: dont_merge
      :type:  BoolProperty(name="Don't Merge Outlines when Cutting", description='this is usefull when you want to cut around everything', default=False, update=update_rest)


   .. py:attribute:: pencil_threshold
      :type:  FloatProperty(name='Pencil Threshold', default=2e-05, min=1e-08, max=1, precision=PRECISION, unit='LENGTH', update=update_rest)


   .. py:attribute:: crazy_threshold_1
      :type:  FloatProperty(name='Min Engagement', default=0.02, min=1e-08, max=100, precision=PRECISION, update=update_rest)


   .. py:attribute:: crazy_threshold_2
      :type:  FloatProperty(name='Max Engagement', default=0.5, min=1e-08, max=100, precision=PRECISION, update=update_rest)


   .. py:attribute:: crazy_threshold_3
      :type:  FloatProperty(name='Max Angle', default=2, min=1e-08, max=100, precision=PRECISION, update=update_rest)


   .. py:attribute:: crazy_threshold_4
      :type:  FloatProperty(name='Test Angle Step', default=0.05, min=1e-08, max=100, precision=PRECISION, update=update_rest)


   .. py:attribute:: crazy_threshold_5
      :type:  FloatProperty(name='Optimal Engagement', default=0.3, min=1e-08, max=100, precision=PRECISION, update=update_rest)


   .. py:attribute:: add_pocket_for_medial
      :type:  BoolProperty(name='Add Pocket Operation', description='Clean unremoved material after medial axis', default=True, update=update_rest)


   .. py:attribute:: add_mesh_for_medial
      :type:  BoolProperty(name='Add Medial mesh', description='Medial operation returns mesh for editing and further processing', default=False, update=update_rest)


   .. py:attribute:: medial_axis_threshold
      :type:  FloatProperty(name='Long Vector Threshold', default=0.001, min=1e-08, max=100, precision=PRECISION, unit='LENGTH', update=update_rest)


   .. py:attribute:: medial_axis_subdivision
      :type:  FloatProperty(name='Fine Subdivision', default=0.0002, min=1e-08, max=100, precision=PRECISION, unit='LENGTH', update=update_rest)


   .. py:attribute:: use_bridges
      :type:  BoolProperty(name='Use Bridges / Tabs', description='Use bridges in cutout', default=False, update=update_bridges)


   .. py:attribute:: bridges_width
      :type:  FloatProperty(name='Bridge / Tab Width', default=0.002, unit='LENGTH', precision=PRECISION, update=update_bridges)


   .. py:attribute:: bridges_height
      :type:  FloatProperty(name='Bridge / Tab Height', description='Height from the bottom of the cutting operation', default=0.0005, unit='LENGTH', precision=PRECISION, update=update_bridges)


   .. py:attribute:: bridges_collection_name
      :type:  StringProperty(name='Bridges / Tabs Collection', default='Bridges (Tabs)', description='Collection of curves used as bridges', update=operation_valid)


   .. py:attribute:: use_bridge_modifiers
      :type:  BoolProperty(name='Use Bridge / Tab Modifiers', description='Include bridge curve modifiers using render level when calculating operation, does not effect original bridge data', default=True, update=update_bridges)


   .. py:attribute:: use_modifiers
      :type:  BoolProperty(name='Use Mesh Modifiers', description='Include mesh modifiers using render level when calculating operation, does not effect original mesh', default=True, update=operation_valid)


   .. py:attribute:: min
      :type:  FloatVectorProperty(name='Operation Minimum', default=(0, 0, 0), unit='LENGTH', precision=PRECISION, subtype='XYZ')


   .. py:attribute:: max
      :type:  FloatVectorProperty(name='Operation Maximum', default=(0, 0, 0), unit='LENGTH', precision=PRECISION, subtype='XYZ')


   .. py:attribute:: output_header
      :type:  BoolProperty(name='Output G-code Header', description='Output user defined G-code command header at start of operation', default=False)


   .. py:attribute:: gcode_header
      :type:  StringProperty(name='G-code Header', description='G-code commands at start of operation. Use ; for line breaks', default='G53 G0')


   .. py:attribute:: enable_dust
      :type:  BoolProperty(name='Dust Collector', description='Output user defined g-code command header at start of operation', default=False)


   .. py:attribute:: gcode_start_dust_cmd
      :type:  StringProperty(name='Start Dust Collector', description='Commands to start dust collection. Use ; for line breaks', default='M100')


   .. py:attribute:: gcode_stop_dust_cmd
      :type:  StringProperty(name='Stop Dust Collector', description='Command to stop dust collection. Use ; for line breaks', default='M101')


   .. py:attribute:: enable_hold
      :type:  BoolProperty(name='Hold Down', description='Output hold down command at start of operation', default=False)


   .. py:attribute:: gcode_start_hold_cmd
      :type:  StringProperty(name='G-code Header', description='G-code commands at start of operation. Use ; for line breaks', default='M102')


   .. py:attribute:: gcode_stop_hold_cmd
      :type:  StringProperty(name='G-code Header', description='G-code commands at end operation. Use ; for line breaks', default='M103')


   .. py:attribute:: enable_mist
      :type:  BoolProperty(name='Mist', description='Mist command at start of operation', default=False)


   .. py:attribute:: gcode_start_mist_cmd
      :type:  StringProperty(name='Start Mist', description='Command to start mist. Use ; for line breaks', default='M104')


   .. py:attribute:: gcode_stop_mist_cmd
      :type:  StringProperty(name='Stop Mist', description='Command to stop mist. Use ; for line breaks', default='M105')


   .. py:attribute:: output_trailer
      :type:  BoolProperty(name='Output G-code Trailer', description='Output user defined g-code command trailer at end of operation', default=False)


   .. py:attribute:: gcode_trailer
      :type:  StringProperty(name='G-code Trailer', description='G-code commands at end of operation. Use ; for line breaks', default='M02')


   .. py:attribute:: offset_image


   .. py:attribute:: zbuffer_image


   .. py:attribute:: silhouette


   .. py:attribute:: ambient


   .. py:attribute:: operation_limit


   .. py:attribute:: borderwidth
      :value: 50



   .. py:attribute:: objects
      :value: None



   .. py:attribute:: path_object_name
      :type:  StringProperty(name='Path Object', description='Actual CNC path')


   .. py:attribute:: changed
      :type:  BoolProperty(name='True if any of the Operation Settings has Changed', description='Mark for update', default=False)


   .. py:attribute:: update_z_buffer_image_tag
      :type:  BoolProperty(name='Mark Z-Buffer Image for Update', description='Mark for update', default=True)


   .. py:attribute:: update_offset_image_tag
      :type:  BoolProperty(name='Mark Offset Image for Update', description='Mark for update', default=True)


   .. py:attribute:: update_silhouette_tag
      :type:  BoolProperty(name='Mark Silhouette Image for Update', description='Mark for update', default=True)


   .. py:attribute:: update_ambient_tag
      :type:  BoolProperty(name='Mark Ambient Polygon for Update', description='Mark for update', default=True)


   .. py:attribute:: update_bullet_collision_tag
      :type:  BoolProperty(name='Mark Bullet Collision World for Update', description='Mark for update', default=True)


   .. py:attribute:: valid
      :type:  BoolProperty(name='Valid', description='True if operation is ok for calculation', default=True)


   .. py:attribute:: change_data
      :type:  StringProperty(name='Changedata', description='change data for checking if stuff changed.')


   .. py:attribute:: computing
      :type:  BoolProperty(name='Computing Right Now', description='', default=False)


   .. py:attribute:: pid
      :type:  IntProperty(name='Process Id', description='Background process id', default=-1)


   .. py:attribute:: out_text
      :type:  StringProperty(name='Outtext', description='outtext', default='')


.. py:class:: CamAddonPreferences

   Bases: :py:obj:`bpy.types.AddonPreferences`


   .. py:attribute:: bl_idname


   .. py:attribute:: op_preset_update
      :type:  BoolProperty(name='Have the Operation Presets Been Updated', default=False)


   .. py:attribute:: wireframe_color
      :type:  EnumProperty(name='Wire Color Source', description='Wireframe color comes from Object, Theme or a Random color', items=[('OBJECT', 'Object', 'Show object color on wireframe'), ('THEME', 'Theme', "Show Scene wireframes with the theme's wire color"), ('RANDOM', 'Random', 'Show random object color on wireframe')], default='OBJECT')


   .. py:attribute:: default_interface_level
      :type:  EnumProperty(name='Interface Level in New File', description='Choose visible options', items=[('0', 'Basic', 'Only show Essential Options'), ('1', 'Advanced', 'Show Advanced Options'), ('2', 'Complete', 'Show All Options'), ('3', 'Experimental', 'Show Experimental Options')], default='3')


   .. py:attribute:: default_shading
      :type:  EnumProperty(name='Viewport Shading in New File', description='Choose viewport shading preset', items=[('DEFAULT', 'Default', 'Standard viewport shading'), ('DELUXE', 'Deluxe', 'Cavity, Curvature, Depth of Field, Shadows & Object Colors'), ('CLEAN_DEFAULT', 'Clean Default', 'Standard viewport shading with no overlays'), ('CLEAN_DELUXE', 'Clean Deluxe', 'Deluxe shading with no overlays'), ('PREVIEW', 'Preview', 'HDRI Lighting Preview')], default='DEFAULT')


   .. py:attribute:: default_layout
      :type:  EnumProperty(name='Panel Layout', description='Presets for all panel locations', items=[('CLASSIC', 'Classic', 'Properties Area holds most panels, Tools holds the rest'), ('MODERN', 'Modern', 'Properties holds Main panels, Sidebar holds Operation panels, Tools holds Tools'), ('USER', 'User', 'Define your own locations for panels')], default='MODERN')


   .. py:attribute:: default_main_location
      :type:  EnumProperty(name='Main Panels', description='Location for Chains, Operations, Material, Machine, Pack, Slice Panels', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='PROPERTIES')


   .. py:attribute:: default_operation_location
      :type:  EnumProperty(name='Operation Panels', description='Location for Setup, Area, Cutter, Feedrate, Optimisation, Movement, G-code', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='SIDEBAR')


   .. py:attribute:: default_tools_location
      :type:  EnumProperty(name='Tools Panels', description='Location for Curve Tools, Curve Creators, Info', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='TOOLS')


   .. py:attribute:: user_main_location
      :type:  EnumProperty(name='Main Panels', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='PROPERTIES')


   .. py:attribute:: user_operation_location
      :type:  EnumProperty(name='Operation Panels', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='SIDEBAR')


   .. py:attribute:: user_tools_location
      :type:  EnumProperty(name='Tools Panels', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='TOOLS')


   .. py:attribute:: default_machine_preset
      :type:  StringProperty(name='Machine Preset in New File', description='So that machine preset choice persists between files', default='')


   .. py:attribute:: default_simulation_material
      :type:  EnumProperty(name='Simulation Shader', items=[('GLASS', 'Glass', 'Glass or Clear Acrylic-type Material'), ('METAL', 'Metal', 'Metallic Material'), ('PLASTIC', 'Plastic', 'Plastic-type Material'), ('WOOD', 'Wood', 'Wood Grain-type Material')], default='WOOD')


   .. py:attribute:: show_popups
      :type:  BoolProperty(name='Show Warning Popups', description='Shows a Popup window when there is a warning', default=True)


   .. py:method:: draw(context)


.. py:function:: on_blender_startup(context)

   Checks for any broken computations on load and resets them.

   This function verifies the presence of necessary Blender add-ons and
   installs any that are missing. It also resets any ongoing computations
   in CAM operations and sets the interface level to the previously used
   level when loading a new file. If the add-on has been updated, it copies
   the necessary presets from the source to the target directory.
   Additionally, it checks for updates to the CAM plugin and updates
   operation presets if required.

   :param context: The context in which the function is executed, typically containing
                   information about
                   the current Blender environment.


.. py:function:: keymap_register()

   Adds a Keyboard Shortcut to the Active Key Config

   This function binds the keyboard shortcut 'Alt+C' to the Fabex
   Pie Menu, and adds that shortcut to the user's active key configuration.


.. py:function:: keymap_unregister()

   Removes a Keyboard Shortcut from the Active Key Config

   This function removes the keyboard shortcut 'Alt+C' from
   the user's active key configuration.


.. py:function:: on_engine_change(*args)

   Callback function to setup Fabex when activated.

   In combination with a message bus (msgbus) listener, this function will
   run when the Render Engine is changed. If it detects that Fabex is active
   it will call the required setup functions, and log the Fabex activation.


.. py:function:: timer_update(context)

   Monitor background processes related to CAM path calculations.

   This function checks the status of background processes that are
   responsible for calculating CAM paths. It retrieves the current
   processes and monitors their state. If a process has finished, it
   updates the corresponding CAM operation and reloads the necessary
   paths. If the process is still running, it restarts the associated
   thread to continue monitoring.

   :param context: The context in which the function is called, typically
                   containing information about the current scene and operations.


.. py:data:: classes

.. py:function:: register() -> None

.. py:function:: unregister() -> None

