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
		self.output_block_numbers = False
		self.output_tool_definitions = False

	def PROGRAM_END(self):	return ' '
	#optimize
	def RAPID(self): return('G0')
	def FEED(self): return('G1')

############################################################################
## Begin Program


	def program_begin(self, id, comment):
		if (self.useCrc == False):
			self.write( ('(Created with grbl post processor ' + str(now.strftime("%Y/%m/%d %H:%M")) + ')' + '\n') )
		else:
			self.write( ('(Created with grbl Cutter Radius Compensation post processor ' + str(now.strftime("%Y/%m/%d %H:%M")) + ')' + '\n') )




############################################################################
##  Settings

	def tool_defn(self, id, name='', params=None):
		pass

	def tool_change(self, id):
		pass


# This is the coordinate system we're using.  G54->G59, G59.1, G59.2, G59.3
# These are selected by values from 1 to 9 inclusive.
	def workplane(self, id):
		if ((id >= 1) and (id <= 6)):
			self.write_blocknum()
			self.write( (self.WORKPLANE() % (id + self.WORKPLANE_BASE())) + '\t (Select Relative Coordinate System)\n')
		if ((id >= 7) and (id <= 9)):
			self.write_blocknum()
			self.write( ((self.WORKPLANE() % (6 + self.WORKPLANE_BASE())) + ('.%i' % (id - 6))) + '\t (Select Relative Coordinate System)\n')


nc.creator = Creator()
