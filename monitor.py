#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# file: monitor.py
# author: kyle isom <coder@kyleisom.net>
# license: ISC / public domain dual-licensed
#
# basic runtime monitoring for broker.

"""
monitor originally designed for use in an automated broker. alerts dev
team on exceptions.

there are three modes supported:
    * production
    * staging
    * development

all three may be set, but it is intended to have only one set. you set
the mode using set_<mode> or toggle_<mode> (i.e. toggle_staging()) and
get the state of that mode with <mode>_p (i.e. staging_p()).

this should be imported into the code's main() function, where the
appropriate mode is set and the function's run() function is called. for
example:

def main(args):
    if not monitor.production_p(): monitor.toggle_production()

    monitor.initialise(
        devs=['dev@example.org', 'dev2@example.net', 'coder@monkey.com'],
        sender='MCP monitor <noreply@example.net>'
    )
    monitor.monitor(run, args)

Note that by default, no mode is set. This is to force the developer to
think about what the proper mode for operation is.
"""

import mailer as mail
import datetime
import os
import sys
import time
import traceback

GLOBALS = {
    'devs': None,
    'sender': None,
    'production': False,
    'staging': False,
    'development': False,
}


def toggle_production():
    """
    Toggle production-mode behaviour.
    """
    GLOBALS['production'] = not GLOBALS['production']


def production_p():
    """
    Indicate whether we are in production-mode.
    """
    return GLOBALS['production']


def toggle_staging():
    """
    Toggle staging-mode behaviour.
    """
    GLOBALS['staging'] = not GLOBALS['staging']


def staging_p():
    """
    Indicate whether we are in staging-mode.
    """
    return GLOBALS['staging']


def toggle_development():
    """
    Toggle development-mode behaviour.
    """
    GLOBALS['development'] = not GLOBALS['development']


def development_p():
    """
    Indicate whether we are in development-mode.
    """
    return GLOBALS['development']


def set_production():
    """
    Set monitor to production mode.
    """
    GLOBALS['production'] = True
    GLOBALS['staging'] = False
    GLOBALS['development'] = False


def set_staging():
    """
    Set monitor to staging mode.
    """
    GLOBALS['production'] = False
    GLOBALS['staging'] = True
    GLOBALS['development'] = False


def set_development():
    """
    Set monitor to development mode.
    """
    GLOBALS['production'] = False
    GLOBALS['staging'] = False
    GLOBALS['development'] = True


class Traceback:
    """
    Internal traceback class, currently only a very basic file target for
    the traceback.print_foo() method
    """
    buf = None

    def __init__(self):
        self.clear()

    def clear(self):
        """
        Wipe the traceback buffer.
        """
        self.buf = ''

    def write(self, buf):
        """
        Append more data to the traceback buffer.
        """
        self.buf += buf

    def read(self):
        """
        Read out the buffer.
        """
        return self.buf


def monitor(target, **kwargs):
    """
    Primary monitor function to ensure proper error handling.
    """
    if not GLOBALS['devs'] or not GLOBALS['sender']:
        raise Exception("need to initialise devs and sender!")

    if (not GLOBALS['production'] and not GLOBALS['staging'] and
       not GLOBALS['development']):
        raise Exception("no mode selected.")

    mail.set_sender(GLOBALS['sender'])

    while True:
        try:
            # should we pass args in or not?
            if not kwargs == None:
                target(**kwargs)
            else:
                target()
        except KeyboardInterrupt:       # die on ^C - for attached processes
            return
        except Exception as error:
            stack = _dump_traceback(error)[0]

            if development_p():
                _handle_development(stack, error)
            if staging_p():
                _handle_staging(stack, error)
            if production_p():
                _handle_production(stack)


def initialise(devs=None, sender=None):
    """
    Initialise the monitor with the list of developers to email and the
    sender to send mail as. A global is only set if it is non-NULL.
    """
    if sender:
        GLOBALS['sender'] = sender
    if devs:
        GLOBALS['devs'] = devs


def test(delay=1):
    """
    Test the monitor functionality.
    """
    while True:
        monitor(testmon, delay=delay)


def testmon(delay=1):
    """
    A quick function to test the monitor function. Call it like this:

    monitor.monitor(testmon, { 'delay': 5 })

    You can also test the module with monitor.test(delay = 5)

    It will run and randomly throw exceptions, handling the exception the
    appropriate way.
    """
    import random

    exception_list = [IOError, KeyError, Exception, SystemError]
    while True:
        if 2 == random.randint(1, 2):
            __testf(random.choice(exception_list))
        time.sleep(delay)


def __testf(exception_type):
    """
    test function to mess with monitor functionality. throws a weird
    error on purpose.
    """
    time.sleep(1)

    if exception_type:
        raise exception_type
    else:
        time.sleep(1)


def _dump_traceback(error):
    """
    internal function to dump the traceback to a string
    """
    tracer = Traceback()
    traceback.print_exc(file=tracer)
    stack = tracer.read()

    return stack, error


def _handle_development(stack, error):
    """
    Handle development-mode. By default, raises the Exception.
    """
    print stack

    raise(error)


def _handle_staging(stack, error):
    """
    Handle staging-mode: execute production-mode then development-mode.
    """
    _handle_production(stack)           # first, production behaviour
    _handle_development(stack, error)   # then, development behaviour


def _handle_production(stack):
    """
    Handle production-mode. By default, sends an email to the devs.
    """
    devs = GLOBALS['devs']
    subject = 'stack dump for %s (pid %d)' % (sys.argv[0], os.getpid())
    body = 'fault occurred at %s\n-----\n\n%s\n' % (
        datetime.datetime.utcnow(),
        stack
    )
    if GLOBALS['production']:
        body += '\n execution has restarted.'
    body += '\n (automated email sent by the python monitor module ('
    body += 'https://github.com/kisom/pymods)'

    mail.simple(devs, subject=subject, body=body)
