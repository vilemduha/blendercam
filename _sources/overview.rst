===========
Overview
===========
BlenderCAM's code can be broken down into categories:

1. Core Functions
2. Extra Functions
3. Reference Files
4. User Interface
5. Dependencies

Core Functions
==============
The core function of the BlenderCAM addon is to take whatever object is in the viewport and generate toolpaths along that object according to a milling strategy set by the user.
These operations can be exported alone, or combined into chains to be exported and run together.

Extra Functions
===============
Beyond simply creating toolpaths for existing objects, BlenderCAM can also create the objects (curves) and edit them through a number of operations.

There are modules dedicated to creating reliefs, joinery, puzzle joinery and gears.

There is also a simulation module to allow a preview of what the final product will look like, as well as an asynchronous module that allows progress reports on calculations.

Reference Files
===============
Presets for machines, tools, operations and preprocessors comprise the majority of the files in the addon.

User Interface
==============
Files related to Blender's UI - all the panels, buttons etc that you can click on in the addon, as well as menus, pie menus, popup dialogs etc.

Dependencies
============
Python wheels - executable binaries packed in for all supported systems.

Complete Addon Layout
---------------------

::

  cam/
  ├── nc/
  │   ├── LICENSE
  │   ├── __init__.py
  │   ├── anilam_crusader_m.py
  │   ├── anilam_crusader_m_read.py
  │   ├── attach.py
  │   ├── cad_iso_read.py
  │   ├── cad_nc_read.py
  │   ├── cad_read.py
  │   ├── centroid1.py
  │   ├── centroid1_read.py
  │   ├── drag_knife.py
  │   ├── emc2.py
  │   ├── emc2_read.py
  │   ├── emc2b.py
  │   ├── emc2b_crc.py
  │   ├── emc2b_crc_read.py
  │   ├── emc2b_read.py
  │   ├── emc2tap.py
  │   ├── emc2tap_read.py
  │   ├── fadal.py
  │   ├── format.py
  │   ├── gantry_router.py
  │   ├── gantry_router_read.py
  │   ├── gravos.py
  │   ├── grbl.py
  │   ├── heiden.py
  │   ├── heiden530.py
  │   ├── heiden_read.py
  │   ├── hm50.py
  │   ├── hm50_read.py
  │   ├── hpgl2d.py
  │   ├── hpgl2d_read.py
  │   ├── hpgl2dv.py
  │   ├── hpgl2dv_read.py
  │   ├── hpgl3d.py
  │   ├── hpgl3d_read.py
  │   ├── hxml_writer.py
  │   ├── iso.py
  │   ├── iso_codes.py
  │   ├── iso_crc.py
  │   ├── iso_crc_read.py
  │   ├── iso_modal.py
  │   ├── iso_modal_read.py
  │   ├── iso_read.py
  │   ├── lathe1.py
  │   ├── lathe1_read.py
  │   ├── lynx_otter_o.py
  │   ├── mach3.py
  │   ├── mach3_read.py
  │   ├── machines.txt
  │   ├── makerbotHBP.py
  │   ├── makerbotHBP_read.py
  │   ├── makerbot_codes.py
  │   ├── nc.py
  │   ├── nc_read.py
  │   ├── nclathe_read.py
  │   ├── num_reader.py
  │   ├── printbot3d.py
  │   ├── printbot3d_read.py
  │   ├── recreator.py
  │   ├── rez2.py
  │   ├── rez2_read.py
  │   ├── series1.py
  │   ├── series1_read.py
  │   ├── shopbot_mtc.py
  │   ├── siegkx1.py
  │   ├── siegkx1_read.py
  │   ├── tnc151.py
  │   ├── tnc151_read.py
  │   └── winpc.py
  ├── opencamlib/
  │   ├── __init__.py
  │   ├── oclSample.py
  │   ├── opencamlib.py
  │   └── opencamlib_readme.txt
  ├── pie_menu/
  │   ├── active_op/
  │   │   ├── pie_area.py
  │   │   ├── pie_cutter.py
  │   │   ├── pie_feedrate.py
  │   │   ├── pie_gcode.py
  │   │   ├── pie_movement.py
  │   │   ├── pie_operation.py
  │   │   └── pie_setup.py
  │   ├── pie_cam.py
  │   ├── pie_chains.py
  │   ├── pie_curvecreators.py
  │   ├── pie_curvetools.py
  │   ├── pie_info.py
  │   ├── pie_machine.py
  │   ├── pie_material.py
  │   └── pie_pack_slice_relief.py
  ├── presets/
  │   ├── cam_cutters/
  │   │   ├── BALLCONE_1.00mm.py
  │   │   ├── ball_1.00mm.py
  │   │   ├── ball_1.50mm.py
  │   │   ├── ball_10.00mm.py
  │   │   ├── ball_12.00mm.py
  │   │   ├── ball_16.00mm.py
  │   │   ├── ball_2.00mm.py
  │   │   ├── ball_2.50mm.py
  │   │   ├── ball_20.00mm.py
  │   │   ├── ball_3.00mm.py
  │   │   ├── ball_3.50mm.py
  │   │   ├── ball_4.00mm.py
  │   │   ├── ball_5.00mm.py
  │   │   ├── ball_6.00mm.py
  │   │   ├── ball_7.00mm.py
  │   │   ├── ball_8.00mm.py
  │   │   ├── end_cyl_1.00mm.py
  │   │   ├── end_cyl_1.50mm.py
  │   │   ├── end_cyl_10.00mm.py
  │   │   ├── end_cyl_12.00mm.py
  │   │   ├── end_cyl_16.00mm.py
  │   │   ├── end_cyl_2.00mm.py
  │   │   ├── end_cyl_2.50mm.py
  │   │   ├── end_cyl_20.00mm.py
  │   │   ├── end_cyl_3.00mm.py
  │   │   ├── end_cyl_3.50mm.py
  │   │   ├── end_cyl_4.00mm.py
  │   │   ├── end_cyl_5.00mm.py
  │   │   ├── end_cyl_6.00mm.py
  │   │   ├── end_cyl_7.00mm.py
  │   │   ├── end_cyl_8.00mm.py
  │   │   ├── v-carve_3mm_45deg.py
  │   │   ├── v-carve_3mm_60deg.py
  │   │   ├── v-carve_6mm_45deg.py
  │   │   └── v-carve_6mm_60deg.py
  │   ├── cam_machines/
  │   │   ├── emc_test_2.py
  │   │   └── kk1000s.py
  │   └── cam_operations/
  │       ├── Fin_Ball_3,0_Block_All.py
  │       ├── Fin_Ball_3,0_Block_Around.py
  │       ├── Fin_Ball_3,0_Circles_All_EXPERIMENTAL.py
  │       ├── Fin_Ball_3,0_Circles_Around_EXPERIMENTAL.py
  │       ├── Fin_Ball_3,0_Cross_All.py
  │       ├── Fin_Ball_3,0_Cross_Around.py
  │       ├── Fin_Ball_3,0_Cutout.py
  │       ├── Fin_Ball_3,0_Outline_Fill_EXPERIMENTAL.py
  │       ├── Fin_Ball_3,0_Parallel_All.py
  │       ├── Fin_Ball_3,0_Parallel_Around.py
  │       ├── Fin_Ball_3,0_Pencil_EXPERIMENTAL.py
  │       ├── Fin_Ball_3,0_Pocket_EXPERIMENTAL.py
  │       ├── Fin_Ball_3,0_Spiral_All.py
  │       ├── Fin_Ball_3,0_Spiral_Around.py
  │       ├── Finishing_3mm_ballnose.py
  │       ├── Rou_Ball_3,0_Block_All.py
  │       ├── Rou_Ball_3,0_Block_Around.py
  │       ├── Rou_Ball_3,0_Circles_All_EXPERIMENTAL.py
  │       ├── Rou_Ball_3,0_Circles_Around_EXPERIMENTAL.py
  │       ├── Rou_Ball_3,0_Cross_All.py
  │       ├── Rou_Ball_3,0_Cross_Around.py
  │       ├── Rou_Ball_3,0_Cutout.py
  │       ├── Rou_Ball_3,0_Outline_Fill_EXPERIMENTAL.py
  │       ├── Rou_Ball_3,0_Parallel_All.py
  │       ├── Rou_Ball_3,0_Parallel_Around.py
  │       ├── Rou_Ball_3,0_Pencil_EXPERIMENTAL.py
  │       ├── Rou_Ball_3,0_Pocket_EXPERIMENTAL.py
  │       ├── Rou_Ball_3,0_Spiral_All.py
  │       └── Rou_Ball_3,0_Spiral_Around.py
  ├── tests/
  │   ├── test_data
  │   ├── TESTING_PROCEDURE
  │   ├── gcode_generator.py
  │   ├── install_addon.py
  │   └── test_suite.py
  └── ui_panels/
      ├── __init__.py
      ├── area.py
      ├── buttons_panel.py
      ├── chains.py
      ├── cutter.py
      ├── feedrate.py
      ├── gcode.py
      ├── info.py
      ├── interface.py
      ├── machine.py
      ├── material.py
      ├── movement.py
      ├── op_properties.py
      ├── operations.py
      ├── optimisation.py
      ├── pack.py
      └── slice.py
  LICENSE
  __init__.py
  async_op.py
  autoupdate.py
  backgroundop_.py
  basrelief.py
  bridges.py
  cam_chunk.py
  cam_operation.py
  chain.py
  collision.py
  constants.py
  curvecamcreate.py
  curvecamequation.py
  curvecamtools.py
  engine.py
  exception.py
  gcodeimportparser.py
  gcodepath.py
  image_utils.py
  involute_gear.py
  joinery.py
  machine_settings.py
  numba_wrapper.py
  ops.py
  pack.py
  parametric.py
  pattern.py
  polygon_utils_cam.py
  preferences.py
  preset_managers.py
  puzzle_joinery.py
  simple.py
  simulation.py
  slice.py
  strategy.py
  testing.py
  ui.py
  utils.py
  version.py
  voronoi.py
