# Code Overview

**Fabex** *(formerly BlenderCAM)* code can be broken down into categories:

1. **Core Functions**
2. **Extra Functions**
3. **Utility Functions**
4. **Blender Files**
5. **Reference Files**
6. **Dependencies**

## Core Functions
The core function of **Fabex** is to take the active object in the viewport, generate toolpaths along that object according to a milling strategy set by the user, and export that path as Gcode so that it can be run on a CNC machine.

These Operations can be exported alone, or combined into Chains to be exported and run together.

**Core Functions** can be found in:
- `cam_chunk` - breaks paths into chunks and layers for calculation
- `collision` - sweep collision functions for cutter tip positioning 
- `constants` - static values for precision, offsets, etc
- `exception` - handles CAM-related exceptions
- `gcode_import_parser` - builds toolpaths from imported Gcode files
- `gcode_path` - builds and exports toolpaths using functions from `pattern` and `strategy`
- `pattern` - build path patterns for various milling strategies
- `strategy` - milling strategy function definitions - how each strategy is calculated

```{note}
Although there is a file called `engine`, it is not actually part of the Core functionality, and mostly functions as a way to collect and register the UI panels that will be shown when **Fabex** is activated.
```

## Extra Functions
Beyond simply creating toolpaths for existing objects, **Fabex** can also create objects and edit them a number of ways.

There are modules dedicated to creating Reliefs, Joinery, Puzzle Joinery and Gears.

There is also a Simulation module to allow a preview of what the finished Operation will look like.

**Extra Functions** can be found in:
- `bas_relief` - generate a Relief mesh using **Blender**'s Camera
- `bridges` - generate and place Bridges / Tabs for Cutout Operations
- `involute_gear` - generate a customizable Rack or Pinion Gear curve
- `joinery` - create mortise, twist, finger, etc. joints
- `pack` - arrange curves on a sheet for bulk cutting
- `parametric` - creates curves with input functions
- `puzzle_joinery` - create jigsaw puzzle joints
- `simulation` - generate a mesh preview of the result of the selected toolpath
- `slice` - cut objects into vertical slices
- `testing` - test function definitions for the Test Suite
- `voronoi` - generate [Voronoi](https://en.wikipedia.org/wiki/Voronoi_diagram) tesselations

## Utility Functions
Utilities are generally low-level, depend only on external code (no local imports), and power Core and Extra functions as well as some Blender-specific functionality.

**Utility Functions** can be found in the `utilities/` folder, and have been broken down into files containing related functions:
- `addon_utils` - check and load dependencies, presets, keymaps and UI
- `async_utils` - asynchronous function for non-blocking updates
- `bounds_utils` - get and update bounding boxes in worldspace
- `chunk_utils` - low-level CAM chunk-related functions
- `compare_utils` - basic comparisons - equal, overlapping etc.
- `dict_utils` - simple Python dict functions
- `geom_utils` - define or create simple geometry
- `image_utils` - image creation, conversion and manipulation
- `index_utils` - related to Indexing Operations - multi-sided jobs
- `loop_utils` - add or remove nested loops
- `machine_utils` - add or update the **CAM_Machine** area object
- `material_utils` - add or update the **CAM_Material** object
- `numba_utils` - add or bypass `numba` acceleration, if available
- `ocl_utils` - `opencamlib` library helpers
- `operation_utils` - add, update, sort Operations and Chains
- `orient_utils` - add or convert Orientation objects
- `shapely_utils` - `shapely` library helpers
- `simple_utils` - select, delete, duplicate, rename etc.
- `strategy_utils` - update available strategies
- `thread_utils` - monitor threads for CAM updates
- `version_utils` - get and set the Extension version

## Reference Files
Reference files contain pre-defined data that can be quickly loaded into Blender, including Gcode Post-Processors that will translate a generic CAM toolpath into instructions specific to your CNC machine, presets for Machines, compatible cutting tools and Operations.

**Reference Files** can be found in the folders:
- `post_processors/` - all currently available Gcode Post-Processors
- `presets/` - Machine, Cutter, Operation preset files
- `tests/` - an automated suite to ensure consistent calculations and output

And the files:
- `testing` - test function definitions
- `version` - Extension version

## Blender Files
All the functionality and data listed above needs to be connecetd to **Blender**.

This is done by registering `PropertyGroups` that contain all the data for our CNC machine and Operations, passing that to Operators that can calculate that data, and exposing those Operators as buttons and controls in the User Interface.

**Blender Files** can be found in the folders:
- `properties/`
- `operators/`
- `ui/`

And also include the `blender_manifest.toml` file, which defines the Extension name, author(s), website, license, tags, wheels etc, and is read by **Blender** when you install **Fabex**.

### Properties
Properties allow you to store data in your **Blender** Scene or Object.
- `chain_props` - CAM Chain-related data
- `info_props` - Info Panel data, like Estimates
- `interface_props` - UI Layout data and callback functions
- `machine_props` - Machine Panel data - your CNC Machine settings
- `material_props` - Stock material-related settings
- `movement_props` - Movement Panel data, like Climb vs Conventional cut
- `operation_props` - all Operation data not covered elsewhere
- `optimisation_props` - Optimisation Panel data, like Path Point reduction

### Operators
Python functions need to be wrapped in a **Blender** Operator to be stored and called in **Blender**.
- `async_op` - asynchronous Operator Mixin class for non-blocking updates
- `bas_relief_ops` - create a Bas Relief mesh from a **Blender** Camera
- `bridges_op` - generate and place Bridges / Tabs for Cutout Operations
- `chain_ops` - add, remove, sort CAM Chains
- `curve_create_ops` - add Sign Plate, Drawer, Mortise, Interlock, Puzzle Joint, Gear objects
- `curve_equation_ops`- add Periodic, Lissajous, Hypotrochoid and Custom Curve objects
- `curve_tools_ops` - Boolean, Convex Hull, Intarsion, Overcuts, Remove Doubles, and Pocket Surfaces
- `gcode_import_op` - creates a toolpath object from an imported Gcode file
- `orient_op` - add Orientation object
- `pack_op` - pack curves on sheet
- `path_ops` - create, chain, calculate, export toolpaths
- `position_op` - position Stock material within Machine Work Area
- `preset_ops` - execute Preset files
- `simulation_ops` - simulate the selected toolpath
- `slice_op` - slice the selected object into a series of curves

### User Interface
Files related to **Blender**'s User Interface (aka UI) are found in the `ui` folder, which has been broken down into sub-folders for easier management:
- `icons/` - custom .png icon images
- `menus/` - the **Fabex CNC** menu in the 3D viewport, and sub-menus
- `panels/` - the main **Fabex** interface
- `pie_menu/` - the Pie Menu system, called with `Alt+C`

## Dependencies
Python wheels - executable binaries packed in for all supported systems.
- `opencamlib`
- `shapely`

```{note}
The wheels are for Python version 3.11, and will not work with other Python versions
```

## Complete Addon Layout
```
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
```