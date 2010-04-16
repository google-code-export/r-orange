# R Signal Thread
## Controls the execution of R funcitons into the underlying R session

import sys, os, orngEnviron, numpy

if sys.platform=="win32":
    from rpy_options import set_options
    #set_options(RHOME=os.environ['RPATH'])
    set_options(RHOME=orngEnviron.directoryNames['RDir'])
else: # need this because linux doesn't need to use the RPATH
    print 'Cant find windows environ varuable RPATH, you are not using a win32 machine.'

    
import rpy
from PyQt4.QtCore import *

def Rcommand(query, processingNotice=False, silent = False, showException=True, wantType = None, listOfLists = True):
    rst = RSessionThread()
    
    output = None
    
    if not silent:
        print query
        
    try:
        output = rst.run(query)
    except rpy.RPyRException as inst:
        print inst
        # print showException
        if showException:
            QMessageBox.information(self, 'Red-R Canvas','R Error: '+ str(inst),  
            QMessageBox.Ok + QMessageBox.Default)
        #self.status.setText('Error occured!!')
        raise rpy.RPyRException
        return None # now processes can catch potential errors
        
    
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
            output = numpy.array([output])
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

def require_librarys(librarys, repository = 'http://cran.r-project.org'):
        libPath = os.path.join(orngEnviron.directoryNames['RDir'],'library').replace('\\','/')
        installedRPackages = Rcommand('as.vector(installed.packages(lib.loc="' + libPath + '")[,1])')
        
        Rcommand('local({r <- getOption("repos"); r["CRAN"] <- "' + repository + '"; options(repos=r)})')

        for library in librarys:
            if library in installedRPackages:
                Rcommand('require(' + library + ', lib.loc="' + libPath + '")')
                
            else:
                try:
                    Rcommand('setRepositories(ind=1:7)')
                    Rcommand('install.packages("' + library + '", lib="' + libPath + '")')
                    Rcommand('require(' + library + ', lib.loc="' + libPath + '")')
                    
                except:
                    print 'Library load failed'
        
class RSessionThread(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, None)
        #self.command = ''
    def run(self, query):
        #print 'asdf11 +' + query
        output = rpy.r(query)

        return output