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
from PyQt4.QtGui import *

mutex = QMutex()
def Rcommand(query, processingNotice=False, silent = False, showException=True, wantType = None, listOfLists = True):
    
    unlocked = mutex.tryLock()
    if not unlocked:
        print 'R Session is LOCKED.  Please re-run your widget.'
        return
        
    
    output = None
    if not silent:
        print query
        
    try:
        output = rpy.r(query)
    except rpy.RPyRException as inst:
        print inst
        # print showException
        #self.status.setText('Error occured!!')
        mutex.unlock()
        raise rpy.RPyRException(str(inst))
        
        return None # now processes can catch potential errors
        
    
    if wantType == None:
        mutex.unlock()
        return output
    elif wantType == 'list':
        if type(output) in [str, int, float, bool]:
            mutex.unlock() 
            return [output]
        elif type(output) in [list, numpy.ndarray] and len(output) == 1 and not listOfLists:
            output = output[0]
            mutex.unlock()
            return output
        else:
            mutex.unlock()
            return output
    elif wantType == 'dict':
        if type(output) == type(''):
            mutex.unlock()
            return {'output':[output]}
        elif type(output) == type([]):
            mutex.unlock()
            return {'output': output}
        else:
            mutex.unlock()
            return output
    elif wantType == 'array': # want a numpy array
        if type(output) == list:
            output = numpy.array(output)
            mutex.unlock()
            return output
        elif type(output) in [str, int, float, bool]:
            output = numpy.array([output])
            mutex.unlock()
            return output
        elif type(output) == dict:
            newOutput = []
            for key in output.keys():
                newOutput.append(output[key])
            mutex.unlock()
            return newOutput
        elif type(output) in [numpy.ndarray]:
            mutex.unlock()
            return output
        else:
            print type(output), 'Non normal type, please add to RSession array logic'
            return output
    else:
        mutex.unlock()
        return output
def getInstalledLibraries():
    libPath = os.path.join(orngEnviron.directoryNames['RDir'],'library').replace('\\','/')
    return Rcommand('as.vector(installed.packages(lib.loc="' + libPath + '")[,1])')
def require_librarys(librarys, repository = 'http://cran.r-project.org'):
        libPath = os.path.join(orngEnviron.directoryNames['RDir'],'library').replace('\\','/')
        installedRPackages = getInstalledLibraries()
        
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

