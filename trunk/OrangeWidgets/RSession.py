import os
try:
    from rpy_options import set_options
    set_options(RHOME=os.environ['RPATH'])
except: pass # need this because linux doesn't need to use the RPATH
import rpy
import time
import RvarClasses
import RAffyClasses
import threading, sys
# from PyQt4 import QtWebKit
from OWWidget import *


class RSession():
    # lock = threading.Lock()
    # rsem = threading.Semaphore(value = 1)
    # occupied = 0
    Rhistory = '<code>'
    def __init__(self):
        # rpy.__init__(self)
        self.device = {}
        self.RPackages = []
        #self.loadSavedSession = False
        #self.loadingSavedSession = False
        #print 'set load ssaved '
        #self.settingsList = ['variable_suffix','loadingSavedSession']
        self.packagesLoaded = 0


                
    def R(self, query, type = 'getRData', processing_notice=False):
        #RThread().start()
        # rthread = RThread()
        # rthread.start()
        
        
        qApp.setOverrideCursor(Qt.WaitCursor)
        
        # RSession.rsem.acquire()
        # RSession.occupied = 1
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
        RSession.Rhistory += histquery + '</code><br><code>'
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
            # RSession.occupied = 0
            # RSession.lock.release()
            # RSession.rsem.release()
            qApp.restoreOverrideCursor()
            self.progressBarFinished()
            print inst.message
            QMessageBox.information(self, 'Orange Canvas','R Error: '+ inst.message,  QMessageBox.Ok + QMessageBox.Default)
            self.processingBox.setHtml('<center>Error occured during processing please check data or <a href="http://red-r.org/">contact the developers.</a></center>')

        RSession.processing = False
        if processing_notice:
            self.processingBox.setHtml('<center>Processing complete</center>')
            #self.progressBarFinished()
        
        #rthread.threadBreaking = True
        
        # RSession.occupied = 0
        # RSession.rsem.release()
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

