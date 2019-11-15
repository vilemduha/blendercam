################################################################################
# iso_read.py
#
# Simple ISO NC code parsing
#
# Hirutso Enni, 2009-01-13

from . import nclathe_read as nc
import re
import sys

################################################################################
class Parser(nc.Parser):

    def __init__(self, writer):
        nc.Parser.__init__(self, writer)

        self.pattern_main = re.compile('([(!;].*|\s+|[a-zA-Z0-9_:](?:[+-])?\d*(?:\.\d*)?|\w\#\d+|\(.*?\)|\#\d+\=(?:[+-])?\d*(?:\.\d*)?)')

        #if ( or ! or ; at least one space or a letter followed by some character or not followed by a +/- followed by decimal, with a possible decimal point
         #  followed by a possible deimcal, or a letter followed by # with a decimal . deimcal
        # add your character here > [(!;] for comments char
        # then look for the 'comment' function towards the end of the file and add another elif

    def Parse(self, name, oname=None):
        self.files_open(name,oname)

        #self.begin_ncblock()
        #self.begin_path(None)
        #self.add_line(z=500)
        #self.end_path()
        #self.end_ncblock()

        path_col = None
        f = None
        arc = 0
        uw  = 0
        while (self.readline()):

            a = None
            b = None
            c = None
            #f = None
            i = None
            j = None
            k = None
            p = None
            q = None
            r = None
            s = None
            x = None
            y = None
            z = None
            u = None
            w = None
            self.begin_ncblock()

            move = False
            #arc = 0
            #path_col = None
            drill = False
            no_move = False

            words = self.pattern_main.findall(self.line)
            for word in words:
                col = None
                cdata = False
                if (word[0] == 'A' or word[0] == 'a'):
                    col = "axis"
                    a = eval(word[1:])
                    move = True
                elif (word[0] == 'B' or word[0] == 'b'):
                    col = "axis"
                    b = eval(word[1:])
                    move = True
                elif (word[0] == 'C' or word[0] == 'c'):
                    col = "axis"
                    c = eval(word[1:])
                    move = True
                elif (word[0] == 'F' or word[0] == 'f'):
                    col = "axis"
                    f = eval(word[1:])
                    move = True
                elif (word == 'G0' or word == 'G00' or word == 'g0' or word == 'g00'):
                    path_col = "rapid"
                    col = "rapid"
                    arc = 0
                elif (word == 'G1' or word == 'G01' or word == 'g1' or word == 'g01'):
                    path_col = "feed"
                    col = "feed"
                    arc = 0
                elif (word == 'G2' or word == 'G02' or word == 'g2' or word == 'g02' or word == 'G12' or word == 'g12'):
                    path_col = "feed"
                    col = "feed"
                    arc = -1
                elif (word == 'G3' or word == 'G03' or word == 'g3' or word == 'g03' or word == 'G13' or word == 'g13'):
                    path_col = "feed"
                    col = "feed"
                    arc = +1
                elif (word == 'G10' or word == 'g10'):
                    no_move = True
                elif (word == 'L1' or word == 'l1'):
                    no_move = True
                elif (word == 'G20' or word == 'G70'):
                    col = "prep"
                    self.set_mode(units=25.4)
                elif (word == 'G21' or word == 'G71'):
                    col = "prep"
                    self.set_mode(units=1.0)
                elif (word == 'G81' or word == 'g81'):
                    drill = True
                    no_move = True
                    path_col = "feed"
                    col = "feed"
                elif (word == 'G82' or word == 'g82'):
                    drill = True;
                    no_move = True
                    path_col = "feed"
                    col = "feed"
                elif (word == 'G83' or word == 'g83'):
                    drill = True
                    no_move = True
                    path_col = "feed"
                    col = "feed"
                elif (word == 'G90' or word == 'g90'):
                    self.absolute()
                elif (word == 'G91' or word == 'g91'):
                    self.incremental()
                elif (word[0] == 'G') : col = "prep"
                elif (word[0] == 'I' or word[0] == 'i'):
                    col = "axis"
                    i = eval(word[1:])
                    move = True
                elif (word[0] == 'J' or word[0] == 'j'):
                    col = "axis"
                    j = eval(word[1:])
                    move = True
                elif (word[0] == 'K' or word[0] == 'k'):
                    col = "axis"
                    k = eval(word[1:])
                    move = True
                elif (word[0] == 'M') : col = "misc"
                elif (word[0] == 'N') : col = "blocknum"
                elif (word[0] == 'O') : col = "program"
                elif (word[0] == 'P' or word[0] == 'p'):
                    col = "axis"
                    p = eval(word[1:])
                    move = True
                elif (word[0] == 'Q' or word[0] == 'q'):
                    col = "axis"
                    q = eval(word[1:])
                    move = True
                elif (word[0] == 'R' or word[0] == 'r'):
                    col = "axis"
                    r = eval(word[1:])
                    move = True
                elif (word[0] == 'S' or word[0] == 's'):
                    col = "axis"
                    s = eval(word[1:])
                    move = True
                elif (word[0] == 'T') :
                    col = "tool"
                    self.set_tool( eval(word[1:]) )
                elif (word[0] == 'X' or word[0] == 'x'):
                    col = "axis"
                    x = eval(word[1:])
                    move = True
                elif (word[0] == 'Y' or word[0] == 'y'):
                    col = "axis"
                    y = eval(word[1:])
                    move = True
                elif (word[0] == 'U' or word[0] == 'u'):
                    col = "axis"
                    u = eval(word[1:])
                    move = True
                    uw=1

                elif (word[0] == 'W' or word[0] == 'w'):
                    col = "axis"
                    w = eval(word[1:])
                    move = True
                    uw=1

                elif (word[0] == 'Z' or word[0] == 'z'):
                    col = "axis"
                    z = eval(word[1:])
                    move = True
                elif (word[0] == '(') : (col, cdata) = ("comment", True)
                elif (word[0] == '!') : (col, cdata) = ("comment", True)
                elif (word[0] == ';') : (col, cdata) = ("comment", True)
                elif (word[0] == '#') : col = "variable"
                elif (word[0] == ':') : col = "blocknum"
                elif (ord(word[0]) <= 32) : cdata = True
                self.add_text(word, col, cdata)

            if (drill):
                self.begin_path("rapid")
                self.add_line(x, y, r)
                self.end_path()

                self.begin_path("feed")
                self.add_line(x, y, z)
                self.end_path()

                self.begin_path("feed")
                self.add_line(x, y, r)
                self.end_path()
            else:
                if (move and not no_move):
                    self.begin_path(path_col)
                    if (arc==-1):
                        self.add_arc(x, y, z, i, j, k, r, arc)
                    elif (arc==1):
                        #self.add_arc(x, y, z, i, j, k, -r, arc) #if you want to use arcs with R values uncomment the first part of this line and comment the next one
                        self.add_arc(x, y, z, i, j, k, r, arc)
                    #else     : self.add_line(x, y, z, a, b, c)
                    elif(uw==1):
                        self.add_lathe_increment_line(u,w)

                    else     : self.add_line(x, y, z, a, b, c)
   	            self.end_path()

            self.end_ncblock()

        self.files_close()
