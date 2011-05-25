# -*- coding: utf-8 -*-
# file: sstream.py
# author: kyle isom <coder@kyleisom.net>
# license: ISC / public-domain dual-licensed
#
# string stream class - provides file-like interface to read / write strings

class StringStream:
    data  = None
    index = None                                     # to emulate read(n)

    def __init__(self, data = ''):
        self.data = data
        self.index     = 0

    def write(self, data):
        self.data += str(data)
    
    def read(self, size = 0):
        if size:
            s = self.data[self.index:self.index + size]
            self.index += size

            if self.index >= len(self.data):
                self.index = len(self.data)

        else:
            s = self.data[self.index:]
            self.index = len(self.data)

        return s
