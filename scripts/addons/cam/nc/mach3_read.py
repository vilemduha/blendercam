from . import iso_read as iso
from . import sys

# just use the iso reader
class Parser(iso.Parser):
    def __init__(self, writer):
        iso.Parser.__init__(self, writer)
