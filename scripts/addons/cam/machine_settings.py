from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
)
from bpy.types import PropertyGroup

from . import constants
from .utils import updateMachine


class machineSettings(PropertyGroup):
    """stores all data for machines"""
    # name = StringProperty(name="Machine Name", default="Machine")
    post_processor: EnumProperty(
        name='Post processor',
        items=(
            ('ISO', 'Iso', 'exports standardized gcode ISO 6983 (RS-274)'),
            ('MACH3', 'Mach3', 'default mach3'),
            ('EMC', 'LinuxCNC - EMC2',
             'Linux based CNC control software - formally EMC2'),
            ('FADAL', 'Fadal', 'Fadal VMC'),
            ('GRBL', 'grbl',
             'optimized gcode for grbl firmware on Arduino with cnc shield'),
            ('HEIDENHAIN', 'Heidenhain', 'heidenhain'),
            ('HEIDENHAIN530', 'Heidenhain530', 'heidenhain530'),
            ('TNC151', 'Heidenhain TNC151',
             'Post Processor for the Heidenhain TNC151 machine'),
            ('SIEGKX1', 'Sieg KX1', 'Sieg KX1'),
            ('HM50', 'Hafco HM-50', 'Hafco HM-50'),
            ('CENTROID', 'Centroid M40', 'Centroid M40'),
            ('ANILAM', 'Anilam Crusader M', 'Anilam Crusader M'),
            ('GRAVOS', 'Gravos', 'Gravos'),
            ('WIN-PC', 'WinPC-NC', 'German CNC by Burkhard Lewetz'),
            ('SHOPBOT MTC', 'ShopBot MTC', 'ShopBot MTC'),
            ('LYNX_OTTER_O', 'Lynx Otter o', 'Lynx Otter o')
        ),
        description='Post processor',
        default='MACH3',
    )
    # units = EnumProperty(name='Units', items = (('IMPERIAL', ''))
    # position definitions:
    use_position_definitions: BoolProperty(
        name="Use position definitions",
        description="Define own positions for op start, "
        "toolchange, ending position",
        default=False,
    )
    starting_position: FloatVectorProperty(
        name='Start position',
        default=(0, 0, 0),
        unit='LENGTH',
        precision=constants.PRECISION,
        subtype="XYZ",
        update=updateMachine,
    )
    mtc_position: FloatVectorProperty(
        name='MTC position',
        default=(0, 0, 0),
        unit='LENGTH',
        precision=constants.PRECISION,
        subtype="XYZ",
        update=updateMachine,
    )
    ending_position: FloatVectorProperty(
        name='End position',
        default=(0, 0, 0),
        unit='LENGTH',
        precision=constants.PRECISION,
        subtype="XYZ",
        update=updateMachine,
    )

    working_area: FloatVectorProperty(
        name='Work Area',
        default=(0.500, 0.500, 0.100),
        unit='LENGTH',
        precision=constants.PRECISION,
        subtype="XYZ",
        update=updateMachine,
    )
    feedrate_min: FloatProperty(
        name="Feedrate minimum /min",
        default=0.0,
        min=0.00001,
        max=320000,
        precision=constants.PRECISION,
        unit='LENGTH',
    )
    feedrate_max: FloatProperty(
        name="Feedrate maximum /min",
        default=2,
        min=0.00001,
        max=320000,
        precision=constants.PRECISION,
        unit='LENGTH',
    )
    feedrate_default: FloatProperty(
        name="Feedrate default /min",
        default=1.5,
        min=0.00001,
        max=320000,
        precision=constants.PRECISION,
        unit='LENGTH',
    )
    hourly_rate: FloatProperty(
        name="Price per hour",
        default=100,
        min=0.005,
        precision=2,
    )

    # UNSUPPORTED:

    spindle_min: FloatProperty(
        name="Spindle speed minimum RPM",
        default=5000,
        min=0.00001,
        max=320000,
        precision=1,
    )
    spindle_max: FloatProperty(
        name="Spindle speed maximum RPM",
        default=30000,
        min=0.00001,
        max=320000,
        precision=1,
    )
    spindle_default: FloatProperty(
        name="Spindle speed default RPM",
        default=15000,
        min=0.00001,
        max=320000,
        precision=1,
    )
    spindle_start_time: FloatProperty(
        name="Spindle start delay seconds",
        description='Wait for the spindle to start spinning before starting '
        'the feeds , in seconds',
        default=0,
        min=0.0000,
        max=320000,
        precision=1,
    )

    axis4: BoolProperty(
        name="#4th axis",
        description="Machine has 4th axis",
        default=0,
    )
    axis5: BoolProperty(
        name="#5th axis",
        description="Machine has 5th axis",
        default=0,
    )

    eval_splitting: BoolProperty(
        name="Split files",
        description="split gcode file with large number of operations",
        default=True,
    )  # split large files
    split_limit: IntProperty(
        name="Operations per file",
        description="Split files with larger number of operations than this",
        min=1000,
        max=20000000,
        default=800000,
    )

    # rotary_axis1 = EnumProperty(name='Axis 1',
    #     items=(
    #         ('X', 'X', 'x'),
    #         ('Y', 'Y', 'y'),
    #         ('Z', 'Z', 'z')),
    #     description='Number 1 rotational axis',
    #     default='X', update = updateOffsetImage)

    collet_size: FloatProperty(
        name="#Collet size",
        description="Collet size for collision detection",
        default=33,
        min=0.00001,
        max=320000,
        precision=constants.PRECISION,
        unit="LENGTH",
    )
    # exporter_start = StringProperty(name="exporter start", default="%")

    # post processor options

    output_block_numbers: BoolProperty(
        name="output block numbers",
        description="output block numbers ie N10 at start of line",
        default=False,
    )

    start_block_number: IntProperty(
        name="start block number",
        description="the starting block number ie 10",
        default=10,
    )

    block_number_increment: IntProperty(
        name="block number increment",
        description="how much the block number should "
        "increment for the next line",
        default=10,
    )

    output_tool_definitions: BoolProperty(
        name="output tool definitions",
        description="output tool definitions",
        default=True,
    )

    output_tool_change: BoolProperty(
        name="output tool change commands",
        description="output tool change commands ie: Tn M06",
        default=True,
    )

    output_g43_on_tool_change: BoolProperty(
        name="output G43 on tool change",
        description="output G43 on tool change line",
        default=False,
    )
