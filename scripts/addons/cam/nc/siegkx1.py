################################################################################
# siegkx1.py
#
# Post Processor for the Sieg KX1 machine
# It is just an ISO machine, but I don't want the tool definition lines
#
# Dan Heeks, 5th March 2009

from . import nc
from . import iso_modal
import math

################################################################################
class Creator(iso_modal.Creator):

    def __init__(self):
        iso_modal.Creator.__init__(self)

    def tool_defn(self, id, name='', radius=None, length=None, gradient=None):
        pass
            
################################################################################

nc.creator = Creator()
