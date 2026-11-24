################################################################################
# emc2b_crc.py
#
# a class derived from emc2b machine, with Cutter Radius Compensation turned on.
#
# Dan Heeks, 18th Jan 2011

from . import emc2b, nc

################################################################################


class Creator(emc2b.Creator):
    def __init__(self):
        emc2b.Creator.__init__(self)
        self.useCrc = True


################################################################################


nc.creator = Creator()
