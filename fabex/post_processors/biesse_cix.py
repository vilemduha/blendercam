################################################################################
# biesse_cix.py
#
# Biesse CIX (CID3) post processor for Fabex
#
# Wraps standard ISO-style G-code as embedded ISO instructions inside a
# CIX (CID3 REL=5.0) container, matching the format Biesse's bSuite/bSolid
# accepts natively via the work list and CAD/CAM import.
#
# Confirmed against real bSuite behaviour:
#   - CID3 REL=5.0 header + MAINDATA panel block imports cleanly
#   - Standalone `BEGIN MACRO / NAME=ISO / PARAM,NAME=ISO,VALUE="..."`
#     blocks import as individual "ISO row" entries in the machining
#     operation timeline, carrying arbitrary embedded G-code text
#   - TP=<n> selects tool pocket n; TP0 releases the tool
#
# 3-axis only for now. 5-axis (G300 + B/C letters) intentionally left
# out until the indexed-rotation pipeline has been verified empirically.
################################################################################

import math

from . import nc
from .iso import Creator as IsoCreator


class Creator(IsoCreator):
    def __init__(self):
        IsoCreator.__init__(self)

        # CIX/bSuite doesn't use ISO block numbers or a program-number
        # header the way generic ISO controls do - the CID3 container
        # itself carries program identity.
        self.output_block_numbers = False
        self.output_tool_definitions = False
        self.output_comment_before_tool_change = False

        # Buffer for building up one logical line at a time before
        # wrapping it as a CIX ISO-row macro.
        self._cix_buffer = ""
        self._wrote_header = False

    ############################################################################
    # CIX container structure

    def _panel_dims(self):
        """Panel size in mm - the machine's real, configured working area.

        PREVIOUSLY computed from the bounding box across all operations
        in the scene. CONFIRMED WRONG via real testing: each operation's
        own min/max is an independent material estimate derived from
        THAT operation's own source object (Fabex's bounds_utils.py -
        for a drill operation, that's just the tiny drill-point curve),
        not a shared "panel" concept at the scene level. Since the real
        workflow only ever posts one operation at a time, relying on
        other operations' bounds being present/valid in the scene at
        export time was fundamentally the wrong model - confirmed by a
        real drill-only export reporting the drill geometry's own tiny
        size as if it were the panel.

        The machine's own configured working area is a stable,
        machine-level setting that doesn't depend on which operation is
        being posted - matches the user's own description of how bSolid
        actually works: the real geometry sits inside a real containing
        shape, not something inferred from whatever's being posted.
        """
        try:
            import bpy

            wa = bpy.context.scene.cam_machine.working_area
            return wa.x * 1000.0, wa.y * 1000.0, wa.z * 1000.0
        except Exception:
            return 0.0, 0.0, 0.0

    def _set_z_shift(self, op):
        # CIX's confirmed real convention (from the actual R370104N.cix
        # vendor file): Z=0 at the panel's TOP surface, negative Z going
        # down into material. The base framework's shift_z mechanism
        # (translate()) exists for exactly this but was never being
        # called anywhere - raw Blender Z was passing straight through
        # unshifted, meaning the output's Z=0 reference silently drifted
        # with whatever Blender's own "material Z placement" setting
        # happened to be, rather than tracking the panel's real top
        # surface. Confirmed via real testing: two different material Z
        # placement settings produced two different (both wrong) depth
        # behaviours - one plunging into the spoilboard, one plunging the
        # full tool length.
        #
        # Takes the operation being exported directly (called from
        # tool_change(), where it's already known) rather than scanning
        # cam_operations - same reasoning as _panel_dims() above: this
        # operation's own max_z is the only bounds guaranteed valid and
        # relevant for what's actually being posted.
        #
        # shift_z is added AFTER feed()/rapid() already convert to mm
        # (gcode_export.py's vz = v.z * unitcorr), so it must be supplied
        # in mm here too.
        if op is None:
            return
        try:
            self.shift_z = -op.max.z * 1000.0
        except Exception:
            pass

    def _write_cix_header(self):
        lpx, lpy, lpz = self._panel_dims()
        self.file.write("BEGIN ID CID3\n")
        self.file.write("  REL=5.0\n")
        self.file.write("END ID\n")
        self.file.write("BEGIN MAINDATA\n")
        self.file.write(f"        LPX={lpx:.4f}\n")
        self.file.write(f"        LPY={lpy:.4f}\n")
        self.file.write(f"        LPZ={lpz:.4f}\n")
        self.file.write('        MATERIAL="Fabex export"\n')
        self.file.write("        FCN=1.0000\n")
        self.file.write('        ORLST="1"\n')
        self.file.write("        SIMMETRY=0\n")
        self.file.write("        UNIQUE=1\n")
        self.file.write("END MAINDATA\n\n\n")
        self._write_geo_outline(lpx, lpy)
        self._wrote_header = True

    def _write_geo_outline(self, lpx, lpy):
        # Confirmed required via real bSuite testing (Fusion-side post,
        # same finding applies here): MAINDATA's LPX/LPY/LPZ only declares
        # bounding-box dimensions, not an actual geometry object. Without
        # a real GEO panel outline, operations attached to "the part" fail
        # with "empty geo (null) has not been imported". Simple rectangle
        # matching the panel corner-origin convention: (0,0) to (lpx,lpy).
        self.file.write("BEGIN MACRO\n")
        self.file.write("        NAME=GEO\n")
        self.file.write('        PARAM,NAME=ID,VALUE="PART1"\n')
        self.file.write("        PARAM,NAME=SIDE,VALUE=0\n")
        self.file.write('        PARAM,NAME=CRN,VALUE="1"\n')
        self.file.write("        PARAM,NAME=DP,VALUE=0\n")
        self.file.write("        PARAM,NAME=RTY,VALUE=rpNO\n")
        self.file.write('        PARAM,NAME=LAY,VALUE="GEO"\n')
        self.file.write("END MACRO\n\n")
        self.file.write("BEGIN MACRO\n")
        self.file.write("        NAME=START_POINT\n")
        self.file.write("        PARAM,NAME=ID,VALUE=1\n")
        self.file.write("        PARAM,NAME=X,VALUE=0\n")
        self.file.write("        PARAM,NAME=Y,VALUE=0\n")
        self.file.write("        PARAM,NAME=Z,VALUE=0\n")
        self.file.write("END MACRO\n\n")
        segments = [(2, lpx, 0.0), (3, lpx, lpy), (4, 0.0, lpy), (5, 0.0, 0.0)]
        for seg_id, xe, ye in segments:
            self.file.write("BEGIN MACRO\n")
            self.file.write("        NAME=LINE_EP\n")
            self.file.write(f"        PARAM,NAME=ID,VALUE={seg_id}\n")
            self.file.write(f"        PARAM,NAME=XE,VALUE={xe:.4f}\n")
            self.file.write(f"        PARAM,NAME=YE,VALUE={ye:.4f}\n")
            self.file.write("        PARAM,NAME=ZS,VALUE=0\n")
            self.file.write("        PARAM,NAME=ZE,VALUE=0\n")
            self.file.write("END MACRO\n\n")
        self.file.write("BEGIN MACRO\n")
        self.file.write("        NAME=ENDPATH\n")
        self.file.write("        PARAM,NAME=ID,VALUE=6\n")
        self.file.write("END MACRO\n\n")

    def _emit_iso_row(self, line):
        line = line.strip()
        if not line:
            return
        # CIX VALUE strings use doubled double-quotes to escape a literal quote
        escaped = line.replace('"', '""')
        self.file.write("BEGIN MACRO\n")
        self.file.write("        NAME=ISO\n")
        self.file.write(f'        PARAM,NAME=ISO,VALUE="{escaped}"\n')
        self.file.write("END MACRO\n\n")

    ############################################################################
    # Override the low-level write() so every accumulated line gets wrapped
    # as its own CIX ISO-row macro instead of written as raw text.

    def write(self, s):
        if self.output_disabled:
            return
        if not self._wrote_header:
            self._write_cix_header()
        self._cix_buffer += s
        while "\n" in self._cix_buffer:
            line, self._cix_buffer = self._cix_buffer.split("\n", 1)
            self._emit_iso_row(line)
        if "\n" in s:
            self.start_of_line = s[-1] == "\n"

    def writem(self, a):
        # nc.Creator.writem() bypasses write() entirely and goes straight
        # to self.file - iso.py's feed()/rapid() use this for every axis
        # word (X/Y/Z/A/B/C), so without this override every coordinate
        # would slip past the CIX-wrapping logic above.
        #
        # Reverted to the original "".join(a) - now that SPACE() itself
        # is fixed to always return a real space (the actual root cause,
        # see SPACE() override below), this join is correct again:
        # calls look like [SPACE(), "Z", "-10"] where SPACE() already
        # contributes the needed leading separator and the letter+value
        # must concatenate directly into "Z-10". An earlier attempt to
        # fix this by always joining with a space here was an
        # overcorrection - it fixed nothing SPACE() didn't already fix,
        # and actively broke this case by inserting an unwanted space
        # between the axis letter and its value ("Z -10" instead of
        # "Z-10"), confirmed via a real "bad instruction beginning" error.
        self.write("".join(a))

    def SPACE(self):
        # ROOT CAUSE of the G17G90/S15000M03/G00X0Y0Z10 concatenation
        # bugs: the base framework's SPACE()/SPACE_STR() always return
        # "" (empty), a deliberate design choice for dialects where
        # letter-prefixed words are self-delimiting (X10Y20 parses fine
        # without a literal space in many controls). Confirmed via real
        # machine errors on both this post and the Fusion-side post that
        # Biesse's CID3 dialect does NOT tolerate this - not even for
        # same-letter pairs (G17/G90) or different-letter pairs (S/M).
        # Always return a real space so every write_preps()/Address.write()
        # call site throughout the inherited codebase gets correct
        # separation, not just the axis-word case writem() already covers.
        return " "

    ############################################################################
    # Program start/end - CID3's own header/MAINDATA replaces the usual
    # O-number program header, and we skip the generic M02 in favour of
    # just releasing the tool (TP0), matching the vendor sample pattern.

    def program_begin(self, id, name=""):
        # Header is written lazily on first real write() call, so nothing
        # extra is needed here - just record identity for reference.
        self.program_id = id
        self.program_name = name

    def write_wfl_macro(self, cangle_rad, tilt_rad, origin=(0.0, 0.0, 0.0)):
        # Native CIX WFL macro - NOT wrapped as an ISO row, since this is a
        # real macro type, not embedded G-code text.
        #
        # cangle_rad/tilt_rad come from Fabex's own rotation_to_2_axes()
        # (utilities/orient_utils.py), which prepare_indexed() calls with
        # the "CA" axis combination - NOT machine-specific to this unit.
        #
        # UPDATE: the machine's real kinematic chain has since been
        # definitively confirmed (from the actual TP1 system.xml file,
        # not simulation inference): C1 is OUTER, B1 is INNER, and B1's
        # real rotation-axis vector is (vx=-cos(40deg), vy=0, vz=sin(40deg))
        # - i.e. entirely in the X-Z plane, exact match to the known 40deg
        # Alpha cant. This is real, confirmed ground truth that did not
        # exist when this function was first written.
        #
        # The AZ/AR formula below has NOT been re-derived against this
        # confirmed geometry yet - it still uses the original placeholder
        # assumption. Given the chain order is now known to be the
        # opposite of what was originally assumed, this formula is
        # SUSPECT and should not be trusted for a real tilted cut without
        # re-deriving it from the confirmed vector above first. Flagging
        # rather than guessing a fix under time pressure - this needs
        # careful geometric work, not a quick patch.
        #
        # Origin defaults to (0,0,0) - a placeholder. Fusion's official
        # post computes this from the section's real work origin relative
        # to the workpiece bounds; Fabex's equivalent hasn't been wired up
        # yet. Flagging rather than guessing.
        wfl_id = getattr(self, "_wfl_id_counter", 6)
        self._wfl_id_counter = wfl_id + 1
        az = 90.0 - math.degrees(tilt_rad)
        ar = math.degrees(cangle_rad)
        self.file.write("BEGIN MACRO\n")
        self.file.write("        NAME=WFL\n")
        self.file.write(f"        PARAM,NAME=ID,VALUE={wfl_id}\n")
        self.file.write(f"        PARAM,NAME=X,VALUE={origin[0]:.4f}\n")
        self.file.write(f"        PARAM,NAME=Y,VALUE={origin[1]:.4f}\n")
        self.file.write(f"        PARAM,NAME=Z,VALUE={origin[2]:.4f}\n")
        self.file.write(f"        PARAM,NAME=AZ,VALUE={az:.3f}\n")
        self.file.write(f"        PARAM,NAME=AR,VALUE={ar:.3f}\n")
        self.file.write("        PARAM,NAME=L,VALUE=0\n")
        self.file.write("        PARAM,NAME=H,VALUE=0\n")
        self.file.write("        PARAM,NAME=AFL,VALUE=1\n")
        self.file.write("        PARAM,NAME=AFH,VALUE=1\n")
        self.file.write("        PARAM,NAME=UCS,VALUE=1\n")
        self.file.write("        PARAM,NAME=RV,VALUE=0\n")
        self.file.write("        PARAM,NAME=FRC,VALUE=1\n")
        self.file.write("END MACRO\n\n")
        return wfl_id

    def PROGRAM_END(self):
        # Confirmed via a real CV production file (R370104N.cix): the
        # program simply ends after the last ENDPATH - no explicit TP0,
        # no M-code, nothing. Emitting an explicit TP0 here is very
        # likely what triggers the machine's own automatic tool-release
        # rotation (uncompensated, confirmed via an isolated test to
        # cause a real plunge) - CV's real files never do this, so the
        # machine evidently doesn't need an explicit release instruction
        # at the end of a program at all. Return empty - nothing gets
        # emitted (an empty ISO row is stripped and skipped).
        return ""

    def comment(self, text):
        # Suppress Fabex's identification/info comments (version banner,
        # rapid-feed note, etc.) entirely - they add no functional value
        # to the actual program, and the long version-banner comment is
        # the suspected cause of a "closed parenthesis missing" parse
        # error from bSuite - possibly a VALUE string length limit
        # silently truncating it. Simplest safe fix: don't emit them.
        pass

    def program_end(self):
        # Flush any drill points buffered for the last operation in the
        # file - there's no subsequent tool_change() to trigger this
        # otherwise.
        self._flush_drill_buffer()

        # iso.py's program_end() runs a post-write pass (number_file()) that
        # reopens the finished file and prepends N<number> to every single
        # line - including CID3 keywords like "BEGIN MACRO" and "END MACRO".
        # That's fundamentally incompatible with the CIX format, regardless
        # of the output_block_numbers setting (which gcode_export.py
        # re-applies from the machine's Blender settings after __init__
        # anyway, so setting it False there doesn't stick). Override the
        # full method here so that pass never runs for this post.
        if self.z_for_g53 is not None:
            self.write(
                self.SPACE()
                + self.MACHINE_COORDINATES()
                + self.SPACE()
                + "Z"
                + self.fmt.string(self.z_for_g53)
                + "\n"
            )
        self.write(self.SPACE() + self.PROGRAM_END() + "\n")

        if self.temp_file_to_append_on_close is not None:
            f_in = open(self.temp_file_to_append_on_close, "r")
            while True:
                line = f_in.readline()
                if len(line) == 0:
                    break
                self.write(line)
            f_in.close()

        self.file_close()

    ############################################################################
    # Tool changes - a bare "TP=<n> M3" ISO-embedded string does NOT
    # properly register tool selection in bSuite's internal state
    # (confirmed empirically: produces "no spindles selected" even with
    # clean, valid syntax). Cross-validated two ways: the Fabex thread's
    # own v10 finding (a real ROUT operation with a real tool was needed
    # before G300 moves would work at all) and a real reference file
    # posted from Fusion's own official stock Biesse CIX post, which
    # activates tools via a native ROUT/ROUTG macro's TNM=<tool name>
    # parameter. This mirrors the same fix already validated on the
    # Fusion-side post (biesse_cix_3axis.cps).
    #
    # Minimal field set (not the full ~55-parameter ROUTG, which requires
    # an external GID-referenced GEO macro and produced "geometry not
    # found" when tested without one) - CV's own proven working export
    # only ever sets tool name and diameter, so those two are the fields
    # trusted here; TTP intentionally omitted for the same reason.
    #
    # DP is intentionally a small positive value, NOT 0 - confirmed via
    # real testing that DP=0 does not mean "no-op cut" and instead
    # produced an uncontrolled deep plunge. Real vendor samples use a
    # genuine positive depth (e.g. DP=5).

    def tool_change(self, id):
        # Flush any drill points buffered for the PREVIOUS operation -
        # tool_change() marks a new operation starting, so this is the
        # right point to finalize whatever came before.
        self._flush_drill_buffer()

        op = getattr(self, "current_operation", None)
        diameter_mm = (op.cutter_diameter * 1000.0) if op is not None else 12.7
        tool_name = (op.cutter_description if op is not None else "") or f"T{id}"
        rpm = getattr(op, "spindle_rpm", 0) if op is not None else 0
        self.t = id
        self.move_done_since_tool_change = False
        self._set_z_shift(op)

        # DRILL strategy: buffer rapid()/feed() calls instead of emitting
        # them immediately, so the real motion pattern can be inspected
        # once the operation completes (see _flush_drill_buffer()) - a
        # clean plunge/retract cycle becomes a native BG macro (matching
        # Biesse's real convention of wanting a location + parameters,
        # not a pre-computed path - confirmed via real .arp mining
        # tonight); anything more complex (e.g. a real helical drill
        # type) falls back to the proven embedded-ISO path unchanged.
        self._drill_buffering = op is not None and getattr(op, "strategy", None) == "DRILL"
        if self._drill_buffering:
            self._drill_buffer = []
            self._drill_tool_name = tool_name
            self._drill_diameter_mm = diameter_mm
            self._drill_rpm = rpm
            return

        # FIRST-DRAFT native-geometry path, scoped specifically to
        # CUTOUT-strategy operations (not general - pockets, drilling,
        # etc. still fall through to the placeholder-ROUT + embedded-ISO
        # motion approach below). Confirmed via all 4 real CV production
        # files that native ROUT (not ROUTG/GEO) is what real production
        # actually uses, even for real cuts - none of them use ROUTG at
        # all. For a simple rectangular cutout (matching the real
        # operation's own bounding box), ROUT's own DX/DY/XRC/YRC fields
        # can represent the real shape directly, with bSuite generating
        # the actual toolpath itself - no embedded ISO motion needed.
        is_native_cutout = op is not None and getattr(op, "strategy", None) == "CUTOUT"
        self._native_cutout_active = False

        # NOTE: DRILL strategy intentionally does NOT get the same
        # blanket suppression as CUTOUT. Confirmed via real testing that
        # at least one drill type (MIDDLE_SYMETRIC) generates a real,
        # substantial toolpath (193 points for a single hole) through
        # ordinary rapid()/feed() calls, not the dedicated drill()
        # method below - unconditionally suppressing motion for any
        # DRILL-strategy operation silently ate that real toolpath,
        # leaving nothing for bSolid to show at all. drill() is kept as
        # an available override for whichever drill types genuinely do
        # invoke it, but nothing here assumes DRILL strategy implies
        # drill() will be called - the fallback embedded-ISO path below
        # handles real motion correctly regardless of drill type.

        if is_native_cutout:
            try:
                # Origin reference is this operation's own min bounds -
                # NOT a scan across other operations in the scene (that
                # relied on other operations' bounds being present/valid
                # at export time, which the real workflow doesn't
                # guarantee - see _panel_dims() for the full reasoning).
                panel_min_x = op.min.x * 1000.0
                panel_min_y = op.min.y * 1000.0

                op_min_x = op.min.x * 1000.0 - panel_min_x
                op_max_x = op.max.x * 1000.0 - panel_min_x
                op_min_y = op.min.y * 1000.0 - panel_min_y
                op_max_y = op.max.y * 1000.0 - panel_min_y
                xrc = (op_min_x + op_max_x) / 2.0
                yrc = (op_min_y + op_max_y) / 2.0
                dx = op_max_x - op_min_x
                dy = op_max_y - op_min_y

                # Real per-layer depths, matching Fabex's own internal
                # layer calculation (confirmed via the real log output:
                # "Layer 0 Depth: -0.01, Layer 1 Depth: -0.019" for a
                # stepdown of 10mm and max depth of 19mm) - computed here
                # from the same op.stepdown/min_z/max_z rather than
                # inferring layer boundaries from the raw vertex stream.
                #
                # POSITIVE here, not negative - confirmed via direct, twice-
                # repeated real simulation evidence (with and without
                # AZ=90) that negative DP produces upward motion for this
                # macro on this machine, contradicting an earlier
                # inference drawn from reading a reference file's text
                # rather than simulating it directly. Trusting the real,
                # repeated empirical result over that indirect reading.
                max_depth_mm = abs(op.max_z - op.min_z) * 1000.0
                stepdown_mm = abs(getattr(op, "stepdown", 0)) * 1000.0 or abs(max_depth_mm)
                depths = []
                d = stepdown_mm
                while d < max_depth_mm:
                    depths.append(d)
                    d += stepdown_mm
                depths.append(max_depth_mm)

                if dx > 0 and dy > 0 and depths:
                    for depth in depths:
                        rout_id = getattr(self, "_rout_id_counter", 1001)
                        self._rout_id_counter = rout_id + 1
                        self.file.write("BEGIN MACRO\n")
                        self.file.write("        NAME=ROUT\n")
                        self.file.write(f'        PARAM,NAME=ID,VALUE="P{rout_id}"\n')
                        self.file.write("        PARAM,NAME=SIDE,VALUE=0\n")
                        self.file.write('        PARAM,NAME=CRN,VALUE="1"\n')
                        self.file.write("        PARAM,NAME=Z,VALUE=0\n")
                        self.file.write(f"        PARAM,NAME=DP,VALUE={depth:.4f}\n")
                        self.file.write("        PARAM,NAME=OPT,VALUE=NO\n")
                        self.file.write(f"        PARAM,NAME=DIA,VALUE={diameter_mm:.3f}\n")
                        self.file.write("        PARAM,NAME=AZ,VALUE=90\n")
                        self.file.write("        PARAM,NAME=RTY,VALUE=rpNO\n")
                        self.file.write(f"        PARAM,NAME=XRC,VALUE={xrc:.4f}\n")
                        self.file.write(f"        PARAM,NAME=YRC,VALUE={yrc:.4f}\n")
                        self.file.write(f"        PARAM,NAME=DX,VALUE={dx:.4f}\n")
                        self.file.write(f"        PARAM,NAME=DY,VALUE={dy:.4f}\n")
                        self.file.write("        PARAM,NAME=R,VALUE=0\n")
                        self.file.write("        PARAM,NAME=A,VALUE=0\n")
                        self.file.write("        PARAM,NAME=THR,VALUE=NO\n")
                        self.file.write("        PARAM,NAME=RV,VALUE=NO\n")
                        self.file.write("        PARAM,NAME=CRC,VALUE=0\n")
                        self.file.write(f"        PARAM,NAME=RSP,VALUE={rpm:.0f}\n")
                        self.file.write(f'        PARAM,NAME=TNM,VALUE="{tool_name}"\n')
                        self.file.write("END MACRO\n\n")
                        self.file.write("BEGIN MACRO\n")
                        self.file.write("        NAME=ENDPATH\n")
                        self.file.write("END MACRO\n\n")
                    self._native_cutout_active = True
            except Exception:
                self._native_cutout_active = False

        if self._native_cutout_active:
            # Real cutting motion now comes entirely from the native ROUT
            # macros above - suppress the embedded-ISO per-vertex motion
            # for this operation (see rapid()/feed() overrides below).
            return

        # Fallback: placeholder-rectangle tool activation only (does NOT
        # represent real cutting geometry) - embedded-ISO motion below
        # still does the actual cutting, same as before. Used for any
        # operation NOT recognized as a simple CUTOUT above.
        self._write_fallback_tool_activation(tool_name, diameter_mm, rpm)

    def _write_fallback_tool_activation(self, tool_name, diameter_mm, rpm):
        rout_id = getattr(self, "_rout_id_counter", 1001)
        self._rout_id_counter = rout_id + 1

        self.file.write("BEGIN MACRO\n")
        self.file.write("        NAME=ROUT\n")
        self.file.write(f'        PARAM,NAME=ID,VALUE="P{rout_id}"\n')
        self.file.write("        PARAM,NAME=SIDE,VALUE=0\n")
        self.file.write('        PARAM,NAME=CRN,VALUE="1"\n')
        self.file.write("        PARAM,NAME=Z,VALUE=0\n")
        self.file.write("        PARAM,NAME=DP,VALUE=1\n")
        self.file.write("        PARAM,NAME=OPT,VALUE=NO\n")
        self.file.write(f"        PARAM,NAME=DIA,VALUE={diameter_mm:.3f}\n")
        self.file.write("        PARAM,NAME=AZ,VALUE=90\n")
        self.file.write("        PARAM,NAME=RTY,VALUE=rpNO\n")
        self.file.write("        PARAM,NAME=XRC,VALUE=16\n")
        self.file.write("        PARAM,NAME=YRC,VALUE=16\n")
        self.file.write("        PARAM,NAME=DX,VALUE=32\n")
        self.file.write("        PARAM,NAME=DY,VALUE=32\n")
        self.file.write("        PARAM,NAME=R,VALUE=0\n")
        self.file.write("        PARAM,NAME=A,VALUE=0\n")
        self.file.write("        PARAM,NAME=THR,VALUE=NO\n")
        self.file.write("        PARAM,NAME=RV,VALUE=NO\n")
        self.file.write("        PARAM,NAME=CRC,VALUE=0\n")
        self.file.write(f"        PARAM,NAME=RSP,VALUE={rpm:.0f}\n")
        self.file.write(f'        PARAM,NAME=TNM,VALUE="{tool_name}"\n')
        self.file.write("END MACRO\n\n")
        self.file.write("BEGIN MACRO\n")
        self.file.write("        NAME=ENDPATH\n")
        self.file.write("END MACRO\n\n")

        # Confirmed required (Fusion-side nickel-and-dime testing): a bare
        # G179 line must come right after tool activation, before ANY
        # embedded-ISO motion - even plain 3-axis moves with no rotary
        # component - or bSuite rejects the first move as a "non-existing
        # axis"/instruction error. Never carried over to this post before.
        self._emit_iso_row("G179")

    def rapid(self, x=None, y=None, z=None, a=None, b=None, c=None):
        if getattr(self, "_native_cutout_active", False):
            return
        if getattr(self, "_drill_buffering", False):
            self._buffer_drill_move(True, x, y, z)
            return
        super().rapid(x=x, y=y, z=z, a=a, b=b, c=c)

    def feed(self, x=None, y=None, z=None, a=None, b=None, c=None):
        if getattr(self, "_native_cutout_active", False):
            return
        if getattr(self, "_drill_buffering", False):
            self._buffer_drill_move(False, x, y, z)
            return
        super().feed(x=x, y=y, z=z, a=a, b=b, c=c)

    def _buffer_drill_move(self, is_rapid, x, y, z):
        # x/y/z are None when unchanged from the last position (Fabex's
        # modal convention - only changed axes are passed) - resolve
        # against the last known position so the buffer holds real,
        # absolute coordinates for later pattern analysis.
        last = getattr(self, "_drill_last_xyz", (0.0, 0.0, 0.0))
        rx = last[0] if x is None else x
        ry = last[1] if y is None else y
        rz = last[2] if z is None else z
        self._drill_last_xyz = (rx, ry, rz)
        self._drill_buffer.append((is_rapid, rx, ry, rz))

    def _flush_drill_buffer(self):
        if not getattr(self, "_drill_buffering", False):
            return
        buf = getattr(self, "_drill_buffer", [])
        self._drill_buffering = False
        self._drill_buffer = []
        if not buf:
            return

        # Simple pattern: every FEED move changes Z only (no X/Y motion
        # during a cutting move) - matches a clean rapid-to-position,
        # plunge, retract drill cycle. Anything where a feed move also
        # changes X/Y (e.g. a real helical/circular drill type) doesn't
        # match and falls back to the proven embedded-ISO path unchanged.
        simple = True
        prev = buf[0]
        for point in buf[1:]:
            is_rapid, x, y, z = point
            if not is_rapid and (x != prev[1] or y != prev[2]):
                simple = False
                break
            prev = point

        if simple:
            self._flush_drill_buffer_native(buf)
        else:
            self._flush_drill_buffer_embedded_iso(buf)

    def _flush_drill_buffer_native(self, buf):
        # Detect individual hole cycles: a rapid move that changes X/Y
        # starts a new hole; the feed moves that follow it (Z-only, per
        # the simple-pattern check above) plunge and retract that hole.
        tool_name = getattr(self, "_drill_tool_name", "")
        diameter_mm = getattr(self, "_drill_diameter_mm", 0.0)
        rpm = getattr(self, "_drill_rpm", 0)

        holes = []  # list of (x, y, min_z_reached)
        current_xy = None
        current_min_z = None
        for is_rapid, x, y, z in buf:
            if is_rapid and (current_xy is None or (x, y) != current_xy):
                if current_xy is not None and current_min_z is not None:
                    holes.append((current_xy[0], current_xy[1], current_min_z))
                current_xy = (x, y)
                current_min_z = None
            elif not is_rapid and current_xy is not None:
                current_min_z = z if current_min_z is None else min(current_min_z, z)
        if current_xy is not None and current_min_z is not None:
            holes.append((current_xy[0], current_xy[1], current_min_z))

        for hx, hy, hz in holes:
            # No origin offset here, unlike the CUTOUT path - this
            # operation's own bounds are just the tiny hole geometry
            # itself, not the real panel, so subtracting them would
            # incorrectly shift every hole toward (0,0). The machine's
            # working area (used for the panel/GEO outline) is a fixed,
            # absolute (0,0)-based frame, so raw Blender coordinates
            # (converted to mm) are used directly.
            # hx/hy/hz already arrive in mm - gcode_export.py applies
            # unitcorr (meters->mm) BEFORE ever calling rapid()/feed(),
            # which is what feeds this buffer. Multiplying by 1000.0
            # again here was a real double-conversion bug, confirmed via
            # real testing producing absurd values (e.g. a real ~261mm
            # position coming out as 260959.0292).
            real_x = hx
            real_y = hy
            depth_mm = abs(hz)
            bg_id = getattr(self, "_bg_id_counter", 2001)
            self._bg_id_counter = bg_id + 1
            self.file.write("BEGIN MACRO\n")
            self.file.write("        NAME=BG\n")
            self.file.write('        PARAM,NAME=CRN,VALUE="1"\n')
            self.file.write(f"        PARAM,NAME=X,VALUE={real_x:.4f}\n")
            self.file.write(f"        PARAM,NAME=Y,VALUE={real_y:.4f}\n")
            self.file.write("        PARAM,NAME=Z,VALUE=0.0000\n")
            self.file.write(f"        PARAM,NAME=DIA,VALUE={diameter_mm:.4f}\n")
            self.file.write(f'        PARAM,NAME=ID,VALUE="P{bg_id}"\n')
            self.file.write(f"        PARAM,NAME=DP,VALUE={depth_mm:.4f}\n")
            self.file.write("        PARAM,NAME=SIDE,VALUE=0\n")
            self.file.write("        PARAM,NAME=TTP,VALUE=0\n")
            self.file.write("        PARAM,NAME=DX,VALUE=0\n")
            self.file.write("        PARAM,NAME=DY,VALUE=0\n")
            self.file.write("        PARAM,NAME=R,VALUE=0\n")
            self.file.write("        PARAM,NAME=TCL,VALUE=0\n")
            self.file.write("        PARAM,NAME=THR,VALUE=NO\n")
            self.file.write(f"        PARAM,NAME=RSP,VALUE={rpm:.0f}\n")
            if tool_name:
                self.file.write(f'        PARAM,NAME=TNM,VALUE="{tool_name}"\n')
            self.file.write("END MACRO\n\n")

    def _flush_drill_buffer_embedded_iso(self, buf):
        # Fallback for anything not matching the simple drill pattern -
        # emit the same placeholder-ROUT + G179 tool activation the
        # non-CUTOUT fallback path already uses, then replay every
        # buffered point through the normal rapid()/feed() text
        # generation (temporarily off, so this call goes through to the
        # base class instead of re-buffering).
        self._write_fallback_tool_activation(
            getattr(self, "_drill_tool_name", ""),
            getattr(self, "_drill_diameter_mm", 12.7),
            getattr(self, "_drill_rpm", 0),
        )
        for is_rapid, x, y, z in buf:
            if is_rapid:
                super(Creator, self).rapid(x=x, y=y, z=z)
            else:
                super(Creator, self).feed(x=x, y=y, z=z)

    def write_noprk(self, start, distance=400):
        # Native NOPRK "magic comment" directive - confirmed via real
        # NOPRK.vbs source, not just documentation (which contradicted
        # itself on this point). start=True emits ";NOPRKSTART DST=<n>"
        # (suppresses the normal park move between operations closer
        # together than `distance`); start=False emits ";NOPRKEND"
        # (restores normal parking). Default distance 400 matches the
        # real hardcoded fallback in Biesse's own wrapper functions.
        # NOT wired in automatically - call explicitly around a run of
        # closely-spaced operations if the default parking behaviour
        # produces unwanted full-park retracts.
        if start:
            self._emit_iso_row(f";NOPRKSTART DST={distance}")
        else:
            self._emit_iso_row(";NOPRKEND")

    def spindle(self, s, clockwise):
        # No-op: the native ROUT macro (see tool_change()) already
        # activates the tool and spindle internally, with its own RSP
        # (speed) parameter. A separate embedded "S<rpm> M03" row here
        # is redundant and confirmed harmful - real testing on the
        # Fusion-side post found this exact pattern produces "no
        # spindles selected"/"M instruction error", since bSuite refuses
        # to re-activate a spindle that a native macro already started.
        pass

    def write_spindle(self):
        # Paired no-op with spindle() above - nothing was queued to flush.
        pass

    def TOOL(self):
        # Not used directly since tool_change() is overridden above,
        # but defined for completeness / in case any base-class path
        # still calls it.
        return "TP=%i"

    ############################################################################
    # Drilling - NOT overridden. A native BG-macro override was tried and
    # reverted: real testing confirmed at least one drill type
    # (MIDDLE_SYMETRIC) generates its real toolpath through ordinary
    # rapid()/feed() calls, not this method, and genuine uncertainty
    # remains about which drill types (if any) actually invoke it.
    # Falling through to the base framework's own drill() implementation
    # (already used successfully by other real posts in this codebase,
    # e.g. heiden.py) avoids a redundant-activation risk against the
    # reverted fallback ROUT, which now always runs for DRILL-strategy
    # operations regardless of drill type.

    ############################################################################
    # Spindle - Biesse dialect uses plain M3/M5, no S-word peculiarities
    # beyond what the base ISO creator already does, so no override needed
    # here beyond what IsoCreator provides.


################################################################################

nc.creator = Creator()
