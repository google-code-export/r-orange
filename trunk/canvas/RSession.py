# R Signal Thread
## Controls the execution of R funcitons into the underlying R session

import sys, os, redREnviron, numpy

os.environ['R_HOME'] = os.path.join(redREnviron.directoryNames['RDir'])
    
import rpy2.robjects as rpy
from PyQt4.QtCore import *
from PyQt4.QtGui import *

mutex = QMutex()
def assign(name, object):
    try:
        rpy.r.assign(name, object)
        return True
    except:
        return False
def Rcommand(query, silent = False, wantType = None, listOfLists = False):
    
    unlocked = mutex.tryLock()
    if not unlocked:
        print 'R Session is LOCKED.  Please re-run your widget.'
        return
        
    
    output = None
    if not silent:
        print '|##| %s' % query
    #####################Forked verions of R##############################
    # try:
        # output = qApp.R.R(query)            
    # except Exception as inst:
        # print inst
        # x, y = inst
        # print showException
        #self.status.setText('Error occured!!')
        # mutex.unlock()
        # raise qApp.rpy.RPyRException(str(y))
        
        # return None # now processes can catch potential errors
    #####################Forked verions of R##############################
    try:
        
        output = rpy.r(query)
    except Exception as inst:
	
        print inst
        mutex.unlock()
        raise RuntimeError(str(inst) + '  Orriginal Query was:  ' + str(query))
        return None # now processes can catch potential errors
    print output.getrclass()
    output = convertToPy(output)
    if type(output) == list and len(output) == 1:
        output = output[0]
    print 'This is the output:', output
    # print '###########  Beginning Conversion ###############', wantType, 'listOfLists', listOfLists
    
    
    if wantType == None:
        print 'Warning!! WantType is None.  This will prevent a return in Red-R 1.90!!!'
        pass
    elif wantType == 'list':
        if type(output) is list:
            pass
        elif type(output) in [str, int, float, bool]:
            output =  [output]
        elif type(output) is dict:
            newOutput = []
            for name in output.keys():
                nl = output[name]
                newOutput.append(nl)
            output = newOutput
        elif type(output) is numpy.ndarray:
            output = output.tolist()
        else:
            print 'Warning, conversion was not of a known type;', str(type(output))
    
    elif wantType == 'dict':
        if type(output) is dict:
            pass
        elif type(output) in [str, int, float, bool]:
            output =  {'output':[output]}
        elif type(output) == type([]):
            output = {'output': output}
        elif type(output) == type({}):
            #print '#--#'+str(output)
            for key in output:
                if type(output[key]) not in [list]:  # the key does not point to a list so now we make some choices
                    if type(output[key]) in [str, int, float, bool]:
                        nd = output.copy()[key]
                        print nd, output[key]
                        output[key] = [nd]  ## forces coersion to a list
                    elif type(output[key]) in [dict]:  # it is a dict, we need to coerce this to a list, com
                        ## for some reason we are seeing dicts of returned statemtns.  This is very strange but we need to deal with it.
                        nd = []
                        for key2 in output[key].keys():
                            nd.append(output[key][key2])
                        output[key] = nd
        else:
            print 'Warning, conversion was not of a known type;', str(type(output))
    elif wantType == 'array': # want a numpy array
        if type(output) == list:
            #print 'Converting list to array'
            output = numpy.array(output)
            
        elif type(output) in [str, int, float, bool]:
            #print 'Converting single type to array'
            output = numpy.array([output])
            
        elif type(output) == dict:
            #print 'Converting Dict to Array'
            newOutput = []
            for key in output.keys():
                newOutput.append(output[key])
            output = newOutput
        elif type(output) in [numpy.ndarray]:
            #print 'Type is already array'
            pass
        else:
            print 'Warning, conversion was not of a known type;', str(type(output))
    elif wantType == 'listOfLists' or listOfLists:
        #print 'Converting to list of lists'
        
        if type(output) in [str, int, float, bool]:
            output =  [[output]]
        elif type(output) in [dict]:
            newOutput = []
            for name in output.keys():
                nl = output[name]
                if type(nl) not in [list]:
                    nl = [nl]
                newOutput.append(nl)
                
            output = newOutput
        
        elif type(output) in [list, numpy.ndarray]:
            if len(output) == 0:
                output = [output]
            elif type(output[0]) not in [list]:
                output = [output]
        else:
            print 'Warning, conversion was not of a known type;', str(type(output))
            
    else:
        pass
    mutex.unlock()
    return output
	
def convertToPy(inobject):
    print inobject.getrclass()
    try:
        newData = {}                                                                                       ## set up a new dict to place the data in, sometimes this is replaced with a vector 
        if inobject.getrclass()[0] in ['numeric', 'logical', 'integer', 'complex']:                                       ## keep the items as ints/floats if they are numeric or logical
            return [i for i in inobject]
        elif inobject.getrclass()[0] in ['factor']:                                                     ## if factor the string representation of the factor levels is returned, this is useful for printing the output when python needs to format the printing
            import rpy2.robjects as ro
            levels = ro.r.levels(inobject)
            return [levels[i-1] for i in inobject]
        elif inobject.getrclass()[0] in ['character']:                                               ## if character we put everything in as a string
            return [str(i) for i in inobject]
        elif inobject.getrclass()[0] in ['array', 'matrix']:                                          ## this one needs the most work, converting 2d matrices into arrays is rather easy, doing this in higher dimentions is more difficult, if the RArray object has more access to the underlying data and it's organization this could be improved.
            if len(inobject.dim) == 2:
                newData = []
                for i in range(inobject.dim[0]):
                    newRow = []
                    for j in range(inobject.dim[1]):
                        newRow.append(inobject[i + inobject.dim[0]*j])
                    newData.append(newRow)
                    
                return newData
            else:
                    raise Exception("Arrays of greater than two dimentions not supported.")

        elif inobject.getrclass()[0] in ['data.frame', 'list']:
            print 'Got data.frame'
            for i in range(len(inobject)):
                newData[inobject.names[i]] = convertToPy(inobject[i])
            return newData
        elif str(inobject.names) == 'NULL': ## names don't exist                            ## if we made it this far then the object could be a list or data.frame or at least something that isn't made of atomics if there are names then we want to make a dict of names, if not then make a dict of indices to work over.
            for i in range(len(inobject)):
                newData[i] = convertToPy([i])
            return newData
        else:                                                                                                     ## if all else fails then return the string representation of the object, it's likely that pure python may be able to do nothing more with the object.
            return str(inobject)
    except Exception as e:
        print str(e)
        return None
def getInstalledLibraries():
    if sys.platform=="win32":
        libPath = os.path.join(redREnviron.directoryNames['RDir'],'library').replace('\\','/')
        return Rcommand('as.vector(installed.packages(lib.loc="' + libPath + '")[,1])', wantType = 'list')
    else:
        Rcommand('.libPaths(new = "'+personalLibDir+'")')
        return Rcommand('as.vector(installed.packages()[,1])', wantType = 'list')
loadedLibraries = []
def setLibPaths(libLoc):
    Rcommand('.libPaths(\''+str(libLoc)+'\')') ## sets the libPaths argument for the directory tree that will be searched for loading and installing librarys
    
if sys.platform=="win32":
    libPath = os.path.join(os.environ['R_HOME'], 'library').replace('\\','/')
else:
    libPath = personalLibDir
setLibPaths(libPath)
def require_librarys(librarys, repository = 'http://cran.r-project.org'):
        
        # if sys.platform=="win32":
            # libPath = '\"'+os.path.join(redREnviron.directoryNames['RDir'],'library').replace('\\','/')+'\"'
        # else:
            # libPath = '\"'+personalLibDir+'\"'
        #Rcommand('Sys.chmod('+libPath+', mode = "7777")') ## set the file permissions
        loadedOK = True
        # print 'libPath', libPath
        installedRPackages = getInstalledLibraries()
        
        Rcommand('local({r <- getOption("repos"); r["CRAN"] <- "' + repository + '"; options(repos=r)})')
        if type(librarys) == str: # convert to list if it isn't already
            librarys = [librarys]
        # print 'librarys', librarys
        # print 'installedRPackages', installedRPackages
        
        for library in librarys:
            if library in loadedLibraries: 
                print 'library already loaded'
                continue
            # print 'in loop', library, library in installedRPackages
            # print installedRPackages
            if installedRPackages and library and (library in installedRPackages):
                Rcommand('require(' + library + ')') #, lib.loc=' + libPath + ')')
                loadedLibraries.append(library)
            elif library:
                if redREnviron.checkInternetConnection():
                    mb = QMessageBox("Download R Library", "You are missing some key files for this widget.\n\n"+str(library)+"\n\nWould you like to download it?", QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton,qApp.canvasDlg)
                    if mb.exec_() == QMessageBox.Ok:
                        try:
                            Rcommand('setRepositories(ind=1:7)')
                            Rcommand('install.packages("' + library + '")')#, lib=' + libPath + ')')
                            loadedOK = Rcommand('require(' + library + ',)')# lib.loc=' + libPath + ')')
                            installedRPackages = getInstalledLibraries() ## remake the installedRPackages list
                            loadedLibraries.append(library)
                        except:
                            print 'Library load failed'
                            loadedOK = False
                    else:
                        loadedOK = False
                else:
                    loadedOK = False
                        
        return loadedOK
