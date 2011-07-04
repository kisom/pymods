# -*- coding: utf-8 -*-
# file: tester.py
# author: kyle isom <coder@kyleisom.net>
# license: ISC / public domain dual-license

import figleaf
import imp
import unittest

class Tester:
    testmod         = None
    test_user_name  = 'kisom'
    test_repo_name  = 'gh-utils'

    def __init__(self, target):
        self.testmod = target
        self.main()


    def main(self, text = True):
        fp, pathname, description   = imp.find_module(self.testmod, ['./tests'])

        try:
            tester = imp.load_module( self.testmod, fp, pathname, description )
        # the documentation example uses an except to catch all errors; any errors at this point means the module
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
    except:
        return False
    else:
        return True
    finally:
        figleaf.stop()
        figleaf.write_coverage('.figleaf')


