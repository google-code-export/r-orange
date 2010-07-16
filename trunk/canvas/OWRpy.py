#
# An Orange-Rpy class
# 
# Should include all the functionally need to connect Orange to R 
#

from widgetGUI import *
from widgetSignals import *
from widgetSession import *
from PyQt4.QtGui import *
import RSession, redREnviron
import rpy

class OWRpy(widgetSignals,widgetGUI,widgetSession):   
    uniqueWidgetNumber = 0
    globalRHistory = []
    def __init__(self,wantGUIDialog = 0):
        
        widgetSignals.__init__(self, None, None)
        self.dontSaveList = self.__dict__.keys()
        #print self.dontSaveList

        widgetGUI.__init__(self, parent=None, signalManager=None, title=None, wantGUIDialog=wantGUIDialog)
        self.dontSaveList = self.__dict__.keys()
        for x in ['status','notes','ROutput','widgetState']: self.dontSaveList.remove(x)
        
        widgetSession.__init__(self,self.dontSaveList)
        
        self.saveSettingsList = []  # a list of lists or strings that we will save.
        OWRpy.uniqueWidgetNumber += 1
        ctime = str(time.time())
        self.sessionID = 0  # a unique ID for the session.  This is not saved or reset when the widget is loaded.  Rather this added when the widget is loaded.  This allows for multiple widgets to use the same 
        self.widgetID = str(OWRpy.uniqueWidgetNumber) + '_' + ctime
        self.variable_suffix = '_' + self.widgetID
        self.Rvariables = {}
        self.RvariablesNames = []
        self.setRvariableNames(['title'])
        self.requiredRLibraries = []
        self.device = {}
        self.packagesLoaded = 0
        self.widgetRHistory = []
        


    def resetRvariableNames(self):
        for x in self.RvariablesNames:
            self.Rvariables[x] = x + self.variable_suffix
    def setRvariableNames(self,names):
        
        #names.append('loadSavedSession')
        for x in names:
            self.Rvariables[x] = x + self.variable_suffix
            self.RvariablesNames.append(x)
            
    def makeCM(self, Variable):
        self.R(Variable+'<-list()')
    def addToCM(self, colname = 'tmepColname', CM = None, values = None):
        if CM == None: return
        if values == None: return
        if type(values) == type([]):
            values = 'c('+','.join(values)+')'
        self.R(CM+'$'+colname+self.variable_suffix+'<-'+values) # commit to R

    def R(self, query, callType = 'getRData', processingNotice=False, silent = False, showException=True, wantType = None, listOfLists = True):
        
        qApp.setOverrideCursor(Qt.WaitCursor)
        #try:
        if processingNotice:
            self.status.setText('Processing Started...')
        try:
            commandOutput = RSession.Rcommand(query = query, silent = silent, wantType = wantType, listOfLists = listOfLists)
        except rpy.RPyRException as inst:
            #print 'asdfasdfasdf', inst
            qApp.restoreOverrideCursor()
            if showException:
                QMessageBox.information(self, 'Red-R Canvas','R Error: '+ str(inst),  
                QMessageBox.Ok + QMessageBox.Default)
            
            raise RuntimeError(str(inst))
            return None # now processes can catch potential errors

        #except: 
        #    print 'R exception occurred'
        self.processing = False
        if processingNotice:
            self.status.setText('Processing complete.')
            #self.progressBarFinished()
        if not silent:
            OWRpy.globalRHistory.append(query)
            self.widgetRHistory.append(query)
            
            self.ROutput.setCursorToEnd()
            self.ROutput.append('> '+ query) #Keep track automatically of what R functions were performed.

        qApp.restoreOverrideCursor()
        return commandOutput
   
    def assignR(self, name, object):
        assignOK = RSession.assign(name, object)
        if not assignOK:
            QMessageBox.information(self, 'Red-R Canvas','Object was not assigned correctly in R, please tell package manager.',  
            QMessageBox.Ok + QMessageBox.Default)
            raise Exception, 'Object was not assigned correctly in R, please tell package manager.'
        else:
            histquery = 'Assign '+str(name)+' to '+str(object)
            OWRpy.globalRHistory.append(histquery)
            self.widgetRHistory.append(histquery)

            self.ROutput.setCursorToEnd()
            self.ROutput.append('> '+ histquery)

    def savePDF(self, query, dwidth= 7, dheight = 7, file = None):
        #print str(redREnviron.settings)
        if file == None and ('HomeFolder' not in redREnviron.settings.keys()):
            file = str(QFileDialog.getSaveFileName(self, "Save File", os.path.abspath(redREnviron.settings['saveSchemaDir']), "PDF (*.PDF)"))
        elif file == None: 
            file = str(QFileDialog.getSaveFileName(self, "Save File", os.path.abspath(redREnviron.settings['HomeFolder']), "PDF (*.PDF)"))
        if file.isEmpty(): return
        if file: redREnviron.settings['HomeFolder'] = os.path.split(file)[0]
        self.R('pdf(file = "'+file+'", width = '+str(dwidth)+', height = '+str(dheight)+')')
        self.R(query, 'setRData')
        self.R('dev.off()')
        self.status.setText('File saved as \"'+file+'\"')
        self.notes.setCursorToEnd()
        self.notes.insertHtml('<br> Image saved to: '+str(file)+'<br>')
    
    def Rplot(self, query, dwidth=8, dheight=8, devNumber = 0, mfrow = None):
        # check that a device is currently used by this widget
        # print 'the devNumber is'+str(devNumber)
        # print str(self.device)
        if str(devNumber) in self.device:
            print '#--# dev exists'
            actdev = self.R('capture.output(dev.set('+str(self.device[str(devNumber)])+'))[2]').replace(' ', '')
            if actdev == 1: #there were no decives present and a new one has been created.
                self.device[str(devNumber)] = self.R('capture.output(dev.cur())[2]').replace(' ', '')
            if actdev != self.device[str(devNumber)]: #other devices were present but not the one you want
                print '#--# dev not in R'
                self.R('dev.off()')
                self.R('x11('+str(dwidth)+','+str(dheight)+') # start a new device for '+str(OWRpy.uniqueWidgetNumber)) # starts a new device 
                self.device[str(devNumber)] = self.R('capture.output(dev.cur())[2]').replace(' ', '')
                print '#--#', str(self.device)
        else:
            print '#--# make new dev for this'
            self.R('x11('+str(dwidth)+','+str(dheight)+') # start a new device for '+str(OWRpy.uniqueWidgetNumber), 'setRData') # starts a new device 
            if type(mfrow) == list:
                self.R('par(mfrow = c('+str(mfrow[0])+','+str(mfrow[1])+'))')
            self.device[str(devNumber)] = self.R('capture.output(dev.cur())[2]').replace(' ', '')
        try:
            self.R(query)
        except:
            self.R('dev.set('+str(self.device[str(devNumber)])+')')
            self.R('dev.off()')
            raise Exception, 'R Plotting Error'
            ## there was an exception and we need to roll back the processor.
    def require_librarys(self, librarys, repository = None):
        qApp.setOverrideCursor(Qt.WaitCursor)
        if not repository and 'CRANrepos' in redREnviron.settings.keys():
            repository = redREnviron.settings['CRANrepos']
        
        print 'Loading required librarys'
        # for i in librarys:
            # if not i in RSession.getInstalledLibraries():
                # print 'need to download'
                # QMessageBox.information(self, 'R Packages','We need to download R packages for this widget to work.',  
                # QMessageBox.Ok + QMessageBox.Default)
                # break
        # if not redREnviron.checkInternetConnection():
            # QMessageBox.information(self, 'R Packages','No active internet connection detected.  Please reconnect and try this again.',  
                # QMessageBox.Ok + QMessageBox.Default)
            # qApp.restoreOverrideCursor()
            # return False
        success = RSession.require_librarys(librarys = librarys, repository = repository)
        self.requiredRLibraries.extend(librarys)
        qApp.restoreOverrideCursor()
        return success
    def onDeleteWidget(self):
        print '|#| onDeleteWidget OWRpy'
        try:
            for device in self.device.keys():
                dev = self.device[device]
                #key = device.keys()[0]
                self.R('dev.set('+str(dev)+')', 'setRData')
                self.R('dev.off() # shut down device for widget '+ str(OWRpy.uniqueWidgetNumber), 'setRData') 
        except:
            import traceback,sys
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60        

        for k in self.Rvariables:
            #print self.Rvariables[k]
            self.R('if(exists("' + self.Rvariables[k] + '")) { rm(' + self.Rvariables[k] + ') }')

        self.customWidgetDelete()
        if self.outputs:
            for output in self.outputs:
                self.callSignalDelete(output[0])

    def customWidgetDelete(self):
        pass #holder function for other widgets

    def reloadWidget(self):
        pass
    def sendRefresh(self):
        self.signalManager.refresh()
            
    def refresh(self):
        pass # function that listens for a refresh signal.  This function should be overloaded in widgets that need to listen.


###########################################
