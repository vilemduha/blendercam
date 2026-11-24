# hpgl3d.py
#
# Copyright (c) 2009, Dan Heeks
# This program is released under the BSD license. See the file COPYING for details.
#

from . import hpgl2d, nc


class Creator(hpgl2d.Creator):
    def __init__(self):
        hpgl2d.Creator.__init__(self)
        self.z = 0
        self.metric()  # set self.units_to_mc_units
        self.doing_rapid = True

    def program_begin(self, id, name=""):
        self.write(";;^IN;!MC0;\n")
        self.write("V50.0;^PR;Z0,0,10500;^PA;\n")
        self.write("!RC15;\n")
        self.write("!MC1;\n")

    def program_end(self):
        self.write("!VZ50.0;!ZM0;\n")
        self.write("!MC0;^IN;\n")

    def get_machine_xyz(self, x=None, y=None, z=None):
        machine_x = self.x
        machine_y = self.y
        machine_z = self.z
        if x is not None:
            machine_x = self.closest_int(x * self.units_to_mc_units)
        if y is not None:
            machine_y = self.closest_int(y * self.units_to_mc_units)
        if z is not None:
            machine_z = self.closest_int(z * self.units_to_mc_units)
        return machine_x, machine_y, machine_z

    def rapid(self, x=None, y=None, z=None, a=None, b=None, c=None):
        # do a rapid move.
        # for now, do all rapid moves at V50 ( 50 mm/s )
        mx, my, mz = self.get_machine_xyz(x, y, z)
        if mx != self.x or my != self.y or mz != self.z:
            if not self.doing_rapid:
                self.write("V50.0;")
            self.write((f"Z{mx}") + (f",{my}") + (f",{mz};\n"))
            self.x = mx
            self.y = my
            self.z = mz
            self.doing_rapid = True

    def feed(self, x=None, y=None, z=None, a=None, b=None, c=None):
        # do a feed move.
        # for now, do all feed moves at V10 ( 10 mm/s )
        mx, my, mz = self.get_machine_xyz(x, y, z)
        if mx != self.x or my != self.y or mz != self.z:
            if self.doing_rapid:
                self.write("V10.0;")
            self.write((f"Z{mx}") + (f",{my}") + (f",{mz};\n"))
            self.x = mx
            self.y = my
            self.z = mz
            self.doing_rapid = False


nc.creator = Creator()
