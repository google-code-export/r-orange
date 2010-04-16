#
# An Orange-Rpy class
# 
# Should include all the functionally need to connect Orange to R 
#

from widgetGUI import *
from widgetSignals import *
import RSession
from session import *
from PyQt4.QtGui import *

class OWRpy(widgetGUI,widgetSignals,session):   
    uniqueWidgetNumber = 0
    
    def __init__(self,parent=None, signalManager=None, 
    title="R Widget", wantGUIDialog = 0, **args):
        widgetGUI.__init__(self, parent=parent, signalManager=signalManager, title=title,wantGUIDialog=wantGUIDialog, **args)
        widgetSignals.__init__(self, parent, signalManager)
        session.__init__(self)
        
        
        OWRpy.uniqueWidgetNumber += 1
        ctime = str(time.time())
        self.variable_suffix = '_' + str(OWRpy.uniqueWidgetNumber) + '_' + ctime
        self.Rvariables = {}
        self.setRvariableNames(['title'])
        self.requiredRLibraries = []
        self.device = {}
        self.Rhistory = '<code>'
        self.packagesLoaded = 0
        
        
        

    def setRvariableNames(self,names):
        
        #names.append('loadSavedSession')
        for x in names:
            self.Rvariables[x] = x + self.variable_suffix
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

    def R(self, query, callType = 'getRData', processingNotice=False, silent = False, showException=True, wantType = None, listOfLists = True):
        qApp.setOverrideCursor(Qt.WaitCursor)
        #try:
        if processingNotice:
            self.status.setText('Processing Started...')
        histquery = query
        histquery = histquery.replace('<', '&lt;') #convert for html
        histquery = histquery.replace('>', '&gt;')
        histquery = histquery.replace("\t", "\x5ct") # convert \t to unicode \t
        self.Rhistory += histquery + '</code><br><code>'
        commandOutput = RSession.Rcommand(query = query, processingNotice = processingNotice, 
        silent = silent, showException = showException, wantType = wantType, listOfLists = listOfLists)
        
        #except: 
        #    print 'R exception occurred'
        self.processing = False
        if processingNotice:
            self.status.setText('Processing complete.')
            #self.progressBarFinished()
        if not silent:
            try:
                self.ROutput.setCursorToEnd()
                self.ROutput.append(str(query.replace('<-', '='))+'<br><br>') #Keep track automatically of what R functions were performed.
            except: pass #there must not be any ROutput to add to, that would be strange as this is in OWRpy
        qApp.restoreOverrideCursor()
        return commandOutput
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
    
    def Rplot(self, query, dwidth=8, dheight=8, devNumber = 0, mfrow = None):
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
                self.R('x11('+str(dwidth)+','+str(dheight)+') # start a new device for '+str(RSession.uniqueWidgetNumber), 'setRData') # starts a new device 
                self.device[str(devNumber)] = self.R('capture.output(dev.cur())[2]').replace(' ', '')
                print str(self.device)
        else:
            print 'make new dev for this'
            self.R('x11('+str(dwidth)+','+str(dheight)+') # start a new device for '+str(RSession.uniqueWidgetNumber), 'setRData') # starts a new device 
            if type(mfrow) == list:
                self.R('par(mfrow = c('+str(mfrow[0])+','+str(mfrow[1])+'))')
            self.device[str(devNumber)] = self.R('capture.output(dev.cur())[2]').replace(' ', '')
        self.R(query, 'setRData')
        
        

    def require_librarys(self, librarys, repository = None):
        if not repository and 'CRANrepos' in qApp.canvasDlg.settings.keys():
            repository = qApp.canvasDlg.settings['CRANrepos']
        
        print 'Loading required librarys'
        RSession.require_librarys(librarys = librarys, repository = repository)
        self.requiredRLibraries.extend(librarys)

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
                self.R('dev.off() # shut down device for widget '+ str(OWRpy.uniqueWidgetNumber), 'setRData') 
                
        except: pass
        self.customWidgetDelete()
    
    def customWidgetDelete(self):
        pass #holder function for other widgets

    def reloadWidget(self):
        pass
    def sendRefresh(self):
        self.signalManager.refresh()
            
    def refresh(self):
        pass # function that listens for a refresh signal.  This function should be overloaded in widgets that need to listen.

        
###########################################
