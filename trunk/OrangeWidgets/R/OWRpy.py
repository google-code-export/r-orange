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
import threading


class OWRpy(OWWidget):
    #a class variable which is incremented every time OWRpy is instantiated.
    # processing  = False
    
    num_widgets = 0
    lock = threading.Lock()
    rsem = threading.Semaphore(value = 1)
    occupied = 0
    
    def __init__(self,parent=None, signalManager=None, title="R Widget",**args):
        OWWidget.__init__(self, parent, signalManager, title, **args)
        
        
        #The class variable is used to create the unique names in R
        OWRpy.num_widgets += 1
        #this should be appended to every R variable
        self.variable_suffix = '_' + str(OWRpy.num_widgets)
        #keep all R variable name in this dict
        self.Rvariables = {}
        self.loadingSavedSession = False
        #self.settingsList = ['variable_suffix','loadingSavedSession']
        self.packagesLoaded = 0
        
    # def setOutputs (self,outputs):
        # self.outputs.extend(outputs)
        # self.outputs = [("Expression Matrix", RvarClasses.RDataFrame), ("Eset", RAffyClasses.Eset)]

    def getSettings(self, alsoContexts = True):
        settings = {}
        if hasattr(self, "settingsList"):
            self.settingsList.extend(['variable_suffix','loadingSavedSession'])
            for name in self.settingsList:
                try:
                    settings[name] =  self.getdeepattr(name)
                except:
                    #print "Attribute %s not found in %s widget. Remove it from the settings list." % (name, self.captionTitle)
                    pass
        
        if alsoContexts:
            contextHandlers = getattr(self, "contextHandlers", {})
            for contextHandler in contextHandlers.values():
                contextHandler.mergeBack(self)
                settings[contextHandler.localContextName] = contextHandler.globalContexts
                settings[contextHandler.localContextName+"Version"] = (contextStructureVersion, contextHandler.contextDataVersion)
            
        return settings
        
    def rSend(self,name, variable):
        print 'send'
        self.loadingSavedSession = False
        self.send(name, variable)
        
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
                
    def R(self, query, type = 'getRData' ,processing_notice=False):
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
            if type == 'getRData':
                output  = rpy.r(query)
            elif type == 'setRData' and not self.loadingSavedSession:
                rpy.r(query)

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
                         
    def require_librarys(self,librarys):
        if self.packagesLoaded == 0:
            for library in librarys:
                if not self.R("require('"+ library +"')"): 
                    self.R('setRepositories(ind=1:7)')
                    self.R('chooseCRANmirror()')
                    self.R('install.packages("' + library + '")')
                try:
                    self.R('require('  + library + ')')
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
        
        col_names = self.rsession('colnames(' + dataFrame_name + ')')
        if type(col_names) is str:
            col_names = [col_names]
        if self.rsession("class(" + dataFrame_name + ")") == 'matrix':
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
                
        if self.rsession('nrow(' + dataFrame_name + ')') > 1000:
            self.rsession('exampleTable_data' + self.variable_suffix + '<- '+ dataFrame_name + '[1:1000,]')
        else:
            self.rsession('exampleTable_data' + self.variable_suffix + '<- '+ dataFrame_name + '')
            
        self.rsession('exampleTable_data' + self.variable_suffix + '[is.na(exampleTable_data' + self.variable_suffix + ')] <- "?"')
        
        d = self.rsession('as.matrix(exampleTable_data' + self.variable_suffix + ')')
        domain = orange.Domain(colClasses)
        data = orange.ExampleTable(domain, d)
        self.rsession('rm(exampleTable_data' + self.variable_suffix + ')')
        return data
        
    def onDeleteWidget(self, supress = 0):
        for k in self.Rvariables:
            print self.Rvariables[k]
            self.R('if(exists("' + self.Rvariables[k] + '")) { rm(' + self.Rvariables[k] + ') }', 'setRData')
        try:
            if supress == 1: # instantiated in orngDoc.py, will fail if orngDoc has not initialized it.
                return
        except:
            for k in self.Rvariables:
                print self.Rvariables[k]
                self.rsession('if(exists("' + self.Rvariables[k] + '")) { rm(' + self.Rvariables[k] + ') }')
            try:
                if self.device: #  if this is true then this widget made an R device and we would like to shut it down
                    key = self.device.keys()[0]
                    self.R('dev.set('+self.device[key]+')', 'setRData')
                    self.R('dev.off() # shut down device for widget '+ str(OWRpy.num_widgets), 'setRData') 
            except: return

    def Rplot(self, query, dwidth=2, dheight=2):
        # check that a device is currently used by this widget
        try: # if this returns true then a device is attached to this widget and should be set to the focus
            key = self.device.keys()
            self.R('dev.set('+self.device[key[0]]+')', 'setRData')
        except:
            self.R('x11('+str(dwidth)+','+str(dheight)+') # start a new device for '+str(OWRpy.num_widgets), 'setRData') # starts a new device 
            self.device = self.R('dev.cur()')  # record the device for later use this records as a dict, though now we only make use of the first element.
        self.R(query, 'setRData')
            
    def onSaveSession(self):
        print 'save session'
        self.loadingSavedSession = True;

