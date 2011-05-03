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


import sys, os, redREnviron, numpy, redR


####### system specific import of rpy in it's various flavors ##########
## if mac ##
if sys.platform == 'darwin':
    os.environ['R_HOME'] = os.path.join(redREnviron.directoryNames['RDir'])
    os.environ['R_HOME_DIR'] = os.path.join(redREnviron.directoryNames['RDir'])
    os.environ['R_ARCH'] = 'i386'
    os.environ['R_INCLUDE_DIR'] = os.path.join(redREnviron.directoryNames['RDir'],'include')
    os.environ['R_SHARE_DIR'] = os.path.join(redREnviron.directoryNames['RDir'],'share')
    os.environ['R_DOC_DIR'] = os.path.join(redREnviron.directoryNames['RDir'],'doc')
    os.environ['R_LD_LIBRARY_PATH'] = os.path.join(redREnviron.directoryNames['RDir'],'lib','i386')
    os.environ['DYLD_LIBRARY_PATH'] = os.path.join(redREnviron.directoryNames['RDir'],'lib','i386')    
    os.environ['JAVA_HOME'] = '/System/Library/Frameworks/JavaVM.framework/Versions/1.5.0/Home'
    import rpy3.robjects as rpy

## if windows ##
elif sys.platform == 'win32':
    os.environ['R_HOME'] = os.path.join(redREnviron.directoryNames['RDir'])
    import rpy3.robjects as rpy
## if linux ##
elif sys.platform == 'linux2':
    print 'loading rpy3'
    import rpy3.robjects as rpy
## if we don't know ##
else:
    import rpy2.robjects as rpy
    
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#print 'importing conversion'
import redrrpy._conversion as co
#print 'done importing conversion'
import redRLog
#print 'Rsession loaded'
# import redRi18n
def _(a):
    return a

mutex = QMutex()


def assign(name, object):
    try:
        rpy.r.assign(name, object)
        redRLog.log(redRLog.R, redRLog.DEBUG, _('Assigned object to %s') % name)
        return True
    except:
        redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
        return False
def Rcommand(query, silent = False, wantType = redR.CONVERT, listOfLists = False):
    if wantType == 'convert':
        wantType = redR.CONVERT
    elif wantType == 'NoConversion':
        wantType = redR.NOCONVERSION
    elif wantType == 'listOfLists':
        wantType = redR.LISTOFLISTS
    elif wantType == 'dict':
        wantType = redR.DICT
    elif wantType == 'list':
        wantType = redR.LIST
    unlocked = mutex.tryLock()
    if not unlocked:
        mb = QMessageBox(_("R Session Locked"), _("The R Session is currently locked, please wait for the prior execution to finish."), QMessageBox.Information, 
        QMessageBox.Ok | QMessageBox.Default,
        QMessageBox.NoButton, 
        QMessageBox.NoButton, 
        qApp.canvasDlg)
        mb.exec_()
        return
        
    
    output = None
    if not silent:
        redRLog.log(redRLog.R, redRLog.DEBUG, redRLog.getSafeString(query))
    #####################Forked verions of R##############################
    # try:
        # output = qApp.R.R(query)            
    # except Exception as inst:
        # print inst
        # x, y = inst
        # print showException
        #self.status.setText('Error occured!!')
        # mutex.unlock()
        # raise qApp.rpy.RPyRException(unicode(y))
        
        # return None # now processes can catch potential errors
    #####################Forked verions of R##############################
    try:
        output = rpy.r(unicode(query).encode('Latin-1'))
        
    except Exception as inst:
        redRLog.log(redRLog.R, redRLog.DEBUG, "<br>##################################<br>Error occured in the R session.<br>%s<br>The original query:<br> <b>%s</b><br>##################################<br>" % (inst,redRLog.getSafeString(query)))
        mutex.unlock()
        raise RuntimeError(unicode(inst) + '  Original Query was:  ' + unicode(query))
        return None # now processes can catch potential errors
    if wantType == redR.NOCONVERSION: 
        mutex.unlock()
        return output
    # elif wantType == 'list':
        # co.setWantType(1)
    # elif wantType == 'dict':
        # co.setWantType(2)
    # print output.getrclass()
    
    output = convertToPy(output)
    # print 'converted', type(output)
    if wantType == None:
        mutex.unlock()
        raise Exception(_('WantType not specified'))
    
    elif wantType == redR.LIST:
        #print 'converting %s to list' % output
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
            print _('Warning, conversion was not of a known type;'), unicode(type(output))
    elif wantType == redR.LISTOFLISTS:
        # print _('Converting to list of lists')
        
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
            print _('Warning, conversion was not of a known type;'), str(type(output))
                
    mutex.unlock()
    return output

def convertToPy(inobject):
    try:
        if sys.platform =='win32':
         rclass = inobject.getrclass()[0]
        elif sys.platform =='darwin':
         rclass=inobject.rclass[0]
        elif sys.platform == 'linux2':
         rclass=inobject.rclass[0] 
        else:
         rclass=inobject.rclass[0] 
        if rclass not in ['data.frame', 'matrix', 'list', 'array', 'numeric', 'vector', 'complex', 'boolean', 'bool', 'factor', 'logical', 'character', 'integer']:
            print 'can not convert %s yet' % rclass
            return inobject
        return co.convert(inobject)
    except Exception as e:
        redRLog.log(redRLog.REDRCORE, redRLog.ERROR, unicode(e))
        return None

def getInstalledLibraries():
   setLibPaths(redREnviron.directoryNames['RlibPath'])
   return Rcommand('as.vector(installed.packages(lib.loc="' + redREnviron.directoryNames['RlibPath'] + '")[,1])', wantType = 'list')
loadedLibraries = []

def setLibPaths(libLoc):
    ## sets the libPaths argument for the directory tree that will be searched for loading and installing librarys
    Rcommand('.libPaths(\''+unicode(libLoc)+'\')', wantType = 'NoConversion') 
    print 'library location is ', libLoc
def require_librarys(librarys, repository = 'http://cran.r-project.org'):
        
        loadedOK = True
        installedRPackages = getInstalledLibraries()
        Rcommand('local({r <- getOption("repos"); r["CRAN"] <- "' + repository + '"; options(repos=r)})')
        if type(librarys) == str: # convert to list if it isn't already
            librarys = [librarys]
        
        if len(newLibs) > 0:
            if not install_libraries(librarys):
                return False
        installedRPackages = getInstalledLibraries() ## remake the installedRPackages list
        for library in [l for l in librarys if l not in loadedLibraries]:
            if installedRPackages and library and (library in installedRPackages):
                redRLog.log(redRLog.R, redRLog.DEBUG, 'Loading library %s.' % library)
                Rcommand('require(' + library + ')') #, lib.loc=' + libPath + ')')
                
                loadedLibraries.append(library)
                loadedOK = True
            else:
                loadedOK = False
        return loadedOK

def install_libraries(librarys):
    installedRPackages = getInstalledLibraries()
    newLibs = [l for l in librarys if l not in installedRPackages]
    if redREnviron.checkInternetConnection():
        mb = QMessageBox(_("Download R Library"), _("You are missing some key files for this widget.\n\n%s\n\nWould you like to download it(them)?"
        ) % unicode(','.join(newLibs)), 
        QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton,qApp.canvasDlg)
        if mb.exec_() == QMessageBox.Ok:
            try:
                redRLog.log(redRLog.R, redRLog.INFO, _('Installing library(s) %s.') % ','.join(newLibs))
                Rcommand('setRepositories(ind=1:7)', wantType = 'NoConversion')
                Rcommand('install.packages(c(%s))' % ','.join(['"%s"' % l for l in newLibs]), wantType = 'NoConversion')
            except:
                redRLog.log(redRLog.REDRCORE, redRLog.CRITICAL,_('Library load failed') +"<br>"+ redRLog.formatException()) 
                return False
        return True
    else:
        return False
                        
                    