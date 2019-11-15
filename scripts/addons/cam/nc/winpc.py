from . import nc
from . import iso_modal
import math
import datetime
import time

now = datetime.datetime.now()

class Creator(iso_modal.Creator):
    def __init__(self):
        iso_modal.Creator.__init__(self)
        self.absolute_flag = True
        self.prev_g91 = ''
        self.useCrc = False
        self.start_of_line = True

    def SPACE_STR(self): return ' '

    def TOOL(self): return('T%i' + self.SPACE() )


############################################################################
## Internal
    def write_spindle(self): return ''

############################################################################
## Programs

    def program_begin(self, id, comment):
        if (self.useCrc == False):
            self.write( ('(Created with win-pc post processor ' + str(now.strftime("%Y/%m/%d %H:%M")) + ')' + '\n') )
        else:
            self.write( ('(Created with win-pc Cutter Radius Compensation post processor ' + str(now.strftime("%Y/%m/%d %H:%M")) + ')' + '\n') )
        #self.rapid( x=0.0, y=0.0, z=30.0 )

    def program_end(self):
        self.write(self.SPACE() + self.PROGRAM_END() + '\n')
        #self.rapid( x=0.0, y=0.0, z=30.0 )

############################################################################
##  Settings

    def tool_defn(self, id, name='', params=None):
        #self.write('G43 \n')
        pass

    def tool_change(self, id):
        self.write(self.SPACE() + (self.TOOL() % id) + self.SPACE() + '\n')
        self.t = id

    def comment(self, text):
        self.write((self.COMMENT(text) + '\n'))

# This is the coordinate system we're using.  G54->G59, G59.1, G59.2, G59.3
# These are selected by values from 1 to 9 inclusive.
    def workplane(self, id):
        if ((id >= 1) and (id <= 6)):
            self.write( (self.WORKPLANE() % (id + self.WORKPLANE_BASE())) + '\t (Select Relative Coordinate System)\n')
        if ((id >= 7) and (id <= 9)):
            self.write( ((self.WORKPLANE() % (6 + self.WORKPLANE_BASE())) + ('.%i' % (id - 6))) + '\t (Select Relative Coordinate System)\n')


############################################################################
##  Moves

############################################################################
##  Rates + Modes

## All feedrates are given in mm/s
    def feedrate(self, f):
        self.f.set(f/60)
        self.fhv = False

    def feedrate_hv(self, fh, fv):
        self.fh = fh/60
        self.fv = fv/60
        self.fhv = True

    def calc_feedrate_hv(self, h, v):
        if math.fabs(v) > math.fabs(h * 2):
            # some horizontal, so it should be fine to use the horizontal feed rate
            self.f.set(self.fv)
        else:
            # not much, if any horizontal component, so use the vertical feed rate
            self.f.set(self.fh)


############################################################################
## Probe routines
    def report_probe_results(self, x1=None, y1=None, z1=None, x2=None, y2=None, z2=None, x3=None, y3=None, z3=None, x4=None, y4=None, z4=None, x5=None, y5=None, z5=None, x6=None, y6=None, z6=None, xml_file_name=None ):
        if (xml_file_name != None):
            self.comment('Generate an XML document describing the probed coordinates found');
            self.write_blocknum()
            self.write('(LOGOPEN,')
            self.write(xml_file_name)
            self.write(')\n')

        self.write_blocknum()
        self.write('(LOG,<POINTS>)\n')

        if ((x1 != None) or (y1 != None) or (z1 != None)):
            self.write_blocknum()
            self.write('(LOG,<POINT>)\n')

        if (x1 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + x1 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<X>#<_value></X>)\n')

        if (y1 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + y1 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<Y>#<_value></Y>)\n')

        if (z1 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + z1 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<Z>#<_value></Z>)\n')

        if ((x1 != None) or (y1 != None) or (z1 != None)):
            self.write_blocknum()
            self.write('(LOG,</POINT>)\n')

        if ((x2 != None) or (y2 != None) or (z2 != None)):
            self.write_blocknum()
            self.write('(LOG,<POINT>)\n')

        if (x2 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + x2 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<X>#<_value></X>)\n')

        if (y2 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + y2 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<Y>#<_value></Y>)\n')

        if (z2 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + z2 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<Z>#<_value></Z>)\n')

        if ((x2 != None) or (y2 != None) or (z2 != None)):
            self.write_blocknum()
            self.write('(LOG,</POINT>)\n')

        if ((x3 != None) or (y3 != None) or (z3 != None)):
            self.write_blocknum()
            self.write('(LOG,<POINT>)\n')

        if (x3 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + x3 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<X>#<_value></X>)\n')

        if (y3 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + y3 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<Y>#<_value></Y>)\n')

        if (z3 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + z3 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<Z>#<_value></Z>)\n')

        if ((x3 != None) or (y3 != None) or (z3 != None)):
            self.write_blocknum()
            self.write('(LOG,</POINT>)\n')

        if ((x4 != None) or (y4 != None) or (z4 != None)):
            self.write_blocknum()
            self.write('(LOG,<POINT>)\n')

        if (x4 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + x4 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<X>#<_value></X>)\n')

        if (y4 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + y4 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<Y>#<_value></Y>)\n')

        if (z4 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + z4 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<Z>#<_value></Z>)\n')

        if ((x4 != None) or (y4 != None) or (z4 != None)):
            self.write_blocknum()
            self.write('(LOG,</POINT>)\n')

        if ((x5 != None) or (y5 != None) or (z5 != None)):
            self.write_blocknum()
            self.write('(LOG,<POINT>)\n')

        if (x5 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + x5 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<X>#<_value></X>)\n')

        if (y5 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + y5 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<Y>#<_value></Y>)\n')

        if (z5 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + z5 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<Z>#<_value></Z>)\n')

        if ((x5 != None) or (y5 != None) or (z5 != None)):
            self.write_blocknum()
            self.write('(LOG,</POINT>)\n')

        if ((x6 != None) or (y6 != None) or (z6 != None)):
            self.write_blocknum()
            self.write('(LOG,<POINT>)\n')

        if (x6 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + x6 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<X>#<_value></X>)\n')

        if (y6 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + y6 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<Y>#<_value></Y>)\n')

        if (z6 != None):
            self.write_blocknum()
            self.write('#<_value>=[' + z6 + ']\n')
            self.write_blocknum()
            self.write('(LOG,<Z>#<_value></Z>)\n')

        if ((x6 != None) or (y6 != None) or (z6 != None)):
            self.write_blocknum()
            self.write('(LOG,</POINT>)\n')

            self.write_blocknum()
            self.write('(LOG,</POINTS>)\n')

        if (xml_file_name != None):
            self.write_blocknum()
            self.write('(LOGCLOSE)\n')

    def open_log_file(self, xml_file_name=None ):
        self.write_blocknum()
        self.write('(LOGOPEN,')
        self.write(xml_file_name)
        self.write(')\n')

    def close_log_file(self):
        self.write_blocknum()
        self.write('(LOGCLOSE)\n')

    def log_coordinate(self, x=None, y=None, z=None):
        if ((x != None) or (y != None) or (z != None)):
            self.write_blocknum()
            self.write('(LOG,<POINT>)\n')

        if (x != None):
            self.write_blocknum()
            self.write('#<_value>=[' + x + ']\n')
            self.write_blocknum()
            self.write('(LOG,<X>#<_value></X>)\n')

        if (y != None):
            self.write_blocknum()
            self.write('#<_value>=[' + y + ']\n')
            self.write_blocknum()
            self.write('(LOG,<Y>#<_value></Y>)\n')

        if (z != None):
            self.write_blocknum()
            self.write('#<_value>=[' + z + ']\n')
            self.write_blocknum()
            self.write('(LOG,<Z>#<_value></Z>)\n')

        if ((x != None) or (y != None) or (z != None)):
            self.write_blocknum()
            self.write('(LOG,</POINT>)\n')

    def log_message(self, message=None ):
        self.write_blocknum()
        self.write('(LOG,' + message + ')\n')

nc.creator = Creator()
