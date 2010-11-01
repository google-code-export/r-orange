################################################################
## Red-R is a visual programming interface for R designed to bring 
## the power of the R statistical environment to a broader audience.
## Copyright (C) 2010  name of Red-R Development
## 
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
################################################################

# R Signal Thread
## Controls the execution of R funcitons into the underlying R session

import sys, os, redREnviron, numpy

os.environ['R_HOME'] = os.path.join(redREnviron.directoryNames['RDir'])
    
import rpy3.robjects as rpy
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import canvas.redrrpy._conversion as co
import log

mutex = QMutex()
def assign(name, object):
    try:
        rpy.r.assign(name, object)
        log.log(2, 5, 3, 'Assigned object to %s' % name)
        return True
    except:
        return False
def Rcommand(query, silent = False, wantType = None, listOfLists = False):
    
    unlocked = mutex.tryLock()
    if not unlocked:
        mb = QMessageBox("R Session Locked", "The R Session is currently locked, please wait for the prior execution to finish.", QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default,qApp.canvasDlg)
        mb.exec_()
        return
        
    
    output = None
    if not silent:
        log.log(2, 2, 3, query)
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
        log.log(2, 8, 1, "Error occured in the R session.\nThe orriginal query was %s.\nThe error is %s." % (query, inst))
        mutex.unlock()
        raise RuntimeError(str(inst) + '  Orriginal Query was:  ' + str(query))
        return None # now processes can catch potential errors
    if wantType == 'NoConversion': 
        mutex.unlock()
        return output
    elif wantType == 'list':
        co.setWantType(1)
    elif wantType == 'dict':
        co.setWantType(2)
    ##print output.getrclass()
    output = convertToPy(output)
    if type(output) == list and len(output) == 1:
        output = output[0]
    ##print 'This is the output:', output
    # print '###########  Beginning Conversion ###############', wantType, 'listOfLists', listOfLists
    
    
    if wantType == None:
        raise Exception, 'WantType not specified'
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
    # elif wantType == 'array': # want a numpy array
        # if type(output) == list:
            ##print 'Converting list to array'
            # output = numpy.array(output)
            
        # elif type(output) in [str, int, float, bool]:
            ##print 'Converting single type to array'
            # output = numpy.array([output])
            
        # elif type(output) == dict:
            ##print 'Converting Dict to Array'
            # newOutput = []
            # for key in output.keys():
                # newOutput.append(output[key])
            # output = newOutput
        # elif type(output) in [numpy.ndarray]:
            ##print 'Type is already array'
            # pass
        # else:
            # print 'Warning, conversion was not of a known type;', str(type(output))
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
    print 'in convertToPy', inobject.getrclass()
    # if inobject.getrclass()[0] in ['data.frame','matrix']:
        # print 'return the r object'
        # return inobject
        
    try:
        if inobject.getrclass()[0] not in ['data.frame', 'matrix', 'list', 'array', 'numeric', 'vector', 'complex', 'boolean', 'bool', 'factor', 'logical', 'character', 'integer']:
            return inobject
        return co.convert(inobject)
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
    Rcommand('.libPaths(\''+str(libLoc)+'\')', wantType = 'NoConversion') ## sets the libPaths argument for the directory tree that will be searched for loading and installing librarys
    
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
                log.log(2, 1, 2, 'Library already loaded')
                continue
            # print 'in loop', library, library in installedRPackages
            # print installedRPackages
            if installedRPackages and library and (library in installedRPackages):
                log.log(2, 7, 3, 'Loading library %s.' % library)
                Rcommand('require(' + library + ')') #, lib.loc=' + libPath + ')')
                
                loadedLibraries.append(library)
            elif library:
                if redREnviron.checkInternetConnection():
                    mb = QMessageBox("Download R Library", "You are missing some key files for this widget.\n\n"+str(library)+"\n\nWould you like to download it?", QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton,qApp.canvasDlg)
                    if mb.exec_() == QMessageBox.Ok:
                        try:
                            log.log(2, 8, 3, 'Installing library %s.' % library)
                            Rcommand('setRepositories(ind=1:7)', wantType = 'NoConversion')
                            Rcommand('install.packages("' + library + '")', wantType = 'NoConversion')#, lib=' + libPath + ')')
                            loadedOK = Rcommand('require(' + library + ')', wantType = 'NoConversion')# lib.loc=' + libPath + ')')
                            installedRPackages = getInstalledLibraries() ## remake the installedRPackages list
                            
                        except:
                            log.log(2, 9, 1, 'Library load failed')
                            loadedOK = False
                    else:
                        loadedOK = False
                else:
                    loadedOK = False
                if loadedOK:
                    loadedLibraries.append(library)
                        
        return loadedOK
