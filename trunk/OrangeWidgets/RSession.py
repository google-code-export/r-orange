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
import orngEnviron
import MyQMoviePlayer
# from PyQt4 import QtWebKit
from PyQt4.QtCore import *
from OWWidget import *

#mutex = QMutex()
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
        self.RSessionThread = RSessionThread()

    def R(self, query, type = 'getRData', processing_notice=False):

        qApp.setOverrideCursor(Qt.WaitCursor)

        output = None
        if processing_notice:
            self.status.setText('Processing Started.Please wait for processing to finish.')

        print query
        histquery = query
        histquery = histquery.replace('<', '&lt;') #convert for html
        histquery = histquery.replace('>', '&gt;')
        histquery = histquery.replace("\t", "\x5ct") # convert \t to unicode \t
        self.Rhistory += histquery + '</code><br><code>'
        try:
            if type == 'getRData':
                output  = self.RSessionThread.run(query)
            elif type == 'setRData':
                self.RSessionThread.run(query)
            elif type == 'getRSummary':
                self.RSessionThread.run('tmp<-('+query+')')
                output = self.RSessionThread.run('list(rowNames=rownames(tmp), colNames=colnames(tmp), Length=length(tmp), Class=class(tmp), Summary=summary(tmp))')
                self.RSessionThread.run('rm(tmp)')
            else:
                self.RSessionThread.run(query) # run the query anyway even if the user put un a wierd value

        except rpy.RPyRException, inst:

            qApp.restoreOverrideCursor()
            self.progressBarFinished()
            print inst.message
            QMessageBox.information(self, 'Orange Canvas','R Error: '+ inst.message,  QMessageBox.Ok + QMessageBox.Default)
            #self.status.setText('Error occured!!')
            return None # now processes can catch potential errors
        self.processing = False
        if processing_notice:
            self.status.setText('Processing complete')
            #self.progressBarFinished()
        try:
            self.notes.setCursorToEnd()
            self.notes.insertHtml('<br> R Query Performed: '+str(query.replace('<-', '='))+'<br><br>') #Keep track automatically of what R functions were performed.
        except: pass #there must not be any notes to add to
        qApp.restoreOverrideCursor()
        return output
                        
    def require_librarys(self,librarys, force = False):
        import orngEnviron
        #lib = os.path.join(os.path.realpath(orngEnviron.directoryNames["canvasSettingsDir"]), "Rpackages").replace("\\", "/")
        #self.R('.libPaths("' + lib  +'")')
        success = 0
        #if self.packagesLoaded == 0:
        for library in librarys:
            if force or (library not in self.RPackages):
                try:
                    if not self.R("require(\'"+ library +"\')"):
                        #print qApp.cavasDlg.settings['CRANrepos']
                        self.R('setRepositories(ind=1:7)')
                        #self.R('chooseCRANmirror()') # change this 
                        self.R('install.packages(\'' + library + 
                        '\', repos = \''+ qApp.canvasDlg.settings['CRANrepos']+
                        '\')')
                        self.R('require(' + library + ')')
                    self.RPackages.append(library)
                    success = 1
                except rpy.RPyRException, inst:
                    print 'asdf'
                    m = re.search("'(.*)'",inst.message)
                    self.require_librarys([m.group(1)])
                    return 0
                except:
                    print 'aaa'
                    return 0
        
            #self.packagesLoaded = 1
            else:
                print 'Packages Loaded'
                return 1
        #add the librarys to a list so that they are loaded when R is loaded.
        return success
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

class RSessionThread(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, None)
        #self.command = ''
    def run(self, query):

        output = rpy.r(query)

        return output
    

# class ProcessingBoxThread(QThread):
    # def __init__(self, parent = None):
        # QThread.__init__(self, parent)
        # self.open = 1
    # def run(self, widget):
        #movie = MyQMoviePlayer.MyQMoviePlayer()
        # widget.show()
        # widget.movie.start()
        # self.waitForMe()
    # def waitForMe(self):
        # self.wait()
    # def start(self):
        # self.run()

# class RSession(RSessionExecutor):
    # def __init__(self):
        # self.RSessionThread = RSessionThread()
        # RSessionExecutor.__init__(self)
    # def R(self, command, type = 'getRData', processing_notice=False):
        # print 'Entered R Thread'
        # movie = MyQMoviePlayer.MyQMoviePlayer()
        # output = self.RSessionThread.run(command, type = type, processing_notice = processing_notice)

        # print 'Exited R Thread'
        # movie.hide()
        # return output