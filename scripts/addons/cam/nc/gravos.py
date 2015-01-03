from . import nc
from . import iso

class Creator(iso.Creator):
	def init(self): 
		iso.Creator.init(self) 
		
	def SPACE(self): return(' ')
	
	def COMMENT(self,comment): return( (';%s' % comment ) )
	
	def PROGRAM(self): return( '')
	
	def comment(self, text):
		self.write((self.COMMENT(text) + '\n'))
	
	def program_begin(self, id, comment):
		self.write( (';' + comment  + '\n') )
	
	def write_blocknum(self):
		#optimise
		#self.write(self.BLOCK() % self.n)
		self.n += 1
	
		
	
	def FORMAT_DWELL(self): return( self.SPACE() + self.DWELL() + ' X%f')
	
	def SPINDLE_OFF(self): return('M05')
	#optimize
	def RAPID(self): return('G0')
	def FEED(self): return('G1')
	'''
	def SPINDLE_DWELL(self,dwell):
		w='\n'+self.BLOCK() % self.n+ self.DWELL() % dwell
		return w
		
	def SPINDLE_CW(self,dwell):
		return('M03' + self.SPINDLE_DWELL(dwell) )

	def SPINDLE_CCW(self,dwell):
		return('M04' + self.SPINDLE_DWELL(dwell))
	
	def write_spindle(self):
		#self.write('\n')
		#self.write_blocknum()
		self.s.write(self)
	'''
	
	def tool_change(self, id):
		self.write_blocknum()
		self.write(self.SPACE() + (self.TOOL() % id) + '\n')
		self.write_blocknum()
		self.write(self.SPACE() + self.s.str)
		self.write('\n')
		self.flush_nc()
		self.t = id
		
	#def write_spindle(self):
	#	if self.s.str!=None:
	#		self.write(self.s.str)
	#	self.s.str = None
	
	def PROGRAM_END(self): return( 'M30')
	
	def program_end(self):
		self.write_blocknum()
		self.write(self.SPACE() + self.SPINDLE_OFF() + self.SPACE() + self.PROGRAM_END() + '\n')
		

nc.creator = Creator()

