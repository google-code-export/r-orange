"""Regression Tester

This module is responsible for regression testing of packages and other Red-R tools.  It is assumed that running regression tester will only be performed on a developer machine and will likely distroy any settings that the user has placed in Red-R.  We do not plan to actually break the installation but we will also not inhibit ourselves from performing distructive operations to settings or other Red-R installation specific tools.

Regression Tester Responsabilities
==================================

- Test package installation for all packages on repository
- Test examples in the CoreTestExamples directory of all packages on repository
- Create logs of errors occuring during testing and report those to the developer.

"""
import os, sys, redREnviron, urllib2, zipfile, traceback, redRLog
from datetime import date

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import redRPackageManager

def installAllPackages():
    # get a list of all packages on the repository
    packages = 