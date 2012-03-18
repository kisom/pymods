# -*- coding: utf-8 -*-
# file: tester.py
# author: kyle isom <coder@kyleisom.net>
# license: ISC / public domain dual-license

"""
Test framework for doing unit tests.

This is designed to operate on a number of files in a 'tests/' directory, where
each test file is a unittest.TestCase test case. This allows for more flexible
conditional testing as well as easier packaging of tests into separate per-module
tests.

Each of the test files should contain a class Tests(unittest.TestCase) that
will be called. This module also expects the 'figleaf' code coverage module
to be installed.

To use, you need a list and a dictionary. The list elements must be keys in the
dictionary, which is in the format { test: description } where test is a file in
the tests/ directory and description is a string to display at the start of that
test case.

The module should be called as tester.main(test_dict, test_order) where test_order
is the list of modules sorted by the order they should be run in.

"""

import figleaf
import imp
import unittest

class Tester:
    """
    Attempt to load a test/ file and call it's Tests
    """
    testmod         = None
    test_user_name  = 'kisom'
    test_repo_name  = 'gh-utils'

    def __init__(self, target):
        """
        target is the file in 'tests/' to attempt to load
        sets up target and runs the main test code.
        """
        self.testmod = target
        self.main()


    def main(self, text = True):
        fp, pathname, description   = imp.find_module(self.testmod, ['./tests'])

        try:
            tester = imp.load_module( self.testmod, fp, pathname, description )

        except Exception as e:
            print e
            print '[!] import error!'

            return
        finally:
            if fp:
                fp.close()

        suite   = unittest.TestSuite()
        loader  = unittest.TestLoader()
        suite.addTests(loader.loadTestsFromTestCase(tester.Tests))

        if text:
            unittest.TextTestRunner(verbosity=5).run(suite)
        else:
            suite.run(res)
            print '[+] %s ->\n\t' % self.testmod, res

            if res.errors:
                print '\t[!] errors:'
                for testcase, traceback in res.errors:
                    print '\t\t[!] ',
                    print testcase.id(),
                    print traceback

            if res.failures:
                print '\t[!] failures:'
                for testcase, test in res.failures:
                    print '\t\t[!]', testcase.id(), test


def main(test_dict, test_order):
    figleaf.start()

    try:
        for test in test_order:
            print '[+]', test_dict[test]
            Tester(test)
    except Exception as e:
        return False
    else:
        return True
    finally:
        figleaf.stop()
        figleaf.write_coverage('.figleaf')


