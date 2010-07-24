# R Signal Thread
## Controls the execution of R funcitons into the underlying R session

import sys, os, redREnviron, numpy
if sys.platform=="win32":
    from rpy_options import set_options
    #set_options(RHOME=os.environ['RPATH'])
    set_options(RHOME=redREnviron.directoryNames['RDir'])
    set_options(VERBOSE=False)
else: # need this because linux doesn't need to use the RPATH
    personalLibDir = os.path.join(redREnviron.directoryNames['settingsDir'], 'RLibraries')
    if not os.path.isdir(personalLibDir):
        os.makedirs(personalLibDir)
    print 'Cant find windows environ varuable RPATH, you are not using a win32 machine.'

    
    
import rpy2.robjects as rpy
import rpy2.conversion2rpy as conversion2rpy
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
        raise Exception(str(inst))
        return None # now processes can catch potential errors
        
    if not wantType == 'rpy2':
        print output.rclass[0]
        if output.rclass[0] in ['data.frame']:
            output = conversion2rpy.rdf2dict(output)
        elif output.rclass[0] in ['factor', 'vector', 'character', 'numeric', 'logical']:
            output = conversion2rpy.rvec2list(output)
        elif output.rclass[0] in ['matrix']:
            output = conversion2rpy.rmat2array(output)
        print '###########  Beginning Conversion ###############', wantType, 'listOfLists', listOfLists
        print '###########  Output #############\n', output, '\n#############\n'
        if wantType == None:
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
                for key in output:
                    if type(output[key]) not in [list]:  # the key does not point to a list so now we make some choices
                        if type(output[key]) in [str, int, float, bool]:
                            nd = output.copy()[key]
                            print nd, output[key]
                            output[key] = [nd]  ## forces coersion to a list
                        elif type(output[key]) in [dict]:  # it is a dict, we need to coerce this to a list, com
                            #for some reason we are seeing dicts of returned statemtns.  This is very strange but we need to deal with it.
                            nd = []
                            for key2 in output[key].keys():
                                nd.append(output[key][key2])
                            output[key] = nd
            else:
                print 'Warning, conversion was not of a known type;', str(type(output))
        elif wantType == 'array': # want a numpy array
            if type(output) == list:
                print 'Converting list to array'
                output = numpy.array(output)
                
            elif type(output) in [str, int, float, bool]:
                print 'Converting single type to array'
                output = numpy.array([output])
                
            elif type(output) == dict:
                print 'Converting Dict to Array'
                newOutput = []
                for key in output.keys():
                    newOutput.append(output[key])
                output = newOutput
            elif type(output) in [numpy.ndarray]:
                print 'Type is already array'
                pass
            else:
                print 'Warning, conversion was not of a known type;', str(type(output))
        elif wantType == 'listOfLists' or listOfLists:
            print 'Converting to list of lists'
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
            elif type(output) in [list, numpy.ndarray] and type(output[0]) not in [list]:
                output = [output]
            else:
                print 'Warning, conversion was not of a known type;', str(type(output))
                
        else:
            pass
    mutex.unlock()
    return output
def getInstalledLibraries():
    if sys.platform=="win32":
        libPath = os.path.join(redREnviron.directoryNames['RDir'],'library').replace('\\','/')
        return Rcommand('as.vector(installed.packages()[,1])') #lib.loc="' + libPath + '")[,1])', wantType = 'list')
    else:
        Rcommand('.libPaths(new = "'+personalLibDir+'")')
        return Rcommand('as.vector(installed.packages()[,1])', wantType = 'list')
def require_librarys(librarys, repository = 'http://cran.r-project.org'):
        
        if sys.platform=="win32":
            libPath = '\"'+os.path.join(redREnviron.directoryNames['RDir'],'library').replace('\\','/')+'\"'
        else:
            libPath = '\"'+personalLibDir+'\"'
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
            # print 'in loop', library, library in installedRPackages
            # print installedRPackages
            if installedRPackages and library and (library in installedRPackages):
                Rcommand('require(' + library + ')')#, lib.loc=' + libPath + ')')
            elif library:
                if redREnviron.checkInternetConnection():
                    mb = QMessageBox("Download R Library", "You are missing some key files for this widget.\n\n"+str(library)+"\n\nWould you like to download it?", QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton,qApp.canvasDlg)
                    if mb.exec_() == QMessageBox.Ok:
                        try:
                            Rcommand('setRepositories(ind=1:7)')
                            Rcommand('install.packages("' + library + '")')#, lib=' + libPath + ')')
                            loadedOK = Rcommand('require(' + library + ')')#, lib.loc=' + libPath + ')')
                            installedRPackages = getInstalledLibraries() ## remake the installedRPackages list
                        except:
                            print 'Library load failed'
                            loadedOK = False
                    else:
                        loadedOK = False
                else:
                    loadedOK = False
                        
        return loadedOK
