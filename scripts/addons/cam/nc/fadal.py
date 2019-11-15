################################################################################
# fadal.py
#
# Fadal ISO NC code creator
#
# TurBoss, 19/06/2016
#
################################################################################

from . import nc
from . import iso
from .format import Format

class Creator(iso.Creator):
	def __init__(self):
		iso.Creator.__init__(self)

		# internal variables

		self.fmt = Format(add_trailing_zeros = True)

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

	def program_end(self):
		if self.z_for_g53 != None:
			self.write(self.SPACE() + self.MACHINE_COORDINATES() + self.SPACE() + 'Z' + self.fmt.string(self.z_for_g53) + '\n')
		self.write(self.SPACE() + self.PROGRAM_END() + '\n')
		self.write('%')

		if self.temp_file_to_append_on_close != None:
			f_in = open(self.temp_file_to_append_on_close, 'r')
			while (True):
				line = f_in.readline()
				if (len(line) == 0) : break
				self.write(line)
			f_in.close()

		self.file_close()

		if self.output_block_numbers:
			# number every line of the file afterwards
			self.number_file(self.filename)

			for f in self.subroutine_files:
				self.number_file(f)

nc.creator = Creator()
