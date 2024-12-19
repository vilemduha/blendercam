"""Fabex 'machine_settings.py'


All CAM machine properties.
"""

from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
)
from bpy.types import PropertyGroup

from ..constants import PRECISION
from ..utilities.machine_utils import update_machine


class CAM_MACHINE_Properties(PropertyGroup):
    """stores all data for machines"""

    # name = StringProperty(name="Machine Name", default="Machine")
    post_processor: EnumProperty(
        name="Post Processor",
        items=(
            (
                "ISO",
                "Iso",
                "Exports standardized gcode ISO 6983 (RS-274)",
            ),
            (
                "MACH3",
                "Mach3",
                "Default mach3",
            ),
            (
                "EMC",
                "LinuxCNC - EMC2",
                "Linux based CNC control software - formally EMC2",
            ),
            (
                "FADAL",
                "Fadal",
                "Fadal VMC",
            ),
            (
                "GRBL",
                "grbl",
                "Optimized gcode for grbl firmware on Arduino with cnc shield",
            ),
            (
                "HEIDENHAIN",
                "Heidenhain",
                "Heidenhain",
            ),
            (
                "HEIDENHAIN530",
                "Heidenhain530",
                "Heidenhain530",
            ),
            (
                "TNC151",
                "Heidenhain TNC151",
                "Post Processor for the Heidenhain TNC151 machine",
            ),
            (
                "SIEGKX1",
                "Sieg KX1",
                "Sieg KX1",
            ),
            (
                "HM50",
                "Hafco HM-50",
                "Hafco HM-50",
            ),
            (
                "CENTROID",
                "Centroid M40",
                "Centroid M40",
            ),
            (
                "ANILAM",
                "Anilam Crusader M",
                "Anilam Crusader M",
            ),
            (
                "GRAVOS",
                "Gravos",
                "Gravos",
            ),
            (
                "WIN-PC",
                "WinPC-NC",
                "German CNC by Burkhard Lewetz",
            ),
            (
                "SHOPBOT MTC",
                "ShopBot MTC",
                "ShopBot MTC",
            ),
            (
                "LYNX_OTTER_O",
                "Lynx Otter o",
                "Lynx Otter o",
            ),
        ),
        description="Post Processor",
        default="MACH3",
    )
    # position definitions:
    use_position_definitions: BoolProperty(
        name="Use Position Definitions",
        description="Define own positions for op start, toolchange, ending position",
        default=False,
    )
    starting_position: FloatVectorProperty(
        name="Start Position",
        default=(0, 0, 0),
        unit="LENGTH",
        precision=PRECISION,
        subtype="XYZ",
        update=update_machine,
    )
    mtc_position: FloatVectorProperty(
        name="MTC Position",
        default=(0, 0, 0),
        unit="LENGTH",
        precision=PRECISION,
        subtype="XYZ",
        update=update_machine,
    )
    ending_position: FloatVectorProperty(
        name="End Position",
        default=(0, 0, 0),
        unit="LENGTH",
        precision=PRECISION,
        subtype="XYZ",
        update=update_machine,
    )
    working_area: FloatVectorProperty(
        name="Work Area",
        default=(0.500, 0.500, 0.100),
        unit="LENGTH",
        precision=PRECISION,
        subtype="XYZ",
        update=update_machine,
    )
    feedrate_min: FloatProperty(
        name="Feedrate Minimum /min",
        default=0.0,
        min=0.00001,
        max=320000,
        precision=PRECISION,
        unit="LENGTH",
    )
    feedrate_max: FloatProperty(
        name="Feedrate Maximum /min",
        default=2,
        min=0.00001,
        max=320000,
        precision=PRECISION,
        unit="LENGTH",
    )
    feedrate_default: FloatProperty(
        name="Feedrate Default /min",
        default=1.5,
        min=0.00001,
        max=320000,
        precision=PRECISION,
        unit="LENGTH",
    )
    hourly_rate: FloatProperty(
        name="Price per Hour",
        default=100,
        min=0.005,
        precision=2,
    )

    # UNSUPPORTED:
    spindle_min: FloatProperty(
        name="Spindle Speed Minimum RPM",
        default=5000,
        min=0.00001,
        max=320000,
        precision=1,
    )
    spindle_max: FloatProperty(
        name="Spindle Speed Maximum RPM",
        default=30000,
        min=0.00001,
        max=320000,
        precision=1,
    )
    spindle_default: FloatProperty(
        name="Spindle Speed Default RPM",
        default=15000,
        min=0.00001,
        max=320000,
        precision=1,
    )
    spindle_start_time: FloatProperty(
        name="Spindle Start Delay Seconds",
        description="Wait for the spindle to start spinning before starting "
        "the feeds , in seconds",
        default=0,
        min=0.0000,
        max=320000,
        precision=1,
    )
    axis_4: BoolProperty(
        name="4th Axis",
        description="Machine has 4th axis",
        default=0,
    )
    axis_5: BoolProperty(
        name="5th Axis",
        description="Machine has 5th axis",
        default=0,
    )
    eval_splitting: BoolProperty(
        name="Split Files",
        description="Split gcode file with large number of operations",
        default=True,
    )  # split large files
    split_limit: IntProperty(
        name="Operations per File",
        description="Split files with larger number of operations than this",
        min=1000,
        max=20000000,
        default=800000,
    )
    collet_size: FloatProperty(
        name="Collet Size",
        description="Collet size for collision detection",
        default=33,
        min=0.00001,
        max=320000,
        precision=PRECISION,
        unit="LENGTH",
    )

    # post processor options

    output_block_numbers: BoolProperty(
        name="Output Block Numbers",
        description="Output block numbers ie N10 at start of line",
        default=False,
    )

    start_block_number: IntProperty(
        name="Start Block Number",
        description="The starting block number ie 10",
        default=10,
    )

    block_number_increment: IntProperty(
        name="Block Number Increment",
        description="How much the block number should " "increment for the next line",
        default=10,
    )

    output_tool_definitions: BoolProperty(
        name="Output Tool Definitions",
        description="Output tool definitions",
        default=True,
    )

    output_tool_change: BoolProperty(
        name="Output Tool Change Commands",
        description="Output tool change commands ie: Tn M06",
        default=True,
    )

    output_G43_on_tool_change: BoolProperty(
        name="Output G43 on Tool Change",
        description="Output G43 on tool change line",
        default=False,
    )
