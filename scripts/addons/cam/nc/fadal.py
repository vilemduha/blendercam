################################################################################
# fadal.py
#
# Fadal ISO NC code creator
#
# TurBoss, 19/06/2016

import math
from . import nc
from . import iso
from .format import Format
from .format import *

class Creator(iso.Creator):
	def __init__(self): 
		iso.Creator.__init__(self) 
		
		# internal variables
		
		self.fmt = Format(add_trailing_zeros = True)
		self.output_block_numbers = True
		self.start_block_number = 0
		self.block_number_increment = 1
		
	############################################################################
	##  Codes
	
	def SPACE_STR(self): return ' '
		  
	############################################################################
	##  Programs

	def program_begin(self, id, name=''):
		if self.use_this_program_id:
			id = self.use_this_program_id
		if self.PROGRAM() != None:
			self.write('%')
			self.write('\n')
			self.writem([(self.PROGRAM() % id), self.SPACE(), (self.COMMENT(name))])
			self.write('\n')
		self.program_id = id
		self.program_name = name

nc.creator = Creator()
