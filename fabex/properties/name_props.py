"""Fabex 'name_props.py'


All CAM related naming properties.
"""

from datetime import datetime

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

name_options = [
    (
        "NONE",
        "(none)",
        "Empty name slots will be ignored",
    ),
    (
        "DATE",
        "Date",
        "The date of the gcode export",
    ),
    (
        "TIME",
        "Time",
        "The time of the gcode export",
    ),
    (
        "DATETIME",
        "Date and Time",
        "The date and time of the gcode export",
    ),
    (
        "FILE",
        "Blend File",
        "Name of the current Blend file",
    ),
    (
        "OBJECT",
        "Object",
        "Name of the Operation object",
    ),
    (
        "INDEX",
        "Index",
        "The index number of the Operation or Chain",
    ),
    (
        "STRATEGY",
        "Strategy",
        "The milling strategy of the Operation",
    ),
    (
        "OP_NAME",
        "Operation Name",
        "The name of the Operation",
    ),
]


def setup_names():
    scene = bpy.context.scene

    get_time = datetime.now().strftime

    current_date = get_time("%y%m%d")
    current_time = get_time("%H%M%S")
    current_datetime = get_time("%y%m%d_%H%M%S")

    if len(scene.cam_operations) > 0:
        active_op = scene.cam_operations[scene.cam_active_operation]
        object_name = active_op.object_name
        strategy = active_op.strategy.title()
        op_name = active_op.name
        operation_index = scene.cam_active_operation + 1
        chain_index = scene.cam_active_chain
    else:
        active_op = ""
        object_name = "OBJECT"
        strategy = "STRATEGY"
        op_name = "OP_NAME"
        operation_index = chain_index = ""

    current_file = bpy.path.display_name_from_filepath(bpy.data.filepath)

    enum_dict = {
        "NONE": "",
        "INDEX": operation_index,
        "DATE": current_date,
        "TIME": current_time,
        "DATETIME": current_datetime,
        "FILE": current_file,
        "OBJECT": object_name,
        "STRATEGY": strategy,
        "OP_NAME": op_name,
    }
    return enum_dict


def build_names(enum_dict, prefix, main_1, main_2, main_3, suffix):
    full_name = ""

    scene = bpy.context.scene

    names = scene.cam_names
    sep = names.separator

    pre = prefix
    p1 = enum_dict[main_1]
    p2 = enum_dict[main_2]
    p3 = enum_dict[main_3]
    suf = suffix

    name_parts = [pre, p1, p2, p3, suf]
    for part in name_parts:
        part = str(part)
        if part != "":
            full_name += part + sep
    if full_name[-1] == "_":
        full_name = full_name[:-1]

    return full_name


def get_path_name(context):
    scene = bpy.context.scene

    names = scene.cam_names
    sep = names.separator

    prefix = names.path_prefix
    main_1 = names.path_main_1
    main_2 = names.path_main_2
    main_3 = names.path_main_3
    suffix = names.path_suffix

    path_name = build_names(
        enum_dict=setup_names(),
        prefix=prefix,
        main_1=main_1,
        main_2=main_2,
        main_3=main_3,
        suffix=suffix,
    )

    return path_name


def get_operation_name(context):
    scene = bpy.context.scene

    names = scene.cam_names
    sep = names.separator

    prefix = names.operation_prefix
    main_1 = names.operation_main_1
    main_2 = names.operation_main_2
    main_3 = names.operation_main_3
    suffix = names.operation_suffix

    operation_name = build_names(
        enum_dict=setup_names(),
        prefix=prefix,
        main_1=main_1,
        main_2=main_2,
        main_3=main_3,
        suffix=suffix,
    )

    return operation_name


def get_chain_name(context):
    scene = bpy.context.scene

    names = scene.cam_names
    sep = names.separator

    prefix = names.chain_prefix
    main_1 = names.chain_main_1
    main_2 = names.chain_main_2
    main_3 = names.chain_main_3
    suffix = names.chain_suffix

    chain_name = build_names(
        enum_dict=setup_names(),
        prefix=prefix,
        main_1=main_1,
        main_2=main_2,
        main_3=main_3,
        suffix=suffix,
    )

    return chain_name


def get_simulation_name(context):
    scene = bpy.context.scene

    names = scene.cam_names
    sep = names.separator

    prefix = names.simulation_prefix
    main_1 = names.simulation_main_1
    main_2 = names.simulation_main_2
    main_3 = names.simulation_main_3
    suffix = names.simulation_suffix

    simulation_name = build_names(
        enum_dict=setup_names(),
        prefix=prefix,
        main_1=main_1,
        main_2=main_2,
        main_3=main_3,
        suffix=suffix,
    )

    return simulation_name


def get_file_name(context):
    scene = bpy.context.scene

    names = scene.cam_names
    sep = names.separator

    prefix = names.file_prefix
    main_1 = names.file_main_1
    main_2 = names.file_main_2
    main_3 = names.file_main_3
    suffix = names.file_suffix

    file_name = build_names(
        enum_dict=setup_names(),
        prefix=prefix,
        main_1=main_1,
        main_2=main_2,
        main_3=main_3,
        suffix=suffix,
    )

    return file_name


def update_name_link(self, context):
    scene = context.scene
    if len(scene.cam_operations) > 0:
        active_op = scene.cam_operations[scene.cam_active_operation]
        active_op.link_operation_file_names = self.link_names
    if len(scene.cam_chains) > 0:
        active_chain = scene.cam_chains[scene.cam_active_chain]
        active_chain.link_chain_file_names = self.link_names


class CAM_NAME_Properties(PropertyGroup):
    default_export_location: StringProperty(
        name="Export Folder",
        description="Folder where Fabex will save exported gcode files",
        subtype="DIR_PATH",
        default="",
    )

    link_names: BoolProperty(
        name="Link Chain/Op and File Names",
        description="Uses the Chain or Operation name as the gcode export File name",
        default=False,
        update=update_name_link,
    )

    # Separator
    separator: StringProperty(
        name="Separator",
        description="Character to place between name items - prefix, main, suffix",
        default="_",
    )

    # Path
    path_prefix: StringProperty(
        name="Path Prefix",
        description="Start of CAM Path's name",
        default="cam_path",
    )
    path_main_1: EnumProperty(
        name="Path Main 1",
        description="Middle of CAM Path's name (1/3)",
        items=name_options,
        default="OP_NAME",
    )
    path_main_2: EnumProperty(
        name="Path Main 2",
        description="Middle of CAM Path's name (2/3)",
        items=name_options,
        default="NONE",
    )
    path_main_3: EnumProperty(
        name="Path Main 3",
        description="Middle of CAM Path's name (3/3)",
        items=name_options,
        default="NONE",
    )
    path_suffix: StringProperty(
        name="Path Suffix",
        description="End of CAM Path's name",
        default="",
    )

    path_name_full: StringProperty(
        name="Path Name (full)",
        get=get_path_name,
    )

    # Operation
    operation_prefix: StringProperty(
        name="Operation Prefix",
        description="Start of CAM Operation's name",
        default="Op",
    )
    operation_main_1: EnumProperty(
        name="Operation Main 1",
        description="Middle of CAM Operation's name (1/3)",
        items=name_options,
        default="OBJECT",
    )
    operation_main_2: EnumProperty(
        name="Operation Main 2",
        description="Middle of CAM Operation's name (2/3)",
        items=name_options,
        default="INDEX",
    )
    operation_main_3: EnumProperty(
        name="Operation Main 3",
        description="Middle of CAM Operation's name (3/3)",
        items=name_options,
        default="NONE",
    )
    operation_suffix: StringProperty(
        name="Operation Suffix",
        description="End of CAM Operation's name",
        default="",
    )

    operation_name_full: StringProperty(
        name="Operation Name (full)",
        get=get_operation_name,
    )

    # Chain
    chain_prefix: StringProperty(
        name="Chain Prefix",
        description="Start of CAM Chain's name",
        default="Chain",
    )
    chain_main_1: EnumProperty(
        name="Chain Main 1",
        description="Middle of CAM Chain's name (1/3)",
        items=name_options,
        default="INDEX",
    )
    chain_main_2: EnumProperty(
        name="Chain Main 2",
        description="Middle of CAM Chain's name (2/3)",
        items=name_options,
        default="NONE",
    )
    chain_main_3: EnumProperty(
        name="Chain Main 3",
        description="Middle of CAM Chain's name (3/3)",
        items=name_options,
        default="NONE",
    )
    chain_suffix: StringProperty(
        name="Chain Suffix",
        description="End of CAM Chain's name",
        default="",
    )

    chain_name_full: StringProperty(
        name="Chain Name (full)",
        get=get_chain_name,
    )

    # Simulation
    simulation_prefix: StringProperty(
        name="Simulation Prefix",
        description="Start of CAM Simulation's name",
        default="csim",
    )
    simulation_main_1: EnumProperty(
        name="Simulation Main 1",
        description="Middle of CAM Simulation's name (1/3)",
        items=name_options,
        default="OP_NAME",
    )
    simulation_main_2: EnumProperty(
        name="Simulation Main 2",
        description="Middle of CAM Simulation's name (2/3)",
        items=name_options,
        default="NONE",
    )
    simulation_main_3: EnumProperty(
        name="Simulation Main 3",
        description="Middle of CAM Simulation's name (3/3)",
        items=name_options,
        default="NONE",
    )
    simulation_suffix: StringProperty(
        name="Simulation Suffix",
        description="End of CAM Simulation's name",
        default="",
    )

    simulation_name_full: StringProperty(
        name="Simulation Name (full)",
        get=get_simulation_name,
    )

    # File
    file_prefix: StringProperty(
        name="File Prefix",
        description="Start of CAM File's name",
        default="",
    )
    file_main_1: EnumProperty(
        name="File Main 1",
        description="Middle of CAM File's name (1/3)",
        items=name_options,
        default="OP_NAME",
    )
    file_main_2: EnumProperty(
        name="File Main 2",
        description="Middle of CAM File's name (2/3)",
        items=name_options,
        default="NONE",
    )
    file_main_3: EnumProperty(
        name="File Main 3",
        description="Middle of CAM File's name (3/3)",
        items=name_options,
        default="NONE",
    )
    file_suffix: StringProperty(
        name="File Suffix",
        description="End of CAM File's name",
        default="",
    )

    file_name_full: StringProperty(
        name="File Name (full)",
        get=get_file_name,
    )
