################################################################################
# iso_read.py
#
# Simple ISO NC code parsing
#
# Hirutso Enni, 2009-01-13

from . import nc_read as nc
import re
import sys

################################################################################
class Parser(nc.Parser):

    def __init__(self, writer):
        nc.Parser.__init__(self, writer)

        self.pattern_main = re.compile('([(!;].*|\s+|[a-zA-Z0-9_:](?:[+-])?\d*(?:\.\d*)?|\w\#\d+|\(.*?\)|\#\d+\=(?:[+-])?\d*(?:\.\d*)?)')
        self.arc_centre_absolute = False
        self.arc_centre_positive = False
        self.oldx = None
        self.oldy = None
        self.oldz = None

        #if ( or ! or ; at least one space or a letter followed by some character or not followed by a +/- followed by decimal, with a possible decimal point
         #  followed by a possible deimcal, or a letter followed by # with a decimal . deimcal
        # add your character here > [(!;] for comments char
        # then look for the 'comment' function towards the end of the file and add another elif

    def ParseWord(self, word):
        if (word[0] == 'A' or word[0] == 'a'):
            self.col = "axis"
            self.a = eval(word[1:])
            self.move = True
        elif (word[0] == 'B' or word[0] == 'b'):
            self.col = "axis"
            self.b = eval(word[1:])
            self.move = True
        elif (word[0] == 'C' or word[0] == 'c'):
            self.col = "axis"
            self.c = eval(word[1:])
            self.move = True
        elif (word[0] == 'F' or word[0] == 'f'):
            self.col = "axis"
            self.writer.feedrate(word[1:])
        elif (word[0] == 'H' or word[0] == 'h'):
            self.col = "axis"
            self.h = eval(word[1:])
            self.move = True
        elif (word == 'G0' or word == 'G00' or word == 'g0' or word == 'g00'):
            self.path_col = "rapid"
            self.col = "rapid"
            self.arc = 0
        elif (word == 'G1' or word == 'G01' or word == 'g1' or word == 'g01'):
            self.path_col = "feed"
            self.col = "feed"
            self.arc = 0
        elif (word == 'G2' or word == 'G02' or word == 'g2' or word == 'g02' or word == 'G12' or word == 'g12'):
            self.path_col = "feed"
            self.col = "feed"
            self.arc = -1
        elif (word == 'G3' or word == 'G03' or word == 'g3' or word == 'g03' or word == 'G13' or word == 'g13'):
            self.path_col = "feed"
            self.col = "feed"
            self.arc = +1
        elif (word == 'G10' or word == 'g10'):
            self.no_move = True
        elif (word == 'L1' or word == 'l1'):
            self.no_move = True
        elif (word == 'G61.1' or word == 'g61.1' or word == 'G61' or word == 'g61' or word == 'G64' or word == 'g64'):
            self.no_move = True
        elif (word == 'G20' or word == 'G70'):
            self.col = "prep"
            self.writer.imperial()
        elif (word == 'G21' or word == 'G71'):
            self.col = "prep"
            self.writer.metric()
        elif (word == 'G43' or word == 'g43'):
            self.height_offset = True
            self.move = True
            self.path_col = "rapid"
            self.col = "rapid"
        elif (word == 'G81' or word == 'g81'):
            self.drill = True
            self.no_move = True
            self.path_col = "feed"
            self.col = "feed"
        elif (word == 'G82' or word == 'g82'):
            self.drill = True;
            self.no_move = True
            self.path_col = "feed"
            self.col = "feed"
        elif (word == 'G83' or word == 'g83'):
            self.drill = True
            self.no_move = True
            self.path_col = "feed"
            self.col = "feed"
        elif (word == 'G90' or word == 'g90'):
            self.absolute()
        elif (word == 'G91' or word == 'g91'):
            self.incremental()
        elif (word[0] == 'G') : col = "prep"
        elif (word[0] == 'I' or word[0] == 'i'):
            self.col = "axis"
            self.i = eval(word[1:])
            self.move = True
        elif (word[0] == 'J' or word[0] == 'j'):
            self.col = "axis"
            self.j = eval(word[1:])
            self.move = True
        elif (word[0] == 'K' or word[0] == 'k'):
            self.col = "axis"
            self.k = eval(word[1:])
            self.move = True
        elif (word[0] == 'M') : self.col = "misc"
        elif (word[0] == 'N') : self.col = "blocknum"
        elif (word[0] == 'O') : self.col = "program"
        elif (word[0] == 'P' or word[0] == 'p'):
             if (self.no_move != True):
                 self.col = "axis"
                 self.p = eval(word[1:])
                 self.move = True
        elif (word[0] == 'Q' or word[0] == 'q'):
             if (self.no_move != True):
                 self.col = "axis"
                 self.q = eval(word[1:])
                 self.move = True
        elif (word[0] == 'R' or word[0] == 'r'):
            self.col = "axis"
            self.r = eval(word[1:])
            self.move = True
        elif (word[0] == 'S' or word[0] == 's'):
            self.col = "axis"
            self.writer.spindle(word[1:], (float(word[1:]) >= 0.0))
        elif (word[0] == 'T') :
            self.col = "tool"
            self.writer.tool_change( eval(word[1:]) )
        elif (word[0] == 'X' or word[0] == 'x'):
            self.col = "axis"
            self.x = eval(word[1:])
            self.move = True
        elif (word[0] == 'Y' or word[0] == 'y'):
            self.col = "axis"
            self.y = eval(word[1:])
            self.move = True
        elif (word[0] == 'Z' or word[0] == 'z'):
            self.col = "axis"
            self.z = eval(word[1:])
            self.move = True
        elif (word[0] == '(') : (self.col, self.cdata) = ("comment", True)
        elif (word[0] == '!') : (self.col, self.cdata) = ("comment", True)
        elif (word[0] == ';') : (self.col, self.cdata) = ("comment", True)
        elif (word[0] == '#') : self.col = "variable"
        elif (word[0] == ':') : self.col = "blocknum"
        elif (ord(word[0]) <= 32) : self.cdata = True
