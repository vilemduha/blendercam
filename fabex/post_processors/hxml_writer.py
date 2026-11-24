import tempfile


class HxmlWriter:
    def __init__(self):
        self.file_out = open(tempfile.gettempdir() + "/backplot.xml", "w")
        self.file_out.write('<?xml version="1.0" ?>\n')
        self.file_out.write("<nccode>\n")

    def __del__(self):
        self.file_out.write("</nccode>\n")
        self.file_out.close()

    def write(self, s):
        self.file_out.write(s)

    ############################################

    def begin_ncblock(self):
        self.file_out.write("\t<ncblock>\n")

    def end_ncblock(self):
        self.file_out.write("\t</ncblock>\n")

    def add_text(self, s, col, cdata):
        s.replace("&", "&amp;")
        s.replace('"', "&quot;")
        s.replace("<", "&lt;")
        s.replace(">", "&gt;")
        if cdata:
            (cd1, cd2) = ("<![CDATA[", "]]>")
        else:
            (cd1, cd2) = ("", "")
        if col is not None:
            self.file_out.write('\t\t<text col="' + col + '">' + cd1 + s + cd2 + "</text>\n")
        else:
            self.file_out.write("\t\t<text>" + cd1 + s + cd2 + "</text>\n")

    def set_mode(self, units):
        self.file_out.write("\t\t<mode")
        if units is not None:
            self.file_out.write(' units="' + str(units) + '"')
        self.file_out.write(" />\n")

    def metric(self):
        self.set_mode(units=1.0)

    def imperial(self):
        self.set_mode(units=25.4)

    def begin_path(self, col):
        if col is not None:
            self.file_out.write('\t\t<path col="' + col + '">\n')
        else:
            self.file_out.write("\t\t<path>\n")

    def end_path(self):
        self.file_out.write("\t\t</path>\n")

    def rapid(self, x=None, y=None, z=None, a=None, b=None, c=None, machine_coordinates=None):
        self.begin_path("rapid")
        self.add_line(x, y, z, a, b, c)
        self.end_path()

    def feed(self, x=None, y=None, z=None):
        self.begin_path("feed")
        self.add_line(x, y, z)
        self.end_path()

    def arc_cw(self, x=None, y=None, z=None, i=None, j=None, k=None, r=None):
        self.begin_path("feed")
        self.add_arc(x, y, z, i, j, k, r, -1)
        self.end_path()

    def arc_ccw(self, x=None, y=None, z=None, i=None, j=None, k=None, r=None):
        self.begin_path("feed")
        self.add_arc(x, y, z, i, j, k, r, 1)
        self.end_path()

    def tool_change(self, id):
        self.file_out.write("\t\t<tool")
        if id is not None:
            self.file_out.write(' number="' + str(id) + '"')
            self.file_out.write(" />\n")

    def spindle(self, s, clockwise):
        pass

    def feedrate(self, f):
        pass

    def add_line(self, x, y, z, a=None, b=None, c=None):
        self.file_out.write("\t\t\t<line")
        if x is not None:
            self.file_out.write(f' x="{x:.6f}"')
        if y is not None:
            self.file_out.write(f' y="{y:.6f}"')
        if z is not None:
            self.file_out.write(f' z="{z:.6f}"')
        if a is not None:
            self.file_out.write(f' a="{a:.6f}"')
        if b is not None:
            self.file_out.write(f' b="{b:.6f}"')
        if c is not None:
            self.file_out.write(f' c="{c:.6f}"')
        self.file_out.write(" />\n")
        if x is not None:
            self.oldx = x
        if y is not None:
            self.oldy = y
        if z is not None:
            self.oldz = z

    def add_arc(self, x, y, z, i, j, k, r=None, d=None):
        self.file_out.write("\t\t\t<arc")
        if x is not None:
            self.file_out.write(f' x="{x:.6f}"')
        if y is not None:
            self.file_out.write(f' y="{y:.6f}"')
        if z is not None:
            self.file_out.write(f' z="{z:.6f}"')
        if i is not None:
            self.file_out.write(' i="%.6f"' % (i - self.oldx))
        if j is not None:
            self.file_out.write(' j="%.6f"' % (j - self.oldy))
        if k is not None:
            self.file_out.write(' k="%.6f"' % (k - self.oldz))
        if r is not None:
            self.file_out.write(f' r="{r:.6f}"')
        if d is not None:
            self.file_out.write(f' d="{d}"')
        self.file_out.write(" />\n")
        if x is not None:
            self.oldx = x
        if y is not None:
            self.oldy = y
        if z is not None:
            self.oldz = z
