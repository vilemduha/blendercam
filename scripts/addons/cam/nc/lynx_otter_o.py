from . import nc
from . import iso


class Creator(iso.Creator):
	def __init__(self):
		iso.Creator.__init__(self)

	def SPACE_STR(self): return(' ')

	def COMMENT(self, comment): return('')

	def PROGRAM(self): return(None)

	def FORMAT_DWELL(self): return( self.SPACE() + self.DWELL() + ' X%f')
	def SPINDLE_OFF(self): return('M05\n')
	#optimize
	def RAPID(self): return('G00')
	def FEED(self): return('G01')

	# def IMPERIAL(self): return('G20\n')
	# def METRIC(self): return('G21\n')
	# def ABSOLUTE(self): return('G90\n')
	# def INCREMENTAL(self): return('G91\n')
	# def PLANE_XY(self): return('17\n')
	# def PLANE_XZ(self): return('18\n')
	# def PLANE_YZ(self): return('19\n')

	def dwell(self, t):
		pass
		"""
		self.write_blocknum()
		self.write_preps()
		self.write(self.FORMAT_DWELL() % t)
		self.write_misc()
		self.write('\n')
		"""
	def tool_change(self, id):
		pass
		# self.write_blocknum()
		# self.write(self.SPACE() + (self.TOOL() % id) + '\n')
		# self.write_blocknum()
		# self.write(self.SPACE() + self.s.str)
		# self.write('\n')
		# self.flush_nc()
		# self.t = id

	def PROGRAM_END(self): return( self.SPACE() + self.SPINDLE_OFF() + self.SPACE() + 'M30')


nc.creator = Creator()
