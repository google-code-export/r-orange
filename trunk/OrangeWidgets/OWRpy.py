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
import RvarClasses
import RAffyClasses
import threading, sys
import urllib


class OWRpy(OWWidget,RSession):
    #a class variable which is incremented every time OWRpy is instantiated.
    # processing  = False
    
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
        self.autoShowDialog = 1
        self.hasAdvancedOptions = wantGUIDialog
        #collect the sent items
        self.sentItems = []
        
        #dont save these variables
        self.blackList= ['blackList','GUIWidgets','RGUIElementsSettings']
        
        
        
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
        
        url = 'http://red-r.org/help.php?widget=' + os.path.basename(self._widgetInfo.fileName)
        self.help = redRGUI.webViewBox(self.helpBox,url=url)
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
        print 'asdfasdf', ev
        print self.windowTitle()
        if self.rightDock.isFloating():
            self.rightDock.setWindowTitle(self.windowTitle() + ' Documentation')
        else:
            self.rightDock.setWindowTitle('Documentation')
        if hasattr(self, "leftDock"): 
            if self.leftDock.isFloating():
                self.leftDock.setWindowTitle(self.windowTitle() + ' Advanced Options')
            else:
                self.leftDock.setWindowTitle('Advanced Options')


    def showGUIDialog(self):
        if self.autoShowDialog:
            self.leftDock.show()
    
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
        if self.hasAdvancedOptions:
            self.leftDockButton.setChecked(self.leftDockState)
            self.showLeftDock()

        print self.documentationState
        self.showHelpButton.setChecked(self.documentationState['helpBox'])
        self.showNotesButton.setChecked(self.documentationState['notesBox'])
        self.showROutputButton.setChecked(self.documentationState['ROutputBox'])
        self.updateDocumentationDock()
        
        if 'state' in self.windowState.keys():
            self.restoreState(self.windowState['state'])
        if 'geometry' in self.windowState.keys():
            self.restoreGeometry(self.windowState['geometry'])
       
        if 'size' in self.windowState.keys():
            self.resize(self.windowState['size'])
        if 'pos' in self.windowState.keys():
            self.move(self.windowState['pos'])
            
        if self.rightDock.isFloating():
            self.rightDock.show()
        if hasattr(self, "leftDock") and self.leftDock.isFloating():
            self.leftDock.show()


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
        
        
        if True in self.documentationState.values():
            self.rightDock.show()
            # print 'resize t'
            # self.resize(10,10)
            # self.updateGeometry()
        else:
            # print 'resize f'
            self.rightDock.hide()
            # self.resize(10,10)
            # self.updateGeometry()
        
    def setRvariableNames(self,names):
        
        #names.append('loadSavedSession')
        for x in names:
            self.Rvariables[x] = x + self.variable_suffix
        
    
    # def setStateVariables(self,names):
        # self.settingsList.extend(names)
    

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
        print '#########################start get settings'
        settings = {}
        allAtts = self.__dict__
        parentVaribles = OWWidget().__dict__.keys()
        self.blackList.extend(parentVaribles)
        #print self.blackList
        for att in allAtts:
            if att in self.blackList:
                # print 'passed:' + att
                continue
            # print 'frist att: ' + att
            if getattr(self, att).__class__.__name__ in redRGUI.qtWidgets:
                #print 'getting gui settings for:' + att + '\n\n'
                try:
                    v = getattr(self, att).getSettings()
                    #print str(v) + '\n\n'
                except: v = {}
                #print 'settings:' + str(v)
                if not 'RGUIElementsSettings' in settings.keys():
                    #print 'RGUIElementsSettings not in settings.keys (OWRpy.py)'
                    settings['RGUIElementsSettings'] = {}
                
                if v: settings['RGUIElementsSettings'][att] = v
                # print settings['RGUIElementsSettings']
                    
            elif type(getattr(self, att)) in [str,int]:
                settings[att] =  self.getdeepattr(att)
            elif type(getattr(self, att)) in [list,dict,tuple]:
                settings[att] =  self.getdeepattr(att)
        ainputs = []
        try:
            for a, b, c in self.inputs:
                ainputs.append(a)
            settings['inputs'] = ainputs
            aoutputs = []
            for a,b in self.outputs:
                aoutputs.append(a)
            settings['outputs'] = aoutputs
        except:
            pass
        #print str(settings) + ' (OWRpy.py)'
        #print 'My settings are ' + str(settings)
        return settings
    def getGlobalSettings(self):
        print 'get global settings'
        settings = {}
        default = ['windowState','documentationState']
        if hasattr(self, "globalSettingsList"):
            self.globalSettingsList.extend(default)
        else:
            self.globalSettingsList =  default
            
        for name in self.globalSettingsList:
            try:
                settings[name] =  self.getdeepattr(name)
            except:
                print "Attribute %s not found in %s widget. Remove it from the settings list." % (name, self.captionTitle)
        return settings
        
    
    def getdeepattr(self, attr, **argkw):
        try:
            return reduce(lambda o, n: getattr(o, n, None),  attr.split("."), self)
        except:
            if argkw.has_key("default"):
                return argkw[default]
            else:
                raise AttributeError, "'%s' has no attribute '%s'" % (self, attr)

    def getSettingsFile(self, file):
        print 'getSettingsFile in owbasewidget'
        if file==None:
            if os.path.exists(os.path.join(self.widgetSettingsDir, os.path.basename(self._widgetInfo.fileName) + ".ini")):
                file = os.path.join(self.widgetSettingsDir, os.path.basename(self._widgetInfo.fileName) + ".ini")
            else:
                return
        if type(file) == str:
            if os.path.exists(file):
                return open(file, "r")
        else:
            return file



    # Loads settings from string str which is compatible with cPickle
    def loadSettingsStr(self, str):
        if str == None or str == "":
            return

        settings = cPickle.loads(str)
        self.setSettings(settings)


    # return settings in string format compatible with cPickle
    def saveSettingsStr(self):
        #print 'saveSettingsStr called'
        settings = self.getSettings()
        #print settings
        #print str(self.RGUIElements)
        #print cPickle.dumps(settings) + 'settings dump'
        try:
            
            return cPickle.dumps(settings)
        except: 
            #print str(settings)
            pass


    # Set all settings
    # settings - the map with the settings
    def setSettings(self,settings):
        for key in settings:
            # print key
            if key == 'inputs': continue
            if key == 'outputs': continue
            self.__setattr__(key, settings[key])
        
    def loadSettings(self, file = None):
        print 'loadSettings in owbasewidget'
        #print self.inputs
        #print str(self.outputs) + ' preload'
        file = self.getSettingsFile(file)
        settings = {}
        if file:
            try:
                settings = cPickle.load(file)
            except:
                settings = None
        #settings = None # do not load ini file
        if hasattr(self, "_settingsFromSchema"):
            if settings: settings.update(self._settingsFromSchema)
            else:        settings = self._settingsFromSchema

        #print 'start loading local variables'
        # print settings
        # can't close everything into one big try-except since this would mask all errors in the below code
        if settings:
            if hasattr(self, "settingsList"):
                self.setSettings(settings)
        #print self.inputs
        #print str(self.outputs) + ' post load'

    def saveSettings(self, file = None):
        print 'owrpy save settings'
        settings = self.getGlobalSettings()
        # print settings
        # print file
        # print self.captionTitle
        if settings:
            if file==None:
                file = os.path.join(self.widgetSettingsDir, os.path.basename(self._widgetInfo.fileName) + ".ini")
            if type(file) == str:
                file = open(file, "w")
            cPickle.dump(settings, file)

    def getSettings2(self, alsoContexts = True): #depreciated
        settings = {}
        allAtts = self.__dict__
        
                
        # if hasattr(self, "settingsList"):
            # self.settingsList.extend(['variable_suffix', 'RGUIElementsSettings', 'RPackages'])

        for att in allAtts:
            #print getattr(self, att).__class__
            #print getattr(self, att).__class__.__name__
            if type(getattr(self, att)) == type('') or type(getattr(self, att)) == type(1): # if they are strings we don't need to worry much
                if att in self.blackList: pass  # allows us to make a blackList so that everything isn't saved, these things can be saved with special calls to settingsList.extend, but they won't be saved normally.
                else:
                    self.settingsList.extend([att])
            elif type(getattr(self, att)) == type({}) or type(getattr(self, att)) == type([]): #we need to chech these types to see if they contain any instances or other things that we can't pickle.
                
                pass
        for name in self.settingsList:
            try:
                settings[name] =  self.getdeepattr(name)
            except:
                
                pass
        for element in self.RGUIElements:
            # print element
            #element.getSettings()
            # element.__class__.__name__
            continue
            
            GUIsetting = {}
            elementClass = element[1]
            elementName = element[0]
            if elementClass == 'widgetBox':
                GUIsetting['class'] = 'widgetBox'
            elif elementClass == 'widgetLabel':
                GUIsetting['text'] = getattr(self, elementName).text()
                GUIsetting['class'] = 'widgetLabel'
            elif elementClass == 'checkBox':
                GUIsetting['checked'] = getattr(self, elementName).isChecked()
                GUIsetting['class'] = 'checkBox'
            elif elementClass == 'lineEdit':
                GUIsetting['text'] = getattr(self, elementName).text()
                GUIsetting['class'] = 'lineEdit'
            elif elementClass == 'button':
                GUIsetting['enabled'] = getattr(self, elementName).isEnabled()
                GUIsetting['class'] = 'button'
            elif elementClass == 'listBox':
                GUIsetting['items'] = []
                for i in range(getattr(self, elementName).count()):
                    GUIsetting['items'].append(getattr(self, elementName).item(i).text())
                GUIsetting['selectedItems'] = []
                for item in getattr(self, elementName).selectedItems():
                    GUIsetting['selectedItems'].append(item.text())
                GUIsetting['class'] = 'listBox'
            elif elementClass == 'radioButtonsInBox':
                GUIsetting['class'] = 'radioButtonsInBox'
            elif elementClass == 'comboBox':
                text = []
                cb = getattr(self, elementName)
                for i in range(cb.count()):
                    text.append(cb.itemText(i))
                GUIsetting['itemText'] = text
                GUIsetting['selectedIndex'] = getattr(self, elementName).currentIndex()
                GUIsetting['class'] = 'comboBox'
            elif elementClass == 'comboBoxWithCaption':
                text = []
                cb = getattr(self, elementName)
                for i in range(cb.count()):
                    text.append(cb.itemText(i))
                GUIsetting['itemText'] = text
                GUIsetting['class'] = 'comboBoxWithCaption'
            elif elementClass == 'tabWidget':
                text = []
                enabled = []
                tab = getattr(self, elementName)
                for i in range(tab.count()):
                    text.append(tab.tabText(i))
                    enabled.append(tab.isEnabled(i))
                GUIsetting['itemText'] = text
                GUIsetting['itemEnabled'] = enabled
                GUIsetting['class'] = 'tabWidget'
            elif elementClass == 'createTabPage':
                GUIsetting['class'] = 'createTabPage'
            elif elementClass == 'table':
                table = getattr(self, elementName)
                #GUIsetting['selectedRanges'] = table.selectedRanges()
                row = table.rowCount()
                col = table.columnCount()
                rowNames = []
                for i in range(row):
                    try:
                        rowNames.append(table.verticalHeaderItem(i).text())
                    except:
                        rowNames.append(None)
                GUIsetting['rowNames'] = rowNames
                
                colNames = []
                for j in range(col):
                    try:
                        colNames.append(table.horizontalHeaderItem(j).text())
                    except:
                        colNames.append(None)
                GUIsetting['colNames'] = colNames
                
                tableItems = []
                tableItemsSelected = []
                for i in range(row):
                    for j in range(col):
                        try:
                            tableItems.append((i,j,table.item(i,j).text()))
                            #tableItemsSelected.append((i,j,table.item(i,j)
                        except: pass
                GUIsetting['tableItems'] = tableItems
                GUIsetting['class'] = 'table'
            elif elementClass == 'textEdit':
                GUIsetting['text'] = getattr(self, elementName).toHtml()
                GUIsetting['class'] = 'textEdit'
            
            self.RGUIElementsSettings[str('GUIelement_'+elementName)] = GUIsetting
            
        self.RGUIElementsSettings['widgetNotes'] = {'text':self.notesAction.textEdit.document().toHtml(), 'class': 'widgetNotes'}
            # if hasattr(self, "settingsList"):
                # self.settingsList.extend([str('GUIelement_'+elementName)])
                # settings[str('GUIelement_'+elementName)] = GUIsetting
            
        if alsoContexts:
            contextHandlers = getattr(self, "contextHandlers", {})
            for contextHandler in contextHandlers.values():
                contextHandler.mergeBack(self)
                settings[contextHandler.localContextName] = contextHandler.globalContexts
                settings[contextHandler.localContextName+"Version"] = (contextStructureVersion, contextHandler.contextDataVersion)
            
        return settings
        
      
    
    
    def onDeleteWidget(self, suppress = 0):
        # for k in self.Rvariables:
            # print self.Rvariables[k]
            # self.R('if(exists("' + self.Rvariables[k] + '")) { rm(' + self.Rvariables[k] + ') }', 'setRData')     #### I don't know why this block was added again up here.

        if suppress == 1: # instantiated in orngDoc.py, will fail if orngDoc has not initialized it.
            return

        for k in self.Rvariables:
            #print self.Rvariables[k]
            self.R('if(exists("' + self.Rvariables[k] + '")) { rm(' + self.Rvariables[k] + ') }')
        # try:
            ##if self.device != []: #  if this is true then this widget made an R device and we would like to shut it down
            # for device in self.device.keys():
                # dev = self.device[device]
                ##key = device.keys()[0]
                # self.R('dev.set('+str(dev)+')', 'setRData')
                # self.R('dev.off() # shut down device for widget '+ str(OWRpy.num_widgets), 'setRData') 
                
        # except: pass
        self.widgetDelete()
    def widgetDelete(self):
        pass #holder function for other widgets
    def onLoadSavedSession(self):
        #print 'in onLoadSavedSession'
        #print self.RGUIElementsSettings['scanarea']
        #print 'Loading the following elements ' + str(self.RGUIElementsSettings) + ' (OWRpy.py)'
        for i in self.RGUIElementsSettings.keys():
            try:            
                #print '**********************' + i
                getattr(self, i).loadSettings(self.RGUIElementsSettings[i])
            except:
                print 'error:' + i
                print "Unexpected error:", sys.exc_info()[0]
                

        for (name, data) in self.sentItems:
            self.send(name, data)
        self.reloadWidget()
        
    def reloadWidget(self):
        pass
    
    def onLoadSavedSession2(self): #depreciated
        #print str(self.RGUIElementsSettings)
        # set the sent items but don't activate the refresh of the widgets (this is handled by signalManager)
        for (name, data) in self.sentItems:
            self.send(name, data)
        #print str(self.RGUIElementsSettings.keys())
        for key in self.RGUIElementsSettings.keys():
            #print key
            elementName = key.replace('GUIelement_', '')
            info = self.RGUIElementsSettings[key]
            try:
                self.updateWidget(elementName, info)
                #print key + ' complete'
            except:
                print 'loading '+key+' failed'
        try:
            self.processSignals()
            self.RWidgetReload()
        except: pass
    
    def onSaveSession(self):
        print 'save session'
        #self.loadSavedSession = value
        
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
        # if self.GUIDialogDialog != None:
            # self.GUIDialogDialog.hide()
        # self.notesBoxDialog.hide()
        # self.helpBoxDialog.hide()
        if self.rightDock.isFloating():
            self.rightDock.hide()
        if hasattr(self, "leftDock") and self.leftDock.isFloating():
            self.leftDock.hide()
        self.windowState["geometry"] = self.saveGeometry()
        self.windowState["state"] = self.saveState()
        self.windowState['pos'] = self.pos()
        self.windowState['size'] = self.size()
        self.saveSettings()

class ToolBarTextEdit(QWidgetAction):
    def __init__(self,parent=None):
        QWidgetAction.__init__(self, parent)
        self.textEdit = QTextEdit()
        self.setDefaultWidget(self.textEdit)
        
        
        