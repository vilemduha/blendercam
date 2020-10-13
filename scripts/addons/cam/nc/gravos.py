from . import nc
from . import iso


class Creator(iso.Creator):
	def __init__(self):
		iso.Creator.__init__(self)

	def SPACE_STR(self): return ' '
	def COMMENT(self, comment): return( (';%s' % comment ) )
	def PROGRAM(self): return(None)

	def program_begin(self, id, comment):
		self.write( (';' + comment  + '\n') )
	def TIME(self): return('X')

	def SPINDLE_OFF(self): return('M05')
	# optimize
	def RAPID(self): return('G0')
	def FEED(self): return('G1')

	# def SPINDLE_DWELL(self,dwell):
	# 	w='\n'+self.BLOCK() % self.n+ self.DWELL() % dwell
	# 	return w
	#
	# def SPINDLE_CW(self,dwell):
	# 	return('M03' + self.SPINDLE_DWELL(dwell) )
	#
	# def SPINDLE_CCW(self,dwell):
	# 	return('M04' + self.SPINDLE_DWELL(dwell))
	#
	# def write_spindle(self):
	# 	#self.write('\n')
	# 	#self.write_blocknum()
	# 	self.s.write(self)


	def tool_change(self, id):
		#print(self.SPACE())
		#print(self.TOOL())
		self.write(self.SPACE() + (self.TOOL() % id) + '\n')
		#self.write('\n')
		self.flush_nc()
		self.t = id

	#def write_spindle(self):
	#	if self.s.str!=None:
	#		self.write(self.s.str)
	#	self.s.str = None

	def PROGRAM_END(self): return( 'M30')

	def program_end(self):
		self.write(self.SPACE() + self.SPINDLE_OFF() + self.SPACE() + self.PROGRAM_END() + '\n')


nc.creator = Creator()
