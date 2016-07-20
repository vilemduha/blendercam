################################################################################
# fadal.py
#
# Fadal ISO NC code creator
#
# TurBoss, 19/06/2016

from . import nc
from . import iso
from .format import Format
from .format import *

class Creator(iso.Creator):
	def __init__(self): 
		iso.Creator.__init__(self) 
		
		self.fmt = Format(add_trailing_zeros = True)

	def SPACE_STR(self): return ' '
nc.creator = Creator()
