import unittest

import rpy3.robjects.tests
import rpy3.rinterface.tests
import rpy3.rlike.tests

import rpy3.tests_rpy_classic

def suite():
    suite_robjects = rpy3.robjects.tests.suite()
    suite_rinterface = rpy3.rinterface.tests.suite()
    suite_rlike = rpy3.rlike.tests.suite()

    suite_rpy_classic = rpy3.tests_rpy_classic.suite()

    alltests = unittest.TestSuite([suite_rinterface,
                                   suite_robjects, 
                                   suite_rlike,
                                   suite_rpy_classic
                                   ])
    return alltests

if __name__ == "__main__":
    print("rpy3 version %s" %rpy3.__version__)
    unittest.main(defaultTest = "suite")

