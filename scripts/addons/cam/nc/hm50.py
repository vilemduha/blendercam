from . import nc
from . import emc2

class Creator(emc2.Creator):
	def __init__(self):
		emc2.Creator.__init__(self)

	def program_begin(self, id, comment):
		self.write( ('(' + comment + ')' + '\n') )

	def tool_change(self, id):
		self.write('G53 G00 Z30\n')
		self.write((self.TOOL() % id) + '\n')
		self.write('G01 Z100.000 F800.000\n')
		self.write('M0\n')
		self.write('G01 Z10.000 F300.000\n')


nc.creator = Creator()
