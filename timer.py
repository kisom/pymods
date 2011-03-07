# simple python profiling timer
# Kyle Isom <coder@kyleisom.net>
#
# released under a public domain / ISC dual license.

import datetime

class Timer():
    """
This is a simple Timer class for basic profiling. It features basic 
start(), stop(), reset(), and elapsed() methods.

Example usage:
    import Timer

    t = timer.Timer()
    t.start()
    foo()
    print 'foo:", t

    t.reset()
    foo2()
    t.stop
    print "foo2:", t
    """

    # class imports
    # instance attributes
    __start                 = None
    __end                   = None
    __running               = None

    def __init__(self):
        __start             = datetime.datetime(1, 1, 1, 0, 0, 0, 0)
        __end               = datetime.datetime(1, 1, 1, 0, 0, 0, 0)
        __running           = False

    def start(self):
        """
        Method to put the Timer into a running state and starts the timer.
        If the timer is already running, this will fail. Otherwise,
        returns True. In most cases, the return value can be ignored.
        """

        if not self.__running:
            self.__start    = datetime.datetime.now()
            self.__running  = True
            return True

        else:
            return False

    def stop(self):
        """
        Method to stop Timer (i.e. puts the Timer in a non-running state).
        If the timer isn't running, this will fail. Otherwise, returns 
        True. In most cases, the return value can be ignored.
        """

        if self.__running:
            self.__running  = False
            self.__end      = datetime.datetime.now()
            return True

        else:
            return False

    def __str__(self):
        return str(self.elapsed)

    def elapsed(self):
        if self.__running:
            return datetime.datetime.now() - self.__start

        else:
            return self.__end - self.__start


