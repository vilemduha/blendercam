cam
===

.. py:module:: cam

.. autoapi-nested-parse::

   BlenderCAM '__init__.py' © 2012 Vilem Novak

   Import Modules, Register and Unregister Classes



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/cam/autoupdate/index
   /autoapi/cam/basrelief/index
   /autoapi/cam/bridges/index
   /autoapi/cam/cam_chunk/index
   /autoapi/cam/cam_operation/index
   /autoapi/cam/chain/index
   /autoapi/cam/collision/index
   /autoapi/cam/constants/index
   /autoapi/cam/curvecamcreate/index
   /autoapi/cam/curvecamequation/index
   /autoapi/cam/curvecamtools/index
   /autoapi/cam/engine/index
   /autoapi/cam/exception/index
   /autoapi/cam/gcodeimportparser/index
   /autoapi/cam/gcodepath/index
   /autoapi/cam/image_utils/index
   /autoapi/cam/involute_gear/index
   /autoapi/cam/joinery/index
   /autoapi/cam/machine_settings/index
   /autoapi/cam/numba_wrapper/index
   /autoapi/cam/ops/index
   /autoapi/cam/pack/index
   /autoapi/cam/parametric/index
   /autoapi/cam/pattern/index
   /autoapi/cam/polygon_utils_cam/index
   /autoapi/cam/preset_managers/index
   /autoapi/cam/puzzle_joinery/index
   /autoapi/cam/simple/index
   /autoapi/cam/simulation/index
   /autoapi/cam/slice/index
   /autoapi/cam/strategy/index
   /autoapi/cam/testing/index
   /autoapi/cam/ui/index
   /autoapi/cam/utils/index
   /autoapi/cam/version/index
   /autoapi/cam/voronoi/index


Attributes
----------

.. autoapisummary::

   cam.classes


Classes
-------

.. autoapisummary::

   cam.UpdateChecker
   cam.Updater
   cam.UpdateSourceOperator
   cam.camOperation
   cam.camChain
   cam.opReference
   cam.CamCurveDrawer
   cam.CamCurveFlatCone
   cam.CamCurveGear
   cam.CamCurveHatch
   cam.CamCurveInterlock
   cam.CamCurveMortise
   cam.CamCurvePlate
   cam.CamCurvePuzzle
   cam.CamCustomCurve
   cam.CamHypotrochoidCurve
   cam.CamLissajousCurve
   cam.CamSineCurve
   cam.CamCurveBoolean
   cam.CamCurveConvexHull
   cam.CamCurveIntarsion
   cam.CamCurveOvercuts
   cam.CamCurveOvercutsB
   cam.CamCurveRemoveDoubles
   cam.CamMeshGetPockets
   cam.CamOffsetSilhouete
   cam.CamObjectSilhouete
   cam.CNCCAM_ENGINE
   cam.machineSettings
   cam.CalculatePath
   cam.CamBridgesAdd
   cam.CamChainAdd
   cam.CamChainRemove
   cam.CamChainOperationAdd
   cam.CamChainOperationRemove
   cam.CamChainOperationUp
   cam.CamChainOperationDown
   cam.CamOperationAdd
   cam.CamOperationCopy
   cam.CamOperationRemove
   cam.CamOperationMove
   cam.CamOrientationAdd
   cam.CamPackObjects
   cam.CamSliceObjects
   cam.CAMSimulate
   cam.CAMSimulateChain
   cam.KillPathsBackground
   cam.PathsAll
   cam.PathsBackground
   cam.PathsChain
   cam.PathExport
   cam.PathExportChain
   cam.PackObjectsSettings
   cam.AddPresetCamCutter
   cam.AddPresetCamMachine
   cam.AddPresetCamOperation
   cam.CAM_CUTTER_MT_presets
   cam.CAM_MACHINE_MT_presets
   cam.CAM_OPERATION_MT_presets
   cam.SliceObjectsSettings
   cam.CustomPanel
   cam.import_settings
   cam.VIEW3D_PT_tools_curvetools
   cam.VIEW3D_PT_tools_create
   cam.WM_OT_gcode_import


Functions
---------

.. autoapisummary::

   cam.get_panels
   cam.timer_update
   cam.check_operations_on_load
   cam.updateOperation
   cam.register
   cam.unregister


Package Contents
----------------

.. py:class:: UpdateChecker

   Bases: :py:obj:`bpy.types.Operator`


   Check for Updates


   .. py:attribute:: bl_idname
      :value: 'render.cam_check_updates'



   .. py:attribute:: bl_label
      :value: 'Check for Updates in BlenderCAM Plugin'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)


.. py:class:: Updater

   Bases: :py:obj:`bpy.types.Operator`


   Update to Newer Version if Possible


   .. py:attribute:: bl_idname
      :value: 'render.cam_update_now'



   .. py:attribute:: bl_label
      :value: 'Update'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)


   .. py:method:: install_zip_from_url(zip_url)


.. py:class:: UpdateSourceOperator

   Bases: :py:obj:`bpy.types.Operator`


   .. py:attribute:: bl_idname
      :value: 'render.cam_set_update_source'



   .. py:attribute:: bl_label
      :value: 'Set BlenderCAM Update Source'



   .. py:attribute:: new_source
      :type:  StringProperty(default='')


   .. py:method:: execute(context)


.. py:class:: camOperation

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
      :type:  StringProperty(name='Operation Name', default='Operation', update=updateRest)


   .. py:attribute:: filename
      :type:  StringProperty(name='File Name', default='Operation', update=updateRest)


   .. py:attribute:: auto_export
      :type:  BoolProperty(name='Auto Export', description='Export files immediately after path calculation', default=True)


   .. py:attribute:: remove_redundant_points
      :type:  BoolProperty(name='Simplify G-code', description='Remove redundant points sharing the same angle as the start vector', default=False)


   .. py:attribute:: simplify_tol
      :type:  IntProperty(name='Tolerance', description='lower number means more precise', default=50, min=1, max=1000)


   .. py:attribute:: hide_all_others
      :type:  BoolProperty(name='Hide All Others', description='Hide all other tool paths except toolpath associated with selected CAM operation', default=False)


   .. py:attribute:: parent_path_to_object
      :type:  BoolProperty(name='Parent Path to Object', description='Parent generated CAM path to source object', default=False)


   .. py:attribute:: object_name
      :type:  StringProperty(name='Object', description='Object handled by this operation', update=updateOperationValid)


   .. py:attribute:: collection_name
      :type:  StringProperty(name='Collection', description='Object collection handled by this operation', update=updateOperationValid)


   .. py:attribute:: curve_object
      :type:  StringProperty(name='Curve Source', description='Curve which will be sampled along the 3D object', update=operationValid)


   .. py:attribute:: curve_object1
      :type:  StringProperty(name='Curve Target', description='Curve which will serve as attractor for the cutter when the cutter follows the curve', update=operationValid)


   .. py:attribute:: source_image_name
      :type:  StringProperty(name='Image Source', description='image source', update=operationValid)


   .. py:attribute:: geometry_source
      :type:  EnumProperty(name='Data Source', items=(('OBJECT', 'Object', 'a'), ('COLLECTION', 'Collection of Objects', 'a'), ('IMAGE', 'Image', 'a')), description='Geometry source', default='OBJECT', update=updateOperationValid)


   .. py:attribute:: cutter_type
      :type:  EnumProperty(name='Cutter', items=(('END', 'End', 'End - Flat cutter'), ('BALLNOSE', 'Ballnose', 'Ballnose cutter'), ('BULLNOSE', 'Bullnose', 'Bullnose cutter ***placeholder **'), ('VCARVE', 'V-carve', 'V-carve cutter'), ('BALLCONE', 'Ballcone', 'Ball with a Cone for Parallel - X'), ('CYLCONE', 'Cylinder cone', 'Cylinder End with a Cone for Parallel - X'), ('LASER', 'Laser', 'Laser cutter'), ('PLASMA', 'Plasma', 'Plasma cutter'), ('CUSTOM', 'Custom-EXPERIMENTAL', 'Modelled cutter - not well tested yet.')), description='Type of cutter used', default='END', update=updateZbufferImage)


   .. py:attribute:: cutter_object_name
      :type:  StringProperty(name='Cutter Object', description='Object used as custom cutter for this operation', update=updateZbufferImage)


   .. py:attribute:: machine_axes
      :type:  EnumProperty(name='Number of Axes', items=(('3', '3 axis', 'a'), ('4', '#4 axis - EXPERIMENTAL', 'a'), ('5', '#5 axis - EXPERIMENTAL', 'a')), description='How many axes will be used for the operation', default='3', update=updateStrategy)


   .. py:attribute:: strategy
      :type:  EnumProperty(name='Strategy', items=getStrategyList, description='Strategy', update=updateStrategy)


   .. py:attribute:: strategy4axis
      :type:  EnumProperty(name='4 Axis Strategy', items=(('PARALLELR', 'Parallel around 1st rotary axis', 'Parallel lines around first rotary axis'), ('PARALLEL', 'Parallel along 1st rotary axis', 'Parallel lines along first rotary axis'), ('HELIX', 'Helix around 1st rotary axis', 'Helix around rotary axis'), ('INDEXED', 'Indexed 3-axis', 'all 3 axis strategies, just applied to the 4th axis'), ('CROSS', 'Cross', 'Cross paths')), description='#Strategy', default='PARALLEL', update=updateStrategy)


   .. py:attribute:: strategy5axis
      :type:  EnumProperty(name='Strategy', items=(('INDEXED', 'Indexed 3-axis', 'All 3 axis strategies, just rotated by 4+5th axes'), ), description='5 axis Strategy', default='INDEXED', update=updateStrategy)


   .. py:attribute:: rotary_axis_1
      :type:  EnumProperty(name='Rotary Axis', items=(('X', 'X', ''), ('Y', 'Y', ''), ('Z', 'Z', '')), description='Around which axis rotates the first rotary axis', default='X', update=updateStrategy)


   .. py:attribute:: rotary_axis_2
      :type:  EnumProperty(name='Rotary Axis 2', items=(('X', 'X', ''), ('Y', 'Y', ''), ('Z', 'Z', '')), description='Around which axis rotates the second rotary axis', default='Z', update=updateStrategy)


   .. py:attribute:: skin
      :type:  FloatProperty(name='Skin', description='Material to leave when roughing ', min=0.0, max=1.0, default=0.0, precision=constants.PRECISION, unit='LENGTH', update=updateOffsetImage)


   .. py:attribute:: inverse
      :type:  BoolProperty(name='Inverse Milling', description='Male to female model conversion', default=False, update=updateOffsetImage)


   .. py:attribute:: array
      :type:  BoolProperty(name='Use Array', description='Create a repetitive array for producing the same thing many times', default=False, update=updateRest)


   .. py:attribute:: array_x_count
      :type:  IntProperty(name='X Count', description='X count', default=1, min=1, max=32000, update=updateRest)


   .. py:attribute:: array_y_count
      :type:  IntProperty(name='Y Count', description='Y count', default=1, min=1, max=32000, update=updateRest)


   .. py:attribute:: array_x_distance
      :type:  FloatProperty(name='X Distance', description='Distance between operation origins', min=1e-05, max=1.0, default=0.01, precision=constants.PRECISION, unit='LENGTH', update=updateRest)


   .. py:attribute:: array_y_distance
      :type:  FloatProperty(name='Y Distance', description='Distance between operation origins', min=1e-05, max=1.0, default=0.01, precision=constants.PRECISION, unit='LENGTH', update=updateRest)


   .. py:attribute:: pocket_option
      :type:  EnumProperty(name='Start Position', items=(('INSIDE', 'Inside', 'a'), ('OUTSIDE', 'Outside', 'a')), description='Pocket starting position', default='INSIDE', update=updateRest)


   .. py:attribute:: pocketType
      :type:  EnumProperty(name='pocket type', items=(('PERIMETER', 'Perimeter', 'a'), ('PARALLEL', 'Parallel', 'a')), description='Type of pocket', default='PERIMETER', update=updateRest)


   .. py:attribute:: parallelPocketAngle
      :type:  FloatProperty(name='Parallel Pocket Angle', description='Angle for parallel pocket', min=-180, max=180.0, default=45.0, precision=constants.PRECISION, update=updateRest)


   .. py:attribute:: parallelPocketCrosshatch
      :type:  BoolProperty(name='Crosshatch #', description='Crosshatch X finish', default=False, update=updateRest)


   .. py:attribute:: parallelPocketContour
      :type:  BoolProperty(name='Contour Finish', description='Contour path finish', default=False, update=updateRest)


   .. py:attribute:: pocketToCurve
      :type:  BoolProperty(name='Pocket to Curve', description='Generates a curve instead of a path', default=False, update=updateRest)


   .. py:attribute:: cut_type
      :type:  EnumProperty(name='Cut', items=(('OUTSIDE', 'Outside', 'a'), ('INSIDE', 'Inside', 'a'), ('ONLINE', 'On Line', 'a')), description='Type of cutter used', default='OUTSIDE', update=updateRest)


   .. py:attribute:: outlines_count
      :type:  IntProperty(name='Outlines Count', description='Outlines count', default=1, min=1, max=32, update=updateCutout)


   .. py:attribute:: straight
      :type:  BoolProperty(name='Overshoot Style', description='Use overshoot cutout instead of conventional rounded', default=True, update=updateRest)


   .. py:attribute:: cutter_id
      :type:  IntProperty(name='Tool Number', description='For machines which support tool change based on tool id', min=0, max=10000, default=1, update=updateRest)


   .. py:attribute:: cutter_diameter
      :type:  FloatProperty(name='Cutter Diameter', description='Cutter diameter = 2x cutter radius', min=1e-06, max=10, default=0.003, precision=constants.PRECISION, unit='LENGTH', update=updateOffsetImage)


   .. py:attribute:: cylcone_diameter
      :type:  FloatProperty(name='Bottom Diameter', description='Bottom diameter', min=1e-06, max=10, default=0.003, precision=constants.PRECISION, unit='LENGTH', update=updateOffsetImage)


   .. py:attribute:: cutter_length
      :type:  FloatProperty(name='#Cutter Length', description='#not supported#Cutter length', min=0.0, max=100.0, default=25.0, precision=constants.PRECISION, unit='LENGTH', update=updateOffsetImage)


   .. py:attribute:: cutter_flutes
      :type:  IntProperty(name='Cutter Flutes', description='Cutter flutes', min=1, max=20, default=2, update=updateChipload)


   .. py:attribute:: cutter_tip_angle
      :type:  FloatProperty(name='Cutter V-carve Angle', description='Cutter V-carve angle', min=0.0, max=180.0, default=60.0, precision=constants.PRECISION, update=updateOffsetImage)


   .. py:attribute:: ball_radius
      :type:  FloatProperty(name='Ball Radius', description='Radius of', min=0.0, max=0.035, default=0.001, unit='LENGTH', precision=constants.PRECISION, update=updateOffsetImage)


   .. py:attribute:: bull_corner_radius
      :type:  FloatProperty(name='Bull Corner Radius', description='Radius tool bit corner', min=0.0, max=0.035, default=0.005, unit='LENGTH', precision=constants.PRECISION, update=updateOffsetImage)


   .. py:attribute:: cutter_description
      :type:  StringProperty(name='Tool Description', default='', update=updateOffsetImage)


   .. py:attribute:: Laser_on
      :type:  StringProperty(name='Laser ON String', default='M68 E0 Q100')


   .. py:attribute:: Laser_off
      :type:  StringProperty(name='Laser OFF String', default='M68 E0 Q0')


   .. py:attribute:: Laser_cmd
      :type:  StringProperty(name='Laser Command', default='M68 E0 Q')


   .. py:attribute:: Laser_delay
      :type:  FloatProperty(name='Laser ON Delay', description='Time after fast move to turn on laser and let machine stabilize', default=0.2)


   .. py:attribute:: Plasma_on
      :type:  StringProperty(name='Plasma ON String', default='M03')


   .. py:attribute:: Plasma_off
      :type:  StringProperty(name='Plasma OFF String', default='M05')


   .. py:attribute:: Plasma_delay
      :type:  FloatProperty(name='Plasma ON Delay', description='Time after fast move to turn on Plasma and let machine stabilize', default=0.1)


   .. py:attribute:: Plasma_dwell
      :type:  FloatProperty(name='Plasma Dwell Time', description='Time to dwell and warm up the torch', default=0.0)


   .. py:attribute:: dist_between_paths
      :type:  FloatProperty(name='Distance Between Toolpaths', default=0.001, min=1e-05, max=32, precision=constants.PRECISION, unit='LENGTH', update=updateRest)


   .. py:attribute:: dist_along_paths
      :type:  FloatProperty(name='Distance Along Toolpaths', default=0.0002, min=1e-05, max=32, precision=constants.PRECISION, unit='LENGTH', update=updateRest)


   .. py:attribute:: parallel_angle
      :type:  FloatProperty(name='Angle of Paths', default=0, min=-360, max=360, precision=0, subtype='ANGLE', unit='ROTATION', update=updateRest)


   .. py:attribute:: old_rotation_A
      :type:  FloatProperty(name='A Axis Angle', description='old value of Rotate A axis\nto specified angle', default=0, min=-360, max=360, precision=0, subtype='ANGLE', unit='ROTATION', update=updateRest)


   .. py:attribute:: old_rotation_B
      :type:  FloatProperty(name='A Axis Angle', description='old value of Rotate A axis\nto specified angle', default=0, min=-360, max=360, precision=0, subtype='ANGLE', unit='ROTATION', update=updateRest)


   .. py:attribute:: rotation_A
      :type:  FloatProperty(name='A Axis Angle', description='Rotate A axis\nto specified angle', default=0, min=-360, max=360, precision=0, subtype='ANGLE', unit='ROTATION', update=updateRotation)


   .. py:attribute:: enable_A
      :type:  BoolProperty(name='Enable A Axis', description='Rotate A axis', default=False, update=updateRotation)


   .. py:attribute:: A_along_x
      :type:  BoolProperty(name='A Along X ', description='A Parallel to X', default=True, update=updateRest)


   .. py:attribute:: rotation_B
      :type:  FloatProperty(name='B Axis Angle', description='Rotate B axis\nto specified angle', default=0, min=-360, max=360, precision=0, subtype='ANGLE', unit='ROTATION', update=updateRotation)


   .. py:attribute:: enable_B
      :type:  BoolProperty(name='Enable B Axis', description='Rotate B axis', default=False, update=updateRotation)


   .. py:attribute:: carve_depth
      :type:  FloatProperty(name='Carve Depth', default=0.001, min=-0.1, max=32, precision=constants.PRECISION, unit='LENGTH', update=updateRest)


   .. py:attribute:: drill_type
      :type:  EnumProperty(name='Holes On', items=(('MIDDLE_SYMETRIC', 'Middle of Symmetric Curves', 'a'), ('MIDDLE_ALL', 'Middle of All Curve Parts', 'a'), ('ALL_POINTS', 'All Points in Curve', 'a')), description='Strategy to detect holes to drill', default='MIDDLE_SYMETRIC', update=updateRest)


   .. py:attribute:: slice_detail
      :type:  FloatProperty(name='Distance Between Slices', default=0.001, min=1e-05, max=32, precision=constants.PRECISION, unit='LENGTH', update=updateRest)


   .. py:attribute:: waterline_fill
      :type:  BoolProperty(name='Fill Areas Between Slices', description='Fill areas between slices in waterline mode', default=True, update=updateRest)


   .. py:attribute:: waterline_project
      :type:  BoolProperty(name='Project Paths - Not Recomended', description='Project paths in areas between slices', default=True, update=updateRest)


   .. py:attribute:: use_layers
      :type:  BoolProperty(name='Use Layers', description='Use layers for roughing', default=True, update=updateRest)


   .. py:attribute:: stepdown
      :type:  FloatProperty(name='', description='Layer height', default=0.01, min=1e-05, max=32, precision=constants.PRECISION, unit='LENGTH', update=updateRest)


   .. py:attribute:: lead_in
      :type:  FloatProperty(name='Lead-in Radius', description='Lead in radius for torch or laser to turn off', min=0.0, max=1, default=0.0, precision=constants.PRECISION, unit='LENGTH')


   .. py:attribute:: lead_out
      :type:  FloatProperty(name='Lead-out Radius', description='Lead out radius for torch or laser to turn off', min=0.0, max=1, default=0.0, precision=constants.PRECISION, unit='LENGTH')


   .. py:attribute:: profile_start
      :type:  IntProperty(name='Start Point', description='Start point offset', min=0, default=0, update=updateRest)


   .. py:attribute:: minz
      :type:  FloatProperty(name='Operation Depth End', default=-0.01, min=-3, max=3, precision=constants.PRECISION, unit='LENGTH', update=updateRest)


   .. py:attribute:: minz_from
      :type:  EnumProperty(name='Max Depth From', description='Set maximum operation depth', items=(('OBJECT', 'Object', 'Set max operation depth from Object'), ('MATERIAL', 'Material', 'Set max operation depth from Material'), ('CUSTOM', 'Custom', 'Custom max depth')), default='OBJECT', update=updateRest)


   .. py:attribute:: start_type
      :type:  EnumProperty(name='Start Type', items=(('ZLEVEL', 'Z level', 'Starts on a given Z level'), ('OPERATIONRESULT', 'Rest Milling', 'For rest milling, operations have to be put in chain for this to work well.')), description='Starting depth', default='ZLEVEL', update=updateStrategy)


   .. py:attribute:: maxz
      :type:  FloatProperty(name='Operation Depth Start', description='operation starting depth', default=0, min=-3, max=10, precision=constants.PRECISION, unit='LENGTH', update=updateRest)


   .. py:attribute:: first_down
      :type:  BoolProperty(name='First Down', description='First go down on a contour, then go to the next one', default=False, update=update_operation)


   .. py:attribute:: source_image_scale_z
      :type:  FloatProperty(name='Image Source Depth Scale', default=0.01, min=-1, max=1, precision=constants.PRECISION, unit='LENGTH', update=updateZbufferImage)


   .. py:attribute:: source_image_size_x
      :type:  FloatProperty(name='Image Source X Size', default=0.1, min=-10, max=10, precision=constants.PRECISION, unit='LENGTH', update=updateZbufferImage)


   .. py:attribute:: source_image_offset
      :type:  FloatVectorProperty(name='Image Offset', default=(0, 0, 0), unit='LENGTH', precision=constants.PRECISION, subtype='XYZ', update=updateZbufferImage)


   .. py:attribute:: source_image_crop
      :type:  BoolProperty(name='Crop Source Image', description='Crop source image - the position of the sub-rectangle is relative to the whole image, so it can be used for e.g. finishing just a part of an image', default=False, update=updateZbufferImage)


   .. py:attribute:: source_image_crop_start_x
      :type:  FloatProperty(name='Crop Start X', default=0, min=0, max=100, precision=constants.PRECISION, subtype='PERCENTAGE', update=updateZbufferImage)


   .. py:attribute:: source_image_crop_start_y
      :type:  FloatProperty(name='Crop Start Y', default=0, min=0, max=100, precision=constants.PRECISION, subtype='PERCENTAGE', update=updateZbufferImage)


   .. py:attribute:: source_image_crop_end_x
      :type:  FloatProperty(name='Crop End X', default=100, min=0, max=100, precision=constants.PRECISION, subtype='PERCENTAGE', update=updateZbufferImage)


   .. py:attribute:: source_image_crop_end_y
      :type:  FloatProperty(name='Crop End Y', default=100, min=0, max=100, precision=constants.PRECISION, subtype='PERCENTAGE', update=updateZbufferImage)


   .. py:attribute:: ambient_behaviour
      :type:  EnumProperty(name='Ambient', items=(('ALL', 'All', 'a'), ('AROUND', 'Around', 'a')), description='Handling ambient surfaces', default='ALL', update=updateZbufferImage)


   .. py:attribute:: ambient_radius
      :type:  FloatProperty(name='Ambient Radius', description='Radius around the part which will be milled if ambient is set to Around', min=0.0, max=100.0, default=0.01, precision=constants.PRECISION, unit='LENGTH', update=updateRest)


   .. py:attribute:: use_limit_curve
      :type:  BoolProperty(name='Use Limit Curve', description='A curve limits the operation area', default=False, update=updateRest)


   .. py:attribute:: ambient_cutter_restrict
      :type:  BoolProperty(name='Cutter Stays in Ambient Limits', description="Cutter doesn't get out from ambient limits otherwise goes on the border exactly", default=True, update=updateRest)


   .. py:attribute:: limit_curve
      :type:  StringProperty(name='Limit Curve', description='Curve used to limit the area of the operation', update=updateRest)


   .. py:attribute:: feedrate
      :type:  FloatProperty(name='Feedrate', description='Feedrate in units per minute', min=5e-05, max=50.0, default=1.0, precision=constants.PRECISION, unit='LENGTH', update=updateChipload)


   .. py:attribute:: plunge_feedrate
      :type:  FloatProperty(name='Plunge Speed', description='% of feedrate', min=0.1, max=100.0, default=50.0, precision=1, subtype='PERCENTAGE', update=updateRest)


   .. py:attribute:: plunge_angle
      :type:  FloatProperty(name='Plunge Angle', description='What angle is already considered to plunge', default=pi / 6, min=0, max=pi * 0.5, precision=0, subtype='ANGLE', unit='ROTATION', update=updateRest)


   .. py:attribute:: spindle_rpm
      :type:  FloatProperty(name='Spindle RPM', description='Spindle speed ', min=0, max=60000, default=12000, update=updateChipload)


   .. py:attribute:: do_simulation_feedrate
      :type:  BoolProperty(name='Adjust Feedrates with Simulation EXPERIMENTAL', description='Adjust feedrates with simulation', default=False, update=updateRest)


   .. py:attribute:: dont_merge
      :type:  BoolProperty(name="Don't Merge Outlines when Cutting", description='this is usefull when you want to cut around everything', default=False, update=updateRest)


   .. py:attribute:: pencil_threshold
      :type:  FloatProperty(name='Pencil Threshold', default=2e-05, min=1e-08, max=1, precision=constants.PRECISION, unit='LENGTH', update=updateRest)


   .. py:attribute:: crazy_threshold1
      :type:  FloatProperty(name='Min Engagement', default=0.02, min=1e-08, max=100, precision=constants.PRECISION, update=updateRest)


   .. py:attribute:: crazy_threshold5
      :type:  FloatProperty(name='Optimal Engagement', default=0.3, min=1e-08, max=100, precision=constants.PRECISION, update=updateRest)


   .. py:attribute:: crazy_threshold2
      :type:  FloatProperty(name='Max Engagement', default=0.5, min=1e-08, max=100, precision=constants.PRECISION, update=updateRest)


   .. py:attribute:: crazy_threshold3
      :type:  FloatProperty(name='Max Angle', default=2, min=1e-08, max=100, precision=constants.PRECISION, update=updateRest)


   .. py:attribute:: crazy_threshold4
      :type:  FloatProperty(name='Test Angle Step', default=0.05, min=1e-08, max=100, precision=constants.PRECISION, update=updateRest)


   .. py:attribute:: add_pocket_for_medial
      :type:  BoolProperty(name='Add Pocket Operation', description='Clean unremoved material after medial axis', default=True, update=updateRest)


   .. py:attribute:: add_mesh_for_medial
      :type:  BoolProperty(name='Add Medial mesh', description='Medial operation returns mesh for editing and further processing', default=False, update=updateRest)


   .. py:attribute:: medial_axis_threshold
      :type:  FloatProperty(name='Long Vector Threshold', default=0.001, min=1e-08, max=100, precision=constants.PRECISION, unit='LENGTH', update=updateRest)


   .. py:attribute:: medial_axis_subdivision
      :type:  FloatProperty(name='Fine Subdivision', default=0.0002, min=1e-08, max=100, precision=constants.PRECISION, unit='LENGTH', update=updateRest)


   .. py:attribute:: use_bridges
      :type:  BoolProperty(name='Use Bridges / Tabs', description='Use bridges in cutout', default=False, update=updateBridges)


   .. py:attribute:: bridges_width
      :type:  FloatProperty(name='Bridge / Tab Width', default=0.002, unit='LENGTH', precision=constants.PRECISION, update=updateBridges)


   .. py:attribute:: bridges_height
      :type:  FloatProperty(name='Bridge / Tab Height', description='Height from the bottom of the cutting operation', default=0.0005, unit='LENGTH', precision=constants.PRECISION, update=updateBridges)


   .. py:attribute:: bridges_collection_name
      :type:  StringProperty(name='Bridges / Tabs Collection', description='Collection of curves used as bridges', update=operationValid)


   .. py:attribute:: use_bridge_modifiers
      :type:  BoolProperty(name='Use Bridge / Tab Modifiers', description='Include bridge curve modifiers using render level when calculating operation, does not effect original bridge data', default=True, update=updateBridges)


   .. py:attribute:: use_modifiers
      :type:  BoolProperty(name='Use Mesh Modifiers', description='Include mesh modifiers using render level when calculating operation, does not effect original mesh', default=True, update=operationValid)


   .. py:attribute:: min
      :type:  FloatVectorProperty(name='Operation Minimum', default=(0, 0, 0), unit='LENGTH', precision=constants.PRECISION, subtype='XYZ')


   .. py:attribute:: max
      :type:  FloatVectorProperty(name='Operation Maximum', default=(0, 0, 0), unit='LENGTH', precision=constants.PRECISION, subtype='XYZ')


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


   .. py:attribute:: silhouete


   .. py:attribute:: ambient


   .. py:attribute:: operation_limit


   .. py:attribute:: borderwidth
      :value: 50



   .. py:attribute:: object
      :value: None



   .. py:attribute:: path_object_name
      :type:  StringProperty(name='Path Object', description='Actual CNC path')


   .. py:attribute:: changed
      :type:  BoolProperty(name='True if any of the Operation Settings has Changed', description='Mark for update', default=False)


   .. py:attribute:: update_zbufferimage_tag
      :type:  BoolProperty(name='Mark Z-Buffer Image for Update', description='Mark for update', default=True)


   .. py:attribute:: update_offsetimage_tag
      :type:  BoolProperty(name='Mark Offset Image for Update', description='Mark for update', default=True)


   .. py:attribute:: update_silhouete_tag
      :type:  BoolProperty(name='Mark Silhouette Image for Update', description='Mark for update', default=True)


   .. py:attribute:: update_ambient_tag
      :type:  BoolProperty(name='Mark Ambient Polygon for Update', description='Mark for update', default=True)


   .. py:attribute:: update_bullet_collision_tag
      :type:  BoolProperty(name='Mark Bullet Collision World for Update', description='Mark for update', default=True)


   .. py:attribute:: valid
      :type:  BoolProperty(name='Valid', description='True if operation is ok for calculation', default=True)


   .. py:attribute:: changedata
      :type:  StringProperty(name='Changedata', description='change data for checking if stuff changed.')


   .. py:attribute:: computing
      :type:  BoolProperty(name='Computing Right Now', description='', default=False)


   .. py:attribute:: pid
      :type:  IntProperty(name='Process Id', description='Background process id', default=-1)


   .. py:attribute:: outtext
      :type:  StringProperty(name='Outtext', description='outtext', default='')


.. py:class:: camChain

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
      :type:  BoolProperty(name='Valid', description='True if whole chain is ok for calculation', default=True)


   .. py:attribute:: computing
      :type:  BoolProperty(name='Computing Right Now', description='', default=False)


   .. py:attribute:: operations
      :type:  CollectionProperty(type=opReference)


.. py:class:: opReference

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: name
      :type:  StringProperty(name='Operation Name', default='Operation')


   .. py:attribute:: computing
      :value: False



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


   Generates cone from flat stock


   .. py:attribute:: bl_idname
      :value: 'object.curve_flat_cone'



   .. py:attribute:: bl_label
      :value: 'Cone Flat Calculator'



   .. py:attribute:: bl_options


   .. py:attribute:: small_d
      :type:  FloatProperty(name='Small Diameter', default=0.025, min=0, max=0.1, precision=4, unit='LENGTH')


   .. py:attribute:: large_d
      :type:  FloatProperty(name='Large Diameter', default=0.3048, min=0, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: height
      :type:  FloatProperty(name='Height of Cone', default=0.457, min=0, max=3.0, precision=4, unit='LENGTH')


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


   Generates Involute Gears // version 1.1 by Leemon Baird, 2011, Leemon@Leemon.com
   http://www.thingiverse.com/thing:5505


   .. py:attribute:: bl_idname
      :value: 'object.curve_gear'



   .. py:attribute:: bl_label
      :value: 'Gears'



   .. py:attribute:: bl_options


   .. py:attribute:: tooth_spacing
      :type:  FloatProperty(name='Distance per Tooth', default=0.01, min=0.001, max=1.0, precision=4, unit='LENGTH')


   .. py:attribute:: tooth_amount
      :type:  IntProperty(name='Amount of Teeth', default=7, min=4)


   .. py:attribute:: spoke_amount
      :type:  IntProperty(name='Amount of Spokes', default=4, min=0)


   .. py:attribute:: hole_diameter
      :type:  FloatProperty(name='Hole Diameter', default=0.003175, min=0, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: rim_size
      :type:  FloatProperty(name='Rim Size', default=0.003175, min=0, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: hub_diameter
      :type:  FloatProperty(name='Hub Diameter', default=0.005, min=0, max=3.0, precision=4, unit='LENGTH')


   .. py:attribute:: pressure_angle
      :type:  FloatProperty(name='Pressure Angle', default=radians(20), min=0.001, max=pi / 2, precision=4, subtype='ANGLE', unit='ROTATION')


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
      :type:  FloatProperty(default=0.003, min=0, max=3.0, precision=4, unit='LENGTH')


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
      :type:  FloatProperty(name='Tangent Deviation', default=0.0, min=0.0, max=2, subtype='ANGLE', unit='ROTATION')


   .. py:attribute:: fixed_angle
      :type:  FloatProperty(name='Fixed Angle', default=0.0, min=0.0, max=2, subtype='ANGLE', unit='ROTATION')


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
      :type:  FloatProperty(name='Adaptive Angle Threshold', default=0.0, min=0.0, max=2, subtype='ANGLE', unit='ROTATION')


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


   Perform Generates Rounded Plate with Mounting Holes


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
      :type:  FloatProperty(name='Angle A', default=pi / 4, min=-10, max=10, subtype='ANGLE', unit='ROTATION')


   .. py:attribute:: angleb
      :type:  FloatProperty(name='Angle B', default=pi / 4, min=-10, max=10, subtype='ANGLE', unit='ROTATION')


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


   Object Custom Curve


   .. py:attribute:: bl_idname
      :value: 'object.customcurve'



   .. py:attribute:: bl_label
      :value: 'Custom Curve'



   .. py:attribute:: bl_options


   .. py:attribute:: xstring
      :type:  StringProperty(name='X Equation', description='Equation x=F(t)', default='t')


   .. py:attribute:: ystring
      :type:  StringProperty(name='Y Equation', description='Equation y=F(t)', default='0')


   .. py:attribute:: zstring
      :type:  StringProperty(name='Z Equation', description='Equation z=F(t)', default='0.05*sin(2*pi*4*t)')


   .. py:attribute:: iteration
      :type:  IntProperty(name='Iteration', default=100, min=50, max=2000)


   .. py:attribute:: maxt
      :type:  FloatProperty(name='Wave Ends at X', default=0.5, min=-3.0, max=10, precision=4, unit='LENGTH')


   .. py:attribute:: mint
      :type:  FloatProperty(name='Wave Starts at X', default=0, min=-3.0, max=3, precision=4, unit='LENGTH')


   .. py:method:: execute(context)


.. py:class:: CamHypotrochoidCurve

   Bases: :py:obj:`bpy.types.Operator`


   Hypotrochoid


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


   Lissajous


   .. py:attribute:: bl_idname
      :value: 'object.lissajous'



   .. py:attribute:: bl_label
      :value: 'Lissajous Figure'



   .. py:attribute:: bl_options


   .. py:attribute:: amplitude_A
      :type:  FloatProperty(name='Amplitude A', default=0.1, min=0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: waveA
      :type:  EnumProperty(name='Wave X', items=(('sine', 'Sine Wave', 'Sine Wave'), ('triangle', 'Triangle Wave', 'triangle wave')), default='sine')


   .. py:attribute:: amplitude_B
      :type:  FloatProperty(name='Amplitude B', default=0.1, min=0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: waveB
      :type:  EnumProperty(name='Wave Y', items=(('sine', 'Sine Wave', 'Sine Wave'), ('triangle', 'Triangle Wave', 'triangle wave')), default='sine')


   .. py:attribute:: period_A
      :type:  FloatProperty(name='Period A', default=1.1, min=0.001, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: period_B
      :type:  FloatProperty(name='Period B', default=1.0, min=0.001, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: period_Z
      :type:  FloatProperty(name='Period Z', default=1.0, min=0.001, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: amplitude_Z
      :type:  FloatProperty(name='Amplitude Z', default=0.0, min=0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: shift
      :type:  FloatProperty(name='Phase Shift', default=0, min=-360, max=360, precision=4, unit='ROTATION')


   .. py:attribute:: iteration
      :type:  IntProperty(name='Iteration', default=500, min=50, max=10000)


   .. py:attribute:: maxt
      :type:  FloatProperty(name='Wave Ends at X', default=11, min=-3.0, max=1000000, precision=4, unit='LENGTH')


   .. py:attribute:: mint
      :type:  FloatProperty(name='Wave Starts at X', default=0, min=-10.0, max=3, precision=4, unit='LENGTH')


   .. py:method:: execute(context)


.. py:class:: CamSineCurve

   Bases: :py:obj:`bpy.types.Operator`


   Object Sine


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


   .. py:attribute:: beatperiod
      :type:  FloatProperty(name='Beat Period Offset', default=0.0, min=0.0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: shift
      :type:  FloatProperty(name='Phase Shift', default=0, min=-360, max=360, precision=4, unit='ROTATION')


   .. py:attribute:: offset
      :type:  FloatProperty(name='Offset', default=0, min=-1.0, max=1, precision=4, unit='LENGTH')


   .. py:attribute:: iteration
      :type:  IntProperty(name='Iteration', default=100, min=50, max=2000)


   .. py:attribute:: maxt
      :type:  FloatProperty(name='Wave Ends at X', default=0.5, min=-3.0, max=3, precision=4, unit='LENGTH')


   .. py:attribute:: mint
      :type:  FloatProperty(name='Wave Starts at X', default=0, min=-3.0, max=3, precision=4, unit='LENGTH')


   .. py:attribute:: wave_distance
      :type:  FloatProperty(name='Distance Between Multiple Waves', default=0.0, min=0.0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: wave_angle_offset
      :type:  FloatProperty(name='Angle Offset for Multiple Waves', default=pi / 2, min=-200 * pi, max=200 * pi, precision=4, unit='ROTATION')


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


.. py:class:: CamCurveOvercuts

   Bases: :py:obj:`bpy.types.Operator`


   Adds Overcuts for Slots


   .. py:attribute:: bl_idname
      :value: 'object.curve_overcuts'



   .. py:attribute:: bl_label
      :value: 'Add Overcuts - A'



   .. py:attribute:: bl_options


   .. py:attribute:: diameter
      :type:  FloatProperty(name='Diameter', default=0.003175, min=0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: threshold
      :type:  FloatProperty(name='Threshold', default=pi / 2 * 0.99, min=-3.14, max=3.14, precision=4, subtype='ANGLE', unit='ROTATION')


   .. py:attribute:: do_outer
      :type:  BoolProperty(name='Outer Polygons', default=True)


   .. py:attribute:: invert
      :type:  BoolProperty(name='Invert', default=False)


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)


   .. py:method:: invoke(context, event)


.. py:class:: CamCurveOvercutsB

   Bases: :py:obj:`bpy.types.Operator`


   Adds Overcuts for Slots


   .. py:attribute:: bl_idname
      :value: 'object.curve_overcuts_b'



   .. py:attribute:: bl_label
      :value: 'Add Overcuts - B'



   .. py:attribute:: bl_options


   .. py:attribute:: diameter
      :type:  FloatProperty(name='Tool Diameter', default=0.003175, description='Tool bit diameter used in cut operation', min=0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: style
      :type:  EnumProperty(name='Style', items=(('OPEDGE', 'opposite edge', 'place corner overcuts on opposite edges'), ('DOGBONE', 'Dog-bone / Corner Point', 'place overcuts at center of corners'), ('TBONE', 'T-bone', 'place corner overcuts on the same edge')), default='DOGBONE', description='style of overcut to use')


   .. py:attribute:: threshold
      :type:  FloatProperty(name='Max Inside Angle', default=pi / 2, min=-3.14, max=3.14, description='The maximum angle to be considered as an inside corner', precision=4, subtype='ANGLE', unit='ROTATION')


   .. py:attribute:: do_outer
      :type:  BoolProperty(name='Include Outer Curve', description='Include the outer curve if there are curves inside', default=True)


   .. py:attribute:: do_invert
      :type:  BoolProperty(name='Invert', description='invert overcut operation on all curves', default=True)


   .. py:attribute:: otherEdge
      :type:  BoolProperty(name='Other Edge', description='change to the other edge for the overcut to be on', default=False)


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)


   .. py:method:: invoke(context, event)


.. py:class:: CamCurveRemoveDoubles

   Bases: :py:obj:`bpy.types.Operator`


   Curve Remove Doubles


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


   .. py:attribute:: zlimit
      :type:  FloatProperty(name='Z Limit', description='Maximum z height considered for pocket operation, default is 0.0', default=0.0, min=-1000.0, max=1000.0, precision=4, unit='LENGTH')


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)


.. py:class:: CamOffsetSilhouete

   Bases: :py:obj:`bpy.types.Operator`


   Curve Offset Operation


   .. py:attribute:: bl_idname
      :value: 'object.silhouete_offset'



   .. py:attribute:: bl_label
      :value: 'Silhouette & Offset'



   .. py:attribute:: bl_options


   .. py:attribute:: offset
      :type:  FloatProperty(name='Offset', default=0.003, min=-100, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: mitrelimit
      :type:  FloatProperty(name='Mitre Limit', default=2, min=1e-08, max=20, precision=4, unit='LENGTH')


   .. py:attribute:: style
      :type:  EnumProperty(name='Corner Type', items=(('1', 'Round', ''), ('2', 'Mitre', ''), ('3', 'Bevel', '')))


   .. py:attribute:: caps
      :type:  EnumProperty(name='Cap Type', items=(('round', 'Round', ''), ('square', 'Square', ''), ('flat', 'Flat', '')))


   .. py:attribute:: align
      :type:  EnumProperty(name='Alignment', items=(('worldxy', 'World XY', ''), ('bottom', 'Base Bottom', ''), ('top', 'Base Top', '')))


   .. py:attribute:: opentype
      :type:  EnumProperty(name='Curve Type', items=(('dilate', 'Dilate open curve', ''), ('leaveopen', 'Leave curve open', ''), ('closecurve', 'Close curve', '')), default='closecurve')


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: isStraight(geom)


   .. py:method:: execute(context)


   .. py:method:: draw(context)


   .. py:method:: invoke(context, event)


.. py:class:: CamObjectSilhouete

   Bases: :py:obj:`bpy.types.Operator`


   Object Silhouette


   .. py:attribute:: bl_idname
      :value: 'object.silhouete'



   .. py:attribute:: bl_label
      :value: 'Object Silhouette'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)


.. py:class:: CNCCAM_ENGINE

   Bases: :py:obj:`bpy.types.RenderEngine`


   .. py:attribute:: bl_idname
      :value: 'CNCCAM_RENDER'



   .. py:attribute:: bl_label
      :value: 'CNC CAM'



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


.. py:class:: machineSettings

   Bases: :py:obj:`bpy.types.PropertyGroup`


   stores all data for machines


   .. py:attribute:: post_processor
      :type:  EnumProperty(name='Post Processor', items=(('ISO', 'Iso', 'Exports standardized gcode ISO 6983 (RS-274)'), ('MACH3', 'Mach3', 'Default mach3'), ('EMC', 'LinuxCNC - EMC2', 'Linux based CNC control software - formally EMC2'), ('FADAL', 'Fadal', 'Fadal VMC'), ('GRBL', 'grbl', 'Optimized gcode for grbl firmware on Arduino with cnc shield'), ('HEIDENHAIN', 'Heidenhain', 'Heidenhain'), ('HEIDENHAIN530', 'Heidenhain530', 'Heidenhain530'), ('TNC151', 'Heidenhain TNC151', 'Post Processor for the Heidenhain TNC151 machine'), ('SIEGKX1', 'Sieg KX1', 'Sieg KX1'), ('HM50', 'Hafco HM-50', 'Hafco HM-50'), ('CENTROID', 'Centroid M40', 'Centroid M40'), ('ANILAM', 'Anilam Crusader M', 'Anilam Crusader M'), ('GRAVOS', 'Gravos', 'Gravos'), ('WIN-PC', 'WinPC-NC', 'German CNC by Burkhard Lewetz'), ('SHOPBOT MTC', 'ShopBot MTC', 'ShopBot MTC'), ('LYNX_OTTER_O', 'Lynx Otter o', 'Lynx Otter o')), description='Post Processor', default='MACH3')


   .. py:attribute:: use_position_definitions
      :type:  BoolProperty(name='Use Position Definitions', description='Define own positions for op start, toolchange, ending position', default=False)


   .. py:attribute:: starting_position
      :type:  FloatVectorProperty(name='Start Position', default=(0, 0, 0), unit='LENGTH', precision=constants.PRECISION, subtype='XYZ', update=updateMachine)


   .. py:attribute:: mtc_position
      :type:  FloatVectorProperty(name='MTC Position', default=(0, 0, 0), unit='LENGTH', precision=constants.PRECISION, subtype='XYZ', update=updateMachine)


   .. py:attribute:: ending_position
      :type:  FloatVectorProperty(name='End Position', default=(0, 0, 0), unit='LENGTH', precision=constants.PRECISION, subtype='XYZ', update=updateMachine)


   .. py:attribute:: working_area
      :type:  FloatVectorProperty(name='Work Area', default=(0.5, 0.5, 0.1), unit='LENGTH', precision=constants.PRECISION, subtype='XYZ', update=updateMachine)


   .. py:attribute:: feedrate_min
      :type:  FloatProperty(name='Feedrate Minimum /min', default=0.0, min=1e-05, max=320000, precision=constants.PRECISION, unit='LENGTH')


   .. py:attribute:: feedrate_max
      :type:  FloatProperty(name='Feedrate Maximum /min', default=2, min=1e-05, max=320000, precision=constants.PRECISION, unit='LENGTH')


   .. py:attribute:: feedrate_default
      :type:  FloatProperty(name='Feedrate Default /min', default=1.5, min=1e-05, max=320000, precision=constants.PRECISION, unit='LENGTH')


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


   .. py:attribute:: axis4
      :type:  BoolProperty(name='#4th Axis', description='Machine has 4th axis', default=0)


   .. py:attribute:: axis5
      :type:  BoolProperty(name='#5th Axis', description='Machine has 5th axis', default=0)


   .. py:attribute:: eval_splitting
      :type:  BoolProperty(name='Split Files', description='Split gcode file with large number of operations', default=True)


   .. py:attribute:: split_limit
      :type:  IntProperty(name='Operations per File', description='Split files with larger number of operations than this', min=1000, max=20000000, default=800000)


   .. py:attribute:: collet_size
      :type:  FloatProperty(name='#Collet Size', description='Collet size for collision detection', default=33, min=1e-05, max=320000, precision=constants.PRECISION, unit='LENGTH')


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


   .. py:attribute:: output_g43_on_tool_change
      :type:  BoolProperty(name='Output G43 on Tool Change', description='Output G43 on tool change line', default=False)


.. py:class:: CalculatePath

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`cam.async_op.AsyncOperatorMixin`


   Calculate CAM Paths


   .. py:attribute:: bl_idname
      :value: 'object.calculate_cam_path'



   .. py:attribute:: bl_label
      :value: 'Calculate CAM Paths'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:


      Check if the current camera operation is valid.

      This method checks the active camera operation in the given context and
      determines if it is valid. It retrieves the active operation from the
      scene's camera operations and validates it using the `isValid` function.
      If the operation is valid, it returns True; otherwise, it returns False.

      :param context: The context containing the scene and camera operations.
      :type context: Context

      :returns: True if the active camera operation is valid, False otherwise.
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

      Execute the camera operation in the given context.

      This function retrieves the active camera operation from the current
      scene and adds automatic bridges to it. It is typically called within
      the context of a Blender operator to perform specific actions related to
      camera operations.

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

      Execute the camera chain creation in the given context.

      This function adds a new camera chain to the current scene in Blender.
      It updates the active camera chain index and assigns a name and filename
      to the newly created chain. The function is intended to be called within
      a Blender operator context.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the operation's completion status,
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

      Execute the camera chain removal process.

      This function removes the currently active camera chain from the scene
      and decrements the active camera chain index if it is greater than zero.
      It modifies the Blender context to reflect these changes.

      :param context: The context in which the function is executed.

      :returns:

                A dictionary indicating the status of the operation,
                    specifically {'FINISHED'} upon successful execution.
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

      Execute an operation in the active camera chain.

      This function retrieves the active camera chain from the current scene
      and adds a new operation to it. It increments the active operation index
      and assigns the name of the currently selected camera operation to the
      newly added operation. This is typically used in the context of managing
      camera operations in a 3D environment.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the execution status, typically {'FINISHED'}.
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

      Execute the operation to remove the active operation from the camera
      chain.

      This method accesses the current scene and retrieves the active camera
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

      Execute the operation to move the active camera operation in the chain.

      This function retrieves the current scene and the active camera chain.
      If there is an active operation (i.e., its index is greater than 0), it
      moves the operation one step up in the chain by adjusting the indices
      accordingly. After moving the operation, it updates the active operation
      index to reflect the change.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the result of the operation,
                    specifically returning {'FINISHED'} upon successful execution.
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

      Execute the operation to move the active camera operation in the chain.

      This function retrieves the current scene and the active camera chain.
      It checks if the active operation can be moved down in the list of
      operations. If so, it moves the active operation one position down and
      updates the active operation index accordingly.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the result of the operation,
                    specifically {'FINISHED'} when the operation completes successfully.
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

      Execute the camera operation based on the active object in the scene.

      This method retrieves the active object from the Blender context and
      performs operations related to camera settings. It checks if an object
      is selected and retrieves its bounding box dimensions. If no object is
      found, it reports an error and cancels the operation. If an object is
      present, it adds a new camera operation to the scene, sets its
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

      Execute the camera operation in the given context.

      This method handles the execution of camera operations within the
      Blender scene. It first checks if there are any camera operations
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

      Execute the camera operation in the given context.

      This function performs the active camera operation by deleting the
      associated object from the scene. It checks if there are any camera
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

      Execute a camera operation based on the specified direction.

      This method modifies the active camera operation in the Blender context
      based on the direction specified. If the direction is 'UP', it moves the
      active operation up in the list, provided it is not already at the top.
      Conversely, if the direction is not 'UP', it moves the active operation
      down in the list, as long as it is not at the bottom. The method updates
      the active operation index accordingly.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the operation has finished, with
                the key 'FINISHED'.
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

      Execute the camera orientation operation in Blender.

      This function retrieves the active camera operation from the current
      scene, creates an empty object to represent the camera orientation, and
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


   .. py:method:: execute(context)

      Execute the operation in the given context.

      This function sets the Blender object mode to 'OBJECT', retrieves the
      currently selected objects, and calls the `packCurves` function from the
      `pack` module. It is typically used to finalize operations on selected
      objects in Blender.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the completion status of the operation.
      :rtype: dict



   .. py:method:: draw(context)


.. py:class:: CamSliceObjects

   Bases: :py:obj:`bpy.types.Operator`


   Slice a Mesh Object Horizontally


   .. py:attribute:: bl_idname
      :value: 'object.cam_slice_objects'



   .. py:attribute:: bl_label
      :value: 'Slice Object - Useful for Lasercut Puzzles etc'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)

      Execute the slicing operation on the active Blender object.

      This function retrieves the currently active object in the Blender
      context and performs a slicing operation on it using the `sliceObject`
      function from the `cam` module. The operation is intended to modify the
      object based on the slicing logic defined in the external module.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the result of the operation,
                    typically containing the key 'FINISHED' upon successful execution.
      :rtype: dict



   .. py:method:: draw(context)


.. py:class:: CAMSimulate

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`cam.async_op.AsyncOperatorMixin`


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


      Execute an asynchronous simulation operation based on the active camera
      operation.

      This method retrieves the current scene and the active camera operation.
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

      Draws the user interface for selecting camera operations.

      This method creates a layout element in the user interface that allows
      users to search and select a specific camera operation from a list of
      available operations defined in the current scene. It utilizes the
      Blender Python API to integrate with the UI.

      :param context: The context in which the drawing occurs, typically
                      provided by Blender's UI system.



.. py:class:: CAMSimulateChain

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`cam.async_op.AsyncOperatorMixin`


   Simulate CAM Chain, Compared to Single Op Simulation Just Writes Into One Image and Thus Enables
   to See how Ops Work Together.


   .. py:attribute:: bl_idname
      :value: 'object.cam_simulate_chain'



   .. py:attribute:: bl_label
      :value: 'CAM Simulation'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:


      Check the validity of the active camera chain in the scene.

      This method retrieves the currently active camera chain from the scene's
      camera chains and checks its validity using the `isChainValid` function.
      It returns a boolean indicating whether the active camera chain is
      valid.

      :param context: The context containing the scene and its properties.
      :type context: object

      :returns: True if the active camera chain is valid, False otherwise.
      :rtype: bool



   .. py:attribute:: operation
      :type:  StringProperty(name='Operation', description='Specify the operation to calculate', default='Operation')


   .. py:method:: execute_async(context)
      :async:


      Execute an asynchronous simulation for a specified camera chain.

      This method retrieves the active camera chain from the current Blender
      scene and determines the operations associated with that chain. It
      checks if all operations are valid and can be simulated. If valid, it
      proceeds to execute the simulation asynchronously. If any operation is
      invalid, it logs a message and returns a finished status without
      performing the simulation.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the status of the operation, either
                operation completed successfully.
      :rtype: dict



   .. py:method:: draw(context)

      Draw the user interface for selecting camera operations.

      This function creates a user interface element that allows the user to
      search and select a specific camera operation from a list of available
      operations in the current scene. It utilizes the Blender Python API to
      create a property search layout.

      :param context: The context in which the drawing occurs, typically containing
                      information about the current scene and UI elements.



.. py:class:: KillPathsBackground

   Bases: :py:obj:`bpy.types.Operator`


   Remove CAM Path Processes in Background.


   .. py:attribute:: bl_idname
      :value: 'object.kill_calculate_cam_paths_background'



   .. py:attribute:: bl_label
      :value: 'Kill Background Computation of an Operation'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)

      Execute the camera operation in the given context.

      This method retrieves the active camera operation from the scene and
      checks if there are any ongoing processes related to camera path
      calculations. If such processes exist and match the current operation,
      they are terminated. The method then marks the operation as not
      computing and returns a status indicating that the execution has
      finished.

      :param context: The context in which the operation is executed.

      :returns: A dictionary with a status key indicating the result of the execution.
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

      Execute camera operations in the current Blender context.

      This function iterates through the camera operations defined in the
      current scene and executes the background calculation for each
      operation. It sets the active camera operation index and prints the name
      of each operation being processed. This is typically used in a Blender
      add-on or script to automate camera path calculations.

      :param context: The current Blender context.
      :type context: bpy.context

      :returns:

                A dictionary indicating the completion status of the operation,
                    typically {'FINISHED'}.
      :rtype: dict



   .. py:method:: draw(context)

      Draws the user interface elements for the operation selection.

      This method utilizes the Blender layout system to create a property
      search interface for selecting operations related to camera
      functionalities. It links the current instance's operation property to
      the available camera operations defined in the Blender scene.

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

      Execute the camera operation in the background.

      This method initiates a background process to perform camera operations
      based on the current scene and active camera operation. It sets up the
      necessary paths for the script and starts a subprocess to handle the
      camera computations. Additionally, it manages threading to ensure that
      the main thread remains responsive while the background operation is
      executed.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the completion status of the operation.
      :rtype: dict



.. py:class:: PathsChain

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`cam.async_op.AsyncOperatorMixin`


   Calculate a Chain and Export the G-code Alltogether.


   .. py:attribute:: bl_idname
      :value: 'object.calculate_cam_paths_chain'



   .. py:attribute:: bl_label
      :value: 'Calculate CAM Paths in Current Chain and Export Chain G-code'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:


      Check the validity of the active camera chain in the given context.

      This method retrieves the active camera chain from the scene and checks
      its validity using the `isChainValid` function. It returns a boolean
      value indicating whether the camera chain is valid or not.

      :param context: The context containing the scene and camera chain information.
      :type context: Context

      :returns: True if the active camera chain is valid, False otherwise.
      :rtype: bool



   .. py:method:: execute_async(context)
      :async:


      Execute asynchronous operations for camera path calculations.

      This method sets the object mode for the Blender scene and processes a
      series of camera operations defined in the active camera chain. It
      reports the progress of each operation and handles any exceptions that
      may occur during the path calculation. After successful calculations, it
      exports the resulting mesh data to a specified G-code file.

      :param context: The Blender context containing scene and
      :type context: bpy.context

      :returns: A dictionary indicating the result of the operation,
                typically {'FINISHED'}.
      :rtype: dict



.. py:class:: PathExport

   Bases: :py:obj:`bpy.types.Operator`


   Export G-code. Can Be Used only when the Path Object Is Present


   .. py:attribute:: bl_idname
      :value: 'object.cam_export'



   .. py:attribute:: bl_label
      :value: 'Export Operation G-code'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)

      Execute the camera operation and export the G-code path.

      This method retrieves the active camera operation from the current scene
      and exports the corresponding G-code path to a specified filename. It
      prints the filename and relevant operation details to the console for
      debugging purposes. The G-code path is generated based on the camera
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


      Check the validity of the active camera chain in the given context.

      This method retrieves the currently active camera chain from the scene
      context and checks its validity using the `isChainValid` function. It
      returns a boolean indicating whether the active camera chain is valid or
      not.

      :param context: The context containing the scene and camera chain information.
      :type context: object

      :returns: True if the active camera chain is valid, False otherwise.
      :rtype: bool



   .. py:method:: execute(context)

      Execute the camera path export process.

      This function retrieves the active camera chain from the current scene
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



.. py:function:: timer_update(context)

   Monitor background processes related to camera path calculations.

   This function checks the status of background processes that are
   responsible for calculating camera paths. It retrieves the current
   processes and monitors their state. If a process has finished, it
   updates the corresponding camera operation and reloads the necessary
   paths. If the process is still running, it restarts the associated
   thread to continue monitoring.

   :param context: The context in which the function is called, typically
                   containing information about the current scene and operations.


.. py:class:: PackObjectsSettings

   Bases: :py:obj:`bpy.types.PropertyGroup`


   stores all data for machines


   .. py:attribute:: sheet_fill_direction
      :type:  EnumProperty(name='Fill Direction', items=(('X', 'X', 'Fills sheet in X axis direction'), ('Y', 'Y', 'Fills sheet in Y axis direction')), description='Fill direction of the packer algorithm', default='Y')


   .. py:attribute:: sheet_x
      :type:  FloatProperty(name='X Size', description='Sheet size', min=0.001, max=10, default=0.5, precision=constants.PRECISION, unit='LENGTH')


   .. py:attribute:: sheet_y
      :type:  FloatProperty(name='Y Size', description='Sheet size', min=0.001, max=10, default=0.5, precision=constants.PRECISION, unit='LENGTH')


   .. py:attribute:: distance
      :type:  FloatProperty(name='Minimum Distance', description='Minimum distance between objects(should be at least cutter diameter!)', min=0.001, max=10, default=0.01, precision=constants.PRECISION, unit='LENGTH')


   .. py:attribute:: tolerance
      :type:  FloatProperty(name='Placement Tolerance', description='Tolerance for placement: smaller value slower placemant', min=0.001, max=0.02, default=0.005, precision=constants.PRECISION, unit='LENGTH')


   .. py:attribute:: rotate
      :type:  BoolProperty(name='Enable Rotation', description='Enable rotation of elements', default=True)


   .. py:attribute:: rotate_angle
      :type:  FloatProperty(name='Placement Angle Rotation Step', description='Bigger rotation angle, faster placemant', default=0.19635 * 4, min=pi / 180, max=pi, precision=5, subtype='ANGLE', unit='ROTATION')


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
      :value: ['d.post_processor', 's.system', 'd.use_position_definitions', 'd.starting_position',...



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
      :value: ['from pathlib import Path', 'bpy.ops.scene.cam_operation_add()', 'scene = bpy.context.scene',...



   .. py:attribute:: preset_values
      :value: ['o.info.duration', 'o.info.chipload', 'o.info.warnings', 'o.material.estimate_from_model',...



   .. py:attribute:: preset_subdir
      :value: 'cam_operations'



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



.. py:class:: CAM_OPERATION_MT_presets

   Bases: :py:obj:`bpy.types.Menu`


   .. py:attribute:: bl_label
      :value: 'Operation Presets'



   .. py:attribute:: preset_subdir
      :value: 'cam_operations'



   .. py:attribute:: preset_operator
      :value: 'script.execute_preset'



   .. py:attribute:: draw


.. py:class:: SliceObjectsSettings

   Bases: :py:obj:`bpy.types.PropertyGroup`


   Stores All Data for Machines


   .. py:attribute:: slice_distance
      :type:  FloatProperty(name='Slicing Distance', description='Slices distance in z, should be most often thickness of plywood sheet.', min=0.001, max=10, default=0.005, precision=constants.PRECISION, unit='LENGTH')


   .. py:attribute:: slice_above0
      :type:  BoolProperty(name='Slice Above 0', description='only slice model above 0', default=False)


   .. py:attribute:: slice_3d
      :type:  BoolProperty(name='3D Slice', description='For 3D carving', default=False)


   .. py:attribute:: indexes
      :type:  BoolProperty(name='Add Indexes', description='Adds index text of layer + index', default=True)


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


.. py:function:: check_operations_on_load(context)

   Checks for any broken computations on load and resets them.

   This function verifies the presence of necessary Blender add-ons and
   installs any that are missing. It also resets any ongoing computations
   in camera operations and sets the interface level to the previously used
   level when loading a new file. If the add-on has been updated, it copies
   the necessary presets from the source to the target directory.
   Additionally, it checks for updates to the camera plugin and updates
   operation presets if required.

   :param context: The context in which the function is executed, typically containing
                   information about
                   the current Blender environment.


.. py:function:: updateOperation(self, context)

   Update the visibility and selection state of camera operations in the
   scene.

   This method manages the visibility of objects associated with camera
   operations based on the current active operation. If the
   'hide_all_others' flag is set to true, it hides all other objects except
   for the currently active one. If the flag is false, it restores the
   visibility of previously hidden objects. The method also attempts to
   highlight the currently active object in the 3D view and make it the
   active object in the scene.

   :param context: The context containing the current scene and
   :type context: bpy.types.Context


.. py:data:: classes

.. py:function:: register() -> None

.. py:function:: unregister() -> None

