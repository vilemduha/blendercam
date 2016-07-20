################################################################################
# iso.py
#
# Simple FADAL ISO
#
# TurBoss, 2016-06-19

from . import nc
from . import iso

class Creator(iso.Creator):
	def __init__(self): 
		iso.Creator.__init__(self) 
		
		self.fmt = Format(add_leading_zeros = 1)
	
	def SPACE_STR(self): return ' '


nc.creator = Creator()
