#
# An Orange-Rpy class
# 
# Should include all the functionally need to connect Orange to R 
#

from OWWidget import *
from PyQt4 import QtWebKit
from rpy_options import set_options
set_options(RHOME=os.environ['RPATH'])
import rpy
from numpy import *



import time
import RvarClasses
import RAffyClasses
import threading, sys


class OWRpy(OWWidget):
    #a class variable which is incremented every time OWRpy is instantiated.
    # processing  = False
    
    num_widgets = 0
    lock = threading.Lock()
    rsem = threading.Semaphore(value = 1)
    occupied = 0
    Rhistory = '<code>'
    
    def __init__(self,parent=None, signalManager=None, title="R Widget",**args):
        
        OWWidget.__init__(self, parent, signalManager, title, **args)
        
        print "R version 2.7.0 (2008-04-22) \nCopyright (C) 2008 The R Foundation for Statistical Computing \
            ISBN 3-900051-07-0\n \
            R is free software and comes with ABSOLUTELY NO WARRANTY. \n \
            You are welcome to redistribute it under certain conditions.\n \
            Type 'license()' or 'licence()' for distribution details."
        
        #The class variable is used to create the unique names in R
        OWRpy.num_widgets += 1
        
        #this should be appended to every R variable
        ctime = str(time.time())
        self.variable_suffix = '_' + str(OWRpy.num_widgets) + '_' + ctime
        #keep all R variable name in this dict
        self.Rvariables = {}
        
        self.device = {}
        
        self.RGUIElements = [] #make a blank one to start with which will be filled as the widget is created.
        self.RGUIElementsSettings = {}
        
        self.RPackages = []
        #self.loadSavedSession = False
        #self.loadingSavedSession = False
        #print 'set load ssaved '
        #self.settingsList = ['variable_suffix','loadingSavedSession']
        self.packagesLoaded = 0
        
        #collect the sent items
        self.sentItems = []
        self.blackList= ['blackList','GUIWidgets','RGUIElementsSettings']
        self.GUIWidgets = ['tabWidget','lineEdit','comboBox','listBox','textEdit','checkBox','widgetLabel','radioButtons','table']
        # self.widgetToolBar = QMenuBar(self)
        # notesMenu = self.widgetToolBar.addMenu('Notes')
        # self.notesAction = ToolBarTextEdit(self)
        # notesMenu.addAction(self.notesAction)
        
        # self.widgetToolBar = QMenuBar(self)
        # notesMenu = self.widgetToolBar.addMenu('Notes')
        # self.notesAction = ToolBarTextEdit(self)
        # notesMenu.addAction(self.notesAction)
        #sidebar = OWGUI.widgetHider(self.defaultLeftArea)
        self.notes = QTextEdit()
        self.help = QtWebKit.QWebView(self)
        self.processingBox = QtWebKit.QWebView(self)
        self.processingBox.moveToThread(QThread())
        webSize = QSize(200,100)
        self.help.setMaximumSize(webSize)
        # self.notes.setBaseSize(webSize)
        # self.help.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        # self.notes.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #QtWebKit.QWebSettings.setAttribute(QtWebKit.QWebSettings.PluginsEnabled)
        self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
        self.help.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.connect(self.help, SIGNAL('linkClicked(QUrl)'), self.followLink)
        
        notesBox = OWGUI.widgetBox(self, "Notes")
        helpBox = OWGUI.widgetBox(self, "Discription")
        processingBoxBox = OWGUI.widgetBox(self, "Processing Status")
        self.processingBox.setMaximumSize(webSize)
        self.processingBox.setHtml('<small>Processing not yet performed, please see the help documentation if you are having trouble using this widget.</small>')
        

        #self.processingBox.setUrl(QUrl("http://en.wikipedia.org/wiki/File:Rotating_earth_(small).gif"))
        processingBoxBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        processingBoxBox.layout().addWidget(self.processingBox)
        notesBox.setBaseSize(webSize)
        helpBox.setBaseSize(webSize)
        helpBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        notesBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        notesText = OWGUI.widgetLabel(notesBox, "Please place notes in this area.")
        notesBox.layout().addWidget(self.notes)
        helpBox.layout().addWidget(self.help)
        #sidebar.layout().addWidget(self.notes)
        #sidebar.layout().addWidget(self.help)
        
        #self.controlArea.layout().addWidget(self.widgetToolBar)
        self.defaultLeftArea.layout().addWidget(helpBox)
        #self.help.mainFrame().show()
        self.defaultLeftArea.layout().addWidget(notesBox)
        self.defaultLeftArea.layout().addWidget(processingBoxBox)
        #self.statusBar = QStatusBar()
        #self.layout().addWidget(self.statusBar)
        # self.splitter = QSplitter(self.controlArea)
        # self.widgetMainArea = OWGUI.widgetBox(self, orientation="vertical", margin=2)
        # self.controlArea.layout().addWidget(self.splitter)
        # self.splitter.addWidget(self.widgetMainArea)
        #self.controlArea.setLayout(self.splitter)
        #self.statusIndicator = OWGUI.widgetLabel(self, "Data not connected")
        #self.statusIndicator.setBackgroundRole(QPalette.Dark)
        
        #self.statusImage = QImage('C:/Python25/Lib/site-packages/orange/OrangeCanvas/ajax-loader.gif')
        #self.statusBar.addWidget(self.statusIndicator)
        #self.statusBar.addWidget(self.statusImage)
        #MoviePlayer().show()



    def getSettings(self, alsoContexts = True):
        print '#########################start get settings'
        settings = {}
        allAtts = self.__dict__#dir(self)
        parentVaribles = OWWidget().__dict__.keys()
        self.blackList.extend(parentVaribles)
        #print self.blackList
        for att in allAtts:
            if att in self.blackList:
                # print 'passed:' + att
                continue
            # print 'frist att: ' + att
            if getattr(self, att).__class__.__name__ in self.GUIWidgets:
                print 'getting gui settings for:' + att
             
                v = getattr(self, att).getSettings()
                # print 'settings:' + str(v)
                if not 'RGUIElementsSettings' in settings.keys():
                    # print 'ba'
                    settings['RGUIElementsSettings'] = {}
                
                settings['RGUIElementsSettings'][att] = v
                # print settings['RGUIElementsSettings']
                    
            elif type(getattr(self, att)) in [str,int, float]:
                settings[att] =  self.getdeepattr(att)
            elif type(getattr(self, att)) in [list,dict,tuple]:
                # if type(QObject) in getattr(self, att):
                    # print str(att)+' has a QObject and can not be saved'
                # else:
                    # print str(self.getdeepattr(att))
                    # settings[att] =  self.getdeepattr(att)
                if self.checkForSipClasses(getattr(self, att)):
                    settings[att] = self.getdeepattr(att)
        
        # print settings
        return settings
        
    def checkForSipClasses(self, object):
        if type(object) in [list, tuple]:
            for item in object:
                if type(item) in [list, dict, tuple]:
                    t = self.checkForSipClasses(item)
                    if not t: return False
                elif type(item) in [str, int, float]:
                    return True
                else:
                    return False
        elif type(object) == dict:
            for key in object.keys():
                if type(object[key]) in [list, dict, tuple]:
                    t = self.checkForSipClasses(object[key])
                    if not t: return False
                elif type(object[key]) in [str, int, float]:
                    return True
                else:
                    return False
                    
    def getGlobalSettings(self):
        print 'get global settings'
        settings = {}
        if hasattr(self, "globalSettingsList"):
            for name in self.globalSettingsList:
                try:
                    settings[name] =  self.getdeepattr(name)
                except:
                    print "Attribute %s not found in %s widget. Remove it from the settings list." % (name, self.captionTitle)
        return settings
        
    def saveSettings(self, file = None):
        print 'save settings'
        settings = self.getGlobalSettings()
        if settings:
            if file==None:
                file = os.path.join(self.widgetSettingsDir, self.captionTitle + ".ini")
            if type(file) == str:
                file = open(file, "w")
            cPickle.dump(settings, file)

    def getSettings2(self, alsoContexts = True):
        settings = {}
        allAtts = self.__dict__
        
                
        # if hasattr(self, "settingsList"):
            # self.settingsList.extend(['variable_suffix', 'RGUIElementsSettings', 'RPackages'])

        for att in allAtts:
            print getattr(self, att).__class__
            print getattr(self, att).__class__.__name__
            if type(getattr(self, att)) == type('') or type(getattr(self, att)) == type(1): # if they are strings we don't need to worry much
                if att in self.blackList: pass  # allows us to make a blackList so that everything isn't saved, these things can be saved with special calls to settingsList.extend, but they won't be saved normally.
                else:
                    self.settingsList.extend([att])
            elif type(getattr(self, att)) == type({}) or type(getattr(self, att)) == type([]): #we need to chech these types to see if they contain any instances or other things that we can't pickle.
                # print att
                # self.settingsList.extend([att])
                pass
        for name in self.settingsList:
            try:
                settings[name] =  self.getdeepattr(name)
            except:
                #print "Attribute %s not found in %s widget. Remove it from the settings list." % (name, self.captionTitle)
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
        
    def rSend(self, name, variable, updateSignalProcessingManager = 1):
        print 'send'
        
        try:
            self.send(name, variable)
            if updateSignalProcessingManager:
                self.needsProcessingHandler(self, 0)
        except:
            self.needsProcessingHandler(self, 1)
        self.sentItems.append((name, variable))
        self.processingBox.setHtml('<center>Data sent.</center>')

        
    #depreciated
    def rsession(self, query,processing_notice=False):
        qApp.setOverrideCursor(Qt.WaitCursor)
        OWRpy.rsem.acquire()
        OWRpy.lock.acquire()
        OWRpy.occupied = 1
        output = None
        if processing_notice:
            self.progressBarInit()
            self.progressBarSet(30)
        print query
        try:
            output  = rpy.r(query)
        except rpy.RPyRException, inst:
            OWRpy.occupied = 0
            OWRpy.lock.release()
            OWRpy.rsem.release()
            qApp.restoreOverrideCursor()
            self.progressBarFinished()
            print inst.message
            return inst
        # OWRpy.processing = False
        if processing_notice:
            self.progressBarFinished()
        
        OWRpy.occupied = 0
        OWRpy.lock.release()
        OWRpy.rsem.release()
        qApp.restoreOverrideCursor()
        return output
                
    def R(self, query, type = 'getRData', processing_notice=False):
        #RThread().start()
        # rthread = RThread()
        # rthread.start()
        
        self.processingBox.setHtml('<center><img src="C:/Python25/Lib/site-packages/orange/OrangeCanvas/ajax-loader.gif" /></center>')
        qApp.setOverrideCursor(Qt.WaitCursor)
        
        OWRpy.rsem.acquire()
        OWRpy.occupied = 1
        output = None
        if processing_notice:
            self.processingBox.setHtml('<center>Processing Started.<br>Please wait for processing to finish.</center>')
            # self.progressBarInit()
            # self.progressBarSet(30)
        print query
        histquery = query
        histquery = histquery.replace('<', '&lt;') #convert for html
        histquery = histquery.replace('>', '&gt;')
        histquery = histquery.replace("\t", "\x5ct") # convert \t to unicode \t
        OWRpy.Rhistory += histquery + '</code><br><code>'
        try:
            if type == 'getRData':
                output  = rpy.r(query)
            elif type == 'setRData':
                rpy.r(query)
            elif type == 'getRSummary':
                rpy.r('tmp<-('+query+')')
                output = rpy.r('list(rowNames=rownames(tmp), colNames=colnames(tmp), Length=length(tmp), Class=class(tmp), Summary=summary(tmp))')
                rpy.r('rm(tmp)')
            else:
                rpy.r(query) # run the query anyway even if the user put un a wierd value

        except rpy.RPyRException, inst:
            OWRpy.occupied = 0
            #OWRpy.lock.release()
            OWRpy.rsem.release()
            qApp.restoreOverrideCursor()
            self.progressBarFinished()
            print inst.message
            QMessageBox.information(self, 'Orange Canvas','R Error: '+ inst.message,  QMessageBox.Ok + QMessageBox.Default)
            self.processingBox.setHtml('<center>Error occured during processing please check data or <a href="http://red-r.org/">contact the developers.</a></center>')

        OWRpy.processing = False
        if processing_notice:
            self.processingBox.setHtml('<center>Processing complete</center>')
            #self.progressBarFinished()
        
        #rthread.threadBreaking = True
        
        OWRpy.occupied = 0
        OWRpy.rsem.release()
        qApp.restoreOverrideCursor()
        return output
                         
    def require_librarys(self,librarys):
        import orngEnviron
        #lib = os.path.join(os.path.realpath(orngEnviron.directoryNames["canvasSettingsDir"]), "Rpackages").replace("\\", "/")
        #self.R('.libPaths("' + lib  +'")')
        
        if self.packagesLoaded == 0:
            for library in librarys:
                try:
                    if not self.R("require('"+ library +"')"): 
                        self.R('setRepositories(ind=1:7)')
                        self.R('chooseCRANmirror()')
                        self.R('install.packages("' + library + '")')
                        self.R('require(' + library + ')')
                    self.RPackages.append(library)
                except rpy.RPyRException, inst:
                    print 'asdf'
                    m = re.search("'(.*)'",inst.message)
                    self.require_librarys([m.group(1)])
                except:
                    print 'aaa'
            self.packagesLoaded = 1
        else:
            print 'Packages Loaded'
        #add the librarys to a list so that they are loaded when R is loaded.
        
    def setRvariableNames(self,names):
        
        #names.append('loadSavedSession')
        for x in names:
            self.Rvariables[x] = x + self.variable_suffix
        
    
    # def setStateVariables(self,names):
        # self.settingsList.extend(names)
    
    def convertDataframeToExampleTable(self, dataFrame_name):
        #set_default_mode(CLASS_CONVERSION)
        dfsummary = self.R(dataFrame_name, 'getRSummary')
        col_names = dfsummary['colNames']
        if type(col_names) is str:
            col_names = [col_names]
        if dfsummary['Class'] == 'matrix':
            col_def = self.rsession("apply(" + dataFrame_name + ",2,class)")
        else:
            col_def = self.rsession("sapply(" + dataFrame_name + ",class)")
        if len(col_def) == 0:
            col_names = [col_names]
        
        colClasses = []
        for i in col_names:
            if col_def[i] == 'numeric' or col_def[i] == 'integer':
                colClasses.append(orange.FloatVariable(i))
            elif col_def[i] == 'factor':
                colClasses.append(orange.StringVariable(i))
            elif col_def[i] == 'character':
                colClasses.append(orange.StringVariable(i))
            elif col_def[i] == 'logical':
                colClasses.append(orange.StringVariable(i))
            else:
                colClasses.append(orange.StringVariable(i))
                
        if len(dfsummary['rowNames']) > 1000:
            self.rsession('exampleTable_data' + self.variable_suffix + '<- '+ dataFrame_name + '[1:1000,]')
        else:
            self.rsession('exampleTable_data' + self.variable_suffix + '<- '+ dataFrame_name + '')
            
        self.rsession('exampleTable_data' + self.variable_suffix + '[is.na(exampleTable_data' + self.variable_suffix + ')] <- "?"')
        
        d = self.rsession('as.matrix(exampleTable_data' + self.variable_suffix + ')')
        if self.R('nrow(exampleTable_data' + self.variable_suffix + ')') == 1:
            d = [d]
        #print d
        #type(d)
        domain = orange.Domain(colClasses)
        data = orange.ExampleTable(domain, d)
        self.rsession('rm(exampleTable_data' + self.variable_suffix + ')')
        return data
        
    def onDeleteWidget(self, suppress = 0):
        # for k in self.Rvariables:
            # print self.Rvariables[k]
            # self.R('if(exists("' + self.Rvariables[k] + '")) { rm(' + self.Rvariables[k] + ') }', 'setRData')     #### I don't know why this block was added again up here.

        if suppress == 1: # instantiated in orngDoc.py, will fail if orngDoc has not initialized it.
            return

        for k in self.Rvariables:
            #print self.Rvariables[k]
            self.rsession('if(exists("' + self.Rvariables[k] + '")) { rm(' + self.Rvariables[k] + ') }')
        try:
            #if self.device != []: #  if this is true then this widget made an R device and we would like to shut it down
            for device in self.device.keys():
                dev = self.device[device]
                #key = device.keys()[0]
                self.R('dev.set('+str(dev)+')', 'setRData')
                self.R('dev.off() # shut down device for widget '+ str(OWRpy.num_widgets), 'setRData') 
        except: return

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
    def onLoadSavedSession(self):
        print 'in onLoadSavedSession'
        #print self.RGUIElementsSettings['scanarea']
        
        for i in self.RGUIElementsSettings.keys():
            try:            
                print '**********************' + i
                # print getattr(self, i).loadSettings
                # print self.RGUIElementsSettings[i]
                # print getattr(self, i).loadSettings
                getattr(self, i).loadSettings(self.RGUIElementsSettings[i])
            except:
                print 'error:' + i
                print "Unexpected error:", sys.exc_info()[0]
                

        for (name, data) in self.sentItems:
            self.send(name, data)
       
    
    def onLoadSavedSession2(self):
        #print str(self.RGUIElementsSettings)
        
        for (name, data) in self.sentItems:
            self.send(name, data)
        #print str(self.RGUIElementsSettings.keys())
        for key in self.RGUIElementsSettings.keys():
            print key
            elementName = key.replace('GUIelement_', '')
            info = self.RGUIElementsSettings[key]
            try:
                self.updateWidget(elementName, info)
                print key + ' complete'
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
        print name
        print str(value)
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
            print value['itemText'] + ' inserted into '+ name
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
            print elementClass
            print str(value['text'])
            self.notesAction.textEdit.setHtml(value['text'])
            
    def followLink(self, url):
        self.rsession('shell.exec("'+str(url.toString())+'")')
        self.notes.setHtml(str(url.toString()))
            
class ToolBarTextEdit(QWidgetAction):
    def __init__(self,parent=None):
        QWidgetAction.__init__(self, parent)
        self.textEdit = QTextEdit()
        self.setDefaultWidget(self.textEdit)
        
        
        