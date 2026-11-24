################################################################################
# cad_nc_read.py
#
# Base class for NC code parsing and backplotting
#
# Dan Falck 2011/01/06


################################################################################
class Parser:
    def __init__(self):
        self.currentx = -1.0
        self.currenty = 0.0
        self.currentz = 0.0
        x, y, z = 0.0, 0.0, 0.0
        self.absolute_flag = True

    ############################################################################
    # Internals

    def files_open(self, name, oname=None):
        if oname is None:
            oname = name + ".scr"
        self.file_in = open(name, "r")
        self.file_out = open(oname, "w")

    def files_close(self):
        self.file_in.close()
        self.file_out.write("-linetype set continuous\n")
        self.file_out.write("\n")
        self.file_out.close()

    def readline(self):
        self.line = self.file_in.readline().rstrip()
        return bool(len(self.line))

    def write(self, s):
        self.file_out.write(s)

    ############################################################################
    def end_ncblock(self):
        self.file_out.write("Delay 0\n")

    def add_text(self, s, col=None, cdata=False):
        return

    def set_mode(self, units=None):
        # self.file_out.write(' units="'+str(units)+'"')
        return

    def set_tool(self, number=None):
        if number is not None:
            self.file_out.write("-LAYER New T" + str(number) + "\n")
            self.file_out.write("-LAYER Set T" + str(number) + "\n")

    def begin_path(self, col=None):
        if col is not None:
            if col == "rapid":
                self.file_out.write("-color Red\n")
                # self.file_out.write('')
                self.file_out.write("-linetype set dashed\n")
                self.file_out.write("\n")
            else:
                self.file_out.write("-color Green\n")
                # self.file_out.write('')
                self.file_out.write("-linetype set continuous\n")
                self.file_out.write("\n")
        else:
            self.file_out.write("\n")

    def end_path(self):
        self.file_out.write("\n")

    def add_line(self, x=None, y=None, z=None, a=None, b=None, c=None):
        if x is None and y is None and z is None and a is None and b is None and c is None:
            return
        # self.file_out.write('line %s,%s %s,%s' %(self.currentx,self.currenty,x,y))
        if x is None:
            x = self.currentx
        if y is None:
            y = self.currenty
        if z is None:
            z = self.currentz
        self.file_out.write(f"line {self.currentx},{self.currenty},{self.currentz} {x},{y},{z}\n")
        self.currentx = x
        self.currenty = y
        self.currentz = z

    def add_arc(self, x=None, y=None, z=None, i=None, j=None, k=None, r=None, d=None):
        if (
            x is None
            and y is None
            and z is None
            and i is None
            and j is None
            and k is None
            and r is None
            and d is None
        ):
            return

        z = self.currentz
        if x is None:
            x = self.currentx
        if y is None:
            y = self.currenty
        if z is None:
            z = self.currentz
        if d == 1:
            self.file_out.write(f"arc {self.currentx},{self.currenty},{self.currentz}\n")
            self.file_out.write("c\n")
            self.file_out.write(f"{self.currentx + i},{self.currenty + j},{self.currentz}\n")
            self.file_out.write(f"{x},{y},{z}")
        else:
            self.file_out.write(f"arc {x},{y},{z}\n")
            self.file_out.write("c\n")
            self.file_out.write(f"{self.currentx + i},{self.currenty + j},{self.currentz}\n")
            self.file_out.write(f"{self.currentx},{self.currenty},{self.currentz}")
        self.currentx = x
        self.currenty = y
        self.currentz = z

    def incremental(self):
        self.absolute_flag = False

    def absolute(self):
        self.absolute_flag = True
