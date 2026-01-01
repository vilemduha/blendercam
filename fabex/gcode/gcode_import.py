"""Fabex 'gcodeimportparser.py'


Code modified from YAGV (Yet Another G-code Viewer) - https://github.com/jonathanwin/yagv

No license terms found in YAGV repo, will assume GNU release
"""

import math
import time

import numpy as np

import bpy


from ..utilities.logging_utils import log


np.set_printoptions(suppress=True)  # suppress scientific notation in subdivide functions linspace


def import_gcode(self, context, filepath):
    """Import G-code data into the scene.


    This function reads G-code from a specified file and processes it

    according to the settings defined in the context. It utilizes the

    GcodeParser to parse the file and classify segments of the model.

    Depending on the options set in the scene, it may subdivide the model

    and draw it with or without layer splitting. The time taken for the
    import process is printed to the console.


    Args:

        context (Context): The context containing the scene and tool settings.

        filepath (str): The path to the G-code file to be imported.


    Returns:

        dict: A dictionary indicating the import status, typically

            {'FINISHED'}.
    """

    log.info("Running read_some_data...")

    scene = context.scene

    mytool = self

    then = time.time()

    parse = GcodeParser()

    model = parse.parse_file(filepath)

    if mytool.subdivide:
        model.subdivide(mytool.max_segment_size)

    model.classify_segments()

    if mytool.split_layers:
        model.draw(split_layers=True)

    else:
        model.draw(split_layers=False)

    now = time.time()

    log.info(f"Importing Gcode Took {round(now - then, 1)} Seconds")

    return {"FINISHED"}


def segments_to_meshdata(segments):
    """Convert a list of segments into mesh data consisting of vertices and
    edges.


    This function processes a list of segment objects, extracting the

    coordinates of vertices and defining edges based on the styles of the

    segments. It identifies when to add vertices and edges based on whether

    the segments are in 'extrude' or 'travel' styles. The resulting mesh

    data can be used for 3D modeling or rendering applications.


    Args:

        segments (list): A list of segment objects, each containing 'style' and

            'coords' attributes.


    Returns:

        tuple: A tuple containing two elements:

            - list: A list of vertices, where each vertex is represented as a

            list of coordinates [X, Y, Z].

            - list: A list of edges, where each edge is represented as a list

            of indices corresponding to the vertices.
    """

    # edges only on extrusion

    segs = segments

    verts = []

    edges = []

    del_offset = (
        0  # to travel segs in a row, one gets deleted, need to keep track of index for edges
    )

    for i in range(len(segs)):
        if i >= len(segs) - 1:
            if segs[i].style == "extrude":
                verts.append(
                    [
                        segs[i].coords["X"],
                        segs[i].coords["Y"],
                        segs[i].coords["Z"],
                    ]
                )

            break

        # start of extrusion for first time

        if segs[i].style == "travel" and segs[i + 1].style == "extrude":
            verts.append(
                [
                    segs[i].coords["X"],
                    segs[i].coords["Y"],
                    segs[i].coords["Z"],
                ]
            )

            verts.append(
                [
                    segs[i + 1].coords["X"],
                    segs[i + 1].coords["Y"],
                    segs[i + 1].coords["Z"],
                ]
            )

            edges.append([i - del_offset, (i - del_offset) + 1])

        # mitte, current and next are extrusion, only add next, current is already in vert list

        if segs[i].style == "extrude" and segs[i + 1].style == "extrude":
            verts.append(
                [
                    segs[i + 1].coords["X"],
                    segs[i + 1].coords["Y"],
                    segs[i + 1].coords["Z"],
                ]
            )

            edges.append([i - del_offset, (i - del_offset) + 1])

        if segs[i].style == "travel" and segs[i + 1].style == "travel":
            del_offset += 1

    return verts, edges


def obj_from_pydata(name, verts, edges=None, close=True, collection_name=None):
    """Create a Blender object from provided vertex and edge data.


    This function generates a mesh object in Blender using the specified

    vertices and edges. If edges are not provided, it automatically creates

    a chain of edges connecting the vertices. The function also allows for

    the option to close the mesh by connecting the last vertex back to the

    first. Additionally, it can place the created object into a specified

    collection within the Blender scene. The object is scaled down to a

    smaller size for better visibility in the Blender environment.


    Args:

        name (str): The name of the object to be created.

        verts (list): A list of vertex coordinates, where each vertex is represented as a

            tuple of (x, y, z).

        edges (list?): A list of edges defined by pairs of vertex indices. Defaults to None.

        close (bool?): Whether to close the mesh by connecting the last vertex to the first.

            Defaults to True.

        collection_name (str?): The name of the collection to which the object should be added. Defaults

            to None.


    Returns:

        None: The function does not return a value; it creates an object in the

            Blender scene.
    """

    if edges is None:
        # join vertices into one uninterrupted chain of edges.

        edges = [[i, i + 1] for i in range(len(verts) - 1)]

        if close:
            edges.append([len(verts) - 1, 0])  # connect last to first

    me = bpy.data.meshes.new(name)

    me.from_pydata(verts, edges, [])

    obj = bpy.data.objects.new(name, me)

    # Move into collection if specified

    if collection_name is not None:  # make argument optional
        # collection exists

        collection = bpy.data.collections.get(collection_name)

        if collection:
            bpy.data.collections[collection_name].objects.link(obj)

        else:
            collection = bpy.data.collections.new(collection_name)

            bpy.context.scene.collection.children.link(collection)  # link collection to main scene

            bpy.data.collections[collection_name].objects.link(obj)

    obj.scale = (0.001, 0.001, 0.001)

    bpy.context.view_layer.objects.active = obj

    obj.select_set(True)

    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    if bpy.context.scene.gcode_output_type == "curve":
        bpy.ops.object.convert(target="CURVE")


class GcodeParser:
    comment = ""

    # global, to access in other classes(to access RGB values in comment above when parsing M163).

    # Theres probably better way

    def __init__(self):
        self.model = GcodeModel(self)

    def parse_file(self, path):
        """Parse a G-code file and update the model.


        This function reads a G-code file line by line, increments a line

        counter for each line, and processes each line using the `parseLine`

        method. The function assumes that the file is well-formed and that each

        line can be parsed without errors. After processing all lines, it

        returns the updated model.


        Args:

            path (str): The file path to the G-code file to be parsed.


        Returns:

            model: The updated model after parsing the G-code file.
        """

        # read the gcode file

        with open(path, "r") as f:
            # init line counter

            self.lineNb = 0

            # for all lines

            for line in f:
                # inc line counter

                self.lineNb += 1

                # remove trailing linefeed

                self.line = line.rstrip()

                # parse a line

                self.parse_line()

        return self.model

    def parse_line(self):
        """Parse a line of G-code and execute the corresponding command.


        This method processes a line of G-code by stripping comments, cleaning

        the command, and identifying the command code and its arguments. It

        handles specific G-code commands and invokes the appropriate parsing

        method if available. If the command is unsupported, it prints an error

        message. The method also manages tool numbers and coordinates based on
        the parsed command.
        """

        # strip comments:

        bits = self.line.split(";", 1)

        if len(bits) > 1:
            GcodeParser.comment = bits[1]

        # extract & clean command

        command = bits[0].strip()

        s = ""

        a = ""

        a_old = ""

        for i in range(len(command)):  # check each character in the line
            a = command[i]

            if a.isupper() and a_old != " " and i > 0:
                # add a space if upper case letter and no space is found before

                s += " "

            s += a

            a_old = a

        log.info(s)

        command = s

        # code is fist word, then args

        comm = command.split(None, 1)

        code = comm[0] if (len(comm) > 0) else None

        args = comm[1] if (len(comm) > 1) else None

        if code:
            # convert all G01 and G00 to G1 and G0

            if code == "G01":
                code = "G1"

            if code == "G00":
                code = "G0"

            if hasattr(self, "parse_" + code):
                getattr(self, "parse_" + code)(args)

                self.last_command = code

            else:
                if code[0] == "T":
                    self.model.toolnumber = int(code[1:])

                    log.info(self.model.toolnumber)

                    # if code doesn't start with a G but starts with a coordinate add the last command to the line

                elif code[0] == "X" or code[0] == "Y" or code[0] == "Z":
                    self.line = self.last_command + " " + self.line

                    self.parse_line()  # parse this line again with the corrections

                else:
                    pass

                    log.info(f"Unsupported gcode {code}")

    def parse_args(self, args):
        """Parse command-line arguments into a dictionary.


        This function takes a string of arguments, splits it into individual

        components, and maps each component's first character to its

        corresponding numeric value. If a numeric value cannot be converted from

        the string, it defaults to 1. The resulting dictionary contains the

        first characters as keys and their associated numeric values as values.


        Args:

            args (str): A string of space-separated arguments, where each argument

                consists of a letter followed by a numeric value.


        Returns:

            dict: A dictionary mapping each letter to its corresponding numeric value.
        """

        dic = {}

        if args:
            bits = args.split()

            for bit in bits:
                letter = bit[0]

                try:
                    coord = float(bit[1:])

                except ValueError:
                    coord = 1

                dic[letter] = coord

        return dic

    def parse_G1(self, args, type="G1"):
        # G1: Controlled move

        self.model.do_G1(self.parse_args(args), type)

    def parse_G0(self, args, type="G0"):
        # G1: Controlled move

        self.model.do_G1(self.parse_args(args), type)

    def parse_G90(self, args):
        # G90: Set to Absolute Positioning

        self.model.set_relative(False)

    def parse_G91(self, args):
        # G91: Set to Relative Positioning

        self.model.set_relative(True)

    def parse_G92(self, args):
        # G92: Set Position

        self.model.do_G92(self.parse_args(args))

    def warn(self, msg):
        log.warning(f"[WARN] Line {self.lineNb}: {msg} (Text:'{self.line}')")

    def error(self, msg):
        """Log an error message and raise an exception.


        This method prints an error message to the console, including the line

        number, the provided message, and the text associated with the error.

        After logging the error, it raises a generic Exception with the same
        message format.


        Args:

            msg (str): The error message to be logged.


        Raises:

            Exception: Always raises an Exception with the formatted error message.
        """

        log.error(f"[ERROR] Line {self.lineNb}: {msg} (Text:'{self.line}')")

        raise Exception(f"[ERROR] Line {self.lineNb}: {msg} (Text:'{self.line}')")


class GcodeModel:
    def __init__(self, parser):
        # save parser for messages

        self.parser = parser

        # latest coordinates & extrusion relative to offset, feedrate

        self.relative = {"X": 0.0, "Y": 0.0, "Z": 0.0, "F": 0.0, "E": 0.0}

        # offsets for relative coordinates and position reset (G92)

        self.offset = {"X": 0.0, "Y": 0.0, "Z": 0.0, "E": 0.0}

        # if true, args for move (G1) are given relatively (default: absolute)

        self.isRelative = False

        self.color = [0, 0, 0, 0, 0, 0, 0, 0]  # RGBCMYKW

        self.toolnumber = 0

        # the segments

        self.segments = []

        self.layers = []

    def do_G1(self, args, type):
        """Perform a rapid or controlled movement based on the provided arguments.


        This method updates the current coordinates based on the input

        arguments, either in relative or absolute terms. It constructs a segment

        representing the movement and adds it to the model if there are changes

        in the XYZ coordinates. The function handles unknown axes by issuing a

        warning and ensures that the segment is only added if there are actual
        changes in position.


        Args:

            args (dict): A dictionary containing movement parameters for each axis.

            type (str): The type of movement (e.g., 'G0' for rapid move, 'G1' for controlled

                move).
        """

        # G0/G1: Rapid/Controlled move

        # clone previous coords

        coords = dict(self.relative)

        # update changed coords

        for axis in args.keys():
            # print(coords)

            if axis in coords:
                if self.isRelative:
                    coords[axis] += args[axis]

                else:
                    coords[axis] = args[axis]

            else:
                self.warn("Unknown axis '%s'" % axis)

        # build segment

        absolute = {
            "X": self.offset["X"] + coords["X"],
            "Y": self.offset["Y"] + coords["Y"],
            "Z": self.offset["Z"] + coords["Z"],
            "F": coords["F"],  # no feedrate offset
        }

        # if gcode line has no E = travel move

        # but still add E = 0 to segment (so coords dictionaries have same shape for subdividing linspace function)

        if "E" not in args:  # "E" in coords:
            absolute["E"] = 0

        else:
            absolute["E"] = args["E"]

        seg = Segment(
            type,
            absolute,
            self.color,
            self.toolnumber,
            # self.layerIdx,
            self.parser.lineNb,
            self.parser.line,
        )

        # only add seg if XYZ changes (skips "G1 Fxxx" only lines and avoids double vertices inside Blender,

        # because XYZ stays the same on such a segment.

        if (
            seg.coords["X"] != self.relative["X"] + self.offset["X"]
            or seg.coords["Y"] != self.relative["Y"] + self.offset["Y"]
            or seg.coords["Z"] != self.relative["Z"] + self.offset["Z"]
        ):
            self.add_segment(seg)

        # update model coords

        self.relative = coords

    def do_G92(self, args):
        """Set the current position of the axes without moving.


        This method updates the current coordinates for the specified axes based

        on the provided arguments. If no axes are mentioned, it sets all axes

        (X, Y, Z) to zero. The method adjusts the offset values by transferring

        the difference between the relative and specified values for each axis.

        If an unknown axis is provided, a warning is issued.


        Args:

            args (dict): A dictionary containing axis names as keys

                (e.g., 'X', 'Y', 'Z') and their corresponding

                position values as float.
        """

        # G92: Set Position

        # this changes the current coords, without moving, so do not generate a segment

        # no axes mentioned == all axes to 0

        if not len(args.keys()):
            args = {"X": 0.0, "Y": 0.0, "Z": 0.0}  # , "E":0.0

        # update specified axes

        for axis in args.keys():
            if axis in self.offset:
                # transfer value from relative to offset

                self.offset[axis] += self.relative[axis] - args[axis]

                self.relative[axis] = args[axis]

            else:
                self.warn("Unknown axis '%s'" % axis)

    def do_M163(self, args):
        """Update the color settings for a specific segment based on given
        parameters.


        This method modifies the color attributes of an object by updating the

        CMYKW values for a specified segment. It first creates a new list from

        the existing color attribute to avoid reference issues. The method then

        extracts the index and weight from the provided arguments and updates

        the color list accordingly. Additionally, it retrieves RGB values from
        the last comment and applies them to the color list.


        Args:

            args (dict): A dictionary containing the parameters for the operation.

                - 'S' (int): The index of the segment to update.

                - 'P' (float): The weight to set for the CMYKW color component.


        Returns:

            None: This method does not return a value; it modifies the object's state.
        """

        col = list(
            self.color
        )  # list() creates new list, otherwise you just change reference and all segs have same color

        extr_idx = int(args["S"])  # e.g. M163 S0 P1

        weight = args["P"]

        # change CMYKW

        col[
            extr_idx + 3
        ] = weight  # +3 weil ersten 3 stellen RGB sind, need only CMYKW values for extrude

        self.color = col

        # take RGB values for seg from last comment (above first M163 statement)

        comment = eval(GcodeParser.comment)  # string comment to list

        # RGB = [GcodeParser.comment[1], GcodeParser.com

        RGB = comment[:3]

        self.color[:3] = RGB

    def set_relative(self, isRelative):
        self.isRelative = isRelative

    def add_segment(self, segment):
        self.segments.append(segment)

    def warn(self, msg):
        self.parser.warn(msg)

    def error(self, msg):
        self.parser.error(msg)

    def classify_segments(self):
        """Classify segments into layers based on their coordinates and extrusion

        style.


        This method processes a list of segments, determining their extrusion

        style (travel, retract, restore, or extrude) based on the movement of

        the coordinates and the state of the extruder. It organizes the segments

        into layers, which are used for later rendering. The classification is

        based on changes in the Z-coordinate and the extruder's position.  The

        function initializes the coordinates and iterates through each segment,

        checking for movements in the X, Y, and Z directions. It identifies when

        a new layer begins based on changes in the Z-coordinate and the

        extruder's state. Segments are then grouped into layers for further

        processing.  Raises:     None
        """

        # start model at 0, act as prev_coords

        coords = {"X": 0.0, "Y": 0.0, "Z": 0.0, "F": 0.0, "E": 0.0}

        # first layer at Z=0

        currentLayerIdx = 0

        currentLayerZ = 0  # better to use self.first_layer_height

        layer = []  # add layer to model.layers

        for i, seg in enumerate(self.segments):
            # default style is travel (move, no extrusion)

            style = "travel"

            # no horizontal movement, but extruder movement: retraction/refill

            # if (

            #     (seg.coords["X"] == coords["X"]) and

            #     (seg.coords["Y"] == coords["Y"]) and

            #     (seg.coords["Z"] == coords["Z"]) and

            #     (seg.coords["E"] != coords["E"])

            # ):

            #     style = "retract" if (seg.coords["E"] < coords["E"]) else "restore"

            # some horizontal movement, and positive extruder movement: extrusion

            if (
                (seg.coords["X"] != coords["X"])
                or (seg.coords["Y"] != coords["Y"])
                or (seg.coords["Z"] != coords["Z"])
            ):  # != coords["E"]
                style = "extrude"

            # #force extrude if there is some movement

            # segments to layer lists

            # look ahead and if next seg has E and differenz Z, add new layer for current segment

            if i == len(self.segments) - 1:
                layer.append(seg)

                currentLayerIdx += 1

                seg.style = style

                seg.layerIdx = currentLayerIdx

                # add layer to list of Layers, used to later draw single layer objects

                self.layers.append(layer)

                break

            # positive extruder movement of next point in a different Z signals a layer change for this segment

            if (
                self.segments[i].coords["Z"] != currentLayerZ
                and self.segments[i + 1].coords["E"] > 0
            ):
                self.layers.append(
                    layer
                )  # layer abschließen, add layer to list of Layers, used to later draw single layer objects

                layer = []  # start new layer

                currentLayerZ = seg.coords["Z"]

                currentLayerIdx += 1

                # lookback, previous point before texrsuion is part of new layer too, both create an edge

            # set style and layer in segment

            seg.style = style

            seg.layerIdx = currentLayerIdx

            layer.append(seg)

            coords = seg.coords

    def subdivide(self, subd_threshold):
        """Subdivide segments based on a specified threshold.


        This method processes a list of segments and subdivides them into

        smaller segments if the distance between consecutive segments exceeds

        the given threshold. The subdivision is performed by interpolating

        points between the original segment's coordinates, ensuring that the

        resulting segments maintain the original order and properties. This is

        particularly useful for manipulating attributes such as color and

        continuous deformation in graphical representations.


        Args:

            subd_threshold (float): The distance threshold for subdividing segments.

                Segments with a distance greater than this value

                will be subdivided.


        Returns:

            None: The method modifies the instance's segments attribute in place.
        """

        # smart subdivide

        # divide edge if > subd_threshold

        # do it in parser to keep index order of vertex and travel/extrude info

        # segmentation of path necessary for manipulation of color, continous deforming ect.

        subdivided_segs = []

        # start model at 0

        coords = {"X": 0.0, "Y": 0.0, "Z": 0.0, "F": 0.0, "E": 0.0}  # no interpolation

        for seg in self.segments:
            # calc XYZ distance

            d = (seg.coords["X"] - coords["X"]) ** 2

            d += (seg.coords["Y"] - coords["Y"]) ** 2

            d += (seg.coords["Z"] - coords["Z"]) ** 2

            seg.distance = math.sqrt(d)

            if seg.distance > subd_threshold:
                subdivs = math.ceil(
                    seg.distance / subd_threshold
                )  # ceil makes sure that linspace interval is at least 2

                P1 = coords

                P2 = seg.coords

                # interpolated points

                interp_coords = np.linspace(
                    list(P1.values()), list(P2.values()), num=subdivs, endpoint=True
                )

                for i in range(
                    len(interp_coords)
                ):  # inteprolated points array back to segment object
                    new_coords = {
                        "X": interp_coords[i][0],
                        "Y": interp_coords[i][1],
                        "Z": interp_coords[i][2],
                        "F": seg.coords["F"],
                    }

                    # E/subdivs is for relative extrusion, absolute extrusion need "E":interp_coords[i][4]

                    # print("interp_coords_new:", new_coords)

                    if seg.coords["E"] > 0:
                        new_coords["E"] = round(seg.coords["E"] / (subdivs - 1), 5)

                    else:
                        new_coords["E"] = 0

                    # make sure P1 hasn't been written before, compare with previous line

                    if (
                        new_coords["X"] != coords["X"]
                        or new_coords["Y"] != coords["Y"]
                        or new_coords["Z"] != coords["Z"]
                    ):
                        # write segment only if movement changes,

                        # avoid double coordinates due to same start and endpoint of linspace

                        new_seg = Segment(
                            seg.type, new_coords, seg.color, seg.toolnumber, seg.lineNb, seg.line
                        )

                        new_seg.layerIdx = seg.layerIdx

                        new_seg.style = seg.style

                        subdivided_segs.append(new_seg)

            else:
                subdivided_segs.append(seg)

            coords = seg.coords  # P1 becomes P2

        self.segments = subdivided_segs

    # create blender curve and vertex_info in text file(coords, style, color...)

    def draw(self, split_layers=False):
        """Draws a mesh from segments and layers.


        This function creates a Blender curve and vertex information in a text

        file, which includes coordinates, style, and color. If the

        `split_layers` parameter is set to True, it processes each layer

        individually, generating vertices and edges for each layer. If False, it

        processes the segments as a whole.


        Args:

            split_layers (bool): A flag indicating whether to split the drawing into

                separate layers or not.
        """

        if split_layers:
            i = 0

            for layer in self.layers:
                verts, edges = segments_to_meshdata(layer)

                if len(verts) > 0:
                    obj_from_pydata(str(i), verts, edges, close=False, collection_name="Layers")

                    i += 1

        else:
            verts, edges = segments_to_meshdata(self.segments)

            obj_from_pydata("Gcode", verts, edges, close=False, collection_name="Layers")


class Segment:
    def __init__(self, type, coords, color, toolnumber, lineNb, line):
        self.type = type

        self.coords = coords

        self.color = color

        self.toolnumber = toolnumber

        self.lineNb = lineNb

        self.line = line

        self.style = None

        self.layerIdx = None

    def __str__(self):
        """Return a string representation of the object.


        This method constructs a string that includes the coordinates, line

        number, style, layer index, and color of the object. It formats these

        attributes into a readable string format for easier debugging and
        logging.


        Returns:

            str: A formatted string representing the object's attributes.
        """

        return " <coords=%s, lineNb=%d, style=%s, layerIdx=%d, color=%s" % (
            str(self.coords),
            self.lineNb,
            self.style,
            self.layerIdx,
            str(self.color),
        )


class Layer:
    def __init__(self, Z):
        self.Z = Z

        self.segments = []

        self.distance = None

        self.extrudate = None

    def __str__(self):
        return "<Layer: Z=%f, len(segments)=%d>" % (self.Z, len(self.segments))


if __name__ == "__main__":
    path = "test.gcode"

    parser = GcodeParser()

    model = parser.parse_file(path)
