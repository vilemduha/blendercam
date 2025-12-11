"""Fabex 'gcodepath.py' © 2012 Vilem Novak

Generate and Export G-Code based on scene, machine, chain, operation and path settings.
"""

# G-code Generaton
from importlib import import_module
from math import (
    ceil,
    floor,
    pi,
    sqrt,
)
import time

import numpy
from shapely.geometry import Polygon

import bpy
from mathutils import Euler, Vector

from . import strategy
from .bridges import use_bridges
from .cam_chunk import (
    curve_to_chunks,
    limit_chunks,
    chunks_coherency,
    shapely_to_chunks,
    sample_chunks,
    sample_chunks_n_axis,
    get_operation_silhouette,
    get_ambient,
    connect_chunks_low,
    sort_chunks,
    oclGetWaterline,
    image_to_shapely,
    crazy_stroke_image_binary,
    get_offset_image_cavities,
)
from .exception import CamException
from .constants import (
    IMPERIAL_CORRECTION,
    METRIC_CORRECTION,
    ROTATION_CORRECTION,
    USE_PROFILER,
)
from .exception import CamException
from .pattern import get_path_pattern, get_path_pattern_4_axis
from .post_processors import iso

from .utilities.async_utils import progress_async
from .utilities.bounds_utils import get_bounds
from .utilities.chunk_utils import (
    chunks_refine,
    parent_child_distance,
)
from .utilities.image_utils import (
    prepare_area,
)
from .utilities.index_utils import (
    cleanup_indexed,
    prepare_indexed,
)
from .utilities.logging_utils import log
from .utilities.operation_utils import get_operation_sources
from .utilities.simple_utils import (
    progress,
    safe_filename,
    unit_value_to_string,
)


def point_on_line(a, b, c, tolerance):
    """Determine if the angle between two vectors is within a specified
    tolerance.

    This function checks if the angle formed by two vectors, defined by
    points `b` and `c` relative to point `a`, is less than or equal to a
    given tolerance. It converts the points into vectors, calculates the dot
    product, and then computes the angle between them using the arccosine
    function. If the angle exceeds the specified tolerance, the function
    returns False; otherwise, it returns True.

    Args:
        a (numpy.ndarray): The origin point as a vector.
        b (numpy.ndarray): The first point as a vector.
        c (numpy.ndarray): The second point as a vector.
        tolerance (float): The maximum allowable angle (in degrees) between the vectors.

    Returns:
        bool: True if the angle between vectors b and c is within the specified
            tolerance,
            False otherwise.
    """

    b = b - a  # convert to vector by subtracting origin
    c = c - a
    dot_pr = b.dot(c)  # b dot c
    norms = numpy.linalg.norm(b) * numpy.linalg.norm(c)  # find norms
    # Ensure that values aren't == 0, which would cause
    # a Divide by Zero error on the next line
    if not dot_pr == 0 and not norms == 0:
        # find angle between the two vectors
        angle = numpy.rad2deg(numpy.arccos(dot_pr / norms))
        if angle > tolerance:
            return False
        else:
            return True
    else:
        return True


def export_gcode_path(filename, vertslist, operations):
    """Exports G-code using the Heeks NC Adopted Library.

    This function generates G-code from a list of vertices and operations
    specified by the user. It handles various post-processor settings based
    on the machine configuration and can split the output into multiple
    files if the total number of operations exceeds a specified limit. The
    G-code is tailored for different machine types and includes options for
    tool changes, spindle control, and various movement commands.

    Args:
        filename (str): The name of the file to which the G-code will be exported.
        vertslist (list): A list of mesh objects containing vertex data.
        operations (list): A list of operations to be performed, each containing
            specific parameters for G-code generation.

    Returns:
        None: This function does not return a value; it writes the G-code to a file.
    """
    log.debug("EXPORT")
    progress("~ Exporting G-code File ~")

    t = time.time()
    s = bpy.context.scene
    m = s.cam_machine

    enable_dust = False
    enable_hold = False
    enable_mist = False
    # find out how many files will be done:
    split = False
    totops = 0
    findex = 0

    if m.eval_splitting:  # detect whether splitting will happen
        for mesh in vertslist:
            totops += len(mesh.vertices)
        log.info(f"Total Operations: {totops}")

        if totops > m.split_limit:
            split = True
            filesnum = ceil(totops / m.split_limit)
            log.info(f"Output Files: {filesnum}")
    else:
        log.info("Output Files: 1")

    if s.cam_names.default_export_location == "":
        filepath = bpy.data.filepath
        basename = bpy.path.basename
        basefilename = filepath[: -len(basename(filepath))] + safe_filename(filename)
    else:
        basefilename = s.cam_names.default_export_location + safe_filename(filename)

    processor_extension = {
        "ANILAM": ("anilam_crusader_m", ".tap"),
        "CENTROID": ("centroid1", ".tap"),
        "EMC": ("emc2b", ".ngc"),
        "FADAL": ("fadal", ".tap"),
        "GRAVOS": ("gravos", ".nc"),
        "GRBL": ("grbl", ".gcode"),
        "HM50": ("hm50", ".tap"),
        "HEIDENHAIN": ("heiden", ".H"),
        "HEIDENHAIN530": ("heiden530", ".H"),
        "ISO": ("iso", ".tap"),
        "LYNX_OTTER_O": ("lynx_otter_o", ".nc"),
        "MACH3": ("mach3", ".tap"),
        "SHOPBOT MTC": ("shopbot_mtc", ".sbp"),
        "SIEGKX1": ("siegkx1", ".tap"),
        "TNC151": ("tnc151", ".tap"),
        "WIN-PC": ("winpc", ".din"),
    }

    module = f".post_processors.{processor_extension[m.post_processor][0]}"
    postprocessor = import_module(module, __package__)
    extension = processor_extension[m.post_processor][1]

    if s.unit_settings.system == "METRIC":
        unitcorr = METRIC_CORRECTION
    elif s.unit_settings.system == "IMPERIAL":
        unitcorr = IMPERIAL_CORRECTION
    else:
        unitcorr = 1

    rotcorr = ROTATION_CORRECTION

    def start_new_file():
        """Start a new file for G-code generation.

        This function initializes a new file for G-code output based on the
        specified parameters. It constructs the filename using a base name, an
        optional index, and a file extension. The function also configures the
        post-processor settings based on user overrides and the selected unit
        system (metric or imperial). Finally, it begins the G-code program and
        sets the necessary configurations for the output.

        Returns:
            Creator: An instance of the post-processor Creator class configured for
            G-code generation.
        """

        fileindex = "_" + str(findex) if split else ""
        filename = basefilename + fileindex + extension

        log.info(f"Writing: {filename}")
        log.info("-")

        c = postprocessor.Creator()

        # process user overrides for post processor settings
        if isinstance(c, iso.Creator):
            c.output_block_numbers = m.output_block_numbers
            c.start_block_number = m.start_block_number
            c.block_number_increment = m.block_number_increment

        c.output_tool_definitions = m.output_tool_definitions
        c.output_tool_change = m.output_tool_change
        c.output_G43_on_tool_change_line = m.output_G43_on_tool_change

        c.file_open(filename)

        # unit system correction
        if s.unit_settings.system == "METRIC":
            c.metric()
        elif s.unit_settings.system == "IMPERIAL":
            c.imperial()

        # start program
        c.program_begin(0, filename)
        c.flush_nc()
        c.comment("G-code Generated with Fabex and NC library")
        # absolute coordinates
        c.absolute()
        # work-plane, by now always xy,
        c.set_plane(0)
        c.flush_nc()

        return c

    c = start_new_file()
    last_cutter = None
    processedops = 0
    last = Vector((0, 0, 0))
    cut_distance = 0

    for i, o in enumerate(operations):
        if o.output_header:
            lines = o.gcode_header.split(";")

            for aline in lines:
                c.write(aline + "\n")

        free_height = o.movement.free_height

        if o.movement.useG64:
            c.set_path_control_mode(2, round(o.movement.G64 * 1000, 5), 0)

        mesh = vertslist[i]
        verts = mesh.vertices[:]

        if o.machine_axes != "3":
            rots = mesh.shape_keys.key_blocks["rotations"].data

        # spindle rpm and direction
        if o.movement.spindle_rotation == "CW":
            spdir_clockwise = True
        else:
            spdir_clockwise = False

        # write tool, not working yet probably
        # print (last_cutter)
        if m.output_tool_change and last_cutter != [
            o.cutter_id,
            o.cutter_diameter,
            o.cutter_type,
            o.cutter_flutes,
        ]:
            if m.output_tool_change:
                c.tool_change(o.cutter_id)

        if m.output_tool_definitions:
            c.comment(
                "Tool: D = %s type %s flutes %s"
                % (
                    unit_value_to_string(o.cutter_diameter, 4),
                    o.cutter_type,
                    o.cutter_flutes,
                )
            )

        c.flush_nc()
        last_cutter = [o.cutter_id, o.cutter_diameter, o.cutter_type, o.cutter_flutes]

        if o.cutter_type not in ["LASER", "PLASMA"]:
            if o.enable_hold:
                c.write("(Hold Down)\n")
                lines = o.gcode_start_hold_cmd.split(";")
                for aline in lines:
                    c.write(aline + "\n")
                enable_hold = True
                stop_hold = o.gcode_stop_hold_cmd
            if o.enable_mist:
                c.write("(Mist)\n")
                lines = o.gcode_start_mist_cmd.split(";")
                for aline in lines:
                    c.write(aline + "\n")
                enable_mist = True
                stop_mist = o.gcode_stop_mist_cmd

            c.spindle(o.spindle_rpm, spdir_clockwise)  # start spindle
            c.write_spindle()
            c.flush_nc()
            c.write("\n")

            if o.enable_dust:
                c.write("(Dust Collector)\n")
                lines = o.gcode_start_dust_cmd.split(";")
                for aline in lines:
                    c.write(aline + "\n")
                enable_dust = True
                stop_dust = o.gcode_stop_dust_cmd

        if m.spindle_start_time > 0:
            c.dwell(m.spindle_start_time)

        # raise the spindle to safe height
        fmh = round(free_height * unitcorr, 2)

        if o.cutter_type not in ["LASER", "PLASMA"]:
            c.write("G00 Z" + str(fmh) + "\n")

        if o.enable_a_axis:
            if o.rotation_a == 0:
                o.rotation_a = 0.0001
            c.rapid(a=o.rotation_a * 180 / pi)

        if o.enable_b_axis:
            if o.rotation_b == 0:
                o.rotation_b = 0.0001
            c.rapid(a=o.rotation_b * 180 / pi)

        c.write("\n")
        c.flush_nc()

        m = bpy.context.scene.cam_machine

        millfeedrate = min(o.feedrate, m.feedrate_max)

        millfeedrate = unitcorr * max(millfeedrate, m.feedrate_min)
        plungefeedrate = millfeedrate * o.plunge_feedrate / 100
        freefeedrate = m.feedrate_max * unitcorr
        fadjust = False
        if (
            o.do_simulation_feedrate
            and mesh.shape_keys is not None
            and mesh.shape_keys.key_blocks.find("feedrates") != -1
        ):
            shapek = mesh.shape_keys.key_blocks["feedrates"]
            fadjust = True

        if m.use_position_definitions:  # dhull
            last = Vector((m.starting_position.x, m.starting_position.y, m.starting_position.z))

        lastrot = Euler((0, 0, 0))
        duration = 0.0
        f = 0.1123456  # nonsense value, so first feedrate always gets written
        fadjustval = 1  # if simulation load data is Not present
        downvector = Vector((0, 0, -1))
        plungelimit = pi / 2 - o.plunge_angle
        scale_graph = 0.05  # warning this has to be same as in export in utils!!!!
        ii = 0
        offline = 0
        online = 0
        cut = True  # active cut variable for laser or plasma
        shapes = 0

        for vi, vert in enumerate(verts):
            # skip the first vertex if this is a chained operation
            # ie: outputting more than one operation
            # otherwise the machine gets sent back to 0,0 for each operation which is unecessary
            shapes += 1  # Count amount of shapes

            if i > 0 and vi == 0:
                continue
            v = vert.co
            # redundant point on line detection
            if o.remove_redundant_points and o.strategy != "DRILL":
                nextv = v
                if ii == 0:
                    firstv = v  # only happens once
                elif ii == 1:
                    middlev = v
                else:
                    if point_on_line(firstv, middlev, nextv, o.simplify_tolerance / 1000):
                        middlev = nextv
                        online += 1
                        continue
                    else:  # create new start point with the last tested point
                        ii = 0
                        offline += 1
                        firstv = nextv
                ii += 1
            # end of redundant point on line detection
            if o.machine_axes != "3":
                v = v.copy()  # we rotate it so we need to copy the vector
                r = Euler(rots[vi].co)
                # conversion to N-axis coordinates
                # this seems to work correctly for 4 axis.
                rcompensate = r.copy()
                rcompensate.x = -r.x
                rcompensate.y = -r.y
                rcompensate.z = -r.z
                v.rotate(rcompensate)

                if r.x == lastrot.x:
                    ra = None
                else:
                    ra = r.x * rotcorr

                if r.y == lastrot.y:
                    rb = None
                else:
                    rb = r.y * rotcorr

            if vi > 0 and v.x == last.x:
                vx = None
            else:
                vx = v.x * unitcorr
            if vi > 0 and v.y == last.y:
                vy = None
            else:
                vy = v.y * unitcorr
            if vi > 0 and v.z == last.z:
                vz = None
            else:
                vz = v.z * unitcorr

            if fadjust:
                fadjustval = shapek.data[vi].co.z / scale_graph

            vect = v - last
            l = vect.length
            if vi > 0 and l > 0 and downvector.angle(vect) < plungelimit:
                if f != plungefeedrate or (fadjust and fadjustval != 1):
                    f = plungefeedrate * fadjustval
                    c.feedrate(f)

                if o.machine_axes == "3":
                    if o.cutter_type in ["LASER", "PLASMA"]:
                        if not cut:
                            if o.cutter_type == "LASER":
                                c.write("(*************dwell->laser on)\n")
                                c.write("G04 P" + str(round(o.laser_delay, 2)) + "\n")
                                c.write(o.laser_on + "\n")
                            elif o.cutter_type == "PLASMA":
                                c.write("(*************dwell->PLASMA on)\n")
                                plasma_delay = round(o.plasma_delay, 5)
                                if plasma_delay > 0:
                                    c.write("G04 P" + str(plasma_delay) + "\n")
                                c.write(o.plasma_on + "\n")
                                plasma_dwell = round(o.plasma_dwell, 5)
                                if plasma_dwell > 0:
                                    c.write("G04 P" + str(plasma_dwell) + "\n")
                            cut = True
                    else:
                        c.feed(x=vx, y=vy, z=vz)
                else:
                    c.feed(x=vx, y=vy, z=vz, a=ra, b=rb)

            elif v.z >= free_height or vi == 0:
                if f != freefeedrate:
                    f = freefeedrate
                    c.feedrate(f)

                if o.machine_axes == "3":
                    if o.cutter_type in ["LASER", "PLASMA"]:
                        if cut:
                            if o.cutter_type == "LASER":
                                c.write("(**************laser off)\n")
                                c.write(o.laser_off + "\n")
                            elif o.cutter_type == "PLASMA":
                                c.write("(**************Plasma off)\n")
                                c.write(o.plasma_off + "\n")

                            cut = False
                        c.rapid(x=vx, y=vy)
                    else:
                        c.rapid(x=vx, y=vy, z=vz)
                        #  this is to evaluate operation time and adds a feedrate for fast moves
                        if vz is not None:
                            # compensate for multiple fast move accelerations
                            f = plungefeedrate * fadjustval * 0.35
                        if vx is not None or vy is not None:
                            f = freefeedrate * 0.8  # compensate for free feedrate acceleration
                else:
                    c.rapid(x=vx, y=vy, z=vz, a=ra, b=rb)

            else:
                if f != millfeedrate or (fadjust and fadjustval != 1):
                    f = millfeedrate * fadjustval
                    c.feedrate(f)

                if o.machine_axes == "3":
                    c.feed(x=vx, y=vy, z=vz)
                else:
                    c.feed(x=vx, y=vy, z=vz, a=ra, b=rb)

            cut_distance += vect.length * unitcorr
            vector_duration = vect.length / f
            duration += vector_duration
            last = v

            if o.machine_axes != "3":
                lastrot = r

            processedops += 1

            if split and processedops > m.split_limit:
                c.rapid(x=last.x * unitcorr, y=last.y * unitcorr, z=free_height * unitcorr)
                c.program_end()
                findex += 1
                c.file_close()
                c = start_new_file()
                c.flush_nc()
                c.comment(
                    "Tool change - D = %s type %s flutes %s"
                    % (unit_value_to_string(o.cutter_diameter, 4), o.cutter_type, o.cutter_flutes)
                )
                c.tool_change(o.cutter_id)
                c.spindle(o.spindle_rpm, spdir_clockwise)
                c.write_spindle()
                c.flush_nc()

                if m.spindle_start_time > 0:
                    c.dwell(m.spindle_start_time)
                    c.flush_nc()

                c.feedrate(unitcorr * o.feedrate)
                c.rapid(x=last.x * unitcorr, y=last.y * unitcorr, z=free_height * unitcorr)
                c.rapid(x=last.x * unitcorr, y=last.y * unitcorr, z=last.z * unitcorr)
                processedops = 0

        if o.remove_redundant_points and o.strategy != "DRILL":
            log.info(f"Online: {online}")
            log.info(f"Offline: {offline}")
            log.info(f"Removal: {round(online / (offline + online) * 100, 1)}%")
        c.feedrate(unitcorr * o.feedrate)

        if o.output_trailer:
            lines = o.gcode_trailer.split(";")
            for aline in lines:
                c.write(aline + "\n")

    o.info.duration = duration * unitcorr
    log.info(f"Total Time: {round(o.info.duration * 60)} seconds")
    if bpy.context.scene.unit_settings.system == "METRIC":
        unit_distance = "m"
        cut_distance /= 1000
    else:
        unit_distance = "feet"
        cut_distance /= 12

    log.info(f"Cut Distance: {round(cut_distance, 3)} {unit_distance}")
    if enable_dust:
        c.write(stop_dust + "\n")
    if enable_hold:
        c.write(stop_hold + "\n")
    if enable_mist:
        c.write(stop_mist + "\n")

    c.program_end()
    c.file_close()
    log.info(f"{time.time() - t}")


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

    get_operation_sources(operation)

    operation.info.warnings = ""
    check_memory_limit(operation)

    log.info(f"Operation Axes: {operation.machine_axes}")

    if operation.machine_axes == "3":
        if USE_PROFILER == True:  # profiler
            import cProfile
            import pstats
            import io

            pr = cProfile.Profile()
            pr.enable()
            await get_path_3_axis(context, operation)
            pr.disable()
            pr.dump_stats(time.strftime("Fabex_%Y%m%d_%H%M.prof"))
        else:
            await get_path_3_axis(context, operation)

    elif (operation.machine_axes == "5" and operation.strategy_5_axis == "INDEXED") or (
        operation.machine_axes == "4" and operation.strategy_4_axis == "INDEXED"
    ):
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


def get_change_data(o):
    """Check if object properties have changed to determine if image updates
    are needed.

    This function inspects the properties of objects specified by the input
    parameter to see if any changes have occurred. It concatenates the
    location, rotation, and dimensions of the relevant objects into a single
    string, which can be used to determine if an image update is necessary
    based on changes in the object's state.

    Args:
        o (object): An object containing properties that specify the geometry source
            and relevant object or collection names.

    Returns:
        str: A string representation of the location, rotation, and dimensions of
            the specified objects.
    """
    changedata = ""
    obs = []
    if o.geometry_source == "OBJECT":
        obs = [bpy.data.objects[o.object_name]]
    elif o.geometry_source == "COLLECTION":
        obs = bpy.data.collections[o.collection_name].objects
    for ob in obs:
        changedata += str(ob.location)
        changedata += str(ob.rotation_euler)
        changedata += str(ob.dimensions)

    return changedata


def check_memory_limit(o):
    """Check and adjust the memory limit for an object.

    This function calculates the resolution of an object based on its
    dimensions and the specified pixel size. If the calculated resolution
    exceeds the defined memory limit, it adjusts the pixel size accordingly
    to reduce the resolution. A warning message is appended to the object's
    info if the pixel size is modified.

    Args:
        o (object): An object containing properties such as max, min, optimisation, and
            info.

    Returns:
        None: This function modifies the object's properties in place and does not
            return a value.
    """

    sx = o.max.x - o.min.x
    sy = o.max.y - o.min.y
    resx = sx / o.optimisation.pixsize
    resy = sy / o.optimisation.pixsize
    res = resx * resy
    limit = o.optimisation.imgres_limit * 1000000

    if res > limit:
        ratio = res / limit
        o.optimisation.pixsize = o.optimisation.pixsize * sqrt(ratio)
        log.warning("!!! Memory Error !!!")
        log.warning("Memory Limit Exceeded!")
        log.warning(f"Detail Size Increased to {round(o.optimisation.pixsize, 5)}")
        o.info.warnings += " \n!!! Memory Error !!!\n"
        o.info.warnings += "Memory Limit Exceeded!\n"
        o.info.warnings += f"Detail Size Increased to {round(o.optimisation.pixsize, 5)}\n"
        log.info("Changing Sampling Resolution to %f" % o.optimisation.pixsize)


# this is the main function.
# FIXME: split strategies into separate file!
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

    if o.strategy == "CUTOUT":
        await strategy.cutout(o)

    elif o.strategy == "CURVE":
        await strategy.curve(o)

    elif o.strategy == "PROJECTED_CURVE":
        await strategy.project_curve(s, o)

    elif o.strategy == "POCKET":
        await strategy.pocket(o)

    elif o.strategy in [
        "PARALLEL",
        "CROSS",
        "BLOCK",
        "SPIRAL",
        "CIRCLES",
        "OUTLINEFILL",
        "CARVE",
        "PENCIL",
        "CRAZY",
    ]:
        if o.strategy == "CARVE":
            pathSamples = []
            ob = bpy.data.objects[o.curve_source]
            pathSamples.extend(curve_to_chunks(ob))
            # sort before sampling
            pathSamples = await sort_chunks(pathSamples, o)
            pathSamples = chunks_refine(pathSamples, o)
        elif o.strategy == "PENCIL":
            await prepare_area(o)
            get_ambient(o)
            pathSamples = get_offset_image_cavities(o, o.offset_image)
            pathSamples = limit_chunks(pathSamples, o)
            # sort before sampling
            pathSamples = await sort_chunks(pathSamples, o)
        elif o.strategy == "CRAZY":
            await prepare_area(o)
            # pathSamples = crazyStrokeImage(o)
            # this kind of worked and should work:
            millarea = o.zbuffer_image < o.min_z + 0.000001
            avoidarea = o.offset_image > o.min_z + 0.000001

            pathSamples = crazy_stroke_image_binary(o, millarea, avoidarea)
            #####
            pathSamples = await sort_chunks(pathSamples, o)
            pathSamples = chunks_refine(pathSamples, o)

        else:
            if o.strategy == "OUTLINEFILL":
                get_operation_silhouette(o)

            pathSamples = get_path_pattern(o)

            if o.strategy == "OUTLINEFILL":
                pathSamples = await sort_chunks(pathSamples, o)
                # have to be sorted once before, because of the parenting inside of samplechunks

            if o.strategy in ["BLOCK", "SPIRAL", "CIRCLES"]:
                pathSamples = await connect_chunks_low(pathSamples, o)

        chunks = []
        layers = strategy.get_layers(o, o.max_z, o.min.z)

        log.info(f"Sampling Object: {o.name}")
        chunks.extend(await sample_chunks(o, pathSamples, layers))
        log.info("Sampling Finished Successfully")

        if o.strategy == "PENCIL":
            chunks = chunks_coherency(chunks)
            log.info("Coherency Check")

        if o.strategy in ["PARALLEL", "CROSS", "PENCIL", "OUTLINEFILL"]:
            log.info("Sorting")
            chunks = await sort_chunks(chunks, o)
            if o.strategy == "OUTLINEFILL":
                chunks = await connect_chunks_low(chunks, o)
        if o.movement.ramp:
            for ch in chunks:
                ch.ramp_zig_zag(ch.zstart, None, o)

        if o.strategy == "CARVE":
            for ch in chunks:
                ch.offset_z(-o.carve_depth)

        if o.use_bridges:
            log.info(chunks)
            for bridge_chunk in chunks:
                use_bridges(bridge_chunk, o)

        strategy.chunks_to_mesh(chunks, o)

    elif o.strategy == "WATERLINE" and o.optimisation.use_opencamlib:
        get_ambient(o)
        chunks = []
        await oclGetWaterline(o, chunks)
        chunks = limit_chunks(chunks, o)
        if (o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CW") or (
            o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CCW"
        ):
            for ch in chunks:
                ch.reverse()

        strategy.chunks_to_mesh(chunks, o)

    elif o.strategy == "WATERLINE" and not o.optimisation.use_opencamlib:
        topdown = True
        chunks = []
        await progress_async("Retrieving Object Slices")
        await prepare_area(o)
        layerstep = 1000000000
        if o.use_layers:
            layerstep = floor(o.stepdown / o.slice_detail)
            if layerstep == 0:
                layerstep = 1

        # for projection of filled areas
        layerstart = o.max.z  #
        layerend = o.min.z  #
        layers = [[layerstart, layerend]]
        #######################
        nslices = ceil(abs((o.min_z - o.max_z) / o.slice_detail))
        lastslice = Polygon()  # polyversion
        layerstepinc = 0

        slicesfilled = 0
        get_ambient(o)

        for h in range(0, nslices):
            layerstepinc += 1
            slicechunks = []
            # lower the layer by the skin value so the slice gets done at the tip of the tool
            z = o.min_z + h * o.slice_detail - o.skin
            if h == 0:
                z += 0.0000001
                # if people do mill flat areas, this helps to reach those...
                # otherwise first layer would actually be one slicelevel above min z.

            islice = o.offset_image > z
            slicepolys = image_to_shapely(o, islice, with_border=True)

            poly = Polygon()  # polygversion
            lastchunks = []

            for p in slicepolys.geoms:
                poly = poly.union(p)  # polygversion TODO: why is this added?
                nchunks = shapely_to_chunks(p, z + o.skin)
                nchunks = limit_chunks(nchunks, o, force=True)
                lastchunks.extend(nchunks)
                slicechunks.extend(nchunks)
            if len(slicepolys.geoms) > 0:
                slicesfilled += 1

            #
            if o.waterline_fill:
                layerstart = min(o.max_z, z + o.slice_detail)  #
                layerend = max(o.min.z, z - o.slice_detail)  #
                layers = [[layerstart, layerend]]
                #####################################
                # fill top slice for normal and first for inverse, fill between polys
                if not lastslice.is_empty or (
                    o.inverse and not poly.is_empty and slicesfilled == 1
                ):
                    restpoly = None
                    if not lastslice.is_empty:  # between polys
                        if o.inverse:
                            restpoly = poly.difference(lastslice)
                        else:
                            restpoly = lastslice.difference(poly)

                    if (not o.inverse and poly.is_empty and slicesfilled > 0) or (
                        o.inverse and not poly.is_empty and slicesfilled == 1
                    ):
                        # first slice fill
                        restpoly = lastslice

                    restpoly = restpoly.buffer(
                        -o.distance_between_paths, resolution=o.optimisation.circle_detail
                    )

                    fillz = z
                    i = 0
                    while not restpoly.is_empty:
                        nchunks = shapely_to_chunks(restpoly, fillz + o.skin)
                        # project paths TODO: path projection during waterline is not working
                        if o.waterline_project:
                            nchunks = chunks_refine(nchunks, o)
                            nchunks = await sample_chunks(o, nchunks, layers)

                        nchunks = limit_chunks(nchunks, o, force=True)
                        #########################
                        slicechunks.extend(nchunks)
                        parent_child_distance(lastchunks, nchunks, o)
                        lastchunks = nchunks
                        restpoly = restpoly.buffer(
                            -o.distance_between_paths, resolution=o.optimisation.circle_detail
                        )

                        i += 1

                i = 0
                #  fill layers and last slice, last slice with inverse is not working yet
                #  - inverse millings end now always on 0 so filling ambient does have no sense.
                if (
                    (slicesfilled > 0 and layerstepinc == layerstep)
                    or (not o.inverse and not poly.is_empty and slicesfilled == 1)
                    or (o.inverse and poly.is_empty and slicesfilled > 0)
                ):
                    fillz = z
                    layerstepinc = 0

                    bound_rectangle = o.ambient
                    restpoly = bound_rectangle.difference(poly)
                    if o.inverse and poly.is_empty and slicesfilled > 0:
                        restpoly = bound_rectangle.difference(lastslice)

                    restpoly = restpoly.buffer(
                        -o.distance_between_paths, resolution=o.optimisation.circle_detail
                    )

                    i = 0

                    while not restpoly.is_empty:
                        nchunks = shapely_to_chunks(restpoly, fillz + o.skin)
                        #########################
                        nchunks = limit_chunks(nchunks, o, force=True)
                        slicechunks.extend(nchunks)
                        parent_child_distance(lastchunks, nchunks, o)
                        lastchunks = nchunks
                        restpoly = restpoly.buffer(
                            -o.distance_between_paths, resolution=o.optimisation.circle_detail
                        )
                        i += 1

                percent = int(h / nslices * 100)
                await progress_async("Waterline Layers", percent)
                lastslice = poly

            if (o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CCW") or (
                o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CW"
            ):
                for chunk in slicechunks:
                    chunk.reverse()
            slicechunks = await sort_chunks(slicechunks, o)
            if topdown:
                slicechunks.reverse()
            # project chunks in between

            chunks.extend(slicechunks)
        if topdown:
            chunks.reverse()
        strategy.chunks_to_mesh(chunks, o)

    elif o.strategy == "DRILL":
        await strategy.drill(o)

    elif o.strategy == "MEDIAL_AXIS":
        await strategy.medial_axis(o)

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

    o = operation
    get_bounds(o)
    if o.strategy_4_axis in ["PARALLELR", "PARALLEL", "HELIX", "CROSS"]:
        path_samples = get_path_pattern_4_axis(o)

        depth = path_samples[0].depth
        chunks = []

        layers = strategy.get_layers(o, 0, depth)

        chunks.extend(await sample_chunks_n_axis(o, path_samples, layers))
        strategy.chunks_to_mesh(chunks, o)
