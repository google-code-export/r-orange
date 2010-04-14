# Major modifications Anup Parikh
# OWWidget.py
# Orange Widget
# A General Orange Widget, from which all the Orange Widgets are derived
#
import orngEnviron
from PyQt4.QtCore import *
from PyQt4.QtGui import *

#from OWContexts import *
import sys, time, random, user, os, os.path, cPickle, copy, orngMisc
import RvarClasses
#import orange
import orngDebugging
from string import *
from orngSignalManager import *
import OWGUI



class OWBaseWidget(QMainWindow):
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


    def __init__(self, parent = None, signalManager = None, title="RedR BaseWidget", 
    modal=False, resizingEnabled = 1, **args):
        # do we want to save widget position and restore it on next load

        if resizingEnabled: QMainWindow.__init__(self, parent, Qt.Window)
        else:               QMainWindow.__init__(self, parent, Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)# | Qt.WindowMinimizeButtonHint)

        # directories are better defined this way, otherwise .ini files get written in many places
        self.__dict__.update(orngEnviron.directoryNames)

        self.setCaption(title.replace("&","")) # used for widget caption

        # number of control signals, that are currently being processed
        # needed by signalWrapper to know when everything was sent
        self.parent = parent
        self.needProcessing = 0     # used by signalManager
        if not signalManager: self.signalManager = globalSignalManager        # use the global instance of signalManager  - not advised
        else:                 self.signalManager = signalManager              # use given instance of signal manager

        self.working = 0     #used to monitor when the widget is working.  Other widgets can check this to supress functions or to check on up/down stream widgets.
        self.linksOutWidgets = {}
        self.inputs = []     # signalName:(dataType, handler, onlySingleConnection)
        self.outputs = []    # signalName: dataType
        self.wrappers =[]    # stored wrappers for widget events
        self.linksIn = {}      # signalName : (dirty, widgetFrom, handler, signalData)
        self.linksOut = {}       # signalName: (signalData, id)
        self.connections = {}   # dictionary where keys are (control, signal) and values are wrapper instances. Used in connect/disconnect
        # self.controlledAttributes = ControlledAttributesDict(self)
        self.progressBarHandler = None  # handler for progress bar events
        self.processingHandler = None   # handler for processing events
        self.eventHandler = None
        self.callbackDeposit = []
        self.startTime = time.time()    # used in progressbar
        self.closing = False # is the widget closing, if so don't process any signals

        self.widgetStateHandler = None
        self.widgetState = {"Info":{}, "Warning":{}, "Error":{}}
        self.blackList = self.__dict__.keys()

    # uncomment this when you need to see which events occured
    """
    def event(self, e):
        #eventDict = dict([(0, 'None'), (1, 'Timer'), (2, 'MouseButtonPress'), (3, 'MouseButtonRelease'), (4, 'MouseButtonDblClick'), (5, 'MouseMove'), (6, 'KeyPress'), (7, 'KeyRelease'), (8, 'FocusIn'), (9, 'FocusOut'), (10, 'Enter'), (11, 'Leave'), (12, 'Paint'), (13, 'Move'), (14, 'Resize'), (15, 'Create'), (16, 'Destroy'), (17, 'Show'), (18, 'Hide'), (19, 'Close'), (20, 'Quit'), (21, 'Reparent'), (22, 'ShowMinimized'), (23, 'ShowNormal'), (24, 'WindowActivate'), (25, 'WindowDeactivate'), (26, 'ShowToParent'), (27, 'HideToParent'), (28, 'ShowMaximized'), (30, 'Accel'), (31, 'Wheel'), (32, 'AccelAvailable'), (33, 'CaptionChange'), (34, 'IconChange'), (35, 'ParentFontChange'), (36, 'ApplicationFontChange'), (37, 'ParentPaletteChange'), (38, 'ApplicationPaletteChange'), (40, 'Clipboard'), (42, 'Speech'), (50, 'SockAct'), (51, 'AccelOverride'), (60, 'DragEnter'), (61, 'DragMove'), (62, 'DragLeave'), (63, 'Drop'), (64, 'DragResponse'), (70, 'ChildInserted'), (71, 'ChildRemoved'), (72, 'LayoutHint'), (73, 'ShowWindowRequest'), (80, 'ActivateControl'), (81, 'DeactivateControl'), (1000, 'User')])
        eventDict = dict([(0, "None"), (130, "AccessibilityDescription"), (119, "AccessibilityHelp"), (86, "AccessibilityPrepare"), (114, "ActionAdded"), (113, "ActionChanged"), (115, "ActionRemoved"), (99, "ActivationChange"), (121, "ApplicationActivated"), (122, "ApplicationDeactivated"), (36, "ApplicationFontChange"), (37, "ApplicationLayoutDirectionChange"), (38, "ApplicationPaletteChange"), (35, "ApplicationWindowIconChange"), (68, "ChildAdded"), (69, "ChildPolished"), (71, "ChildRemoved"), (40, "Clipboard"), (19, "Close"), (82, "ContextMenu"), (52, "DeferredDelete"), (60, "DragEnter"), (62, "DragLeave"), (61, "DragMove"), (63, "Drop"), (98, "EnabledChange"), (10, "Enter"), (150, "EnterEditFocus"), (124, "EnterWhatsThisMode"), (116, "FileOpen"), (8, "FocusIn"), (9, "FocusOut"), (97, "FontChange"), (159, "GraphicsSceneContextMenu"), (164, "GraphicsSceneDragEnter"), (166, "GraphicsSceneDragLeave"), (165, "GraphicsSceneDragMove"), (167, "GraphicsSceneDrop"), (163, "GraphicsSceneHelp"), (160, "GraphicsSceneHoverEnter"), (162, "GraphicsSceneHoverLeave"), (161, "GraphicsSceneHoverMove"), (158, "GraphicsSceneMouseDoubleClick"), (155, "GraphicsSceneMouseMove"), (156, "GraphicsSceneMousePress"), (157, "GraphicsSceneMouseRelease"), (168, "GraphicsSceneWheel"), (18, "Hide"), (27, "HideToParent"), (127, "HoverEnter"), (128, "HoverLeave"), (129, "HoverMove"), (96, "IconDrag"), (101, "IconTextChange"), (83, "InputMethod"), (6, "KeyPress"), (7, "KeyRelease"), (89, "LanguageChange"), (90, "LayoutDirectionChange"), (76, "LayoutRequest"), (11, "Leave"), (151, "LeaveEditFocus"), (125, "LeaveWhatsThisMode"), (88, "LocaleChange"), (153, "MenubarUpdated"), (43, "MetaCall"), (102, "ModifiedChange"), (4, "MouseButtonDblClick"), (2, "MouseButtonPress"), (3, "MouseButtonRelease"), (5, "MouseMove"), (109, "MouseTrackingChange"), (13, "Move"), (12, "Paint"), (39, "PaletteChange"), (131, "ParentAboutToChange"), (21, "ParentChange"), (75, "Polish"), (74, "PolishRequest"), (123, "QueryWhatsThis"), (14, "Resize"), (117, "Shortcut"), (51, "ShortcutOverride"), (17, "Show"), (26, "ShowToParent"), (50, "SockAct"), (112, "StatusTip"), (100, "StyleChange"), (87, "TabletMove"), (92, "TabletPress"), (93, "TabletRelease"), (171, "TabletEnterProximity"), (172, "TabletLeaveProximity"), (1, "Timer"), (120, "ToolBarChange"), (110, "ToolTip"), (78, "UpdateLater"), (77, "UpdateRequest"), (111, "WhatsThis"), (118, "WhatsThisClicked"), (31, "Wheel"), (132, "WinEventAct"), (24, "WindowActivate"), (103, "WindowBlocked"), (25, "WindowDeactivate"), (34, "WindowIconChange"), (105, "WindowStateChange"), (33, "WindowTitleChange"), (104, "WindowUnblocked"), (126, "ZOrderChange"), (169, "KeyboardLayoutChange"), (170, "DynamicPropertyChange")])
        if eventDict.has_key(e.type()):
            print str(self.windowTitle()), eventDict[e.type()]
        return QMainWindow.event(self, e)
    """

    def send(self, signalName, value, id = None):
        if not self.hasOutputName(signalName):
            print "Warning! Signal '%s' is not a valid signal name for the '%s' widget. Please fix the signal name." % (signalName, self.captionTitle)

        if self.linksOut.has_key(signalName):
            self.linksOut[signalName][id] = value
        else:
            self.linksOut[signalName] = {id:value}

        self.signalManager.send(self, signalName, value, id)


    # does widget have a signal with name in inputs
    def hasInputName(self, name):
        for input in self.inputs:
            if name == input[0]: return 1
        return 0

    # does widget have a signal with name in outputs
    def hasOutputName(self, name):
        for output in self.outputs:
            if name == output[0]: return 1
        return 0

    def getInputType(self, signalName):
        for input in self.inputs:
            if input[0] == signalName: return input[1]
        return None

    def getOutputType(self, signalName):
        for output in self.outputs:
            if output[0] == signalName: return output[1]
        return None

    # ########################################################################
    def connect(self, control, signal, method):
        wrapper = SignalWrapper(self, method)
        self.connections[(control, signal)] = wrapper   # save for possible disconnect
        self.wrappers.append(wrapper)
        QMainWindow.connect(control, signal, wrapper)
        #QWidget.connect(control, signal, method)        # ordinary connection useful for dialogs and windows that don't send signals to other widgets


    def disconnect(self, control, signal, method=None):
        wrapper = self.connections[(control, signal)]
        QMainWindow.disconnect(control, signal, wrapper)


    def getConnectionMethod(self, control, signal):
        if (control, signal) in self.connections:
            wrapper = self.connections[(control, signal)]
            return wrapper.method
        else:
            return None


    def signalIsOnlySingleConnection(self, signalName):
        for i in self.inputs:
            input = InputSignal(*i)
            if input.name == signalName: return input.single
    
    def addOutputConnection(self, widgetTo, signalName):
        existing = []
        if self.linksOutWidgets.has_key(signalName):
            existing = self.linksOutWidgets[signalName]
            existing.append(widgetTo)
        else:
            self.linksOutWidgets[signalName] = [widgetTo]
    def addInputConnection(self, widgetFrom, signalName):
        for i in range(len(self.inputs)):
            if self.inputs[i][0] == signalName:
                handler = self.inputs[i][2]
                break

        existing = []
        if self.linksIn.has_key(signalName):
            existing = self.linksIn[signalName]
            for (dirty, widget, handler, data) in existing:
                if widget == widgetFrom: return             # no need to add new tuple, since one from the same widget already exists
        self.linksIn[signalName] = existing + [(0, widgetFrom, handler, [])]    # (dirty, handler, signalData)
        #if not self.linksIn.has_key(signalName): self.linksIn[signalName] = [(0, widgetFrom, handler, [])]    # (dirty, handler, signalData)

    # delete a link from widgetFrom and this widget with name signalName
    
    def removeOutputConnection(self, widgetTo, signalName):
        if self.linksOutWidgets.has_key(signalName):
            links = self.linksOutWidgets[signalName]
            links.remove(widgetTo)
            self.linksOutWidgets[signalName] = links
            
        
    def removeInputConnection(self, widgetFrom, signalName):
        if self.linksIn.has_key(signalName):
            links = self.linksIn[signalName]
            for i in range(len(self.linksIn[signalName])):
                if widgetFrom == self.linksIn[signalName][i][1]:
                    self.linksIn[signalName].remove(self.linksIn[signalName][i])
                    if self.linksIn[signalName] == []:  # if key is empty, delete key value
                        del self.linksIn[signalName]
                    return

    # return widget, that is already connected to this singlelink signal. If this widget exists, the connection will be deleted (since this is only single connection link)
    def removeExistingSingleLink(self, signal):
        #print str(self.inputs)
        #print str(self.outputs)
        for i in self.inputs:
            #print str(*i) + ' input owbasewidget'
            input = InputSignal(*i)
            if input.name == signal and not input.single: return None

        for signalName in self.linksIn.keys():
            if signalName == signal:
                widget = self.linksIn[signalName][0][1]
                del self.linksIn[signalName]
                return widget

        return None


    def handleNewSignals(self):
        # this is called after all new signals have been handled
        # implement this in your widget if you want to process something only after you received multiple signals
        pass

    # signal manager calls this function when all input signals have updated the data
    def processSignals(self,processHandler = True):
        print 'processing Signals'
        if self.closing == True:
            return
        if self.processingHandler: self.processingHandler(self, 1)    # focus on active widget
        newSignal = 0        # did we get any new signals
        self.working = 1
        # we define only a way to handle signals that have defined a handler function
        for signal in self.inputs:        # we go from the first to the last defined input
            key = signal[0]
            if self.linksIn.has_key(key):
                for i in range(len(self.linksIn[key])):
                    (dirty, widgetFrom, handler, signalData) = self.linksIn[key][i]
                    #print dirty,widgetFrom,handler, signalData
                    #print 'processHandler: ' + str(processHandler)
                    print 'data being passed: ' + str(signalData)
                     
                    if not (handler and dirty): continue
                    #print 'do the work'
                    newSignal = 1
                    qApp.setOverrideCursor(Qt.WaitCursor)
                    try:
                        
                        for (oldValue, id, nameFrom) in signalData:
                            if type(oldValue) == dict:
                                value = oldValue.copy()
                                if value == None:
                                    for output in self.outputs:
                                        self.send(output[0], None)
                                    continue
                                ### block to convert to higher data type
                                if issubclass(signal[1], RvarClasses.RVector): # the deepest of the common types
                                    value['data'] = value['data']
                                elif issubclass(signal[1], RvarClasses.RDataFrame): # the data frame type is a child of list
                                    value['data'] = 'as.data.frame('+value['data']+')'
                                elif issubclass(signal[1], RvarClasses.RList): # the list type is the most general of the group types
                                    if self.R('class('+value['data']+')') in ['list']:
                                        value['data'] = 'as.data.frame('+value['data']+')'  # need to coerce to a data frame so we can get it into the list
                                    value['data'] = 'as.list('+value['data']+')'
                                else:
                                    pass
                            else:
                                value = oldValue
                            ### end block
                            
                            if self.signalIsOnlySingleConnection(key):
                                self.printEvent("ProcessSignals: Calling %s with %s" % (handler, value), eventVerbosity = 2)
                                if processHandler:
                                    handler(value)
                                
                            else:
                                self.printEvent("ProcessSignals: Calling %s with %s (%s, %s)" % (handler, value, nameFrom, id), eventVerbosity = 2)
                                if processHandler:
                                    handler(value, (widgetFrom, nameFrom, id))
                            
                    except:
                        thistype, val, traceback = sys.exc_info()
                        sys.excepthook(thistype, val, traceback)  # we pretend that we handled the exception, so that we don't crash other widgets
                    qApp.restoreOverrideCursor()

                    if processHandler:
                        self.linksIn[key][i] = (0, widgetFrom, handler, []) # clear the dirty flag

        if newSignal == 1:
            self.handleNewSignals()

        if self.processingHandler:
            self.processingHandler(self, 0)    # remove focus from this widget
            
        self.working = 0
        self.needProcessing = 0

    # set new data from widget widgetFrom for a signal with name signalName
    def updateNewSignalData(self, widgetFrom, signalName, value, id, signalNameFrom):
        print 'updating new signal data'
        if not self.linksIn.has_key(signalName): return
        for i in range(len(self.linksIn[signalName])):
            (dirty, widget, handler, signalData) = self.linksIn[signalName][i]
            if widget == widgetFrom:
                if self.linksIn[signalName][i][3] == []:
                    self.linksIn[signalName][i] = (1, widget, handler, [(value, id, signalNameFrom)])
                else:
                    found = 0
                    for j in range(len(self.linksIn[signalName][i][3])):
                        (val, ID, nameFrom) = self.linksIn[signalName][i][3][j]
                        if ID == id and nameFrom == signalNameFrom:
                            self.linksIn[signalName][i][3][j] = (value, id, signalNameFrom)
                            found = 1
                    if not found:
                        self.linksIn[signalName][i] = (1, widget, handler, self.linksIn[signalName][i][3] + [(value, id, signalNameFrom)])
        self.needProcessing = 1
        self.needsProcessingHandler(self, 1)


    # ############################################
    # PROGRESS BAR FUNCTIONS
    def progressBarInit(self):
        self.progressBarValue = 0
        self.startTime = time.time()
        self.setWindowTitle(self.captionTitle + " (0% complete)")
        if self.progressBarHandler:
            self.progressBarHandler(self, 0)

    def progressBarSet(self, value):
        if value > 0:
            self.progressBarValue = value
            usedTime = max(1, time.time() - self.startTime)
            totalTime = (100.0*usedTime)/float(value)
            remainingTime = max(0, totalTime - usedTime)
            h = int(remainingTime/3600)
            min = int((remainingTime - h*3600)/60)
            sec = int(remainingTime - h*3600 - min*60)
            if h > 0: text = "%(h)d:%(min)02d:%(sec)02d" % vars()
            else:     text = "%(min)d:%(sec)02d" % vars()
            self.setWindowTitle(self.captionTitle + " (%(value).2f%% complete, remaining time: %(text)s)" % vars())
        else:
            self.setWindowTitle(self.captionTitle + " (0% complete)" )
        if self.progressBarHandler: self.progressBarHandler(self, value)
        qApp.processEvents()

    def progressBarAdvance(self, value):
        self.progressBarSet(self.progressBarValue+value)

    def progressBarFinished(self):
        self.setWindowTitle(self.captionTitle)
        if self.progressBarHandler: self.progressBarHandler(self, 101)

    # handler must be a function, that receives 2 arguments. First is the widget instance, the second is the value between -1 and 101
    def setProgressBarHandler(self, handler):
        self.progressBarHandler = handler

    def setProcessingHandler(self, handler):
        self.processingHandler = handler
        
    def setNeedsProcessingHandler(self, handler): # added by KRC
        self.needsProcessingHandler = handler

    def setEventHandler(self, handler):
        self.eventHandler = handler

    def setWidgetStateHandler(self, handler):
        self.widgetStateHandler = handler


    # if we are in debug mode print the event into the file
    def printEvent(self, text, eventVerbosity = 1):
        self.signalManager.addEvent(self.captionTitle + ": " + text, eventVerbosity = eventVerbosity)
        if self.eventHandler:
            self.eventHandler(self.captionTitle + ": " + text, eventVerbosity)

    def openWidgetHelp(self):
        if self.orangeDir:
#            try:
#                import win32help
#                if win32help.HtmlHelp(0, "%s/doc/catalog.chm::/catalog/%s/%s.htm" % (orangedir, self._category, self.__class__.__name__[2:]), win32help.HH_DISPLAY_TOPIC):
#                    return
#            except:
#                pass

#===============================================================================
#            from PyQt4 import QtWebKit
#            qApp.helpWindow = helpWindow = QtWebKit.QWebView()
#            print "file://%s/doc/widgets/catalog/%s/%s.htm" % (self.orangeDir, self._category, self.__class__.__name__[2:])
#            helpWindow.load(QUrl("file:///%s/doc/widgets/catalog/%s/%s.htm" % (self.orangeDir, self._category, self.__class__.__name__[2:])))
#            helpWindow.show()
#===============================================================================
            qApp.canvasDlg.helpWindow.showHelpFor(self, True)
            return
            try:
                import webbrowser
                webbrowser.open("file://%s/doc/widgets/catalog/%s/%s.htm" % (self.orangeDir, self._category, self.__class__.__name__[2:]), 0, 1)
                return
            except:
                pass

        try:
            import webbrowser
            webbrowser.open("http://www.ailab.si/orange/doc/widgets/catalog/%s/%s.htm" % (self._category, self.__class__.__name__[2:]))
            return
        except:
            pass

    def focusInEvent(self, *ev):
        #print "focus in"
        #if qApp.canvasDlg.settings["synchronizeHelp"]:  on ubuntu: pops up help window on first widget focus for every widget   
        #    qApp.canvasDlg.helpWindow.showHelpFor(self, True)
        QMainWindow.focusInEvent(self, *ev)
        
    
    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Help, Qt.Key_F1):
            self.openWidgetHelp()
#            e.ignore()
        else:
            QMainWindow.keyPressEvent(self, e)



if __name__ == "__main__":
    a=QApplication(sys.argv)
    oww=OWBaseWidget()
    oww.show()
    a.exec_()
    oww.saveGlobalSettings()
