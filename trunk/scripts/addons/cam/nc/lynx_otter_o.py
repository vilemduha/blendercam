from . import nc
from . import iso

class Creator(iso.Creator):
	def init(self): 
		iso.Creator.init(self) 
		
	def SPACE(self): return(' ')
	
	def COMMENT(self,comment): return( ('' ) )
	
	def PROGRAM(self): return( '')
	
	def comment(self, text):
		self.write((self.COMMENT(text)))
	
	def program_begin(self, id, comment):
		self.write( ('') )
	
	#def write_blocknum(self):
	#	#optimise
		#self.write(self.BLOCK() % self.n)
	#	self.n += 1
	
	
	
	def FORMAT_DWELL(self): return( self.SPACE() + self.DWELL() + ' X%f')
	def SPINDLE_CW(self): return('M03')
	def SPINDLE_OFF(self): return('M05\n')
	#optimize
	def RAPID(self): return('G00')
	def FEED(self): return('G01')
	'''
	def IMPERIAL(self): return('G20\n')
	def METRIC(self): return('G21\n')
	def ABSOLUTE(self): return('G90\n')
	def INCREMENTAL(self): return('G91\n')
	def PLANE_XY(self): return('17\n')
	def PLANE_XZ(self): return('18\n')
	def PLANE_YZ(self): return('19\n')
	'''
	
	def dwell(self, t):
		pass;
		'''
		self.write_blocknum()
		self.write_preps()
		self.write(self.FORMAT_DWELL() % t)
		self.write_misc()
		self.write('\n')
		'''
	def tool_change(self, id):
		pass;
		#self.write_blocknum()
		#self.write(self.SPACE() + (self.TOOL() % id) + '\n')
		#self.write_blocknum()
		#self.write(self.SPACE() + self.s.str)
		#self.write('\n')
		#self.flush_nc()
		#self.t = id
		
	def write_spindle(self):
		if self.s.str!=None:
			self.write(self.s.str)
		self.s.str = None
		
	def write_misc(self):
		if (len(self.m)) : self.write('\n' + self.m.pop())
		
	def PROGRAM_END(self): return( 'M30')
	
	def program_end(self):
		self.write_blocknum()
		self.write(self.SPACE() + self.SPINDLE_OFF() + self.SPACE() + self.PROGRAM_END() + '\n')
		

nc.creator = Creator()

