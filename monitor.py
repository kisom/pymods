#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# file: monitor.py
# author: kyle isom <coder@kyleisom.net>
# license: ISC / public domain dual-licensed
#
# basic runtime monitoring for broker.

"""
monitor for automated broker. alerts dev team on exceptions.

there are three modes supported:
    * production
    * staging
    * development

all three may be set, but it is intended to have only one set. you set the mode
using toggle_<mode> (i.e. toggle_staging()) and get the state of that mode with
<mode>_p (i.e. staging_p()).

this should be imported into the code's main() function, where the appropriate
mode is set and the function's run() function is called. for example:

def main(args):
    if not monitor.production_p(): monitor.toggle_production()
    
    monitor.Monitor(run())
    
"""

import mailer as mail
import pdb
import pickle
import sys
import time
import traceback
    
devs                = [ 'coder@kyleisom.net' ]
sender              = 'pymon@brokenlcd.net'
production          = False
staging             = False
development         = False

def toggle_production():
    global production
    
    production = not production
    
def production_p():
    return production

def toggle_staging():
    global staging
    
    staging = not staging

def staging_p():
    return staging

def toggle_development():
    global development
    
    development = not development

def development_p():
    return development
    

class Traceback:
    """
    Internal traceback class, currently only a very basic file target for
    traceback.print_foo()
    """
    s       = None
    
    def __init__(self):
        self.clear()
    
    def clear(self):
        self.s  = ''
    
    def write(self, s):
        self.s += s
        
    def read(self):
        return self.s


def Monitor(target, **kwargs):
    """
    Primary Monitor function to ensure proper error handling.
    """
    target_args     =  ''
    mail.set_sender(sender)
    
    while True:
        try:
            # should we pass args in or not?
            if not kwargs == None:
                target(**kwargs)
            else:
                target()
        except KeyboardInterrupt:           # die on ^C - for attach processes
            return
        except Exception as e:
            stack = dump_traceback()
            
            if development_p(): _handle_development(stack)
            if staging_p():     _handle_staging(stack)
            if production_p():  _handle_production(stack)


def testf(exception_type):
    """
    test function to mess with Monitor functionality. throws a weird error on
    purpose.
    """
    time.sleep(1)
    
    if exception_type:
        raise SystemError
    else:
        time.sleep(1)
    
            
def _dump_traceback():
    """
    internal function to dump the traceback to a string
    """
    tracer  = Traceback()
    traceback.print_exc(file=tracer)
    ex      = tracer.read()
    
    return str(e[0]), str(e[1]), ex


def _handle_development(stack):
    raise()
    
def _handle_staging(stack):
    _handle_production(stack)       # first do what we'd do in production
    _handle_development(stack)      # then do what we'd do in development
    
def _handle_production(stack):
    mail.simple(devs, subject = 'stack dump', body = stack[2])
