import os, numpy
import time
#import RvarClasses
#import RAffyClasses
import threading, sys
import orngEnviron
# import MyQMoviePlayer
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import re
from PyQt4.QtCore import *
#from OWWidget import *

if sys.platform=="win32":
    from rpy_options import set_options
    #set_options(RHOME=os.environ['RPATH'])
    set_options(RHOME=orngEnviron.directoryNames['RDir'])
else: # need this because linux doesn't need to use the RPATH
    print 'Cant find windows environ varuable RPATH, you are not using a win32 machine.'

import rpy

class RSession():
    # lock = threading.Lock()
    # rsem = threading.Semaphore(value = 1)
    # occupied = 0
    uniqueWidgetNumber = 0

    Rhistory = '<code>'
    def __init__(self):
        # rpy.__init__(self)
        RSession.uniqueWidgetNumber += 1
        ctime = str(time.time())
        self.variable_suffix = '_' + str(RSession.uniqueWidgetNumber) + '_' + ctime
        self.Rvariables = {}
        self.setRvariableNames(['title'])
        self.requiredRLibraries = []
        self.device = {}
        
        self.packagesLoaded = 0
        self.RSessionThread = RSessionThread()
        
        

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

        output = None
        if processingNotice:
            self.status.setText('Processing Started...')
        if not silent:
            print query
        histquery = query
        histquery = histquery.replace('<', '&lt;') #convert for html
        histquery = histquery.replace('>', '&gt;')
        histquery = histquery.replace("\t", "\x5ct") # convert \t to unicode \t
        self.Rhistory += histquery + '</code><br><code>'
        
        try:
            if callType == 'getRData':
                output  = self.RSessionThread.run(query)
            elif callType == 'setRData':
                self.RSessionThread.run(query)
            elif callType == 'getRSummary':
                self.RSessionThread.run('tmp<-('+query+')')
                output = self.RSessionThread.run('list(rowNames=rownames(tmp), colNames=colnames(tmp), Length=length(tmp), Class=class(tmp), Summary=summary(tmp))')
                self.RSessionThread.run('rm(tmp)')
            else:
                self.RSessionThread.run(query) # run the query anyway even if the user put un a wierd value

        except rpy.RPyRException as inst:
            qApp.restoreOverrideCursor()
            #self.progressBarFinished()
            print inst
            # print showException
            if showException:
                QMessageBox.information(self, 'Red-R Canvas','R Error: '+ str(inst),  
                QMessageBox.Ok + QMessageBox.Default)
            #self.status.setText('Error occured!!')
            raise rpy.RPyRException
            return None # now processes can catch potential errors
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
        
        if wantType == None:
            return output
        elif wantType == 'list':
            if type(output) in [str, int, float, bool]:
                return [output]
            elif type(output) in [list, numpy.ndarray] and len(output) == 1 and not listOfLists:
                output = output[0]
                return output
            else:
                return output
        elif wantType == 'dict':
            if type(output) == type(''):
                return {'output':[output]}
            elif type(output) == type([]):
                return {'output': output}
            else:
                return output
        elif wantType == 'array': # want a numpy array
            if type(output) == list:
                output = numpy.array(output)
                return output
            elif type(output) in [str, int, float, bool]:
                output = numpu.appay([output])
                return output
            elif type(output) == dict:
                newOutput = []
                for key in output.keys():
                    newOutput.append(output[key])
                return newOutput
            elif type(output) in [numpy.ndarray]:
                return output
            else:
                print type(output), 'Non normal type, please add to RSession array logic'
                return output
        else:
            return output
    
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
        
        

    def require_librarys(self,librarys, force = False):
        libPath = os.path.join(orngEnviron.directoryNames['RDir'],'library').replace('\\','/')
        
        
        #if self.packagesLoaded == 0:
        installedRPackages = self.R('as.vector(installed.packages(lib.loc="' + libPath + '")[,1])')
        # print installedRPackages
        # print type(installedRPackages)
        print self.R('getOption("repos")')
        if 'CRANrepos' not in qApp.canvasDlg.settings.keys():
            qApp.canvasDlg.settings['CRANrepos'] = 'http://cran.r-project.org'
        else:
            #print qApp.canvasDlg.settings['CRANrepos']
            self.R('local({r <- getOption("repos"); r["CRAN"] <- "' + qApp.canvasDlg.settings['CRANrepos'] + '"; options(repos=r)})')

        for library in librarys:
            if library in installedRPackages:
                self.R('require(' + library + ', lib.loc="' + libPath + '")')
                
            else:
                try:
                    self.R('setRepositories(ind=1:7)')
                    self.R('install.packages("' + library + '", lib="' + libPath + '")')
                    self.R('require(' + library + ', lib.loc="' + libPath + '")')
                    
                except:
                    print 'Library load failed. This widget will not work!!!'
        self.requiredRLibraries.extend(librarys)


class RSessionThread(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, None)
        #self.command = ''
    def run(self, query):
        #print 'asdf11 +' + query
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