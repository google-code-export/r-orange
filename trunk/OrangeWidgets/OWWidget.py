# modifications by Kyle R Covington and Anup Parikh#
# OWWidget.py
# Orange Widget
# A General Orange Widget, from which all the Orange Widgets are derived
#

from OWBaseWidget import *
import redRGUI 
from PyQt4 import QtWebKit
import urllib

# remove the try-except after reporting is ready for deployment
import OWReport
from datetime import date

class OWWidget(OWBaseWidget):
    def __init__(self, parent=None, signalManager=None, title="Orange Widget", 
    savePosition=True, wantGUIDialog = 0, resizingEnabled=1, **args):
        """
        Initialization
        Parameters:
            title - The title of the\ widget, including a "&" (for shortcut in about box)
            wantGraph - displays a save graph button or not
        """

        OWBaseWidget.__init__(self, parent, signalManager, title,resizingEnabled=resizingEnabled, **args)

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
        painter.setBrushOrigin(0, int(self.height())+20)
        self.ROutput.document().drawContents(painter)
        painter.setBrushOrigin(0, int(self.height()+self.ROutput.height()+40))
        self.notes.document().drawContents(painter)
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
        if self.savePosition:
            # print 'moveevent'
            # self.widgetXPosition = self.frameGeometry().x()
            # self.widgetYPosition = self.frameGeometry().y()
            self.saveWidgetWindowState()



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

        if self.hasAdvancedOptions:
            self.leftDockButton.setChecked(self.windowState['leftDockState'])
            self.showLeftDock()
        
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
#            frame = QPixmap(os.path.join(self.widgetDir, "icons/frame.png"))
#            icon = QPixmap(iconName)
#            result = QPixmap(icon.size())
#            painter = QPainter()
#            painter.begin(result)
#            painter.drawPixmap(0,0, frame)
#            painter.drawPixmap(0,0, icon)
#            painter.end()

        self.setWindowIcon(icon)
        


    def setCaption(self, caption):
        if self.parent != None and isinstance(self.parent, QTabWidget):
            self.parent.setTabText(self.parent.indexOf(self), caption)
        else:
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
            elif text: # and stateType != "Info":
                self.printEvent(stateType + " - " + text)
            #qApp.processEvents()
        return changed


if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWWidget()
    ow.show()
    a.exec_()
