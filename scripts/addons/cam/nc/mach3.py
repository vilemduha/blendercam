from . import nc
from . import iso

class Creator(iso.Creator):
	def __init__(self):
		iso.Creator.__init__(self)

	def SPACE_STR(self): return(' ')

	def program_begin(self, id, comment):
		self.write( ('(' + 'GCode created using the HeeksCNC Mach3 post processor' + ')' + '\n') )
		self.write( ('(' + comment + ')' + '\n') )

	def tool_change(self, id):
		self.write('G43H%i'% id +'\n')
		self.write((self.TOOL() % id) + '\n')
		self.t = id

nc.creator = Creator()
