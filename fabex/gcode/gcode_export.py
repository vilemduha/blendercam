"""Fabex 'gcodepath.py' © 2012 Vilem Novak

Generate and Export G-Code based on scene, machine, chain, operation and path settings.
"""

# G-code Generaton
from importlib import import_module
from math import (
    ceil,
    pi,
)
import time


import bpy
from mathutils import Euler, Vector

from .. import __package__ as base_package
from ..constants import (
    IMPERIAL_CORRECTION,
    METRIC_CORRECTION,
    ROTATION_CORRECTION,
)
from ..post_processors import iso

from ..utilities.compare_utils import point_on_line
from ..utilities.logging_utils import log
from ..utilities.simple_utils import (
    progress,
    safe_filename,
    unit_value_to_string,
)


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
        "USER": {"user", ".gcode"},
        "WIN-PC": ("winpc", ".din"),
    }

    module = f".post_processors.{processor_extension[m.post_processor][0]}"
    postprocessor = import_module(module, base_package)
    extension = processor_extension[m.post_processor][1]

    unit_system = s.unit_settings.system
    unitcorr = (
        METRIC_CORRECTION
        if unit_system == "METRIC"
        else IMPERIAL_CORRECTION
        if unit_system == "IMPERIAL"
        else 1
    )

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
        spdir_clockwise = True if o.movement.spindle_rotation == "CW" else False

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

                ra = None if r.x == lastrot.x else r.x * rotcorr
                rb = None if r.y == lastrot.y else r.y * rotcorr

            vx = None if vi > 0 and v.x == last.x else v.x * unitcorr
            vy = None if vi > 0 and v.y == last.y else v.y * unitcorr
            vz = None if vi > 0 and v.z == last.z else v.z * unitcorr

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
                    f"Tool change - D = {unit_value_to_string(o.cutter_diameter, 4)} type {o.cutter_type} flutes {o.cutter_flutes}"
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
