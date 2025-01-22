===========
Code Overview
===========
Fabex (formerly BlenderCAM) code can be broken down into categories:

1. Core Functions
2. Extra Functions
3. Reference Files
4. User Interface
5. Dependencies

Core Functions
****************
The core function of the Fabex addon is to take whatever object is in the viewport and generate toolpaths along that object according to a milling strategy set by the user.

These operations can be exported alone, or combined into chains to be exported and run together.

Extra Functions
*****************
Beyond simply creating toolpaths for existing objects, Fabex can also create the objects (curves) and edit them through a number of operations.

There are modules dedicated to creating reliefs, joinery, puzzle joinery and gears.

There is also a simulation module to allow a preview of what the final product will look like, as well as an asynchronous module that allows progress reports on calculations.

Reference Files
******************
Presets for machines, tools, operations and post-processors.

User Interface
****************
Files related to Blender's UI - panels, menus, pie menus, popup dialogs etc.

Dependencies
***************
Python wheels - executable binaries packed in for all supported systems.

Complete Addon Layout
***********************

::

scripts/addons/
└── cam/
    ├── operators/
    │   ├── __init__.py
    │   ├── async_op.py
    │   ├── bas_relief_op.py
    │   ├── bridges_op.py
    │   ├── chain_ops.py
    │   ├── curve_create_ops.py
    │   ├── curve_equation_ops.py
    │   ├── curve_tools_ops.py
    │   ├── gcode_import_op.py
    │   ├── operation_ops.py
    │   ├── orient_op.py
    │   ├── pack_op.py
    │   ├── path_ops.py
    │   ├── position_op.py
    │   ├── preset_ops.py
    │   ├── simulation_ops.py
    │   └── slice_op.py
    ├── post_processors/
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
    ├── properties/
    │   ├── __init__.py
    │   ├── chain_props.py
    │   ├── info_props.py
    │   ├── interface_props.py
    │   ├── machine_props.py
    │   ├── material_props.py
    │   ├── movement_props.py
    │   ├── operation_props.py
    │   └── optimisation_props.py
    ├── tests/
    │   ├── test_data
    │   ├── TESTING_PROCEDURE
    │   ├── gcode_generator.py
    │   ├── install_addon.py
    │   └── test_suite.py
    ├── ui/
    │   ├── icons/
    │   │   ├── __init__.py
    │   │   ├── BallconeIcon.png
    │   │   ├── BallnoseIcon.png
    │   │   ├── BullnoseIcon.png
    │   │   ├── CylinderConeIcon.png
    │   │   ├── EnMillIcon.png
    │   │   ├── FabexCNC_Logo.png
    │   │   ├── LaserPlasmaIcon.png
    │   │   └── VCarveIcon.png
    │   ├── menus/
    │   │   ├── curve_creators.py
    │   │   ├── curve_tools.py
    │   │   ├── import_gcode.py
    │   │   ├── preset_menus.py
    │   │   └── viewport.py
    │   ├── panels/
    │   │   ├── __init__.py
    │   │   ├── area_panel.py
    │   │   ├── basrelief.py
    │   │   ├── blank_panel.py
    │   │   ├── chains_panel.py
    │   │   ├── curve_create_panel.py
    │   │   ├── curve_tools_panel.py
    │   │   ├── cutter_panel.py
    │   │   ├── feedrate_panel.py
    │   │   ├── gcode_panel.py
    │   │   ├── info_panel.py
    │   │   ├── machine_panel.py
    │   │   ├── material_panel.py
    │   │   ├── movement_panel.py
    │   │   ├── op_properties_panel.py
    │   │   ├── operations_panel.py
    │   │   ├── optimisation_panel.py
    │   │   ├── pack_panel.py
    │   │   ├── parent_panel.py
    │   │   ├── popup_panel.py
    │   │   └── slice_panel.py
    │   ├── pie_menu/
    │   │   ├── pie_cam.py
    │   │   ├── pie_chains.py
    │   │   ├── pie_operation.py
    │   │   └── pie_pack_slice_relief.py
    │   └── __init__.py
    ├── utilities/
    │   ├── __init__.py
    │   ├── addon_utils.py
    │   ├── async_utils.py
    │   ├── bounds_utils.py
    │   ├── chunk_utils.py
    │   ├── compare_utils.py
    │   ├── dict_utils.py
    │   ├── geom_utils.py
    │   ├── image_utils.py
    │   ├── index_utils.py
    │   ├── loop_utils.py
    │   ├── machine_utils.py
    │   ├── material_utils.py
    │   ├── numba_utils.py
    │   ├── ocl_utils.py
    │   ├── operation_utils.py
    │   ├── orient_utils.py
    │   ├── shapely_utils.py
    │   ├── simple_utils.py
    │   ├── strategy_utils.py
    │   ├── thread_utils.py
    │   └── version_utils.py
    ├── wheels/
    │   ├── opencamlib-2023.1.11-cp311-cp311-macosx_10_9_x86_64.whl
    │   ├── opencamlib-2023.1.11-cp311-cp311-macosx_11_0_arm64.whl
    │   ├── opencamlib-2023.1.11-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
    │   ├── opencamlib-2023.1.11-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
    │   ├── opencamlib-2023.1.11-cp311-cp311-win32.whl
    │   ├── opencamlib-2023.1.11-cp311-cp311-win_amd64.whl
    │   ├── shapely-2.0.5-cp311-cp311-macosx_10_9_x86_64.whl
    │   ├── shapely-2.0.5-cp311-cp311-macosx_11_0_arm64.whl
    │   ├── shapely-2.0.5-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
    │   ├── shapely-2.0.5-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
    │   ├── shapely-2.0.5-cp311-cp311-win32.whl
    │   └── shapely-2.0.5-cp311-cp311-win_amd64.whl
    ├── __init__.py
    ├── bas_relief.py
    ├── blender_manifest.toml
    ├── bridges.py
    ├── cam_chunk.py
    ├── collision.py
    ├── constants.py
    ├── engine.py
    ├── exception.py
    ├── gcode_import_parser.py
    ├── gcode_path.py
    ├── involute_gear.py
    ├── joinery.py
    ├── pack.py
    ├── parametric.py
    ├── pattern.py
    ├── preferences.py
    ├── puzzle_joinery.py
    ├── simulation.py
    ├── slice.py
    ├── strategy.py
    ├── testing.py
    ├── version.py
    └── voronoi.py
