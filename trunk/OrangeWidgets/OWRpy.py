#
# An Orange-Rpy class
# 
# Should include all the functionally need to connect Orange to R 
#

from OWWidget import *
from PyQt4 import QtWebKit
from RSession import *
import redRGUI 
import inspect, os
import time
import numpy
import RvarClasses
import RAffyClasses
import threading, sys
import urllib
import pprint
import cPickle
import re

pp = pprint.PrettyPrinter(indent=4)


class OWRpy(OWWidget,RSession):   
    num_widgets = 0
    lock = threading.Lock()
    rsem = threading.Semaphore(value = 1)
    occupied = 0
    Rhistory = '<code>'
    
    def __init__(self,parent=None, signalManager=None, 
    title="R Widget", wantGUIDialog = 0, **args):
        
        OWWidget.__init__(self, parent, signalManager, title, **args)
        RSession.__init__(self)
        
        #The class variable is used to create the unique names in R
        OWRpy.num_widgets += 1
        
        ctime = str(time.time())
        self.variable_suffix = '_' + str(OWRpy.num_widgets) + '_' + ctime
        #keep all R variable name in this dict
        self.Rvariables = {}
        self.setRvariableNames(['title'])
        self.RGUIElements = [] #make a blank one to start with which will be filled as the widget is created.
        self.RGUIElementsSettings = {}
        self.redRGUIObjects = {}
        self.autoShowDialog = 1
        self.hasAdvancedOptions = wantGUIDialog
        #collect the sent items
        self.sentItems = []
        
        #dont save these variables
        self.blackList= ['blackList','GUIWidgets','RGUIElementsSettings','redRGUIObjects','_settingsFromSchema']
        
        
        
        #start widget GUI
        
        self.printButton = redRGUI.button(self.bottomAreaLeft, "Print", callback = self.printWidget)
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
        
        url = 'http://red-r.org/help.php?widget=' + os.path.basename(self._widgetInfo.fullName)
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
        
        self.documentationState = {'helpBox':True,'notesBox':True,'ROutputBox':True}
        self.showHelpButton = redRGUI.button(self.bottomAreaLeft, 'Help',toggleButton=True, callback = self.updateDocumentationDock)
        self.showNotesButton = redRGUI.button(self.bottomAreaLeft, 'Notes',toggleButton=True, callback = self.updateDocumentationDock)
        self.showROutputButton = redRGUI.button(self.bottomAreaLeft, 'R Output',toggleButton=True, callback = self.updateDocumentationDock)
        self.statusBar.addPermanentWidget(self.showHelpButton)
        self.statusBar.addPermanentWidget(self.showNotesButton)
        self.statusBar.addPermanentWidget(self.showROutputButton)
        
        self.GUIDialogDialog = None
        
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
            self.leftDockState = True

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

    # def showGUIDialog(self):
        # if self.autoShowDialog:
            # self.leftDock.show()
    
    def showLeftDock(self):
        print 'in updatedock left'
        if self.leftDockButton.isChecked():
            self.leftDock.show()
            self.leftDockState = True
        else:
            self.leftDock.hide()
            self.leftDockState = False
    
        
    def onShow(self):
        print 'in onShow'
        try:
            if self.hasAdvancedOptions:
                self.leftDockButton.setChecked(self.leftDockState)
                self.showLeftDock()
            if self.rightDock.isFloating():
                self.rightDock.show()
            if hasattr(self, "leftDock") and self.leftDock.isFloating():
                self.leftDock.show()
        except:
            print 'Some problem with loading advanced options and docks, you will see the default'

        
        if 'state' in self.windowState.keys():
            self.restoreState(self.windowState['state'])
        if 'geometry' in self.windowState.keys():
            self.restoreGeometry(self.windowState['geometry'])
       
        if 'size' in self.windowState.keys():
            self.resize(self.windowState['size'])
        if 'pos' in self.windowState.keys():
            self.move(self.windowState['pos'])

        #print self.documentationState
        self.showHelpButton.setChecked(self.documentationState['helpBox'])
        self.showNotesButton.setChecked(self.documentationState['notesBox'])
        self.showROutputButton.setChecked(self.documentationState['ROutputBox'])
        self.updateDocumentationDock()

    def updateDocumentationDock(self):
        print 'in updatedock right'
        
        if self.showHelpButton.isChecked():
            self.helpBox.show()
            self.documentationState['helpBox'] = True
        else:
            self.helpBox.hide()
            self.documentationState['helpBox'] = False
        
        if self.showNotesButton.isChecked():
            self.notesBox.show()
            self.documentationState['notesBox'] = True
        else:
            self.notesBox.hide()
            self.documentationState['notesBox'] = False

        if self.showROutputButton.isChecked():
            self.ROutputBox.show()
            self.documentationState['ROutputBox'] = True
        else:
            self.ROutputBox.hide()
            self.documentationState['ROutputBox'] = False
        
        # print self.documentationState.values()
        if True in self.documentationState.values():
            self.rightDock.show()
            # print 'resize t'
            # self.resize(10,10)
            # self.updateGeometry()
        else:
            # print 'hide'
            self.rightDock.hide()
        
    def setRvariableNames(self,names):
        
        #names.append('loadSavedSession')
        for x in names:
            self.Rvariables[x] = x + self.variable_suffix
        

    def rSend(self, name, variable, updateSignalProcessingManager = 1):
        print 'send'
        
        try:
            self.send(name, variable)
            if updateSignalProcessingManager:
                self.needsProcessingHandler(self, 0)
        except:
            self.needsProcessingHandler(self, 1)
        self.sentItems.append((name, variable))
        self.status.setText('Data sent.')
    def makeCM(self, Variable, Parent):
        if self.R('rownames('+Parent+')') != 'NULL':
            self.R(Variable+'<-data.frame(row.names = rownames('+Parent+'))')
        else:
            self.R(Variable+'<-data.frame(row.names = c('+','.join(range(1, int(self.R('length('+Parent+'[,1])'))))+'))')
    def addToCM(self, colname = 'tmepColname', CM = None, values = None):
        if CM == None: return
        if values == None: return
        if type(values) == type([]):
            values = 'c('+','.join(values)+')'
        self.R(CM+'$'+colname+self.variable_suffix+'<-'+values) # commit to R
    
    
    def getSettings(self, alsoContexts = True):
        # print 'moving to save'
        import re
        settings = {}
        allAtts = self.__dict__
        self.blackList.extend(RSession().__dict__.keys())
        self.blackList.extend(OWWidget().__dict__.keys())
        #print 'all atts:', allAtts
        # try:
        for att in allAtts:
            if att in self.blackList:
                continue
            #print 'frist att: ' + att
            if re.search('^_', att):
                continue
            var = getattr(self, att)
            settings[att] = self.returnSettings(var)
        # except:
            # print 'Exception occured in saving settings'
            # print sys.exc_info()[0]
        settings['_customSettings'] = self.saveCustomSettings()
        
        #try:
        if self.inputs and len(self.inputs) != 0:
            ainputs = []
            for (a, b, c) in [input for input in self.inputs]:
                
                if issubclass(b, RvarClasses.RDataFrame):
                    bc = 'Data Frame'
                elif issubclass(b, RvarClasses.RVector):
                    bc = 'Vector'
                elif issubclass(b, RvarClasses.RList):
                    bc = 'List'
                else:
                    bc = 'Variable'
                ainputs.append((a, bc))
            settings['inputs'] = ainputs
        else: settings['inputs'] = None
        if self.outputs and len(self.outputs) != 0:
            aoutputs = []
            for (a,b) in [output for output in self.outputs]:
                print 'Output type', type(b)
                if issubclass(b, RvarClasses.RDataFrame):
                    bc = 'Data Frame'
                elif issubclass(b, RvarClasses.RVector):
                    bc = 'Vector'
                elif issubclass(b, RvarClasses.RList):
                    bc = 'List'
                else:
                    bc = 'Variable'
                aoutputs.append((a, bc))
            settings['outputs'] = aoutputs
        else: settings['outputs'] = None
        #except:
            #print 'Saving inputs and outputs failed.  This widget will not be reloaded by a dummyWidget!'
        #print str(settings) + ' (OWRpy.py)'
        #print 'My settings are ' + str(settings)
        return settings
    def saveCustomSettings(self):
        pass
    def isPickleable(self,d):
        import re
        #if isinstance(d,QObject):
        # print str(type(d))
        if re.search('PyQt4',str(type(d))) or d.__class__.__name__ in redRGUI.qtWidgets:
            # print 'QT object NOT Pickleable'
            return False
        elif type(d) in [list, dict, tuple]:
            #ok = True
            if type(d) in [list, tuple]:
                for i in d:
                    if self.isPickleable(i) == False:
                        #ok = False
                        return False
                return True
            elif type(d) in [dict]:
                for k in d.keys():
                    if self.isPickleable(d[k]) == False:
                        #ok = False
                        return False
                return True
        elif type(d) in [type(None), str, int, float, bool, numpy.float64]:
            return True
        else: 
            print 'This type is not supported at the moment, if you would like it to be and think that this is a mistake contact the developers so they can add it to the list.'
            print str(d)
            return False
    def printWidget(self, printer = None):
        ## establish a printer that will print the widget
        if not printer:
            printer = QPrinter()
            printDialog = QPrintDialog(printer)
            if printDialog.exec_() == QDialog.Rejected: 
                print 'Printing Rejected'
                return
        #painter = QPainter(printer)
        self.render(printer)
        
            
    def returnSettings(self,var):
        settings = {}
        if var.__class__.__name__ in redRGUI.qtWidgets:
            #print 'getting gui settings for:' + att + '\n\n'
            try:
                v = {}
                v = var.getSettings()
                if v == None:
                    v = var.getDefaultState()
                else:
                    v.update(var.getDefaultState())
            except: 
                v = var.getDefaultState()
                import traceback
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60        

            settings['redRGUIObject'] = {}
            if v: settings['redRGUIObject'] = v
        elif self.isPickleable(var):
            settings['pythonObject'] =  var
        #elif type(var) in [str, int, float, bool]:
        #   settings = var
        elif type(var) in [list]:
           settings['list'] = []
           for i in var:
               settings['list'].append(self.returnSettings(i))
        elif type(var) is dict:
           #print var
           settings['dict'] = {}
           for k,v in var.iteritems():
               settings['dict'][k] = self.returnSettings(v)
        else:
            settings = None
        return settings
    def setSettings(self,settings):
        # print 'on set settings'
        self.redRGUIObjects = {}
        for k,v in settings.iteritems():
            if k in ['inputs', 'outputs']: continue
            if v == None:
                continue
            # elif k =='_customSettings':
                # self.__setattr__(k, v)
            elif 'pythonObject' in v.keys(): 
                # print k
                self.__setattr__(k, v['pythonObject'])
            else:
                self.redRGUIObjects[k] = v;
    def onLoadSavedSession(self):
        # print 'in onLoadSavedSession'
        for k,v in self.redRGUIObjects.iteritems():
            # print str(k)+ ' in onLoadSavedSession widget attribute'
            # pp.pprint(v)
            if not hasattr(self,k):
                continue
            try:
                if 'redRGUIObject' in v.keys():
                    getattr(self, k).loadSettings(v['redRGUIObject'])
                    getattr(self, k).setDefaultState(v['redRGUIObject'])
                
                elif 'dict' in v.keys():
                    var = getattr(self, k)
                    # print 'dict',len(var),len(v['dict'])
                    if len(var) != len(v['dict']): continue
                    self.recursiveSetSetting(var,v['dict'])
                elif 'list' in v.keys():
                    var = getattr(self, k)
                    # print 'list',len(var),len(v['list'])
                    if len(var) != len(v['list']): continue
                    self.recursiveSetSetting(var,v['list'])
            except:
                print 'Error occured in loading data self.'+str(k)
                
                pp.pprint(v)
                import traceback,sys
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60        
            
        if '_customSettings' in self.redRGUIObjects.keys():
            self.loadCustomSettings(self.redRGUIObjects['_customSettings'])
        else:
            self.loadCustomSettings(self.redRGUIObjects)
        
        for (name, data) in self.sentItems:
            self.send(name, data)
        self.needsProcessingHandler(self, 0)
        qApp.restoreOverrideCursor()
    def recursiveSetSetting(self,var,d):
        # print 'recursiveSetSetting'
        
        if type(var) in [list,tuple]:
            for k in xrange(len(d)):
                if type(d[k]) is dict and 'redRGUIObject' in d[k].keys():
                    var[k].loadSettings(d[k]['redRGUIObject'])
                    var[k].setDefaultState(d[k]['redRGUIObject'])
                else:
                    self.recursiveSetSetting(var[k],d[k])
        elif type(var) is dict:
            for k,v in d.iteritems():
                if type(v) is dict and 'redRGUIObject' in v.keys():
                    var[k].loadSettings(v['redRGUIObject'])
                    var[k].setDefaultState(v['redRGUIObject'])
                else:
                    self.recursiveSetSetting(var[k],d[k])
        
    def loadCustomSettings(self,settings=None):
        pass

    def saveSettingsStr(self):
        
        # print 'saveSettingsStr called'
        
        settings = self.getSettings()
        #print settings
        #print str(self.RGUIElements)
        #print cPickle.dumps(settings) + 'settings dump'
        try:
            return cPickle.dumps(settings)
        except: 
            print "ERROR in Pickle", sys.exc_info()[0] 
            pass

    def loadSettings(self, file = None):
        
        file = self.getGlobalSettingsFile(file)
        settings = {}
        if file:
            try:
                file = open(file, "r")
                settings = cPickle.load(file)
            except:
                settings = None

        if hasattr(self, "_settingsFromSchema"):
            if settings: settings.update(self._settingsFromSchema)
            else:        settings = self._settingsFromSchema

        # can't close everything into one big try-except since this would mask all errors in the below code
        if settings:
            # if hasattr(self, "settingsList"):
            self.setSettings(settings)
    
        
#############widget specific settings#####################
    def getdeepattr(self, attr, **argkw):
        try:
            return reduce(lambda o, n: getattr(o, n, None),  attr.split("."), self)
        except:
            if argkw.has_key("default"):
                return argkw[default]
            else:
                raise AttributeError, "'%s' has no attribute '%s'" % (self, attr)

    def getGlobalSettingsFile(self, file=None):
        # print 'getSettingsFile in owbasewidget'
        if file==None:
            file = os.path.join(self.widgetSettingsDir, self._widgetInfo.fileName + ".ini")
        # print file
        return file

    
    # save global settings
    def saveGlobalSettings(self, file = None):
        print 'owrpy global save settings'
        settings = {}
        default = ['windowState','documentationState']
        if hasattr(self, "globalSettingsList"):
            self.globalSettingsList.extend(default)
        else:
            self.globalSettingsList =  default
            
        for name in self.globalSettingsList:
            try:
                settings[name] = {}
                settings[name]['pythonObject'] =  self.getdeepattr(name)
            except:
                print "Attribute %s not found in %s widget. Remove it from the settings list." % (name, self.captionTitle)
        if settings:
            file = self.getGlobalSettingsFile(file)
            file = open(file, "w")
            cPickle.dump(settings, file)

    def onDeleteWidget(self, suppress = 0):
        if suppress == 1: # instantiated in orngDoc.py, will fail if orngDoc has not initialized it.
            return

        for k in self.Rvariables:
            #print self.Rvariables[k]
            self.R('if(exists("' + self.Rvariables[k] + '")) { rm(' + self.Rvariables[k] + ') }')
        try:
            #if self.device != []: #  if this is true then this widget made an R device and we would like to shut it down
            for device in self.device.keys():
                dev = self.device[device]
                #key = device.keys()[0]
                self.R('dev.set('+str(dev)+')', 'setRData')
                self.R('dev.off() # shut down device for widget '+ str(OWRpy.num_widgets), 'setRData') 
                
        except: pass
        self.widgetDelete()
    def widgetDelete(self):
        pass #holder function for other widgets

    def reloadWidget(self):
        pass

        
    def updateWidget(self, name, value):
        print 'update widget called'
        #print name
        #print str(value)
        elementClass = value['class']
        if elementClass == 'widgetBox':
            pass
        elif elementClass == 'widgetLabel':
            getattr(self, name).setText(value['text'])
        elif elementClass == 'checkBox':
            getattr(self, name).setChecked(value['checked'])
        elif elementClass == 'lineEdit':
            getattr(self, name).setText(value['text'])
        elif elementClass == 'button':
            getattr(self, name).setEnabled(value['enabled'])
        elif elementClass == 'listBox':
            getattr(self, name).clear()
            getattr(self, name).insertItems(0, value['items'])
            for item in value['selectedItems']:
                thisItem = getattr(self, name).findItems(item, Qt.MatchExactly)
                #print str(thisItem)
                if thisItem:
                    getattr(self, name).setItemSelected(thisItem[0], 1)
        elif elementClass == 'radioButtonsInBox':
            pass
        elif elementClass == 'comboBox':
            getattr(self, name).clear()
            getattr(self, name).addItems(value['itemText'])
            #print value['itemText'] + ' inserted into '+ name
            try:
                getattr(self, name).setCurrentIndex(value['selectedIndex'])
            except:
                print 'setting index failed'
        elif elementClass == 'comboBoxWithCaption':
            getattr(self, name).clear()
            for i in range(len(value['itemText'])):
                getattr(self, name).setItemText(i, value['itemText'][i])
        elif elementClass == 'tabWidget':
        
            tab = getattr(self, name)
            tab.clear()
            
            for i in range(len(value['itemText'])):
                tab.addTab()
                tab.setTabText(value['itemText'][i])
                tab.setTabEnabled(value['itemEnabled'])
        elif elementClass == 'createTabPage':
            pass
        elif elementClass == 'table':
            table = getattr(self, name)
            row = len(value['rowNames'])
            col = len(value['colNames'])
            table.setColumnCount(col)
            table.setRowCount(row)
            vheaders = value['rowNames']
            hheaders = value['colNames']
            for i in range(len(vheaders)):
                if vheaders[i] != None:
                    table.setVerticalHeaderLabel(i, vheaders[i])
            for j in range(len(hheaders)):
                if hheaders[j] != None:
                    table.setHorizontalHeaderLables(j, hheaders[j])
            for item in value['tableItems']:
                ti = QTableWidgetItem(item[2])
                table.setItem(item[0], item[1], ti)
                
            # for srange in value['selectedRanges']:
                # table.setRangeSelected(srange, 1)
                
        elif elementClass == 'textEdit':
            getattr(self, elementName).setText(value['text'])
        elif elementClass == 'widgetNotes':
            #print elementClass
            #print str(value['text'])
            self.notesAction.textEdit.setHtml(value['text'])
            
    
    def savePDF(self, query, dwidth= 7, dheight = 7, file = None):
        #print str(qApp.canvasDlg.settings)
        if file == None and ('HomeFolder' not in qApp.canvasDlg.settings.keys()):
            file = str(QFileDialog.getSaveFileName(self, "Save File", os.path.abspath(qApp.canvasDlg.settings['saveSchemaDir']), "PDF (*.PDF)"))
        elif file == None: 
            file = str(QFileDialog.getSaveFileName(self, "Save File", os.path.abspath(qApp.canvasDlg.settings['HomeFolder']), "PDF (*.PDF)"))
        if file.isEmpty(): return
        if file: qApp.canvasDlg.settings['HomeFolder'] = os.path.split(file)[0]
        self.R('pdf(file = "'+file+'", width = '+str(dwidth)+', height = '+str(dheight)+')')
        self.R(query, 'setRData')
        self.R('dev.off()')
        self.status.setText('File saved as \"'+file+'\"')
        self.notes.setCursorToEnd()
        self.notes.insertHtml('<br> Image saved to: '+str(file)+'<br>')
    
    def Rplot(self, query, dwidth=8, dheight=8, devNumber = 0):
        # check that a device is currently used by this widget
        # print 'the devNumber is'+str(devNumber)
        # print str(self.device)
        if str(devNumber) in self.device:
            print 'dev exists'
            actdev = self.R('capture.output(dev.set('+str(self.device[str(devNumber)])+'))[2]').replace(' ', '')
            if actdev == 1: #there were no decives present and a new one has been created.
                self.device[str(devNumber)] = self.R('capture.output(dev.cur())[2]').replace(' ', '')
            if actdev != self.device[str(devNumber)]: #other devices were present but not the one you want
                print 'dev not in R'
                self.R('dev.off()')
                self.R('x11('+str(dwidth)+','+str(dheight)+') # start a new device for '+str(OWRpy.num_widgets), 'setRData') # starts a new device 
                self.device[str(devNumber)] = self.R('capture.output(dev.cur())[2]').replace(' ', '')
                print str(self.device)
        else:
            print 'make new dev for this'
            self.R('x11('+str(dwidth)+','+str(dheight)+') # start a new device for '+str(OWRpy.num_widgets), 'setRData') # starts a new device 
            self.device[str(devNumber)] = self.R('capture.output(dev.cur())[2]').replace(' ', '')
        #self.require_librarys(['playwith', 'RGtk2'])
        
        #self.R('playwith('+query+')', 'setRData')
        self.R(query, 'setRData')
        self.needsProcessingHandler(self, 0)
        
    def sendRefresh(self):
        self.signalManager.refresh()
            
            
    def refresh(self):
        pass # function that listens for a refresh signal.  This function should be overloaded in widgets that need to listen.
    def closeEvent(self, event):
        print 'in owrpy close'
        if self.rightDock.isFloating():
            self.rightDock.hide()
        if hasattr(self, "leftDock") and self.leftDock.isFloating():
            self.leftDock.hide()
        
        for i in self.findChildren(QDialog):
            i.setHidden(True)

        self.windowState["geometry"] = self.saveGeometry()
        self.windowState["state"] = self.saveState()
        self.windowState['pos'] = self.pos()
        self.windowState['size'] = self.size()
        
        self.saveGlobalSettings()
        self.customCloseEvent()
    
    def customCloseEvent(self):
        pass

class ToolBarTextEdit(QWidgetAction):
    def __init__(self,parent=None):
        QWidgetAction.__init__(self, parent)
        self.textEdit = QTextEdit()
        self.setDefaultWidget(self.textEdit)
        
        
        
