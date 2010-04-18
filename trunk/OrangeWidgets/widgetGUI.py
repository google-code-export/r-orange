# modifications by Kyle R Covington and Anup Parikh#
# OWWidget.py
# Orange Widget
# A General Orange Widget, from which all the Orange Widgets are derived
#

import redRGUI 
from PyQt4 import QtWebKit
import urllib, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from datetime import date

class widgetGUI(QMainWindow):
    def __new__(cls, *arg, **args):
        self = QMainWindow.__new__(cls)
        
        #print "arg", arg
        #print "args: ", args
        self.currentContexts = {}   # the "currentContexts" MUST be the first thing assigned to a widget
        self._useContexts = 1       # do you want to use contexts
        self._owInfo = 1            # currently disabled !!!
        self._owWarning = 1         # do we want to see warnings
        self._owError = 1           # do we want to see errors
        self._owShowStatus = 0      # do we want to see warnings and errors in status bar area of the widget
        self._guiElements = []      # used for automatic widget debugging

        
        for key in args:
            if key in ["_owInfo", "_owWarning", "_owError", "_owShowStatus", "_useContexts", "_category", "_settingsFromSchema"]:
                self.__dict__[key] = args[key]        # we cannot use __dict__.update(args) since we can have many other

        return self

    def __init__(self, parent=None, signalManager=None, title="Red-R Widget", 
    savePosition=True, wantGUIDialog = 0, resizingEnabled=1, **args):
        """
        Initialization
        Parameters:
            title - The title of the\ widget, including a "&" (for shortcut in about box)
            wantGraph - displays a save graph button or not
        """

        if resizingEnabled: QMainWindow.__init__(self, parent, Qt.Window)
        else:               QMainWindow.__init__(self, parent, Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)# | Qt.WindowMinimizeButtonHint)

        # directories are better defined this way, otherwise .ini files get written in many places
        #self.__dict__.update(orngEnviron.directoryNames)

        self.setCaption(title.replace("&","")) # used for widget caption


        self.progressBarHandler = None  # handler for progress bar events
        self.processingHandler = None   # handler for processing events


        self.widgetStateHandler = None
        self.widgetState = {"Info":{}, "Warning":{}, "Error":{}}

        self.windowState = {}
        self.savePosition = True
        self.hasAdvancedOptions = wantGUIDialog
        self.setLayout(QVBoxLayout())
        self.layout().setMargin(2)
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        topWidgetPart = redRGUI.widgetBox(self, orientation="vertical", margin=0)
        topWidgetPart.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.setCentralWidget(topWidgetPart)
        self.controlArea = redRGUI.widgetBox(topWidgetPart, orientation="vertical", margin=4)
        self.controlArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        bottomArea = redRGUI.widgetBox(topWidgetPart, orientation="horizontal", margin=4)
        self.bottomAreaLeft = redRGUI.widgetBox(bottomArea, orientation = 'horizontal')
        self.bottomAreaCenter = redRGUI.widgetBox(bottomArea, sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed),
        orientation = 'horizontal')
        self.bottomAreaRight = redRGUI.widgetBox(bottomArea, orientation = 'horizontal')
        #start widget GUI
        
        
        ### status bar ###
        self.statusBar = QStatusBar()
        self.statusBar.setLayout(QHBoxLayout())
        self.statusBar.setSizeGripEnabled(False)
        
        self.setStatusBar(self.statusBar)
        
        self.status = redRGUI.widgetLabel(self.statusBar, '')
        self.status.setText('Processing not yet performed.')
        self.status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.statusBar.addWidget(self.status,4)
        #self.statusBar.setStyleSheet("QStatusBar { border-top: 2px solid gray; } ")
        # self.statusBar.setStyleSheet("QLabel { border-top: 2px solid red; } ")

        ### Right Dock ###
        minWidth = 200
        self.rightDock=QDockWidget('Documentation')
        self.rightDock.setObjectName('rightDock')
        self.connect(self.rightDock,SIGNAL('topLevelChanged(bool)'),self.updateDock)
        self.rightDock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.rightDock.setMinimumWidth(minWidth)
        
        self.rightDock.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.addDockWidget(Qt.RightDockWidgetArea,self.rightDock)
        
        
        self.rightDockArea = redRGUI.groupBox(self.rightDock,orientation=QVBoxLayout())
        self.rightDockArea.setMinimumWidth(minWidth)
        self.rightDockArea.setMinimumHeight(150)
        self.rightDockArea.layout().setMargin(4)
        self.rightDockArea.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        self.rightDock.setWidget(self.rightDockArea)

        
        ### help ####
        self.helpBox = redRGUI.widgetBox(self.rightDockArea,orientation=QVBoxLayout())
        self.helpBox.setMinimumHeight(50)
        self.helpBox.setMinimumWidth(minWidth)
        self.helpBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        if hasattr(self,'_widgetInfo'):
            url = 'http://www.red-r.org/help.php?widget=' + os.path.basename(self._widgetInfo['fullName'])
            self.help = redRGUI.webViewBox(self.helpBox)
            self.help.load(QUrl(url))
            self.help.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        
        
        ### notes ####
        self.notesBox = redRGUI.widgetBox(self.rightDockArea,orientation=QVBoxLayout())
        self.notesBox.setMinimumWidth(minWidth)
        self.notesBox.setMinimumHeight(50)
        self.notesBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        redRGUI.widgetLabel(self.notesBox, label="Notes:")

        self.notes = redRGUI.textEdit(self.notesBox)
        self.notes.setMinimumWidth(minWidth)
        self.notes.setMinimumHeight(50)
        self.notes.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        ### R output ####        
        self.ROutputBox = redRGUI.widgetBox(self.rightDockArea,orientation=QVBoxLayout())
        self.ROutputBox.setMinimumHeight(50)
        redRGUI.widgetLabel(self.ROutputBox, label="R code executed in this widget:")

        self.ROutput = redRGUI.textEdit(self.ROutputBox)
        self.ROutput.setMinimumWidth(minWidth)
        self.ROutput.setMinimumHeight(50)
        self.ROutput.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        
        self.windowState['documentationState'] = {'helpBox':True,'notesBox':True,'ROutputBox':True}
        self.showHelpButton = redRGUI.button(self.bottomAreaLeft, 'Help',toggleButton=True, callback = self.updateDocumentationDock)
        self.showNotesButton = redRGUI.button(self.bottomAreaLeft, 'Notes',toggleButton=True, callback = self.updateDocumentationDock)
        self.showROutputButton = redRGUI.button(self.bottomAreaLeft, 'R Output',toggleButton=True, callback = self.updateDocumentationDock)
        self.printButton = redRGUI.button(self.bottomAreaLeft, "Print", callback = self.printWidget)
        self.statusBar.addPermanentWidget(self.showHelpButton)
        self.statusBar.addPermanentWidget(self.showNotesButton)
        self.statusBar.addPermanentWidget(self.showROutputButton)
        self.statusBar.addPermanentWidget(self.printButton)
        
        
        self.GUIDialogDialog = None
        self.windowState['leftDockState'] = False
        if self.hasAdvancedOptions:
            self.leftDock=QDockWidget('Advanced Options')
            self.leftDock.setObjectName('leftDock')
            self.connect(self.leftDock,SIGNAL('topLevelChanged(bool)'),self.updateDock)
            self.leftDock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
            self.leftDock.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.addDockWidget(Qt.LeftDockWidgetArea,self.leftDock)
            self.GUIDialog = redRGUI.widgetBox(self.leftDock,orientation='vertical')
            self.GUIDialog.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.leftDock.setWidget(self.GUIDialog)
            self.leftDockButton = redRGUI.button(self.bottomAreaLeft, 'Advanced Options',toggleButton=True, callback = self.showLeftDock)
            self.statusBar.insertPermanentWidget(1,self.leftDockButton)
            self.windowState['leftDockState'] = True
  
    # uncomment this when you need to see which events occured
    """
    def event(self, e):
        #eventDict = dict([(0, 'None'), (1, 'Timer'), (2, 'MouseButtonPress'), (3, 'MouseButtonRelease'), (4, 'MouseButtonDblClick'), (5, 'MouseMove'), (6, 'KeyPress'), (7, 'KeyRelease'), (8, 'FocusIn'), (9, 'FocusOut'), (10, 'Enter'), (11, 'Leave'), (12, 'Paint'), (13, 'Move'), (14, 'Resize'), (15, 'Create'), (16, 'Destroy'), (17, 'Show'), (18, 'Hide'), (19, 'Close'), (20, 'Quit'), (21, 'Reparent'), (22, 'ShowMinimized'), (23, 'ShowNormal'), (24, 'WindowActivate'), (25, 'WindowDeactivate'), (26, 'ShowToParent'), (27, 'HideToParent'), (28, 'ShowMaximized'), (30, 'Accel'), (31, 'Wheel'), (32, 'AccelAvailable'), (33, 'CaptionChange'), (34, 'IconChange'), (35, 'ParentFontChange'), (36, 'ApplicationFontChange'), (37, 'ParentPaletteChange'), (38, 'ApplicationPaletteChange'), (40, 'Clipboard'), (42, 'Speech'), (50, 'SockAct'), (51, 'AccelOverride'), (60, 'DragEnter'), (61, 'DragMove'), (62, 'DragLeave'), (63, 'Drop'), (64, 'DragResponse'), (70, 'ChildInserted'), (71, 'ChildRemoved'), (72, 'LayoutHint'), (73, 'ShowWindowRequest'), (80, 'ActivateControl'), (81, 'DeactivateControl'), (1000, 'User')])
        eventDict = dict([(0, "None"), (130, "AccessibilityDescription"), (119, "AccessibilityHelp"), (86, "AccessibilityPrepare"), (114, "ActionAdded"), (113, "ActionChanged"), (115, "ActionRemoved"), (99, "ActivationChange"), (121, "ApplicationActivated"), (122, "ApplicationDeactivated"), (36, "ApplicationFontChange"), (37, "ApplicationLayoutDirectionChange"), (38, "ApplicationPaletteChange"), (35, "ApplicationWindowIconChange"), (68, "ChildAdded"), (69, "ChildPolished"), (71, "ChildRemoved"), (40, "Clipboard"), (19, "Close"), (82, "ContextMenu"), (52, "DeferredDelete"), (60, "DragEnter"), (62, "DragLeave"), (61, "DragMove"), (63, "Drop"), (98, "EnabledChange"), (10, "Enter"), (150, "EnterEditFocus"), (124, "EnterWhatsThisMode"), (116, "FileOpen"), (8, "FocusIn"), (9, "FocusOut"), (97, "FontChange"), (159, "GraphicsSceneContextMenu"), (164, "GraphicsSceneDragEnter"), (166, "GraphicsSceneDragLeave"), (165, "GraphicsSceneDragMove"), (167, "GraphicsSceneDrop"), (163, "GraphicsSceneHelp"), (160, "GraphicsSceneHoverEnter"), (162, "GraphicsSceneHoverLeave"), (161, "GraphicsSceneHoverMove"), (158, "GraphicsSceneMouseDoubleClick"), (155, "GraphicsSceneMouseMove"), (156, "GraphicsSceneMousePress"), (157, "GraphicsSceneMouseRelease"), (168, "GraphicsSceneWheel"), (18, "Hide"), (27, "HideToParent"), (127, "HoverEnter"), (128, "HoverLeave"), (129, "HoverMove"), (96, "IconDrag"), (101, "IconTextChange"), (83, "InputMethod"), (6, "KeyPress"), (7, "KeyRelease"), (89, "LanguageChange"), (90, "LayoutDirectionChange"), (76, "LayoutRequest"), (11, "Leave"), (151, "LeaveEditFocus"), (125, "LeaveWhatsThisMode"), (88, "LocaleChange"), (153, "MenubarUpdated"), (43, "MetaCall"), (102, "ModifiedChange"), (4, "MouseButtonDblClick"), (2, "MouseButtonPress"), (3, "MouseButtonRelease"), (5, "MouseMove"), (109, "MouseTrackingChange"), (13, "Move"), (12, "Paint"), (39, "PaletteChange"), (131, "ParentAboutToChange"), (21, "ParentChange"), (75, "Polish"), (74, "PolishRequest"), (123, "QueryWhatsThis"), (14, "Resize"), (117, "Shortcut"), (51, "ShortcutOverride"), (17, "Show"), (26, "ShowToParent"), (50, "SockAct"), (112, "StatusTip"), (100, "StyleChange"), (87, "TabletMove"), (92, "TabletPress"), (93, "TabletRelease"), (171, "TabletEnterProximity"), (172, "TabletLeaveProximity"), (1, "Timer"), (120, "ToolBarChange"), (110, "ToolTip"), (78, "UpdateLater"), (77, "UpdateRequest"), (111, "WhatsThis"), (118, "WhatsThisClicked"), (31, "Wheel"), (132, "WinEventAct"), (24, "WindowActivate"), (103, "WindowBlocked"), (25, "WindowDeactivate"), (34, "WindowIconChange"), (105, "WindowStateChange"), (33, "WindowTitleChange"), (104, "WindowUnblocked"), (126, "ZOrderChange"), (169, "KeyboardLayoutChange"), (170, "DynamicPropertyChange")])
        if eventDict.has_key(e.type()):
            print str(self.windowTitle()), eventDict[e.type()]
        return QMainWindow.event(self, e)
    """

    def printWidget(self, printer = None):
        ## establish a printer that will print the widget
        if not printer:
            printer = QPrinter()
            printDialog = QPrintDialog(printer)
            if printDialog.exec_() == QDialog.Rejected: 
                print 'Printing Rejected'
                return
        #painter = QPainter(printer)
        painter = QPainter(printer)
        self.render(painter)
        tempDoc = QTextEdit()
        tempDoc.setText('R Output:</br>'+self.ROutput.toHtml()+'</br> Notes: </br>'+self.notes.toHtml())
        tempDoc.render(printer)
        painter.end()
        
    

    def updateDock(self,ev):
        #print self.windowTitle()
        if self.rightDock.isFloating():
            self.rightDock.setWindowTitle(self.windowTitle() + ' Documentation')
        else:
            self.rightDock.setWindowTitle('Documentation')
        if hasattr(self, "leftDock"): 
            if self.leftDock.isFloating():
                self.leftDock.setWindowTitle(self.windowTitle() + ' Advanced Options')
            else:
                self.leftDock.setWindowTitle('Advanced Options')

    
    def showLeftDock(self):
        print 'in updatedock left', self.leftDockButton.isChecked()
        
        if self.leftDockButton.isChecked():
            self.leftDock.show()
            self.windowState['leftDockState'] = True
        else:
            self.leftDock.hide()
            self.windowState['leftDockState'] = False

    def updateDocumentationDock(self):
        print 'in updatedock right'
        if 'documentationState' not in self.windowState.keys():
            self.windowState['documentationState'] = {}
        
        
        if self.showHelpButton.isChecked():
            self.helpBox.show()
            self.windowState['documentationState']['helpBox'] = True
        else:
            self.helpBox.hide()
            self.windowState['documentationState']['helpBox'] = False
        
        if self.showNotesButton.isChecked():
            self.notesBox.show()
            self.windowState['documentationState']['notesBox'] = True
        else:
            self.notesBox.hide()
            self.windowState['documentationState']['notesBox'] = False

        if self.showROutputButton.isChecked():
            self.ROutputBox.show()
            self.windowState['documentationState']['ROutputBox'] = True
        else:
            self.ROutputBox.hide()
            self.windowState['documentationState']['ROutputBox'] = False
        
        # print self.windowState['documentationState'].values()
        if True in self.windowState['documentationState'].values():
            self.rightDock.show()
            # print 'resize t'
            # self.resize(10,10)
            # self.updateGeometry()
        else:
            # print 'hide'
            self.rightDock.hide()
        

    def saveWidgetWindowState(self):
        self.windowState["geometry"] = self.saveGeometry()
        self.windowState["state"] = self.saveState()
        self.windowState['pos'] = self.pos()
        self.windowState['size'] = self.size()
        #self.saveGlobalSettings()
    def closeEvent(self, event):
        print 'in owrpy close'
        if self.rightDock.isFloating():
            self.rightDock.hide()
        if hasattr(self, "leftDock") and self.leftDock.isFloating():
            self.leftDock.hide()
        
        for i in self.findChildren(QDialog):
            i.setHidden(True)
        self.saveWidgetWindowState()
        self.saveGlobalSettings()
        self.customCloseEvent()

        
    def customCloseEvent(self):
        pass

    # when widget is resized, save new width and height into widgetWidth and widgetHeight. some widgets can put this two
    # variables into settings and last widget shape is restored after restart
    def resizeEvent(self, ev):
        QMainWindow.resizeEvent(self, ev)
        if self.savePosition:
            # print 'resizeevent'
            # self.widgetWidth = self.width()
            # self.widgetHeight = self.height()
            self.saveWidgetWindowState()

    # when widget is moved, save new x and y position into widgetXPosition and widgetYPosition. some widgets can put this two
    # variables into settings and last widget position is restored after restart
    def moveEvent(self, ev):
        QMainWindow.moveEvent(self, ev)
        #if self.savePosition:
            #print 'moveevent'
            # self.widgetXPosition = self.frameGeometry().x()
            # self.widgetYPosition = self.frameGeometry().y()
            #self.saveWidgetWindowState()



    # override the default show function.
    # after show() we must call processEvents because show puts some LayoutRequests in queue
    # and we must process them immediately otherwise the width(), height(), ... of elements in the widget will be wrong
    def show(self):
        
        # print 'owbasewidget show'
        print 'in onShow'

        
        if 'state' in self.windowState.keys():
            self.restoreState(self.windowState['state'])
        if 'geometry' in self.windowState.keys():
            self.restoreGeometry(self.windowState['geometry'])
       
        if 'size' in self.windowState.keys():
            self.resize(self.windowState['size'])
        if 'pos' in self.windowState.keys():
            self.move(self.windowState['pos'])

        if self.hasAdvancedOptions and ('leftDockState' in self.windowState):
            self.leftDockButton.setChecked(self.windowState['leftDockState'])
            self.showLeftDock()
        
        if 'documentationState' in self.windowState.keys():
            self.showHelpButton.setChecked(self.windowState['documentationState']['helpBox'])
            self.showNotesButton.setChecked(self.windowState['documentationState']['notesBox'])
            self.showROutputButton.setChecked(self.windowState['documentationState']['ROutputBox'])
        self.updateDocumentationDock()
        
        self.hide()
        QMainWindow.show(self)
        qApp.processEvents()


    def getIconNames(self, iconName):
        if type(iconName) == list:      # if canvas sent us a prepared list of valid names, just return those
            return iconName
        
        names = []
        name, ext = os.path.splitext(iconName)
        for num in [16, 32, 42, 60]:
            names.append("%s_%d%s" % (name, num, ext))
        fullPaths = []
        for paths in [(self.widgetDir, name), (self.widgetDir, "icons", name), (os.path.dirname(sys.modules[self.__module__].__file__), "icons", name)]:
            for name in names + [iconName]:
                fname = os.path.join(*paths)
                if os.path.exists(fname):
                    fullPaths.append(fname)
            if fullPaths != []:
                break

        if len(fullPaths) > 1 and fullPaths[-1].endswith(iconName):
            fullPaths.pop()     # if we have the new icons we can remove the default icon
        return fullPaths
    

    def setWidgetIcon(self, iconName):
        iconNames = self.getIconNames(iconName)
            
        icon = QIcon()
        for name in iconNames:
            pix = QPixmap(name)
            icon.addPixmap(pix)


        self.setWindowIcon(icon)
        


    def setCaption(self, caption):
        # if self.parent != None and isinstance(self.parent, QTabWidget):
            # self.parent.setTabText(self.parent.indexOf(self), caption)
        # else:
        self.captionTitle = caption     # we have to save caption title in case progressbar will change it
        self.setWindowTitle(caption)


    def setWidgetStateHandler(self, handler):
        self.widgetStateHandler = handler

    def setInformation(self, id = 0, text = None):
        self.setState("Info", id, text)
        #self.setState("Warning", id, text)

    def setWarning(self, id = 0, text = ""):
        self.setState("Warning", id, text)
        #self.setState("Info", id, text)        # if we want warning just set information

    def setError(self, id = 0, text = ""):
        self.setState("Error", id, text)
    
    def removeInformation(self,id=None):
        if id == None:
            print 'remove information'
            self.setState("Info", self.widgetState['Info'].keys())
        else:
            self.setState("Info", id)
    
    def removeWarning(self,id=None):
        if id == None:
            self.setState("Warning", self.widgetState['Warning'].keys())
        else:
            self.setState("Warning", id)
            
    def removeError(self,id=None):
        if id == None:
            self.setState("Error", self.widgetState['Error'].keys())
        else:
            self.setState("Error", id)
            
    def setState(self, stateType, id, text =None):
        changed = 0
        if type(id) == list:
            for val in id:
                if self.widgetState[stateType].has_key(val):
                    self.widgetState[stateType].pop(val)
                    print 'pop',val
                    changed = 1
        else:
            #if type(id) == str:
                #text = id; id = 0       # if we call information(), warning(), or error() function with only one parameter - a string - then set id = 0
            if not text:
                if self.widgetState[stateType].has_key(id):
                    self.widgetState[stateType].pop(id)
                    changed = 1
            else:
                self.widgetState[stateType][id] = text
                changed = 1

        if changed:
            if self.widgetStateHandler:
                self.widgetStateHandler()
            # elif text: # and stateType != "Info":
                # self.printEvent(stateType + " - " + text)
            #qApp.processEvents()
        return changed

    def openWidgetHelp(self):

        try:
            import webbrowser
            url = 'http://www.red-r.org/help.php?widget=' + os.path.basename(self._widgetInfo['fullName'])
            webbrowser.open(url, 0, 1)
            return
        except:
            pass

        # try:
            # import webbrowser
            # webbrowser.open("http://www.ailab.si/orange/doc/widgets/catalog/%s/%s.htm" % (self._category, self.__class__.__name__[2:]))
            # return
        # except:
            # pass
    
    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Help, Qt.Key_F1):
            self.openWidgetHelp()
#            e.ignore()
        else:
            QMainWindow.keyPressEvent(self, e)

    def focusInEvent(self, *ev):
        #print "focus in"
        #if qApp.canvasDlg.settings["synchronizeHelp"]:  on ubuntu: pops up help window on first widget focus for every widget   
        #    qApp.canvasDlg.helpWindow.showHelpFor(self, True)
        QMainWindow.focusInEvent(self, *ev)
        
    # ############################################
    # PROGRESS BAR FUNCTIONS
    def progressBarInit(self):
        self.progressBarValue = 0
        # self.startTime = time.time()
        # self.setWindowTitle(self.captionTitle + " (0% complete)")
        if self.progressBarHandler:
            self.progressBarHandler(self, 0)

    def progressBarSet(self, value):
        self.progressBarValue = value
        if self.progressBarHandler: self.progressBarHandler(self, value)
        qApp.processEvents()

    def progressBarAdvance(self, value):
        self.progressBarSet(self.progressBarValue+value)

    def progressBarFinished(self):
        # self.setWindowTitle(self.captionTitle)
        if self.progressBarHandler: self.progressBarHandler(self, 101)

    # handler must be a function, that receives 2 arguments. First is the widget instance, the second is the value between -1 and 101
    def setProgressBarHandler(self, handler):
        self.progressBarHandler = handler

    def setProcessingHandler(self, handler):
        self.processingHandler = handler
        




if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWWidget()
    ow.show()
    a.exec_()
    ow.saveGlobalSettings()
