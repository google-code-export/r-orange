#
# An Orange-Rpy class
# 
# Should include all the functionally need to connect Orange to R 
#

from OWWidget import *
from rpy_options import set_options
set_options(RHOME=os.environ['RPATH'])
import rpy



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
        #self.loadSavedSession = False
        #self.loadingSavedSession = False
        #print 'set load ssaved '
        #self.settingsList = ['variable_suffix','loadingSavedSession']
        self.packagesLoaded = 0
        
        #collect the sent items
        self.sentItems = []
        
        
    # def setOutputs (self,outputs):
        # self.outputs.extend(outputs)
        # self.outputs = [("Expression Matrix", RvarClasses.RDataFrame), ("Eset", RAffyClasses.Eset)]

    def getSettings(self, alsoContexts = True):
        settings = {}
        if hasattr(self, "settingsList"):
            self.settingsList.extend(['variable_suffix', 'RGUIElementsSettings'])
            for name in self.settingsList:
                try:
                    settings[name] =  self.getdeepattr(name)
                except:
                    #print "Attribute %s not found in %s widget. Remove it from the settings list." % (name, self.captionTitle)
                    pass
        for element in self.RGUIElements:
            print element
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
                GUIsetting['items'] = getattr(self, elementName).items()
                GUIsetting['selectedItems'] = getattr(self, elementName).selectedItems()
                GUIsetting['class'] = 'listBox'
            elif elementClass == 'radioButtonsInBox':
                GUIsetting['class'] = 'radioButtonsInBox'
            elif elementClass == 'comboBox':
                text = []
                cb = getattr(self, elementName)
                for i in range(cb.count()):
                    text.append(cb.itemText(i))
                GUIsetting['itemText'] = text
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
                GUIsetting['text'] = getattr(self, elementName).text()
                GUIsetting['class'] = 'textEdit'
            
            self.RGUIElementsSettings[str('GUIelement_'+elementName)] = GUIsetting
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
        qApp.setOverrideCursor(Qt.WaitCursor)
        OWRpy.rsem.acquire()
        OWRpy.lock.acquire()
        OWRpy.occupied = 1
        output = None
        if processing_notice:
            self.progressBarInit()
            self.progressBarSet(30)
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
            OWRpy.lock.release()
            OWRpy.rsem.release()
            qApp.restoreOverrideCursor()
            self.progressBarFinished()
            print inst.message
            QMessageBox.information(self, 'Orange Canvas','R Error: '+ inst.message,  QMessageBox.Ok + QMessageBox.Default)
            #sys.exit()
            
            #raise rpy.RPyException('Unable to process')

        # OWRpy.processing = False
        if processing_notice:
            self.progressBarFinished()
        
        OWRpy.occupied = 0
        OWRpy.lock.release()
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
                except rpy.RPyRException, inst:
                    print 'asdf'
                    m = re.search("'(.*)'",inst.message)
                    self.require_librarys([m.group(1)])
                except:
                    print 'aaa'
            self.packagesLoaded = 1
        else:
            print 'Packages Loaded'
                
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
        print 'the devNumber is'+str(devNumber)
        if str(devNumber) in self.device:
            print 'dev exists'
            actdev = self.R('capture.output(dev.set('+str(self.device[str(devNumber)])+'))[2]').replace(' ', '')
            if actdev != self.device[str(devNumber)]:
                print 'dev not in R'
                self.R('x11('+str(dwidth)+','+str(dheight)+') # start a new device for '+str(OWRpy.num_widgets), 'setRData') # starts a new device 
                self.device[str(devNumber)] = self.R('capture.output(dev.cur())[2]').replace(' ', '')
                print str(self.device)
        else:
            print 'make new dev for this'
            self.R('x11('+str(dwidth)+','+str(dheight)+') # start a new device for '+str(OWRpy.num_widgets), 'setRData') # starts a new device 
            self.device[str(devNumber)] = self.R('capture.output(dev.cur())[2]').replace(' ', '')
        self.R(query, 'setRData')
        self.needsProcessingHandler(self, 0)
    def onLoadSavedSession(self):
        print str(self.RGUIElementsSettings)
        for (name, data) in self.sentItems:
            self.send(name, data)
        for key in self.RGUIElementsSettings.keys():
            elementName = key.replace('GUIelement_', '')
            info = self.RGUIElementsSettings[key]
            self.updateWidget(elementName, info)
    
    def onSaveSession(self):
        print 'save session'
        self.loadSavedSession = value;
        
    def updateWidget(self, name, value):
        print 'update widget called'
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
        elif elementClass == 'radioButtonsInBox':
            pass
        elif elementClass == 'comboBox':
            getattr(self, name).clear()
            for i in range(len(value['itemText'])):
                getattr(self, name).setItemText(i, value['itemText'][i])
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

