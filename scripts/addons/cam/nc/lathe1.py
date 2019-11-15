################################################################################
# lathe1.py
#
# Simple ISO NC code creator for lathe
#
# Dan Falck 2010/09/28

from . import iso_lathe_codes as iso
from . import nc
import math

################################################################################
class CreatorIso(nc.Creator):

    def __init__(self):
        nc.Creator.__init__(self)

        self.a = 0
        self.b = 0
        self.c = 0
        self.f = ''
        self.fh = None
        self.fv = None
        self.fhv = False
        self.g = ''
        self.i = 0
        self.j = 0
        self.k = 0
        self.m = []
        self.n = 10
        self.r = 0
        self.s = ''
        self.t = None
        self.x = 0
        self.y = 0
        self.z = 500
        self.f_modal = False
        self.g0123_modal = False
        self.drill_modal = False
        self.prev_f = ''
        self.prev_g0123 = ''
        self.prev_drill = ''
        self.prev_retract = ''
        self.prev_z = ''
        self.useCrc = False
        self.gCRC = ''
        self.fmt = iso.codes.FORMAT_MM()
        self.absolute_flag = True
        self.ffmt = iso.codes.FORMAT_FEEDRATE()
    ############################################################################
    ##  Internals

    def write_feedrate(self):
        if self.f_modal:
            if self.f != self.prev_f:
                self.write(self.f)
                self.prev_f = self.f
        else:
            self.write(self.f)
            self.f = ''

    def write_preps(self):
        self.write(self.g)
        self.g = ''

    def write_misc(self):
        if (len(self.m)) : self.write(self.m.pop())

    def write_spindle(self):
        self.write(self.s)
        self.s = ''

    ############################################################################
    ##  Programs

    def program_begin(self, id, name=''):
        self.write((iso.codes.PROGRAM() % id) + iso.codes.SPACE() + (iso.codes.COMMENT(name)))
        self.write('\n')

    def program_stop(self, optional=False):
        if (optional) :
            self.write(iso.codes.STOP_OPTIONAL() + '\n')
            self.prev_g0123 = ''
        else :
            self.write(iso.codes.STOP() + '\n')
            self.prev_g0123 = ''


    def program_end(self):
        self.write(iso.codes.PROGRAM_END() + '\n')

    def flush_nc(self):
        if len(self.g) == 0 and len(self.m) == 0: return
        self.write_preps()
        self.write_misc()
        self.write('\n')

    ############################################################################
    ##  Subprograms

    def sub_begin(self, id, name=''):
        self.write((iso.codes.PROGRAM() % id) + iso.codes.SPACE() + (iso.codes.COMMENT(name)))
        self.write('\n')

    def sub_call(self, id):
        self.write((iso.codes.SUBPROG_CALL() % id) + '\n')

    def sub_end(self):
        self.write(iso.codes.SUBPROG_END() + '\n')

    ############################################################################
    ##  Settings

    def imperial(self):
        self.g += iso.codes.IMPERIAL()
        self.fmt = iso.codes.FORMAT_IN()

    def metric(self):
        self.g += iso.codes.METRIC()
        self.fmt = iso.codes.FORMAT_MM()

    def absolute(self):
        self.g += iso.codes.ABSOLUTE()
        self.absolute_flag = True

    def incremental(self):
        self.g += iso.codes.INCREMENTAL()
        self.absolute_flag = False

    def polar(self, on=True):
        if (on) : self.g += iso.codes.POLAR_ON()
        else : self.g += iso.codes.POLAR_OFF()

    def set_plane(self, plane):
        if (plane == 0) : self.g += iso.codes.PLANE_XY()
        elif (plane == 1) : self.g += iso.codes.PLANE_XZ()
        elif (plane == 2) : self.g += iso.codes.PLANE_YZ()

    def set_temporary_origin(self, x=None, y=None, z=None, a=None, b=None, c=None):
        self.write((iso.codes.SET_TEMPORARY_COORDINATE_SYSTEM()))
        if (x != None): self.write( iso.codes.SPACE() + 'X ' + (self.fmt % x) )
        if (y != None): self.write( iso.codes.SPACE() + 'Y ' + (self.fmt % y) )
        if (z != None): self.write( iso.codes.SPACE() + 'Z ' + (self.fmt % z) )
        if (a != None): self.write( iso.codes.SPACE() + 'A ' + (self.fmt % a) )
        if (b != None): self.write( iso.codes.SPACE() + 'B ' + (self.fmt % b) )
        if (c != None): self.write( iso.codes.SPACE() + 'C ' + (self.fmt % c) )
        self.write('\n')

    def remove_temporary_origin(self):
        self.write((iso.codes.REMOVE_TEMPORARY_COORDINATE_SYSTEM()))
        self.write('\n')

    ############################################################################
    ##  Tools

    def tool_change(self, id):
        self.write((iso.codes.TOOL() % id) + '\n')
        self.t = id

    def tool_defn(self, id, name='', params=None):
        pass

    def offset_radius(self, id, radius=None):
        pass

    def offset_length(self, id, length=None):
        pass

    ############################################################################
    ##  Datums

    def datum_shift(self, x=None, y=None, z=None, a=None, b=None, c=None):
        pass

    def datum_set(self, x=None, y=None, z=None, a=None, b=None, c=None):
        pass

    # This is the coordinate system we're using.  G54->G59, G59.1, G59.2, G59.3
    # These are selected by values from 1 to 9 inclusive.
    def workplane(self, id):
        if ((id >= 1) and (id <= 6)):
            self.g += iso.codes.WORKPLANE() % (id + iso.codes.WORKPLANE_BASE())
        if ((id >= 7) and (id <= 9)):
            self.g += ((iso.codes.WORKPLANE() % (6 + iso.codes.WORKPLANE_BASE())) + ('.%i' % (id - 6)))


    ############################################################################
    ##  Rates + Modes

    def feedrate(self, f):
        self.f = iso.codes.FEEDRATE() + (self.ffmt % f)
        self.fhv = False

    def feedrate_hv(self, fh, fv):
        self.fh = fh
        self.fv = fv
        self.fhv = True

    def calc_feedrate_hv(self, h, v):
        if math.fabs(v) > math.fabs(h * 2):
            # some horizontal, so it should be fine to use the horizontal feed rate
            self.f = iso.codes.FEEDRATE() + (self.ffmt % self.fv)
        else:
            # not much, if any horizontal component, so use the vertical feed rate
            self.f = iso.codes.FEEDRATE() + (self.ffmt % self.fh)

    def spindle(self, s, clockwise):
        if s < 0: clockwise = not clockwise
        s = abs(s)
        self.s = iso.codes.SPINDLE(iso.codes.FORMAT_ANG(), s)
        if clockwise:
            self.s = self.s + iso.codes.SPINDLE_CW()
        else:
            self.s = self.s + iso.codes.SPINDLE_CCW()

    def coolant(self, mode=0):
        if (mode <= 0) : self.m.append(iso.codes.COOLANT_OFF())
        elif (mode == 1) : self.m.append(iso.codes.COOLANT_MIST())
        elif (mode == 2) : self.m.append(iso.codes.COOLANT_FLOOD())

    def gearrange(self, gear=0):
        if (gear <= 0) : self.m.append(iso.codes.GEAR_OFF())
        elif (gear <= 4) : self.m.append(iso.codes.GEAR() % (gear + GEAR_BASE()))

    ############################################################################
    ##  Moves

    def rapid(self, x=None, y=None, z=None, a=None, b=None, c=None):
        self.write_blocknum()
        if self.g0123_modal:
            if self.prev_g0123 != iso.codes.RAPID():
                self.write(iso.codes.RAPID())
                self.prev_g0123 = iso.codes.RAPID()
        else:
            self.write(iso.codes.RAPID())
        self.write_preps()

        if (y != None):
            dy = y - self.y
            if (self.absolute_flag ):
                self.write(iso.codes.X() + (self.fmt % (y*2)))
            else:
                self.write(iso.codes.X() + (self.fmt % (dy*2)))

            self.y = y

        if (x != None):
            dx = x - self.x
            if (self.absolute_flag ):
                self.write(iso.codes.Z() + (self.fmt % x))
            else:
                self.write(iso.codes.Z() + (self.fmt % dx))
            self.x = x


        if (z != None):
            dz = z - self.z
            if (self.absolute_flag ):
                pass
                #self.write(iso.codes.Z() + (self.fmt % z))
            else:
                pass
                #self.write(iso.codes.Z() + (self.fmt % dz))

            self.z = z

        if (a != None):
            da = a - self.a
            if (self.absolute_flag ):
                self.write(iso.codes.A() + (self.fmt % a))
            else:
                self.write(iso.codes.A() + (self.fmt % da))
            self.a = a

        if (b != None):
            db = b - self.b
            if (self.absolute_flag ):
                self.write(iso.codes.B() + (self.fmt % b))
            else:
                self.write(iso.codes.B() + (self.fmt % db))
            self.b = b

        if (c != None):
            dc = c - self.c
            if (self.absolute_flag ):
                self.write(iso.codes.C() + (self.fmt % c))
            else:
                self.write(iso.codes.C() + (self.fmt % dc))
            self.c = c
        self.write_spindle()
        self.write_misc()
        self.write('\n')

    def feed(self, x=None, y=None, z=None, a=None, b=None, c=None):
        if self.same_xyz(x, y, z): return
        self.write_blocknum()
        if self.g0123_modal:
            if self.prev_g0123 != iso.codes.FEED():
                self.write(iso.codes.FEED())
                self.prev_g0123 = iso.codes.FEED()
        else:
            self.write(iso.codes.FEED())
        self.write_preps()
        dx = dy = dz = 0

        if (y != None):
            dy = y - self.y
            if (self.absolute_flag ):
                self.write(iso.codes.X() + (self.fmt % (y*2)))
            else:
                self.write(iso.codes.X() + (self.fmt % (dy*2)))

            self.y = y

        if (x != None):
            dx = x - self.x
            if (self.absolute_flag ):
                self.write(iso.codes.Z() + (self.fmt % x))
            else:
                self.write(iso.codes.Z() + (self.fmt % dx))
            self.x = x

        if (z != None):
            dz = z - self.z
            if (self.absolute_flag ):
                pass
                #self.write(iso.codes.Z() + (self.fmt % z))
            else:
                pass
                #self.write(iso.codes.Z() + (self.fmt % dz))

            self.z = z
        if (self.fhv) : self.calc_feedrate_hv(math.sqrt(dx*dx+dy*dy), math.fabs(dz))
        self.write_feedrate()
        self.write_spindle()
        self.write_misc()
        self.write('\n')

    def same_xyz(self, x=None, y=None, z=None):
        if (x != None):
            if (self.fmt % x) != (self.fmt % self.x):
                return False
        if (y != None):
            if (self.fmt % y) != (self.fmt % self.y):
                return False
        if (z != None):
            if (self.fmt % z) != (self.fmt % self.z):
                return False

        return True

    def arc(self, cw, x=None, y=None, z=None, i=None, j=None, k=None, r=None):
        if self.same_xyz(x, y, z): return
        self.write_blocknum()
        arc_g_code = ''
        if cw: arc_g_code = iso.codes.ARC_CW()
        else: arc_g_code = iso.codes.ARC_CCW()
        if self.g0123_modal:
            if self.prev_g0123 != arc_g_code:
                self.write(arc_g_code)
                self.prev_g0123 = arc_g_code
        else:
            self.write(arc_g_code)
        self.write_preps()
# make X take y values and multiply by 2 for diameter values for lathe
        if (y != None):
            dy = y - self.y
            if (self.absolute_flag ):
                self.write(iso.codes.X() + (self.fmt % (y*2)))
            else:
                self.write(iso.codes.X() + (self.fmt % (dy*2)))
            self.y = y

#make Z take x values for lathe
        if (x != None):
            dx = x - self.x
            if (self.absolute_flag ):
                self.write(iso.codes.Z() + (self.fmt % x))
            else:
                self.write(iso.codes.Z() + (self.fmt % dx))
            self.x = x
        if (z != None):
            dz = z - self.z
            if (self.absolute_flag ):
                pass
                #self.write(iso.codes.X() + (self.fmt % z))
            else:
                pass
                #self.write(iso.codes.X() + (self.fmt % dz))
            self.z = z

        if (j != None) : self.write(iso.codes.CENTRE_X() + (self.fmt % j)) #change the order
        if (i != None) : self.write(iso.codes.CENTRE_Z() + (self.fmt % i)) #and reversed i and j
        if (k != None) :pass # self.write(iso.codes.CENTRE_Z() + (self.fmt % k))
        if (r != None) : self.write(iso.codes.RADIUS() + (self.fmt % r))
#       use horizontal feed rate
        if (self.fhv) : self.calc_feedrate_hv(1, 0)
        self.write_feedrate()
        self.write_spindle()
        self.write_misc()
        self.write('\n')

    def arc_cw(self, x=None, y=None, z=None, i=None, j=None, k=None, r=None):
        self.arc(True, x, y, z, i, j, k, r)

    def arc_ccw(self, x=None, y=None, z=None, i=None, j=None, k=None, r=None):
        self.arc(False, x, y, z, i, j, k, r)

    def dwell(self, t):
        self.write_blocknum()
        self.write_preps()
        self.write(iso.codes.DWELL() + (iso.codes.TIME() % t))
        self.write_misc()
        self.write('\n')

    def rapid_home(self, x=None, y=None, z=None, a=None, b=None, c=None):
        pass

    def rapid_unhome(self):
        pass

    def set_machine_coordinates(self):
        self.write(iso.codes.MACHINE_COORDINATES())
        self.prev_g0123 = ''

    ############################################################################
    ##  CRC

    def use_CRC(self):
        return self.useCrc

    def start_CRC(self, left = True, radius = 0.0):
        # set up prep code, to be output on next line
        if self.t == None:
            raise "No tool specified for start_CRC()"
        self.g = ('G41' + iso.codes.SPACE() + 'D%i') % self.t

    def end_CRC(self):
        self.g = 'G40'
        self.write_blocknum()
        self.write_preps()
        self.write_misc()
        self.write('\n')

    ############################################################################
    ##  Cycles

    def pattern(self):
        pass


    def profile(self):
        pass

    def end_canned_cycle(self):
        self.write_blocknum()
        self.write(iso.codes.END_CANNED_CYCLE() + '\n')
        self.prev_drill = ''
        self.prev_g0123 = ''
        self.prev_z = ''
        self.prev_f = ''
        self.prev_retract = ''
    ############################################################################
    ##  Misc

    def comment(self, text):
        self.write((iso.codes.COMMENT(text) + '\n'))

    def insert(self, text):
        pass

    def block_delete(self, on=False):
        pass

    def variable(self, id):
        return (iso.codes.VARIABLE() % id)

    def variable_set(self, id, value):
        self.write_blocknum()
        self.write((iso.codes.VARIABLE() % id) + (iso.codes.VARIABLE_SET() % value) + '\n')

################################################################################

nc.creator = CreatorIso()
