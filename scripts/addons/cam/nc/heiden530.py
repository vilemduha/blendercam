################################################################################
# heiden.py
#
# Post for heidenhain
#
# TurBoss 01/07/2016
#
################################################################################

from . import nc
from . import iso
import math
from .format import Format
from .format import *

class Creator(iso.Creator):
    def __init__(self):
        iso.Creator.__init__(self)

        self.program_id = 0

        self.n = 0
        self.t = 0

        self.fmt = Format()

        self.absolute_flag = True

        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        self.shift_x = 0.0
        self.shift_y = 0.0
        self.shift_z = 0.0


    ############################################################################
    ##  Codes

    def SPACE(self): return(' ')
    def NEW_LINE(self): return('\n')

    def BLOCK(self): return('%i')
    def COMMENT(self,comment): return( (';%s' % comment ) )

    def BEGIN_PGM(self): return('BEGIN PGM %i')
    def END_PGM(self): return('END PGM %i')

    def TOOL(self): return('TOOL CALL %i Z')

    def METRIC(self): return('MM')

    def RAPID(self): return('L')
    def FEED(self): return('L')

    def ARC_CC(self): return('CC')
    def ARC_C(self): return('C')

    def ARC_CW(self): return('DR-')
    def ARC_CCW(self): return('DR+')

    def X(self): return('X')
    def Y(self): return('Y')
    def Z(self): return('Z')

    ############################################################################
    ##  Internals

    def write_blocknum(self):
        self.write(self.BLOCK() % self.n)
        self.n += 1

    def write_spindle(self):
        self.s.write(self)
        self.write(self.NEW_LINE())

    ############################################################################
    ##  Programs

    def program_begin(self, id, name=''):
        self.program_id = id

        self.write_blocknum()

        self.write(self.SPACE())
        self.write(self.BEGIN_PGM() % self.program_id)
        self.write(self.SPACE())
        self.write(self.METRIC())
        self.write(self.NEW_LINE())

    def program_end(self):
        self.write_blocknum()

        self.write(self.SPACE())
        self.write(self.END_PGM() % self.program_id)
        self.write(self.SPACE())
        self.write(self.METRIC())
        self.write(self.NEW_LINE())

    ############################################################################
    ##  Settings

    def absolute(self):
        pass

    def metric(self):
        pass

    def set_plane(self, plane):
        pass

    ############################################################################
    ##  Tools

    def tool_change(self, id):
        self.t = id

        self.write_blocknum()

        self.write(self.SPACE())
        self.write(self.TOOL() % self.t)

    ############################################################################
    ##  Moves

    def rapid(self, x=None, y=None, z=None, a=None, b=None, c=None ):

        self.write_blocknum()

        self.write(self.SPACE())
        self.write(self.RAPID())

        self.write_preps()

        if (x != None):
            dx = x - self.x
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.X() + (self.fmt.string(x + self.shift_x)))
            else:
                self.write(self.SPACE() + self.X() + (self.fmt.string(dx)))
            self.x = x
        if (y != None):
            dy = y - self.y
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.Y() + (self.fmt.string(y + self.shift_y)))
            else:
                self.write(self.SPACE() + self.Y() + (self.fmt.string(dy)))

            self.y = y
        if (z != None):
            dz = z - self.z
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.Z() + (self.fmt.string(z + self.shift_z)))
            else:
                self.write(self.SPACE() + self.Z() + (self.fmt.string(dz)))

            self.z = z

        self.write_spindle()
        self.write_misc()

    def feed(self, x=None, y=None, z=None, a=None, b=None, c=None):

        if self.same_xyz(x, y, z): return

        self.write_blocknum()

        self.write(self.SPACE())
        self.write(self.FEED())

        dx = dy = dz = 0

        if (x != None):
            dx = x - self.x
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.X() + (self.fmt.string(x + self.shift_x)))
            else:
                self.write(self.SPACE() + self.X() + (self.fmt.string(dx)))
            self.x = x
        if (y != None):
            dy = y - self.y
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.Y() + (self.fmt.string(y + self.shift_y)))
            else:
                self.write(self.SPACE() + self.Y() + (self.fmt.string(dy)))

            self.y = y
        if (z != None):
            dz = z - self.z
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.Z() + (self.fmt.string(z + self.shift_z)))
            else:
                self.write(self.SPACE() + self.Z() + (self.fmt.string(dz)))

            self.z = z

        self.write_feedrate()
        self.write_spindle()
        self.write_misc()

    ############################################################################
    ##  Misc

    def comment(self, text):
        self.write((self.COMMENT(text) + '\n'))
nc.creator = Creator()
