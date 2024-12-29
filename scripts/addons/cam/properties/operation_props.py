"""Fabex 'cam_operation.py'

All properties of a single CAM Operation.
"""

from math import pi

import numpy
from shapely import geometry as sgeometry

from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import PropertyGroup
from ..constants import PRECISION
from ..utilities.strategy_utils import (
    get_strategy_list,
    update_strategy,
    update_cutout,
)
from ..utilities.operation_utils import (
    operation_valid,
    update_operation,
    update_bridges,
    update_chipload,
    update_offset_image,
    update_operation_valid,
    update_rest,
    update_rotation,
    update_Z_buffer_image,
    update_image_size_y,
)
from .info_props import CAM_INFO_Properties
from .material_props import CAM_MATERIAL_Properties
from .movement_props import CAM_MOVEMENT_Properties
from .optimisation_props import CAM_OPTIMISATION_Properties


class CAM_OPERATION_Properties(PropertyGroup):
    #######################
    # Imported Properties #
    #######################

    material: PointerProperty(type=CAM_MATERIAL_Properties)
    info: PointerProperty(type=CAM_INFO_Properties)
    optimisation: PointerProperty(type=CAM_OPTIMISATION_Properties)
    movement: PointerProperty(type=CAM_MOVEMENT_Properties)

    ########################
    # Property Definitions #
    ########################

    name: StringProperty(
        name="Operation Name",
        default="Operation",
        update=update_rest,
    )
    filename: StringProperty(
        name="File Name",
        default="Operation",
        update=update_rest,
    )
    auto_export: BoolProperty(
        name="Auto Export",
        description="Export files immediately after path calculation",
        default=True,
    )
    remove_redundant_points: BoolProperty(
        name="Simplify G-code",
        description="Remove redundant points sharing the same angle" " as the start vector",
        default=False,
    )
    simplify_tolerance: IntProperty(
        name="Tolerance",
        description="lower number means more precise",
        default=50,
        min=1,
        max=1000,
    )
    hide_all_others: BoolProperty(
        name="Hide All Others",
        description="Hide all other tool paths except toolpath"
        " associated with selected CAM operation",
        default=False,
    )
    parent_path_to_object: BoolProperty(
        name="Parent Path to Object",
        description="Parent generated CAM path to source object",
        default=False,
    )
    object_name: StringProperty(
        name="Object",
        description="Object handled by this operation",
        update=update_operation_valid,
    )
    collection_name: StringProperty(
        name="Collection",
        description="Object collection handled by this operation",
        update=update_operation_valid,
    )
    curve_source: StringProperty(
        name="Curve Source",
        description="Curve which will be sampled along the 3D object",
        update=operation_valid,
    )
    curve_target: StringProperty(
        name="Curve Target",
        description="Curve which will serve as attractor for the "
        "cutter when the cutter follows the curve",
        update=operation_valid,
    )
    source_image_name: StringProperty(
        name="Image Source",
        description="image source",
        update=operation_valid,
    )
    geometry_source: EnumProperty(
        name="Data Source",
        items=(
            ("OBJECT", "Object", "a"),
            ("COLLECTION", "Collection of Objects", "a"),
            ("IMAGE", "Image", "a"),
        ),
        description="Geometry source",
        default="OBJECT",
        update=update_operation_valid,
    )
    cutter_type: EnumProperty(
        name="Cutter",
        items=(
            ("END", "End", "End - Flat cutter"),
            ("BALLNOSE", "Ballnose", "Ballnose cutter"),
            ("BULLNOSE", "Bullnose", "Bullnose cutter ***placeholder **"),
            ("VCARVE", "V-carve", "V-carve cutter"),
            ("BALLCONE", "Ballcone", "Ball with a Cone for Parallel - X"),
            ("CYLCONE", "Cylinder cone", "Cylinder End with a Cone for Parallel - X"),
            ("LASER", "Laser", "Laser cutter"),
            ("PLASMA", "Plasma", "Plasma cutter"),
            ("CUSTOM", "Custom-EXPERIMENTAL", "Modelled cutter - not well tested yet."),
        ),
        description="Type of cutter used",
        default="END",
        update=update_Z_buffer_image,
    )
    cutter_object_name: StringProperty(
        name="Cutter Object",
        description="Object used as custom cutter for this operation",
        update=update_Z_buffer_image,
    )
    machine_axes: EnumProperty(
        name="Number of Axes",
        items=(
            ("3", "3 axis", "a", "EMPTY_DATA", 0),
            ("4", "4 axis - EXPERIMENTAL", "a", "EXPERIMENTAL", 1),
            ("5", "5 axis - EXPERIMENTAL", "a", "EXPERIMENTAL", 2),
        ),
        description="How many axes will be used for the operation",
        default="3",
        update=update_strategy,
    )
    strategy: EnumProperty(
        name="Strategy",
        items=get_strategy_list,
        description="Strategy",
        update=update_strategy,
    )
    strategy_4_axis: EnumProperty(
        name="4 Axis Strategy",
        items=(
            (
                "PARALLELR",
                "Parallel around 1st rotary axis",
                "Parallel lines around first rotary axis",
            ),
            (
                "PARALLEL",
                "Parallel along 1st rotary axis",
                "Parallel lines along first rotary axis",
            ),
            ("HELIX", "Helix around 1st rotary axis", "Helix around rotary axis"),
            ("INDEXED", "Indexed 3-axis", "all 3 axis strategies, just applied to the 4th axis"),
            ("CROSS", "Cross", "Cross paths"),
        ),
        description="#Strategy",
        default="PARALLEL",
        update=update_strategy,
    )
    strategy_5_axis: EnumProperty(
        name="Strategy",
        items=(("INDEXED", "Indexed 3-axis", "All 3 axis strategies, just rotated by 4+5th axes"),),
        description="5 axis Strategy",
        default="INDEXED",
        update=update_strategy,
    )
    rotary_axis_1: EnumProperty(
        name="Rotary Axis",
        items=(
            ("X", "X", ""),
            ("Y", "Y", ""),
            ("Z", "Z", ""),
        ),
        description="Around which axis rotates the first rotary axis",
        default="X",
        update=update_strategy,
    )
    rotary_axis_2: EnumProperty(
        name="Rotary Axis 2",
        items=(
            ("X", "X", ""),
            ("Y", "Y", ""),
            ("Z", "Z", ""),
        ),
        description="Around which axis rotates the second rotary axis",
        default="Z",
        update=update_strategy,
    )
    skin: FloatProperty(
        name="Skin",
        description="Material to leave when roughing ",
        min=0.0,
        max=1.0,
        default=0.0,
        precision=PRECISION,
        unit="LENGTH",
        update=update_offset_image,
    )
    inverse: BoolProperty(
        name="Inverse Milling",
        description="Male to female model conversion",
        default=False,
        update=update_offset_image,
    )
    array: BoolProperty(
        name="Use Array",
        description="Create a repetitive array for producing the " "same thing many times",
        default=False,
        update=update_rest,
    )
    array_x_count: IntProperty(
        name="X Count",
        description="X count",
        default=1,
        min=1,
        max=32000,
        update=update_rest,
    )
    array_y_count: IntProperty(
        name="Y Count",
        description="Y count",
        default=1,
        min=1,
        max=32000,
        update=update_rest,
    )
    array_x_distance: FloatProperty(
        name="X Distance",
        description="Distance between operation origins",
        min=0.00001,
        max=1.0,
        default=0.01,
        precision=PRECISION,
        unit="LENGTH",
        update=update_rest,
    )
    array_y_distance: FloatProperty(
        name="Y Distance",
        description="Distance between operation origins",
        min=0.00001,
        max=1.0,
        default=0.01,
        precision=PRECISION,
        unit="LENGTH",
        update=update_rest,
    )

    ##########
    # Pocket #
    ##########

    pocket_option: EnumProperty(
        name="Start Position",
        items=(("INSIDE", "Inside", "a"), ("OUTSIDE", "Outside", "a")),
        description="Pocket starting position",
        default="INSIDE",
        update=update_rest,
    )
    pocket_type: EnumProperty(
        name="pocket type",
        items=(
            ("PERIMETER", "Perimeter", "a", "", 0),
            ("PARALLEL", "Parallel", "a", "EXPERIMENTAL", 1),
        ),
        description="Type of pocket",
        default="PERIMETER",
        update=update_rest,
    )
    parallel_pocket_angle: FloatProperty(
        name="Parallel Pocket Angle",
        description="Angle for parallel pocket",
        min=-180,
        max=180.0,
        default=45.0,
        precision=PRECISION,
        update=update_rest,
    )
    parallel_pocket_crosshatch: BoolProperty(
        name="Crosshatch #",
        description="Crosshatch X finish",
        default=False,
        update=update_rest,
    )
    parallel_pocket_contour: BoolProperty(
        name="Contour Finish",
        description="Contour path finish",
        default=False,
        update=update_rest,
    )
    pocket_to_curve: BoolProperty(
        name="Pocket to Curve",
        description="Generates a curve instead of a path",
        default=False,
        update=update_rest,
    )

    ##########
    # Cutout #
    ##########

    cut_type: EnumProperty(
        name="Cut",
        items=(("OUTSIDE", "Outside", "a"), ("INSIDE", "Inside", "a"), ("ONLINE", "On Line", "a")),
        description="Type of cutter used",
        default="OUTSIDE",
        update=update_rest,
    )
    outlines_count: IntProperty(
        name="Outlines Count",
        description="Outlines count",
        default=1,
        min=1,
        max=32,
        update=update_cutout,
    )
    straight: BoolProperty(
        name="Overshoot Style",
        description="Use overshoot cutout instead of conventional rounded",
        default=True,
        update=update_rest,
    )

    ##########
    # Cutter #
    ##########

    cutter_id: IntProperty(
        name="Tool Number",
        description="For machines which support tool change based on tool id",
        min=0,
        max=10000,
        default=1,
        update=update_rest,
    )
    cutter_diameter: FloatProperty(
        name="Cutter Diameter",
        description="Cutter diameter = 2x cutter radius",
        min=0.000001,
        max=10,
        default=0.003,
        precision=PRECISION,
        unit="LENGTH",
        update=update_offset_image,
    )
    cylcone_diameter: FloatProperty(
        name="Bottom Diameter",
        description="Bottom diameter",
        min=0.000001,
        max=10,
        default=0.003,
        precision=PRECISION,
        unit="LENGTH",
        update=update_offset_image,
    )
    cutter_length: FloatProperty(
        name="#Cutter Length",
        description="#not supported#Cutter length",
        min=0.0,
        max=100.0,
        default=25.0,
        precision=PRECISION,
        unit="LENGTH",
        update=update_offset_image,
    )
    cutter_flutes: IntProperty(
        name="Cutter Flutes",
        description="Cutter flutes",
        min=1,
        max=20,
        default=2,
        update=update_chipload,
    )
    cutter_tip_angle: FloatProperty(
        name="Cutter V-carve Angle",
        description="Cutter V-carve angle",
        default=pi / 3,
        min=0.0,
        max=pi,
        subtype="ANGLE",
        unit="ROTATION",
        precision=PRECISION,
        step=500,
        update=update_offset_image,
    )
    ball_radius: FloatProperty(
        name="Ball Radius",
        description="Radius of",
        min=0.0,
        max=0.035,
        default=0.001,
        unit="LENGTH",
        precision=PRECISION,
        update=update_offset_image,
    )
    bull_corner_radius: FloatProperty(
        name="Bull Corner Radius",
        description="Radius tool bit corner",
        min=0.0,
        max=0.035,
        default=0.005,
        unit="LENGTH",
        precision=PRECISION,
        update=update_offset_image,
    )
    cutter_description: StringProperty(
        name="Tool Description",
        default="",
        update=update_offset_image,
    )

    ##################
    # Laser & Plasma #
    ##################

    laser_on: StringProperty(
        name="Laser ON String",
        default="M68 E0 Q100",
    )
    laser_off: StringProperty(
        name="Laser OFF String",
        default="M68 E0 Q0",
    )
    laser_cmd: StringProperty(
        name="Laser Command",
        default="M68 E0 Q",
    )
    laser_delay: FloatProperty(
        name="Laser ON Delay",
        description="Time after fast move to turn on laser and " "let machine stabilize",
        default=0.2,
    )
    plasma_on: StringProperty(
        name="Plasma ON String",
        default="M03",
    )
    plasma_off: StringProperty(
        name="Plasma OFF String",
        default="M05",
    )
    plasma_delay: FloatProperty(
        name="Plasma ON Delay",
        description="Time after fast move to turn on Plasma and " "let machine stabilize",
        default=0.1,
    )
    plasma_dwell: FloatProperty(
        name="Plasma Dwell Time",
        description="Time to dwell and warm up the torch",
        default=0.0,
    )

    #########
    # Steps #
    #########

    distance_between_paths: FloatProperty(
        name="Distance Between Toolpaths",
        default=0.001,
        min=0.00001,
        max=32,
        precision=PRECISION,
        unit="LENGTH",
        update=update_rest,
    )
    distance_along_paths: FloatProperty(
        name="Distance Along Toolpaths",
        default=0.0002,
        min=0.00001,
        max=32,
        precision=PRECISION,
        unit="LENGTH",
        update=update_rest,
    )
    parallel_angle: FloatProperty(
        name="Angle of Paths",
        default=0,
        min=-360,
        max=360,
        precision=0,
        step=500,
        subtype="ANGLE",
        unit="ROTATION",
        update=update_rest,
    )
    # OBSOLETE?, REMOVE ?
    old_rotation_a: FloatProperty(
        name="A Axis Angle",
        description="old value of Rotate A axis\nto specified angle",
        default=0,
        min=-360,
        max=360,
        precision=0,
        subtype="ANGLE",
        unit="ROTATION",
        update=update_rest,
    )
    # OBSOLETE?, REMOVE ?
    old_rotation_b: FloatProperty(
        name="A Axis Angle",
        description="old value of Rotate A axis\nto specified angle",
        default=0,
        min=-360,
        max=360,
        precision=0,
        subtype="ANGLE",
        unit="ROTATION",
        update=update_rest,
    )
    rotation_a: FloatProperty(
        name="A Axis Angle",
        description="Rotate A axis\nto specified angle",
        default=0,
        min=-360,
        max=360,
        precision=0,
        step=500,
        subtype="ANGLE",
        unit="ROTATION",
        update=update_rotation,
    )
    enable_a_axis: BoolProperty(
        name="Enable A Axis",
        description="Rotate A axis",
        default=False,
        update=update_rotation,
    )
    a_along_x: BoolProperty(
        name="A Along X ",
        description="A Parallel to X",
        default=True,
        update=update_rest,
    )
    rotation_b: FloatProperty(
        name="B Axis Angle",
        description="Rotate B axis\nto specified angle",
        default=0,
        min=-360,
        max=360,
        precision=0,
        step=500,
        subtype="ANGLE",
        unit="ROTATION",
        update=update_rotation,
    )
    enable_b_axis: BoolProperty(
        name="Enable B Axis",
        description="Rotate B axis",
        default=False,
        update=update_rotation,
    )

    #########
    # Carve #
    #########

    carve_depth: FloatProperty(
        name="Carve Depth",
        default=0.001,
        min=-0.100,
        max=32,
        precision=PRECISION,
        unit="LENGTH",
        update=update_rest,
    )

    #########
    # Drill #
    #########

    drill_type: EnumProperty(
        name="Holes On",
        items=(
            ("MIDDLE_SYMETRIC", "Middle of Symmetric Curves", "a"),
            ("MIDDLE_ALL", "Middle of All Curve Parts", "a"),
            ("ALL_POINTS", "All Points in Curve", "a"),
        ),
        description="Strategy to detect holes to drill",
        default="MIDDLE_SYMETRIC",
        update=update_rest,
    )

    #############
    # Waterline #
    #############

    slice_detail: FloatProperty(
        name="Distance Between Slices",
        default=0.001,
        min=0.00001,
        max=32,
        precision=PRECISION,
        unit="LENGTH",
        update=update_rest,
    )
    waterline_fill: BoolProperty(
        name="Fill Areas Between Slices",
        description="Fill areas between slices in waterline mode",
        default=True,
        update=update_rest,
    )
    waterline_project: BoolProperty(
        name="Project Paths - Not Recomended",
        description="Project paths in areas between slices",
        default=True,
        update=update_rest,
    )

    ####################
    # Movement & Ramps #
    ####################

    use_layers: BoolProperty(
        name="Use Layers",
        description="Use layers for roughing",
        default=True,
        update=update_rest,
    )
    stepdown: FloatProperty(
        name="",
        description="Layer height",
        default=0.01,
        min=0.00001,
        max=32,
        precision=PRECISION,
        unit="LENGTH",
        update=update_rest,
    )
    lead_in: FloatProperty(
        name="Lead-in Radius",
        description="Lead in radius for torch or laser to turn off",
        min=0.00,
        max=1,
        default=0.0,
        precision=PRECISION,
        unit="LENGTH",
    )
    lead_out: FloatProperty(
        name="Lead-out Radius",
        description="Lead out radius for torch or laser to turn off",
        min=0.00,
        max=1,
        default=0.0,
        precision=PRECISION,
        unit="LENGTH",
    )
    profile_start: IntProperty(
        name="Start Point",
        description="Start point offset",
        min=0,
        default=0,
        update=update_rest,
    )
    min_z: FloatProperty(
        name="Operation Depth End",
        default=-0.01,
        min=-3,
        max=3,
        precision=PRECISION,
        unit="LENGTH",
        update=update_rest,
    )
    min_z_from: EnumProperty(
        name="Max Depth From",
        description="Set maximum operation depth",
        items=(
            ("OBJECT", "Object", "Set max operation depth from Object"),
            ("MATERIAL", "Material", "Set max operation depth from Material"),
            ("CUSTOM", "Custom", "Custom max depth"),
        ),
        default="OBJECT",
        update=update_rest,
    )
    start_type: EnumProperty(
        name="Start Type",
        items=(
            ("ZLEVEL", "Z level", "Starts on a given Z level"),
            (
                "OPERATIONRESULT",
                "Rest Milling",
                "For rest milling, operations have to be " "put in chain for this to work well.",
            ),
        ),
        description="Starting depth",
        default="ZLEVEL",
        update=update_strategy,
    )
    max_z: FloatProperty(
        name="Operation Depth Start",
        description="operation starting depth",
        default=0,
        min=-3,
        max=10,
        precision=PRECISION,
        unit="LENGTH",
        update=update_rest,
    )  # EXPERIMENTAL
    first_down: BoolProperty(
        name="First Down",
        description="First go down on a contour, then go to the next one",
        default=False,
        update=update_operation,
    )

    #########
    # Image #
    #########

    source_image_scale_z: FloatProperty(
        name="Image Source Depth Scale",
        default=0.01,
        min=-1,
        max=1,
        precision=PRECISION,
        unit="LENGTH",
        update=update_Z_buffer_image,
    )
    source_image_size_x: FloatProperty(
        name="Image Source X Size",
        default=0.1,
        min=-10,
        max=10,
        precision=PRECISION,
        unit="LENGTH",
        update=update_Z_buffer_image,
    )
    source_image_size_y: FloatProperty(
        name="Image Source Y Size",
        default=0.1,
        min=-10,
        max=10,
        precision=PRECISION,
        unit="LENGTH",
        update=update_image_size_y,
    )
    source_image_offset: FloatVectorProperty(
        name="Image Offset",
        default=(0, 0, 0),
        unit="LENGTH",
        precision=PRECISION,
        subtype="XYZ",
        update=update_Z_buffer_image,
    )

    source_image_crop: BoolProperty(
        name="Crop Source Image",
        description="Crop source image - the position of the sub-rectangle "
        "is relative to the whole image, so it can be used for e.g. "
        "finishing just a part of an image",
        default=False,
        update=update_Z_buffer_image,
    )
    source_image_crop_start_x: FloatProperty(
        name="Crop Start X",
        default=0,
        min=0,
        max=100,
        precision=PRECISION,
        subtype="PERCENTAGE",
        update=update_Z_buffer_image,
    )
    source_image_crop_start_y: FloatProperty(
        name="Crop Start Y",
        default=0,
        min=0,
        max=100,
        precision=PRECISION,
        subtype="PERCENTAGE",
        update=update_Z_buffer_image,
    )
    source_image_crop_end_x: FloatProperty(
        name="Crop End X",
        default=100,
        min=0,
        max=100,
        precision=PRECISION,
        subtype="PERCENTAGE",
        update=update_Z_buffer_image,
    )
    source_image_crop_end_y: FloatProperty(
        name="Crop End Y",
        default=100,
        min=0,
        max=100,
        precision=PRECISION,
        subtype="PERCENTAGE",
        update=update_Z_buffer_image,
    )

    #####################
    # Toolpath and Area #
    #####################

    ambient_behaviour: EnumProperty(
        name="Ambient",
        items=(("ALL", "All", "a"), ("AROUND", "Around", "a")),
        description="Handling ambient surfaces",
        default="ALL",
        update=update_Z_buffer_image,
    )
    ambient_radius: FloatProperty(
        name="Ambient Radius",
        description="Radius around the part which will be milled if " "ambient is set to Around",
        min=0.0,
        max=100.0,
        default=0.01,
        precision=PRECISION,
        unit="LENGTH",
        update=update_rest,
    )
    use_limit_curve: BoolProperty(
        name="Use Limit Curve",
        description="A curve limits the operation area",
        default=False,
        update=update_rest,
    )
    ambient_cutter_restrict: BoolProperty(
        name="Cutter Stays in Ambient Limits",
        description="Cutter doesn't get out from ambient limits otherwise "
        "goes on the border exactly",
        default=True,
        update=update_rest,
    )  # restricts cutter inside ambient only
    limit_curve: StringProperty(
        name="Limit Curve",
        description="Curve used to limit the area of the operation",
        update=update_rest,
    )

    #########
    # Feeds #
    #########

    feedrate: FloatProperty(
        name="Feedrate",
        description="Feedrate in units per minute",
        min=0.00005,
        max=50.0,
        default=1.0,
        precision=PRECISION,
        unit="LENGTH",
        update=update_chipload,
    )
    plunge_feedrate: FloatProperty(
        name="Plunge Speed",
        description="% of feedrate",
        min=0.1,
        max=100.0,
        default=50.0,
        precision=1,
        subtype="PERCENTAGE",
        update=update_rest,
    )
    plunge_angle: FloatProperty(
        name="Plunge Angle",
        description="What angle is already considered to plunge",
        default=pi / 6,
        min=0,
        max=pi * 0.5,
        precision=0,
        step=500,
        subtype="ANGLE",
        unit="ROTATION",
        update=update_rest,
    )
    spindle_rpm: FloatProperty(
        name="Spindle RPM",
        description="Spindle speed ",
        min=0,
        max=60000,
        default=12000,
        update=update_chipload,
    )

    ##############################
    # Optimisation & Performance #
    ##############################

    do_simulation_feedrate: BoolProperty(
        name="Adjust Feedrates with Simulation EXPERIMENTAL",
        description="Adjust feedrates with simulation",
        default=False,
        update=update_rest,
    )
    dont_merge: BoolProperty(
        name="Don't Merge Outlines when Cutting",
        description="this is usefull when you want to cut around everything",
        default=False,
        update=update_rest,
    )
    pencil_threshold: FloatProperty(
        name="Pencil Threshold",
        default=0.00002,
        min=0.00000001,
        max=1,
        precision=PRECISION,
        unit="LENGTH",
        update=update_rest,
    )
    crazy_threshold_1: FloatProperty(
        name="Min Engagement",
        default=0.02,
        min=0.00000001,
        max=100,
        precision=PRECISION,
        update=update_rest,
    )
    crazy_threshold_2: FloatProperty(
        name="Max Engagement",
        default=0.5,
        min=0.00000001,
        max=100,
        precision=PRECISION,
        update=update_rest,
    )
    crazy_threshold_3: FloatProperty(
        name="Max Angle",
        default=2,
        min=0.00000001,
        max=100,
        precision=PRECISION,
        update=update_rest,
    )
    crazy_threshold_4: FloatProperty(
        name="Test Angle Step",
        default=0.05,
        min=0.00000001,
        max=100,
        precision=PRECISION,
        update=update_rest,
    )
    crazy_threshold_5: FloatProperty(
        name="Optimal Engagement",
        default=0.3,
        min=0.00000001,
        max=100,
        precision=PRECISION,
        update=update_rest,
    )

    ##########
    # Medial #
    ##########

    add_pocket_for_medial: BoolProperty(
        name="Add Pocket Operation",
        description="Clean unremoved material after medial axis",
        default=True,
        update=update_rest,
    )
    add_mesh_for_medial: BoolProperty(
        name="Add Medial mesh",
        description="Medial operation returns mesh for editing and " "further processing",
        default=False,
        update=update_rest,
    )
    medial_axis_threshold: FloatProperty(
        name="Long Vector Threshold",
        default=0.001,
        min=0.00000001,
        max=100,
        precision=PRECISION,
        unit="LENGTH",
        update=update_rest,
    )
    medial_axis_subdivision: FloatProperty(
        name="Fine Subdivision",
        default=0.0002,
        min=0.00000001,
        max=100,
        precision=PRECISION,
        unit="LENGTH",
        update=update_rest,
    )

    ###########
    # Bridges #
    ###########

    use_bridges: BoolProperty(
        name="Use Bridges / Tabs",
        description="Use bridges in cutout",
        default=False,
        update=update_bridges,
    )
    bridges_width: FloatProperty(
        name="Bridge / Tab Width",
        default=0.002,
        unit="LENGTH",
        precision=PRECISION,
        update=update_bridges,
    )
    bridges_height: FloatProperty(
        name="Bridge / Tab Height",
        description="Height from the bottom of the cutting operation",
        default=0.0005,
        unit="LENGTH",
        precision=PRECISION,
        update=update_bridges,
    )
    bridges_collection_name: StringProperty(
        name="Bridges / Tabs Collection",
        description="Collection of curves used as bridges",
        update=operation_valid,
    )
    use_bridge_modifiers: BoolProperty(
        name="Use Bridge / Tab Modifiers",
        description="Include bridge curve modifiers using render level when "
        "calculating operation, does not effect original bridge data",
        default=True,
        update=update_bridges,
    )
    use_modifiers: BoolProperty(
        name="Use Mesh Modifiers",
        description="Include mesh modifiers using render level when "
        "calculating operation, does not effect original mesh",
        default=True,
        update=operation_valid,
    )

    ############
    # Material #
    ############

    min: FloatVectorProperty(
        name="Operation Minimum",
        default=(0, 0, 0),
        unit="LENGTH",
        precision=PRECISION,
        subtype="XYZ",
    )
    max: FloatVectorProperty(
        name="Operation Maximum",
        default=(0, 0, 0),
        unit="LENGTH",
        precision=PRECISION,
        subtype="XYZ",
    )

    #########
    # Gcode #
    #########

    output_header: BoolProperty(
        name="Output G-code Header",
        description="Output user defined G-code command header" " at start of operation",
        default=False,
    )
    gcode_header: StringProperty(
        name="G-code Header",
        description="G-code commands at start of operation." " Use ; for line breaks",
        default="G53 G0",
    )
    enable_dust: BoolProperty(
        name="Dust Collector",
        description="Output user defined g-code command header" " at start of operation",
        default=False,
    )
    gcode_start_dust_cmd: StringProperty(
        name="Start Dust Collector",
        description="Commands to start dust collection. Use ; for line breaks",
        default="M100",
    )
    gcode_stop_dust_cmd: StringProperty(
        name="Stop Dust Collector",
        description="Command to stop dust collection. Use ; for line breaks",
        default="M101",
    )
    enable_hold: BoolProperty(
        name="Hold Down",
        description="Output hold down command at start of operation",
        default=False,
    )
    gcode_start_hold_cmd: StringProperty(
        name="G-code Header",
        description="G-code commands at start of operation." " Use ; for line breaks",
        default="M102",
    )
    gcode_stop_hold_cmd: StringProperty(
        name="G-code Header",
        description="G-code commands at end operation. Use ; for line breaks",
        default="M103",
    )
    enable_mist: BoolProperty(
        name="Mist",
        description="Mist command at start of operation",
        default=False,
    )
    gcode_start_mist_cmd: StringProperty(
        name="Start Mist",
        description="Command to start mist. Use ; for line breaks",
        default="M104",
    )
    gcode_stop_mist_cmd: StringProperty(
        name="Stop Mist",
        description="Command to stop mist. Use ; for line breaks",
        default="M105",
    )
    output_trailer: BoolProperty(
        name="Output G-code Trailer",
        description="Output user defined g-code command trailer" " at end of operation",
        default=False,
    )
    gcode_trailer: StringProperty(
        name="G-code Trailer",
        description="G-code commands at end of operation." " Use ; for line breaks",
        default="M02",
    )

    ############
    # Internal #
    ############

    offset_image = numpy.array([], dtype=float)
    zbuffer_image = numpy.array([], dtype=float)
    silhouette = sgeometry.Polygon()
    ambient = sgeometry.Polygon()
    operation_limit = sgeometry.Polygon()
    borderwidth = 50
    object = None
    path_object_name: StringProperty(name="Path Object", description="Actual CNC path")

    #################
    # Update & Tags #
    #################

    changed: BoolProperty(
        name="True if any of the Operation Settings has Changed",
        description="Mark for update",
        default=False,
    )
    update_z_buffer_image_tag: BoolProperty(
        name="Mark Z-Buffer Image for Update",
        description="Mark for update",
        default=True,
    )
    update_offset_image_tag: BoolProperty(
        name="Mark Offset Image for Update",
        description="Mark for update",
        default=True,
    )
    update_silhouette_tag: BoolProperty(
        name="Mark Silhouette Image for Update",
        description="Mark for update",
        default=True,
    )
    update_ambient_tag: BoolProperty(
        name="Mark Ambient Polygon for Update",
        description="Mark for update",
        default=True,
    )
    update_bullet_collision_tag: BoolProperty(
        name="Mark Bullet Collision World for Update",
        description="Mark for update",
        default=True,
    )
    valid: BoolProperty(
        name="Valid",
        description="True if operation is ok for calculation",
        default=True,
    )
    change_data: StringProperty(
        name="Changedata",
        description="change data for checking if stuff changed.",
    )

    ###########
    # Process #
    ###########

    computing: BoolProperty(
        name="Computing Right Now",
        description="",
        default=False,
    )
    pid: IntProperty(
        name="Process Id",
        description="Background process id",
        default=-1,
    )
    out_text: StringProperty(
        name="Outtext",
        description="outtext",
        default="",
    )
