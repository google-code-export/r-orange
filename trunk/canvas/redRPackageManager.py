## package manager class redRPackageManager.  Contains a dlg for the package manager which reads xml from the red-r.org website and compares it with a local package system on the computer

import os, sys, redREnviron, urllib
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import xml.dom.minidom
import redRGUI


## packageManager class handles package functions such as resolving rrp's resolving dependencies, appending packages to the package xml or any function that remotely has to do with handling packages
class packageManager:
    def __init__(self):
        self.urlOpener = urllib.FancyURLopener()
    def loadRRP(self, filename = None, fileText = None, force = False):  # loads either the rrp files or the xml text for resolving dependencies
        try:
            if filename == None and fileText == None:
                raise Exception, 'Must specify either a fileName or fileText'
            if filename != None and fileText != None:
                raise Exception, 'Only one of fileName or fileText can be specified'
                
            
            print 'Loading RRP file.  This will update your system.'
            
                
            if filename: ## if we specify an rrp zipfile then we should load that into the temp directory and work with it.
                #try:
                tempDir = redREnviron.directoryNames['tempDir']
                installDir = os.path.join(os.path.abspath(tempDir), str(os.path.split(filename)[1].split('.')[0]))
                print installDir
                os.mkdir(installDir) ## make the directory to store the zipfile into
                ## here we need to unzip the zip file and place it into the tempDir
                import re
                zfile = zipfile.ZipFile(str(filename), "r" )
                zfile.extractall(installDir)
                zfile.close()
                tempPackageName = os.path.split(filename)[1].split('-')[0]  ## this should be the package name
                if os.path.isfile(os.path.join(str(installDir), tempPackageName+'.xml')):
                    f = open(os.path.join(str(installDir), tempPackageName+'.xml'), 'r') # read in the special file for the rrp_structure
                elif os.path.isfile(os.path.join(str(installDir), 'rrp_structure.xml')):
                    f = open(os.path.join(str(installDir), 'rrp_structure.xml'), 'r')
                else:
                    print 'No structure file, aborting insallation!!!'
                    return False
                mainTabs = xml.dom.minidom.parse(f)
                f.close() 
                # except: 
                    # print 'Can\'t open the file or something is wrong'
                    # return False
                    
                ## check the version number before we do anything else, who knows what version the usef downloaded????
                version = self.getXMLText(mainTabs.getElementsByTagName('Version')[0].childNodes)
                if self.version not in version:
                    print 'Warning, this widget does not work with your current version.  Please update!!'
                    return False
                    
                ## resolve the package dependencies first
                ## set the repository for downloading the package if it is needed.
                try:
                    repository = self.getXMLText(mainTabs.getElementsByTagName('Repository')[0].childNodes)
                except:
                    repository = 'http://www.red-r.org/Libraries/'
                    
                ## attach the version number to the repository
                repository += str(self.version)
                ### resolve the dependencies
                dependencies = self.getXMLText(mainTabs.getElementsByTagName('Dependencies')[0].childNodes)
                if dependencies != 'None':
                    alldeps = dependencies.split(',')
                    print '|##| Dependencies are:'+str(alldeps)
                    if not self.resolveRRPDependencies(alldeps, repository):
                        print 'Error occured during resolution of dependencies.'
                        QMessageBox.information(None, "Dependencies Failed", "Error occured during resolution of dependencies.\nWe will continue loading the file, but you may have problems with the widgets.\nPlease try to reload this package later to fix the dependencies.", QMessageBox.Ok)

                # run the install file if there is one, this should take care of the dependencies that are non-R related and install the needed files for the package
                
                if os.path.isfile(os.path.join(str(installDir), 'installFile.py')):
                    ## need to import and execute the run statement of the installFile.  installFile may import many other modules at it's discression.
                    print 'Executing file'
                    passed = True
                    execfile(os.path.join(str(installDir), 'installFile.py'))
                    if passed == False: # there was an error in loading.  We should stop the installation, clear the tempdirectory of the failed zipfile and return
                        QMessageBox.information(None, "Installation Failed", "Error occured during resolution of dependencies.\nWe will continue loading the file, but you may have problems with the widgets.\nPlease try to reload this package later to fix the dependencies.", QMessageBox.Ok)
                        
                ## now move all of the files in the tempDir into the libraries dir of Red-R
                packageName = self.getXMLText(mainTabs.getElementsByTagName('PackageName')[0].childNodes).split('/')[0] # get the base package name, this is the base folder of the package.
                import shutil
                shutil.copytree(os.path.abspath(installDir), os.path.join(redREnviron.directoryNames['libraryDir'], packageName))
                shutil.rmtree(installDir, True)
                ## we copied everything now return
                print 'Installation successful'
                qApp.canvasDlg.reloadWidgets()
                return True
            elif fileText:
                mainTabs = xml.dom.minidom.parseString(fileText)
            
                # check the version number to make sure that it is compatible
                version = self.getXMLText(mainTabs.getElementsByTagName('Version')[0].childNodes)
                if self.version not in version:
                    print 'Warning, this widget does not work with your current version.  Please update!!'
                    return False
                
                    
                packageName = self.getXMLText(mainTabs.getElementsByTagName('PackageName')[0].childNodes)
                
                ## set the repository for downloading the package if it is needed.
                try:
                    repository = self.getXMLText(mainTabs.getElementsByTagName('Repository')[0].childNodes)
                except:
                    repository = 'http://www.red-r.org/Libraries/'
                    
                ## attach the version number to the repository
                repository += str(self.version)
                ### resolve the dependencies
                dependencies = self.getXMLText(mainTabs.getElementsByTagName('Dependencies')[0].childNodes)
                if dependencies != 'None':
                    alldeps = dependencies.split(',')
                    alldeps.append(packageName)
                else:
                    alldeps = [packageName]
                if not self.resolveRRPDependencies(alldeps, repository):
                    print 'Error occured during resolution of dependencies.'
                    QMessageBox.information(self, "Dependencies Failed", "Error occured during resolution of dependencies.\nWe will continue loading the file, but you may have problems with the widgets.\nPlease try to reload this package later to fix the dependencies.", QMessageBox.Ok)

                print 'Package loaded successfully'
                qApp.canvasDlg.reloadWidgets()
        except:
            print 'Error occured during rrp loading.  Please try again later.'
            return False
    def resolveRRPDependencies(self, alldeps, repository):
        loadedOk = 1
        if not redREnviron.checkInternetConnection():
            return False
        mb = QMessageBox("Download Packages", "You are missing some key packages.\n\n"+'\n'.join(alldeps)+"\nDo you want to download them?\nIf you click NO your packages WON\'T WORK!!!", QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton)
        if mb.exec_() == QMessageBox.Ok:
            for dep in alldeps:
                try:
                    [pack, ver] = dep.split('/')
                    ## check to see if the directory exists, if it does then there is no need to worry, unless someone is playing a cruel joke and made the directory with nothing in it.
                    if not os.path.exists(os.path.join(redREnviron.directoryNames['libraryDir'], pack)):
                        print 'Downloading dependencies', dep
                        try:
                            ## make the url for the dep
                            url = repository+'/'+pack+'/'+ver
                            ## download the package, place in the tempDir for resolution
                            self.urlOpener.retrieve(url, os.path.join(redREnviron.directoryNames['tempDir'], pack, ver))
                            ## install the package
                            self.loadRRP(filename = os.path.join(redREnviron.directoryNames['tempDir'], pack, ver))
                        except:
                            loadedOk = 0
                            print 'Problem resolving dependencies, some will not be availabel.  Please try again later'
                    else:
                        return False
                except:
                    loadedOk = 0
                    print 'Problem resolving dependencies: '+str(dep)+', this will not be availabel.  Please try again later'
                    continue
            return loadedOk
        else:
            return False
    def getXMLText(self, nodelist):
        rc = ''
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc
    def readXML(self, fileName):
        f = open(libraryDir, 'r')
        mainTabs = xml.dom.minidom.parse(f)
        f.close()
        return mainTabs
    def getLocalPackages(self):
        ## moves through the local package file and returns a dict of packages with version, stability, update date, etc
        fileDir = os.path.join(redREnviron.directoryNames['libraryDir'], 'packages.xml')
        mainTabs = self.readXML(fileDir)
        
        packageDict = {}
        packageNodes = mainTabs.getElementsByTagName('Packages')
        for node in packageNodes:
            name = self.getXMLText(node.getElementsByTagName('Name')[0].childNodes)
            version = self.getXMLText(node.getElementsByTagName('Version')[0].childNodes)
            stability = self.getXMLText(node.getElementsByTagName('Stability')[0].childNodes)
            packageDict[name] = {'version':version, 'stability':stability}
            
        return packageDict
        
    def getRedRPackages(self):
        ## moves through the local package file and returns a dict of packages with version, stability, update date, etc
        self.urlOpener.retrieve(url, os.path.join(redREnviron.directoryNames['tempDir'], 'redRPachages.xml'))
        fileDir = os.path.join(redREnviron.directoryNames['tempDir'], 'redRPachages.xml')
        mainTabs = self.readXML(fileDir)
        
        packageDict = {}
        packageNodes = mainTabs.getElementsByTagName('Packages')
        for node in packageNodes:
            name = self.getXMLText(node.getElementsByTagName('Name')[0].childNodes)
            version = self.getXMLText(node.getElementsByTagName('Version')[0].childNodes)
            stability = self.getXMLText(node.getElementsByTagName('Stability')[0].childNodes)
            packageDict[name] = {'version':version, 'stability':stability}
            
        return packageDict
        
    
        
        
        