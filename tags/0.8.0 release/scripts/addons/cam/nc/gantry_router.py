from . import nc
from . import emc2

class Creator(emc2.Creator):
	def init(self): 
		emc2.Creator.init(self) 

	def program_begin(self, id, comment):
		self.write( ('(' + comment + ')' + '\n') )

	def tool_defn(self, id, name='', radius=None, length=None, gradient=None):
		pass

	def spindle(self, s, clockwise):
		pass

nc.creator = Creator()

