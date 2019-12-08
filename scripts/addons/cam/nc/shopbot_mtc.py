################################################################################
# shopbot_prs.py
#
# Simple ShopBot NC code creator, manual tool change (MTC)
#
# dhull, January 2015
#	from iso.py
#
#	TTD:
#		3.	need to get tool description from system
#		4.	get arcs working
#

from . import nc
import math
from .format import Format
from .format import *
# to allow access to other CAM data:
import bpy

################################################################################
class Creator(nc.Creator):

	def __init__(self):
		nc.Creator.__init__(self)

		s=bpy.context.scene
		cm=s.cam_machine
		self.fmt = Format()
		self.ffmt = Format(number_of_decimal_places = 2)
		self.sfmt = Format(number_of_decimal_places = 1)
		self.unitscale = 1
		self.startx = cm.starting_position.x
		self.starty = cm.starting_position.y
		self.startz = cm.starting_position.z
		self.tcx = cm.mtc_position.x
		self.tcy = cm.mtc_position.y
		self.tcz = cm.mtc_position.z
		self.endx = cm.ending_position.x
		self.endy = cm.ending_position.y
		self.endz = cm.ending_position.z
		self.metric_flag = False
		self.absolute_flag = True

	############################################################################
	##	Codes

	def SPACE(self): return('')
	def COMMENT(self,comment): return( '\' %s' % comment  )
	def TOOL(self): return('T%i' + self.SPACE() + 'M06')

	############################################################################
	##	Internals

	def write_feedrate(self):
		self.f.write(self)

	def write_spindle(self):
		self.s.write(self)

	############################################################################
	##	Programs

	def program_begin(self, id, name=''):
		self.writem([self.SPACE() , self.COMMENT(name)])
		self.write('\n\n')
		self.write('IF %(25)=1 THEN GOTO UNIT_ERROR\n')
		self.write('\n')

	def program_end(self):
		self.write('C7\n')
		self.write('JZ,' + self.fmt.string(self.endz) + '\n')
		self.write('J2,' + self.fmt.string(self.endx) + ',' + self.fmt.string(self.endy) + '\n')
		self.write('END\n')
		self.write('\'\n')
		self.write('UNIT_ERROR:\n')
		self.write('C#,91\n')
		self.write('END\n')

	def flush_nc(self):
		return

	############################################################################
	##	Subprograms


	############################################################################
	##	Settings

	def imperial(self):
		self.fmt.number_of_decimal_places = 4
		self.unitscale = 0.0254
		self.metric_flag=False

	def metric(self):
		self.metric_flag=True
		self.unitscale = 1
		self.fmt.number_of_decimal_places = 3

	def absolute(self):
		self.absolute_flag = True
		self.write('SA\n')

	def incremental(self):
		self.absolute_flag = False
		self.write('SR\n')

	def set_plane(self, plane):
		return

	############################################################################
	##	new graphics origin- make a new coordinate system and snap it onto the geometry
	##	the toolpath generated should be translated


	############################################################################
	##	Tools

	def tool_change(self, id):
		self.write('C7\n')
		self.write('&Tool=' + self.fmt.string(id) + '\n')
		self.write('JZ,' + (self.fmt.string(self.tcz)) + '\n')
		self.write('J2,' + (self.fmt.string(self.tcx)) + ',' + (self.fmt.string(self.tcy)) + '\n')
		self.write('\' Use tool '+ self.fmt.string(id) + '\n')
		self.write('PAUSE\n')
		self.write('C2\n')
		self.t = id
		self.write('C6\n')
		self.write('PAUSE 2\n')

	############################################################################
	##	Datums


	############################################################################
	##	Rates + Modes

	def feedrate(self, f):
		if (self.metric_flag == True):
		  self.write('MS,' + (self.sfmt.string(f)) + ',' +	(self.sfmt.string(f)) + '\n')
		else:
		  self.write('MS,' + (self.sfmt.string(f*self.unitscale)) + ',' +  (self.sfmt.string(f*self.unitscale)) + '\n')

	def spindle(self, s, clockwise):
		self.write('TR,' + self.fmt.string(s) + '\n')

	############################################################################
	##	Moves

	def rapid(self, x=None, y=None, z=None, a=None, b=None, c=None):
		# different commands for X only, or Y only, or Z only, or (X and Y), or (X, Y, and Z)
		if (x != None and y != None and z != None):
			self.write('J3,' + (self.fmt.string(x * self.unitscale)))
			self.write(',' + (self.fmt.string(y * self.unitscale)))
			self.write(',' + (self.fmt.string(z * self.unitscale)))
			self.write('\n')
		elif (x != None and y != None and z == None):
			self.write('J2,' + (self.fmt.string(x * self.unitscale)))
			self.write(',' + (self.fmt.string(y * self.unitscale)))
			self.write('\n')
		elif (x != None):
			self.write('JX,' + (self.fmt.string(x * self.unitscale)) + '\n')
		elif (y != None):
			self.write('JY,' + (self.fmt.string(y * self.unitscale)) + '\n')
		elif (z != None):
			self.write('JZ,' + (self.fmt.string(z * self.unitscale)) + '\n')

	def feed(self, x=None, y=None, z=None, a=None, b=None, c=None):
		if (x != None and y != None and z != None):
			self.write('M3,' + (self.fmt.string(x * self.unitscale)))
			self.write(',' + (self.fmt.string(y * self.unitscale)))
			self.write(',' + (self.fmt.string(z * self.unitscale)))
			self.write('\n')
		elif (x != None and y != None and z == None):
			self.write('M2,' + (self.fmt.string(x * self.unitscale)))
			self.write(',' + (self.fmt.string(y * self.unitscale)))
			self.write('\n')
		elif (x != None):
			self.write('MX,' + (self.fmt.string(x * self.unitscale)) + '\n')
		elif (y != None):
			self.write('MY,' + (self.fmt.string(y * self.unitscale)) + '\n')
		elif (z != None):
			self.write('MZ,' + (self.fmt.string(z * self.unitscale)) + '\n')

	def arc(self, cw, x=None, y=None, z=None, i=None, j=None, k=None, r=None):
		if (r != None):
			self.write('CG,' + self.fmt.string(r * self.unitscale * 2))
			self.write(',' + self.fmt.string(x * self.unitscale))
			self.write(',' + self.fmt.string(y * self.unitscale))
			self.write(', ,')
			self.write(',T,1')
			self.write('\n')
		else:
			self.write('CG, ')
			self.write(',' + self.fmt.string(x * self.unitscale))
			self.write(',' + self.fmt.string(y * self.unitscale))
			self.write(',' + self.fmt.string(i * self.unitscale))
			self.write(',' + self.fmt.string(j * self.unitscale))
			self.write(',T,1')
			self.write('\n')
		return

	############################################################################
	##	CRC


	############################################################################
	##	Cycles


	############################################################################
	##	Misc

	def comment(self, text):
		self.write((self.COMMENT(text) + '\n'))

	def variable(self, id):
		return (self.VARIABLE() % id)

	def variable_set(self, id, value):
		self.write('&' + (self.VARIABLE() % id) + self.SPACE() + (self.VARIABLE_SET() % value) + '\n')


################################################################################

nc.creator = Creator()
