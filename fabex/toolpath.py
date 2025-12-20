"""Fabex 'toolpath.py' © 2012 Vilem Novak

Generate toolpaths from path chunks.
"""

# Path Generaton
import time

import bpy

from .constants import USE_PROFILER
from .exception import CamException
from .gcode.gcode_export import export_gcode_path

# 3 Axis Strategies
from .strategies.block import block
from .strategies.carve import carve
from .strategies.circles import circles
from .strategies.crazy import crazy
from .strategies.cross import cross
from .strategies.cutout import cutout
from .strategies.curve_to_path import curve
from .strategies.drill import drill
from .strategies.medial_axis import medial_axis
from .strategies.outline_fill import outline_fill
from .strategies.pencil import pencil
from .strategies.project_curve import projected_curve
from .strategies.pocket import pocket
from .strategies.parallel import parallel
from .strategies.spiral import spiral
from .strategies.waterline import waterline

# 4 Axis Strategies
from .strategies.parallel_4_axis import parallel_four_axis
from .strategies.helix_4_axis import helix_four_axis

from .utilities.async_utils import progress_async
from .utilities.bounds_utils import get_bounds
from .utilities.index_utils import (
    cleanup_indexed,
    prepare_indexed,
)
from .utilities.logging_utils import log
from .utilities.operation_utils import (
    get_operation_sources,
    get_change_data,
    check_memory_limit,
)
from .utilities.simple_utils import progress


async def get_path(context, operation):
    """Calculate the path for a given operation in a specified context.

    This function performs various calculations to determine the path based
    on the operation's parameters and context. It checks for changes in the
    operation's data and updates relevant tags accordingly. Depending on the
    number of machine axes specified in the operation, it calls different
    functions to handle 3-axis, 4-axis, or 5-axis operations. Additionally,
    if automatic export is enabled, it exports the generated G-code path.

    Args:
        context: The context in which the operation is being performed.
        operation: An object representing the operation with various
            attributes such as machine_axes, strategy, and
            auto_export.
    """
    # should do all path calculations.
    t = time.process_time()

    if operation.feedrate > context.scene.cam_machine.feedrate_max:
        raise CamException("Operation Feedrate is greater than Machine Maximum!")

    # these tags are for caching of some of the results. Not working well still
    # - although it can save a lot of time during calculation...

    chd = get_change_data(operation)

    if operation.change_data != chd:  # or 1:
        operation.update_offset_image_tag = True
        operation.update_z_buffer_image_tag = True
        operation.change_data = chd

    operation.update_silhouette_tag = True
    operation.update_ambient_tag = True
    operation.update_bullet_collision_tag = True

    indexed_five_axis = operation.machine_axes == "5" and operation.strategy_5_axis == "INDEXED"
    indexed_four_axis = operation.machine_axes == "4" and operation.strategy_4_axis == "INDEXED"

    get_operation_sources(operation)

    operation.info.warnings = ""
    check_memory_limit(operation)

    log.info(f"Operation Axes: {operation.machine_axes}")

    if operation.machine_axes == "3":
        if USE_PROFILER == True:  # profiler
            import cProfile

            pr = cProfile.Profile()
            pr.enable()
            await get_path_3_axis(context, operation)
            pr.disable()
            pr.dump_stats(time.strftime("Fabex_%Y%m%d_%H%M.prof"))
        else:
            await get_path_3_axis(context, operation)

    elif indexed_five_axis or indexed_four_axis:
        # 5 axis operations are now only 3 axis operations that get rotated...
        operation.orientation = prepare_indexed(operation)  # TODO RENAME THIS

        await get_path_3_axis(context, operation)  # TODO RENAME THIS

        cleanup_indexed(operation)  # TODO RENAME THIS
    # transform5axisIndexed
    elif operation.machine_axes == "4":
        await get_path_4_axis(context, operation)

    # export gcode if automatic.
    if operation.auto_export:
        path_name = context.scene.cam_names.path_name_full
        if bpy.data.objects.get(path_name) is None:
            return
        p = bpy.data.objects[path_name]
        name = operation.name if operation.link_operation_file_names else operation.filename
        export_gcode_path(name, [p.data], [operation])

    operation.changed = False
    t1 = time.process_time() - t
    progress("Total Time: ", t1)


# this is the main function.
async def get_path_3_axis(context, operation):
    """Generate a machining path based on the specified operation strategy.

    This function evaluates the provided operation's strategy and generates
    the corresponding machining path. It supports various strategies such as
    'CUTOUT', 'CURVE', 'PROJECTED_CURVE', 'POCKET', and others. Depending on
    the strategy, it performs specific calculations and manipulations on the
    input data to create a path that can be used for machining operations.
    The function handles different strategies by calling appropriate methods
    from the `strategy` module and processes the path samples accordingly.
    It also manages the generation of chunks, which represent segments of
    the machining path, and applies any necessary transformations based on
    the operation's parameters.

    Args:
        context (bpy.context): The Blender context containing scene information.
        operation (Operation): An object representing the machining operation,
            which includes strategy and other relevant parameters.

    Returns:
        None: This function does not return a value but modifies the state of
        the operation and context directly.
    """

    s = bpy.context.scene
    o = operation
    get_bounds(o)
    tw = time.time()

    strategy_from_operation = {
        "BLOCK": block,
        "CARVE": carve,
        "CIRCLES": circles,
        "CRAZY": crazy,
        "CROSS": cross,
        "CUTOUT": cutout,
        "CURVE": curve,
        "DRILL": drill,
        "MEDIAL_AXIS": medial_axis,
        "OUTLINEFILL": outline_fill,
        "PENCIL": pencil,
        "PROJECTED_CURVE": projected_curve,
        "POCKET": pocket,
        "PARALLEL": parallel,
        "SPIRAL": spiral,
        "WATERLINE": waterline,
    }

    await strategy_from_operation[o.strategy](o)

    await progress_async(f"Done", time.time() - tw, "s")


async def get_path_4_axis(context, operation):
    """Generate a path for a specified axis based on the given operation.

    This function retrieves the bounds of the operation and checks the
    strategy associated with the axis. If the strategy is one of the
    specified types ('PARALLELR', 'PARALLEL', 'HELIX', 'CROSS'), it
    generates path samples and processes them into chunks for meshing. The
    function utilizes various helper functions to achieve this, including
    obtaining layers and sampling chunks.

    Args:
        context: The context in which the operation is executed.
        operation: An object that contains the strategy and other
            necessary parameters for generating the path.

    Returns:
        None: This function does not return a value but modifies
            the state of the operation by processing chunks for meshing.
    """

    s = bpy.context.scene
    o = operation
    get_bounds(o)
    tw = time.time()

    strategy_from_operation = {
        "PARALLEL": parallel_four_axis,
        "PARALLELR": parallel_four_axis,
        "HELIX": helix_four_axis,
    }

    await strategy_from_operation[o.strategy_4_axis](o)

    await progress_async(f"Done", time.time() - tw, "s")
