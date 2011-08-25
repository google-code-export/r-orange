# -*- coding: utf-8 -*-
# Author: Kyle R Covington and Anup Parikh, adapted from orangeCanvas
# Description:
#    main file, that creates the MDI environment

import sys, os, cPickle, time
#print time.time()
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import redRApplication, redREnviron, redRUpdateManager, redRLog
        
        
#####################Forked verions of R##############################
# import sys, os, redREnviron, numpy
# if sys.platform=="win32":
    # from rpy_options import set_options
    # set_options(RHOME=redREnviron.directoryNames['RDir'])
# else: # need this because linux doesn't need to use the RPATH
    # print 'Cant find windows environ varuable RPATH, you are not using a win32 machine.'

    
# import rpy
# from multiprocessing.managers import BaseManager
# from multiprocessing import freeze_support
# import Queue


# class Rclass():
    # def R(self, query):
        # try:
            # out = rpy.r(query)  
            # return out
        # except rpy.RPyRException as inst:
            # print inst
            # raise Exception(_('R Error'), unicode(inst)) 


# class MyManager(BaseManager):
    # pass

#####################Forked verions of R##############################

def main(argv = None):
    if argv == None:
        argv = sys.argv
#####################Forked verions of R##############################
    # qApp.rpy = rpy
    # MyManager.register('Rclass', Rclass)
    # manager = MyManager(address=('localhost', 5000), authkey='abracadabra')
    # manager.start()
    # qApp.R = manager.Rclass()
#####################Forked verions of R##############################
    
    app = redRApplication.RedRQApplication(sys.argv)
    QCoreApplication.setOrganizationName("Red-R");
    QCoreApplication.setOrganizationDomain("red-r.com");
    QCoreApplication.setApplicationName("Red-R");
    dlg = redRApplication.OrangeCanvasDlg(app)
    qApp.canvasDlg = dlg
    dlg.show()
    
    # do we need to load a schema, this happens if you open a saved session.
    if os.path.exists(sys.argv[-1]) and os.path.splitext(sys.argv[-1])[1].lower() == ".rrs": 
        dlg.schema.loadDocument(sys.argv[-1])

    # for arg in sys.argv[1:]:
        # if arg == "-reload":
            # dlg.menuItemOpenLastSchema()
    app.exec_()
    
    # manager.shutdown()
    # dlg.saveSettings()
    app.closeAllWindows()

def updates():
    #print time.time(), 'Starting updates'
    app = redRApplication.RedRQApplication(sys.argv)
    QCoreApplication.setOrganizationName("Red-R");
    QCoreApplication.setOrganizationDomain("red-r.com");
    QCoreApplication.setApplicationName("Red-R");
    updateManager = redRUpdateManager.updateManager(app)
    if redREnviron.settings['checkForUpdates']:
        updateManager.checkForUpdate(auto=True)
    print 'is avaliable', redREnviron.settings['updateAvailable']
    if redREnviron.settings['updateAvailable']:
        updateGUI = updateManager.showUpdateDialog()  
        updateGUI = app.exec_()
        app.closeAllWindows()
        redREnviron.saveSettings()
        return updateGUI
    else:
        return 0
    
if __name__ == "__main__":
    # freeze_support()
    wasUpdated = 0
    #if redREnviron.settings['checkForUpdates'] and not redREnviron.settings['updateAvailable']:
    try:
        wasUpdated = updates()
    except:
        redRLog.log(redRLog.REDRCORE, redRLog.CRITICAL,redRLog.formatException())
    print 'updated ended with', wasUpdated
    if wasUpdated == 0:
        sys.exit(main())
    else:
        sys.exit()