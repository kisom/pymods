# -*- coding: utf-8 -*-
# file: sstream.py
# author: kyle isom <coder@kyleisom.net>
# license: ISC / public-domain dual-licensed
#
# string stream class - provides file-like interface to read / write strings

import pdb

class StringStream:
    data  = None
    index = None                                     # to emulate read(n)
    closed = None

    def __init__(self, data = ''):
        self.data = data
        self.index     = 0
        self.closed    = False

    def write(self, data):
        if self.closed: raise TypeError("I/O operation on closed file")
        self.data += str(data)
    
    def read(self, size = 0):
        if self.closed: raise TypeError("I/O operation on closed file")
        if size:
            start = self.index
            stop  = start + size
            self.index += size

            if self.index >= len(self.data):
                self.index = len(self.data)
            if stop >= len(self.data):
                stop = len(self.data)

        else:
            start = self.index
            stop = len(self.data)
            self.index = len(self.data)

        return self.data[start:stop]

    def readline(self, size = 0):
        if self.closed: raise TypeError("I/O operation on closed file")

        s = self.data[self.index:]

        end = s.find('\n')

        # what constraints on end?
        # if end is non-zero, read everything
        if not end: 
            print 'not end'
            end = len(self.data)

        if size and end > size: 
            print 'zoop!'
            end = size

        
        print 'index: %d\tsize: %d\tend:%d' % (self.index,
                                                          size, end)

        self.index += end

        return s[:end]

    def readlines(self): pass

    def close(self):
        self.closed = True


    def flush(self):
        # flush is not a relevant operation
        pass
