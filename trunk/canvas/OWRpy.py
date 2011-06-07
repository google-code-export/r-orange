"""OWRpy

General Documentation

OWRpy is the base class for all Red-R widgets.  All widgets in the Red-R Framework must inherit from this class.
OWRpy provides, by default, an importation of many of the standard base classes as indicated in the following...

"""

from redRWidgetGUI import *
from widgetSignals import *
from widgetSession import *
from PyQt4.QtGui import *
import RSession, redREnviron, os, redRReports,redRLog, redR, globalData
import redRi18n
uniqueWidgetNumber = 0
_ = redRi18n.Coreget_()
class OWRpy(widgetSignals,redRWidgetGUI,widgetSession):   
    """This is the base class.
    
    The class is a meta class of :mod:`widgetSignals`, :mod:`redRWidgetGUI`, and :mod:`widgetSession`
    """
    globalRHistory = []
    def __init__(self,wantGUIDialog = 0, **kwargs):
        """Initialization of the class.
        
        This sets the unique widget number as well as the "Don't save list", a list of variables that will not be saved for the widget, this significantly reduces the time to load and save a schema.
        """
        global uniqueWidgetNumber
        widgetSignals.__init__(self, None, None)
        self.dontSaveList = self.__dict__.keys()
        #print self.dontSaveList

        redRWidgetGUI.__init__(self, parent=None, signalManager=None, title=None, wantGUIDialog=wantGUIDialog)
        self.dontSaveList = self.__dict__.keys()
        for x in ['status','notes','ROutput','widgetState']: self.dontSaveList.remove(x)
        
        widgetSession.__init__(self,self.dontSaveList)
        
        self.saveSettingsList = []  # a list of lists or strings that we will save.
        #uniqueWidgetNumber += 1
        #ctime = unicode(time.time())
        self.sessionID = 0  # a unique ID for the session.  This is not saved or reset when the widget is loaded.  Rather this added when the widget is loaded.  This allows for multiple widgets to use the same 
        if 'id' in kwargs:
            self.widgetID = kwargs['id']
        else:
            self.widgetID = unicode(uniqueWidgetNumber) + '_' + ctime
        self.variable_suffix = '_' + self.widgetID
        if 'Rvariables' in kwargs:
            self.Rvariables = kwargs['Rvariables']
        else:
            self.Rvariables = {}
        self.RvariablesNames = []
        self.setRvariableNames(['title'])
        self.requiredRLibraries = []
        self.device = {}
        self.packagesLoaded = 0
        self.widgetRHistory = []
        self.reportOrder = None
        self.tempID = None
        
    def log(self, comment, level = redRLog.DEVEL):
        """Class implemnetation of logging
        
        Passes parameters to the :mod:`redRLog` module.
        """
        redRLog.log(redRLog.REDRWIDGET,level,comment,widget=self.widgetID)
        
    def resetRvariableNames(self, id = None):
        """Sets the self.Rvariables dict with a unique string for each variable desired.
        
        This should be considered a private function to core but there may be the extreme case where it would be useful.  One major problem with calling this function after setting a new widgetID (using self.widgetID = float) would be that variables that are already declared would be lost to Red-R and would be a waste of memory.
        """
        if id:
            self.widgetID = id
            self.variable_suffix = '_' + self.widgetID
        for x in self.RvariablesNames:
            self.Rvariables[x] = x + self.variable_suffix
            
        self.resetRVariableNameEdits()
        
    def setRvariableNames(self,names):
        """Sets the self.Rvariables dict with a unicode string for each variable, this is called in __init__.
        
        """
        #names.append('loadSavedSession')
        for x in names:
            self.Rvariables[x] = x + self.variable_suffix
            self.RvariablesNames.append(x)
            
        self.resetRVariableNameEdits()
        
    def makeCM(self, Variable):
        self.R(Variable+'<-list()', wantType = 'NoConversion')
    def addToCM(self, colname = 'tmepColname', CM = None, values = None):
        if CM == None: return
        if values == None: return
        if type(values) == type([]):
            values = 'c('+','.join(values)+')'
        self.R(CM+'$'+colname+self.variable_suffix+'<-'+values, wantType = 'NoConversion') # commit to R

    def R(self, query, callType = 'getRData', processingNotice=False, silent = False, showException=True, wantType = 'convert', listOfLists = True):
        """Connection to the R session for widgets.  
        
        This function passes most arguments to :mod:`RSession` as Rcommand.  callType is currently depricated. processingNotice sets the widget status to processing.  silent indicates that the function call should be run in silent mode, silent calls will not be appended to the log or the history, silent should only be set when checking the value of an R object while assignment should not be slient.  Note that if silent is True, exceptions will not be raised should they occur and None will be returned silently.  showException indicates if a popup dialog should be shown when an exception occurs.
        """
        
        self.setRIndicator(True)
        #try:
        if processingNotice:
            self.status.setStatus(4)
            
        qApp.setOverrideCursor(Qt.WaitCursor)
        try:
            commandOutput = RSession.Rcommand(query = query, silent = silent, wantType = wantType, listOfLists = listOfLists)
        except RuntimeError as inst:
            qApp.restoreOverrideCursor()
            self.setRIndicator(False)
            if silent: return None
            if showException:
                QMessageBox.information(self, _('Red-R Canvas'),_('R Error: ')+ unicode(inst),  
                QMessageBox.Ok + QMessageBox.Default)
            
            raise RuntimeError(unicode(inst))
            return None # now processes can catch potential errors
        
        #except: 
        #    print _('R exception occurred')
        self.processing = False
        if processingNotice:
            self.status.setStatus(5)
            

            #self.progressBarFinished()
        if not silent:
            OWRpy.globalRHistory.append(query)
            self.widgetRHistory.append(query)
            
            self.ROutput.setCursorToEnd()
            self.ROutput.append('> '+ query) #Keep track automatically of what R functions were performed.
    
        qApp.restoreOverrideCursor()
        self.setRIndicator(False)
        return commandOutput
   
    def assignR(self, name, object):
        assignOK = RSession.assign(name, object)
        if not assignOK:
            QMessageBox.information(self, _('Red-R Canvas'),_('Object was not assigned correctly in R, please tell package manager.'),  
            QMessageBox.Ok + QMessageBox.Default)
            raise Exception, _('Object was not assigned correctly in R, please tell package manager.')
        else:
            histquery = _('Assign ')+unicode(name)+_(' to ')+unicode(object)
            OWRpy.globalRHistory.append(histquery)
            self.widgetRHistory.append(histquery)

            self.ROutput.setCursorToEnd()
            self.ROutput.append('> '+ histquery)

    def getReportText2(self, fileDir):
        ## move through all of the qtWidgets in self and show their report outputs, should be implimented by each widget.
        children = self.controlArea.children()
        #print children
        import re
        text = ''
        for i in children:
            try:
                #print i.__class__.__name__
                if isinstance(i, QBoxLayout):
                    c = i.children()
                    for c1 in c:
                        text += c1.getReportText(fileDir)
                elif re.search('PyQt4|OWGUIEx|OWToolbars',unicode(type(i))) or i.__class__.__name__ in redRGUI.qtWidgets:
                    ## we can try to get the settings of this.
                    text += i.getReportText(fileDir)
                    #print i.__class__.__name__
            except Exception as inst:
                redRLog.log(redRLog.REDRCORE, redRLog.ERROR, inst)
                continue
        return text
    def getReportText3(self, fileDir):
        ## move through all of the qtWidgets in self and show their report outputs, 
        ## should be implimented by each widget.
        from redRGUI import qtWidgetBox
        children = self.controlArea.children() + self.bottomAreaRight.children() + self.bottomAreaCenter.children() + self.bottomAreaLeft.children()
        # print 'OWRpy= ',children
        #import re
        reportData = {}
        for i in children:
            if isinstance(i, qtWidgetBox):
                d = i.getReportText(fileDir)
                if type(d) is dict:
                    reportData.update(d)
                # dd = []
                # if type(d) is list:
                    # for x in d:
                        # x['includeInReports'] = i.includeInReports
                        # dd.append(x)
                    # reportData = reportData + dd
                # elif d:
                    # d['includeInReports'] = i.includeInReports
                    # reportData.append(d)
        
        return reportData

        # arrayOfArray = []
        # for d in reportData:
            # if type(d) is dict:
                # arrayOfArray.append([d['label'], d['text']])
            # elif type(d) is list:
                # for x in d:
                    # arrayOfArray.append([x['label'], x['text']])
                    
        # import pprint
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(arrayOfArray)
        # text = redRReports.createTable(arrayOfArray,columnNames = [_('Parameter'),_('Value')],
        # tableName=_('Parameters'))
        # return text        

    def require_librarys(self, librarys, repository = None):
        """Load R libraries using the :mod:`RSession` require_librarys function.
        
        Takes a list of strings as R libraries to load.  These should be valid R packages or an error will occur.  repository is an optional argument to specity a custom repository if the library is not in a standard location.
        """
        qApp.setOverrideCursor(Qt.WaitCursor)
        if not repository and 'CRANrepos' in redREnviron.settings.keys():
            repository = redREnviron.settings['CRANrepos']
        
        #print _('Loading required librarys')
        success = RSession.require_librarys(librarys = librarys, repository = repository)
        self.requiredRLibraries.extend(librarys)
        qApp.restoreOverrideCursor()
        return success
    def onDeleteWidget(self):
        """Called when widget is deleted.
        
        This should be called by Red-R Core only.
        """
        for k in self.Rvariables:
            #print self.Rvariables[k]
            self.R('if(exists("%(NAME)s")) { rm(%(NAME)s) }' % {'NAME':self.Rvariables[k]}, wantType = 'NoConversion')
        # send none through the signals
        globalData.removeGlobalData(self)
        self.outputs.propogateNone(ask = False)
        self.outputs.clearAll()
        self.customWidgetDelete()
        
    def customWidgetDelete(self):
        """Called by onDeleteWidget and can run arbitrary code to handle the deletion of a widget.
        
        Should be reimplemented in child classes if desired.
        """
        pass #holder function for other widgets

    def reloadWidget(self):
        """Called on widget reload.
        
        Should be reimplemented in child classes if desired.
        """
        pass
    def sendRefresh(self):
        """Indicates that all widgets should run their refresh functions.
        """
        for i in redRObjects.instances():
            i.refresh()
            
    def refresh(self):
        """Called by the sendRefresh command.
        
        Should be reimplemented in child classes if desired.
        """
        pass # function that listens for a refresh signal.  This function should be overloaded in widgets that need to listen.


###########################################
