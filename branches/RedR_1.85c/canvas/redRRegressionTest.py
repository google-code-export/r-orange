"""Regression Tester

This module is responsible for regression testing of packages and other Red-R tools.  It is assumed that running regression tester will only be performed on a developer machine and will likely distroy any settings that the user has placed in Red-R.  We do not plan to actually break the installation but we will also not inhibit ourselves from performing distructive operations to settings or other Red-R installation specific tools.

Regression Tester Responsabilities
==================================

- Test package installation for all packages on repository
- Test examples in the CoreTestExamples directory of all packages on repository
- Create logs of errors occuring during testing and report those to the developer.

"""
import os, sys, redREnviron, glob, urllib2, zipfile, traceback, redRLog, redRObjects
from datetime import date

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import redRPackageManager, redRSaveLoad

def installAllPackages():
    # get a list of all packages on the repository
    pm = redRPackageManager.packageManager(redRObjects.canvasDlg)
    pm.installAllPakcages()
    
def testCoreTestExamples():
    packages = [os.path.split(f)[1] for f in glob.glob(redREnviron.directoryNames['libraryDir'] + '/*') if '.svn' not in f]
    for p in packages:
        try:
            redRLog.log(redRLog.REDRCORE, redRLog.INFO, 'Loading test examples for package %s' % p)
            coreTestExamplesDir = os.path.join(redREnviron.directoryNames['libraryDir'], p, 'CoreTestExamples')
            if not os.path.exists(coreTestExamplesDir): raise Exception('No CoreTestExamples Directory in package')
            for ef in glob.glob(coreTestExamplesDir + '/*.rrs'):
                try:
                    redRLog.log(redRLog.REDRCORE, redRLog.INFO, 'Loading test file %s' % ef)
                    redRObjects.schemaDoc.clear()
                    redRSaveLoad.loadDocument(unicode(ef), freeze = 0, importing = False)
                except Exception as inst:
                    redRLog.log(redRLog.REDRCORE, redRLog.CRITICAL, redRLog.formatException())
        except:
            redRLog.log(redRLog.REDRCORE, redRLog.CRITICAL, redRLog.formatException())
def test(val):
    # install all packages
    if val == 1:
        installAllPackages()
    
    # test the core examples.
    testCoreTestExamples()
    #testCoreTestExamples()
    #for p in package:
    