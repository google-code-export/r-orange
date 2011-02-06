# -*- coding: utf-8 -*-
# Author: Kyle R Covington and Anup Parikh, adapted from orangeCanvas
# Description:
#    main file, that creates the MDI environment
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys, os, cPickle, time
# for x in sys.path:
   # print x
   
   
mypath = os.path.split(os.path.split(os.path.abspath(sys.argv[0]))[0])[0]
sys.path.append(mypath)
import redREnviron
#print 'loading log'
try:
  import redRLog
except Exception as inst:
  print unicode(inst)

#print 'loading style'
import redRStyle
import redRReports
#print 'loading R session'
import RSession
#print 'loading histry'
import redRHistory
#print 'loading international'
import redRi18n
#print 'loading registery'
import orngRegistry#, OWGUI
#print 'loading r output and loadsave'
import redROutput, redRSaveLoad
#print 'loading orngdoc'
import orngDoc, orngDlgs
import redRWidgetsTree
import redRPackageManager, redRGUI,signals, redRInitWizard
#print 'loading reports'
import redRReports, redRObjects, redRUpdateManager
#print 'loading R session'
import redRCanvasToolbar

#print 'Core module Load complete'

from libraries.base.qtWidgets.button import button as redRbutton
from libraries.base.qtWidgets.widgetBox import widgetBox as redRwidgetBox
from libraries.base.qtWidgets.textEdit import textEdit as redRTextEdit
# def _(a):
    # return a
_ = redRi18n.Coreget_()
class OrangeCanvasDlg(QMainWindow):
    def __init__(self, app, parent = None, flags =  0):
        QMainWindow.__init__(self, parent)
        # self._ = redRi18n.Coreget_('messages', os.path.join(redREnviron.directoryNames['redRDir'], 'languages'), languages = ['French'])
        self.setWindowTitle(_("Red-R Canvas %s") % redREnviron.version['REDRVERSION'])
        if os.path.exists(redRStyle.canvasIcon):
            self.setWindowIcon(QIcon(redRStyle.canvasIcon))
        
        ###############################
        #####Start splashWindow####
        ###############################
        logo = QPixmap(redRStyle.redRLogo)
        splashWindow = QSplashScreen(logo, Qt.WindowStaysOnTopHint)
        splashWindow.setMask(logo.mask())
        splashWindow.show()
        
        
        ###############################
        #####Notes and output Docks####
        ###############################
        
        self.notesDock = QDockWidget(_('Notes'))
        self.notesDock.setObjectName(_('CanvasNotes'))
        self.notes = redRTextEdit(None, label = _('Notes'))
        self.notes.setMinimumWidth(200)
        redRSaveLoad.setNotesWidget(self.notes)
        self.notesDock.setWidget(self.notes)
        self.addDockWidget(Qt.RightDockWidgetArea, self.notesDock)
        self.connect(self.notesDock,SIGNAL('visibilityChanged(bool)'),self.updateDock)
        
        self.outputDock = QDockWidget(_('Output'))
        self.outputDock.setObjectName(_('CanvasOutput'))
        outbox = redRwidgetBox(None)
        self.printOutput = redRTextEdit(outbox, label = _('Output'),displayLabel=False, editable=False)
        hbox = redRwidgetBox(outbox,orientation='horizontal',alignment=Qt.AlignLeft)
        
        redRbutton(hbox, label = _('Save Output'), callback = self.saveOutputToFile)
        redRbutton(hbox, label = _('Clear Output'), callback = lambda: self.printOutput.clear())
        if redREnviron.settings["writeLogFile"]:
            redRbutton(hbox, label = _('Show in Browser'), callback = lambda: redRLog.fileLogger.showLogFile())
        
        self.outputDock.setWidget(outbox)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.outputDock)
        self.connect(self.outputDock,SIGNAL('visibilityChanged(bool)'),self.updateDock)
        #redRLog.setOutputWindow(self.printOutput)
        redRLog.setOutputManager('dock', self.dockOutputManger)
        
        #######################
        #####Output Manager####
        #######################

        # self.output = redROutput.OutputWindow(self)
        # redRLog.setOutputManager('window', self.output.outputManager)
        
        
        ###################
        #Register Widgets##
        ###################
  
        self.widgetRegistry = redRObjects.widgetRegistry() # the widget registry has been created
        redRGUI.registerQTWidgets()
        signals.registerRedRSignals()
        
        ###################
        #Main Cavas########
        ###################
        splashWindow.showMessage(_("Main Cavas"), Qt.AlignHCenter + Qt.AlignBottom)

        self.schema = orngDoc.SchemaDoc(self)
        self.setCentralWidget(self.schema)
        self.schema.setFocus()

        ###################
        #Toolbar and Menu##
        ###################
        
        splashWindow.showMessage(_("Creating Menu and Toolbar"), Qt.AlignHCenter + Qt.AlignBottom)
        self.toolbar = self.addToolBar(_("Toolbar"))
        self.toolbarFunctions = redRCanvasToolbar.redRCanvasToolbarandMenu(self,self.toolbar)
        self.toolbarFunctions.updateStyle()
        ######################
        #Create Widgets Dock##
        ######################
        
        self.widgetDock = QDockWidget(_('Widgets'))
        self.widgetDock.setObjectName('widgetDock')
        self.widgetDockBox = redRwidgetBox(None)
        self.widgetDockBox.setMinimumWidth(200)
        
        self.widgetDock.setWidget(self.widgetDockBox)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.widgetDock)
        self.connect(self.widgetDock,SIGNAL('visibilityChanged(bool)'),self.updateDock)
        
        self.widgetsToolBar = redRWidgetsTree.WidgetTree(self.widgetDockBox, self, self.widgetRegistry)
        self.suggestButtonsList = redRWidgetsTree.widgetSuggestions(self.widgetDockBox,self)
        
        # self.createWidgetsToolbar() # also creates the categories popup
        # self.toolbar.addWidget(self.widgetsToolBar.widgetSuggestEdit) ## kind of a hack but there you are.        

        ###################
        #####Status Bar####
        ###################
        splashWindow.showMessage(_("Creating Status Bar"), Qt.AlignHCenter + Qt.AlignBottom)
        
        self.statusBar = QStatusBar()
        self.statusBar.setSizeGripEnabled(False)
        self.setStatusBar(self.statusBar)
        
        docBox = redRwidgetBox(None,orientation='horizontal',spacing=4)
        
        self.showWidgetToolbar = redRbutton(docBox, '',toggleButton=True, 
        icon=redRStyle.defaultWidgetIcon, toolTip=_('Widget Tree'), callback = self.updateDockState)   
        
        self.showROutputButton = redRbutton(docBox, '',toggleButton=True, 
        icon=redRStyle.canvasIcon, toolTip=_('Log'), callback = self.updateDockState)   

        self.showNotesButton = redRbutton(docBox, '',toggleButton=True, 
        icon=redRStyle.notesIcon, toolTip=_('Notes'), callback = self.updateDockState)
        
        
        self.statusBar.addPermanentWidget(docBox)
        if 'dockState' in redREnviron.settings.keys() and 'widgetBox' in redREnviron.settings['dockState'].keys():
            self.showNotesButton.setChecked(redREnviron.settings['dockState']['notesBox'])
            self.showROutputButton.setChecked(redREnviron.settings['dockState']['outputBox'])
            self.showWidgetToolbar.setChecked(redREnviron.settings['dockState']['widgetBox'])
        

        ###################
        #Package Manager###
        ###################
        splashWindow.showMessage("Creating Package Manager", Qt.AlignHCenter + Qt.AlignBottom)
        
        self.packageManagerGUI = redRPackageManager.packageManagerDialog(self)
        

        ###################
        ##Reports##########
        ###################
        splashWindow.showMessage(_("Creating Reports"), Qt.AlignHCenter + Qt.AlignBottom)
        
        self.reports = redRReports.reports(self,self.schema)

        ###################
        ##Update Manager###
        ###################
        splashWindow.showMessage(_("Creating Update Manager"), Qt.AlignHCenter + Qt.AlignBottom)
        
        self.updateManager = redRUpdateManager.updateManager(self)
        
        
        
        
        ########################
        #Load Windows Settings##
        ########################

        splashWindow.showMessage(_("Setting States"), Qt.AlignHCenter + Qt.AlignBottom)

        #qtsettings = QSettings("Red-R", "Red-R")
        #print 'adsfasdf', qtsettings.value('windowState').toByteArray()
        #print self.restoreState(qtsettings.value('windowState').toByteArray())


        if 'windowState' in redREnviron.settings.keys():
            print self.restoreState(redREnviron.settings['windowState'])

        if 'geometry' in redREnviron.settings.keys():
            self.restoreGeometry(redREnviron.settings['geometry'])

        if 'size' in redREnviron.settings.keys():
            self.resize(redREnviron.settings['size'])
        else:
            # center window in the desktop
            # in newer versions of Qt we can also find the center of a primary screen
            # on multiheaded desktops
            
            width, height = redREnviron.settings.get("canvasWidth", 700), redREnviron.settings.get("canvasHeight", 600)
            desktop = app.desktop()
            deskH = desktop.screenGeometry(desktop.primaryScreen()).height()
            deskW = desktop.screenGeometry(desktop.primaryScreen()).width()
            h = max(0, deskH/2 - height/2)  # if the window is too small, resize the window to desktop size
            w = max(0, deskW/2 - width/2)
            self.move(w,h+2)
            self.resize(width,height)
        if 'pos' in redREnviron.settings.keys():
            self.move(redREnviron.settings['pos'])

        #########################
        #Show Main Red-R window##
        #########################
        
        self.show()

        if splashWindow:
            splashWindow.hide()

        #########################
        #First Load##
        #########################
        
        try:
            if 'firstLoad' not in redREnviron.settings.keys():
                redREnviron.settings['firstLoad'] = True
            if redREnviron.settings['firstLoad']:
                redRInitWizard.startSetupWizard()
        except:
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
            pass
        redRSaveLoad.setCanvasDlg(self)
        qApp.processEvents()
        
    def saveOutputToFile(self):
        self.toolbarFunctions.menuItemSaveOutputWindow()
    def dockOutputManger(self,table, level, string, html):
        cursor = QTextCursor( self.printOutput.textCursor())                
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      
        self.printOutput.setTextCursor(cursor)                             
        if html:
            self.printOutput.insertHtml(string)
        else:
            self.printOutput.insertPlainText(string)
        
        self.printOutput.ensureCursorVisible()
        sb = self.printOutput.verticalScrollBar()
        sb.setValue(sb.maximum())
        

    def updateDock(self,ev):
        if self.notesDock.isHidden():
            self.showNotesButton.setChecked(False)
        else:
            self.showNotesButton.setChecked(True)
        
        if self.outputDock.isHidden():
            self.showROutputButton.setChecked(False)
        else:
            self.showROutputButton.setChecked(True)
            
        if self.widgetDock.isHidden():
            self.showWidgetToolbar.setChecked(False)
        else:
            self.showWidgetToolbar.setChecked(True)
            
    def updateDockState(self):
        #print _('in updatedock right')
        if 'dockState' not in redREnviron.settings.keys():
            redREnviron.settings['dockState'] = {'notesBox':True, 'outputBox':True, 'widgetBox':True}
        
        
        if self.showNotesButton.isChecked():
            self.notesDock.show()
            redREnviron.settings['dockState']['notesBox'] = True
        else:
            self.notesDock.hide()
            redREnviron.settings['dockState']['notesBox'] = False

        if self.showROutputButton.isChecked():
            self.outputDock.show()
            redREnviron.settings['dockState']['outputBox'] = True
        else:
            self.outputDock.hide()
            redREnviron.settings['dockState']['outputBox'] = False
        
        if self.showWidgetToolbar.isChecked():
            self.widgetDock.show()
            redREnviron.settings['dockState']['widgetBox'] = True
        else:
            self.widgetDock.hide()
            redREnviron.settings['dockState']['widgetBox'] = False
        
    
    def createWidgetsToolbar(self,widgetRegistry=None):
        if widgetRegistry:
            self.widgetRegistry = widgetRegistry
        # self.widgetsToolBar.hide()
        # self.widgetsToolBar = redRWidgetsTree.WidgetTree(self.widgetDockBox, self, self.widgetRegistry)
        self.widgetsToolBar.clear()
        self.widgetsToolBar.createWidgetTabs(self.widgetRegistry) 

       
    def setCaption(self, caption = ""):
        if caption:
            caption = caption.split(".")[0]
            self.setWindowTitle(_("%s - Red Canvas") % caption)
        else:
            self.setWindowTitle(_("Red Canvas"))

    def closeEvent(self, ce, postCloseFun=None):
        # save the current width of the toolbox, if we are using it
        # if isinstance(self.widgetsToolBar, orngTabs.WidgetToolBox):
            # redREnviron.settings["toolboxWidth"] = self.widgetsToolBar.toolbox.width()
        # redREnviron.settings["showWidgetToolbar"] = self.widgetsToolBar.isVisible()
        # redREnviron.settings["showToolbar"] = self.toolbar.isVisible()
#         qtsettings = QSettings("Red-R", "Red-R")
#         qtsettings.setValue("geometry", saveGeometry())
#         qtsettings.setValue("windowState", saveState())
        
        
        redREnviron.settings["geometry"] = self.saveGeometry()
        redREnviron.settings["windowState"] = self.saveState()
        redREnviron.settings['pos'] = self.pos()
        redREnviron.settings['size'] = self.size()

        
        
        redREnviron.saveSettings()
        # closed = self.schema.close()
        if redREnviron.settings['dontAskBeforeClose']:
            res = QMessageBox.No
        else:
            res = QMessageBox.question(self, _('Red-R Canvas'),_('Do you wish to save the schema?'), QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
        
        if res == QMessageBox.Yes:
            self.RVariableRemoveSupress = 1
            saveComplete = self.schema.saveDocument()
            closed=True
        elif res == QMessageBox.No:
            closed=True
        else:
            closed=False
    
        if closed:
            if postCloseFun:
                postCloseFun()

            self.canvasIsClosing = 1        # output window (and possibly report window also) will check this variable before it will close the window
            redRObjects.closeAllWidgets() # close all the widget first so their global data is saved
            import shutil
            shutil.rmtree(redREnviron.directoryNames['tempDir'], True) # remove the tempdir, better hope we saved everything we wanted.
            # close the entire session dropping anything that was open in case it was left by something else, 
            # makes the closing much cleaner than just loosing the session.
            
            redRHistory.saveConnectionHistory()
            redRLog.fileLogger.closeLogFile()
            #redRLog.closeLogger()
            ce.accept()
            QMainWindow.closeEvent(self,ce)

        else:
            ce.ignore()
        
    
        
class RedRQApplication(QApplication):
    def __init__(self, *args):
        QApplication.__init__(self, *args)

        
        
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
    app = RedRQApplication(sys.argv)
    QCoreApplication.setOrganizationName("Red-R");
    QCoreApplication.setOrganizationDomain("red-r.com");
    QCoreApplication.setApplicationName("Red-R");
    dlg = OrangeCanvasDlg(app)
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

if __name__ == "__main__":
    # freeze_support()
    sys.exit(main())
