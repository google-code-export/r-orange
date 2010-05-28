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
                
                ### add the package info to the packages.xml
                fileDir = os.path.join(redREnviron.directoryNames['libraryDir'], 'packages.xml')
                localPackagesXML = self.readXML(fileDir)
                
                
                ###
                
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
    def resolveRRPDependencies(self, alldeps, repository, dontAsk = False):
        loadedOk = 1
        if not redREnviron.checkInternetConnection():
            return False
            
        if not dontAsk:
            mb = QMessageBox("Download Packages", "You are missing some key packages.\n\n"+'\n'.join(alldeps)+"\nDo you want to download them?\nIf you click NO your packages WON\'T WORK!!!", QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton)
            if mb.exec_() != QMessageBox.Ok: return False
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
        
    def getXMLText(self, nodelist):
        rc = ''
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc
    def readXML(self, fileName):
        f = open(fileName, 'r')
        mainTabs = xml.dom.minidom.parse(f)
        f.close()
        return mainTabs
    def getLocalPackages(self):
        ## moves through the local package file and returns a dict of packages with version, stability, update date, etc
        fileDir = os.path.join(redREnviron.directoryNames['libraryDir'], 'packages.xml')
        mainTabs = self.readXML(fileDir)
        
        packageDict = {}
        packageNodes = mainTabs.getElementsByTagName('Package')
        for node in packageNodes:
            name = self.getXMLText(node.getElementsByTagName('Name')[0].childNodes)
            author = self.getXMLText(node.getElementsByTagName('Author')[0].childNodes)
            version = self.getXMLText(node.getElementsByTagName('Version')[0].childNodes)
            stability = self.getXMLText(node.getElementsByTagName('Stability')[0].childNodes)
            summary = self.getXMLText(node.getElementsByTagName('Summary')[0].childNodes)
            used = self.getXMLText(node.getElementsByTagName('Used')[0].childNodes)
            description = self.getXMLText(node.getElementsByTagName('Description')[0].childNodes)
            packageDict[name] = {'Author':author, 'Stability':stability, 'Version':version, 'Summary':summary, 'Used':used, 'Description':description}
            
        print packageDict
        return packageDict
        
    def getRedRPackages(self):
        ## moves through the local package file and returns a dict of packages with version, stability, update date, etc
        url = 'http://www.red-r.org/packages/' + redREnviron.version['REDRVERSION'] + '/packages.xml'
        print url
        self.urlOpener.retrieve(url, os.path.join(redREnviron.directoryNames['tempDir'], 'redRPachages.xml'))
        fileDir = os.path.join(redREnviron.directoryNames['tempDir'], 'redRPachages.xml')
        #fileDir = os.path.join(redREnviron.directoryNames['libraryDir'], 'testOnlinePackages.xml')
        mainTabs = self.readXML(fileDir)
        
        packageDict = {}
        packageNodes = mainTabs.getElementsByTagName('Package')
        for node in packageNodes:
            name = self.getXMLText(node.getElementsByTagName('Name')[0].childNodes)
            author = self.getXMLText(node.getElementsByTagName('Author')[0].childNodes)
            summary = self.getXMLText(node.getElementsByTagName('Summary')[0].childNodes)
            description = self.getXMLText(node.getElementsByTagName('Description')[0].childNodes)
            versions = self.getRedRPackagesVersions(node)
            headVersion = self.getXMLText(node.getElementsByTagName('HeadVersion')[0].childNodes)
            repository = self.getXMLText(node.getElementsByTagName('Repository')[0].childNodes)
            
            packageDict[name] = {'Author':author, 'Summary':summary, 'Description':description, 'Repository':repository, 'Versions':versions, 'HeadVersion':headVersion}
            
        print packageDict
        return packageDict
    def getRedRPackagesVersions(self, node):
        versionDict = {}
        for version in node.getElementsByTagName('Version'):
            name = self.getXMLText(version.getElementsByTagName('Name')[0].childNodes)
            stability = self.getXMLText(version.getElementsByTagName('Stability')[0].childNodes)
            date = self.getXMLText(version.getElementsByTagName('Date')[0].childNodes)
            
            versionDict[name] = {'Stability':stability, 'Date':date}
            
        return versionDict
        
    def getDiffPackages(self):
        ## returns a collection of packages that have been upgraded since the user last downloaded the packages
        homePackages = self.getLocalPackages()
        sitePackages = self.getRedRPackages()
        
        updatePackages = {}
        ## loop through the package names and see what should be upgraded.
        for name in homePackages.keys():
            try:
                spName = sitePackages[name]
            except:  # this package must not be on Red-R.org any more.
                continue
            if homePackages[name]['Version'] != spName['HeadVersion']:
                updatePackages[name] = spName
                updatePackages[name]['Version'] = homePackages[name]['Version']
                updatePackages[name]['Stability'] = homePackages[name]['Stability']
        print updatePackages
        return (updatePackages, homePackages, sitePackages)
        
class PackageManagerDialog(redRGUI.dialog):
    def __init__(self):
        redRGUI.dialog.__init__(self, title = 'Package Manager')
        
        self.packageManager = packageManager()
        
        ## GUI ##
        
        #### set up a screen that will show a listbox of packages that are on the system that should be updated, 
        
        self.tabsArea = redRGUI.tabWidget(self)
        self.updatesTab = self.tabsArea.createTabPage(name = 'Updates')
        self.installedTab = self.tabsArea.createTabPage(name = 'Installed Packages')
        self.availableTab = self.tabsArea.createTabPage(name = 'Available Packages')
        
        #### layout of the tabsArea
        self.treeViewUpdates = redRGUI.treeWidget(self.updatesTab, callback = self.updateItemClicked)  ## holds the tree view of all of the packages that need updating
        #self.treeViewUpdates.setSelectionModel(QItemSelectModel.Rows)
        self.treeViewUpdates.setSelectionMode(QAbstractItemView.MultiSelection)
        self.infoViewUpdates = redRGUI.textEdit(self.updatesTab)  ## holds the info for a package
        redRGUI.button(self.updatesTab, 'Install Updates', callback = self.installUpdates)
        
        self.treeViewInstalled = redRGUI.treeWidget(self.installedTab, callback = self.installItemClicked)
        #self.treeViewInstalled.setSelectionModel(QItemSelectModel.Rows)
        self.treeViewInstalled.setSelectionMode(QAbstractItemView.MultiSelection)
        self.infoViewInstalled = redRGUI.textEdit(self.installedTab)
        redRGUI.button(self.installedTab, 'Remove Packages', callback = self.uninstallPackages)
        
        self.treeViewAvailable = redRGUI.treeWidget(self.availableTab, callback = self.availableItemClicked)
        #self.treeViewAvailable.setSelectionModel(QItemSelectModel.Rows)
        self.treeViewAvailable.setSelectionMode(QAbstractItemView.MultiSelection)
        self.infoViewAvailable = redRGUI.textEdit(self.availableTab)
        redRGUI.button(self.availableTab, 'Install Packages', callback = self.installNewPackage)
        
        #### buttons and the like
        buttonArea2 = redRGUI.widgetBox(self)
        redRGUI.button(buttonArea2, label = 'Reload Packages', callback = self.loadPackagesLists)
        redRGUI.button(buttonArea2, label = 'Done', callback = self.accept())
        
        self.loadPackagesLists()
    def installItemClicked(self, item1, item2):
        self.infoViewInstalled.setHtml(self.localPackages[str(item1.text(0))]['Description'])
        pass
    def updateItemClicked(self, item1, item2):
        
        pass
    def availableItemClicked(self, item1, item2):
        pass
    def loadPackagesLists(self):
        #### get the pakcages that are on Red-R.org  we ask before we do this and record the xml so we only have to get it once.
        #if redREnviron.checkInternetConnection():
        if True:
            mb = QMessageBox("Check Packages", "I need to go online to check for available packages.\nDo you want me to do this?", QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton)
            if mb.exec_() == QMessageBox.Ok:
                self.connectionOKGetTuple()
                
            else: self.noConnectGetLocal()
        else:
            self.noConnectGetLocal()
    def connectionOKGetTuple(self):
        self.packageDicts = self.packageManager.getDiffPackages()
        self.localPackages = self.packageDicts[1]
        self.updatesTab.setEnabled(True)
        self.availableTab.setEnabled(True)
        self.setUpdates(self.packageDicts[0])
        self.setInstalled(self.packageDicts[1])
        self.setAvailable(self.packageDicts[2])
    def noConnectGetLocal(self):
        self.packageDicts = None
        self.localPackages = self.packageManager.getLocalPackages()
        self.setUpdates(None)
        self.setInstalled(self.localPackages)
        self.setAvailable(None)
        self.updatesTab.setEnabled(False)
        self.availableTab.setEnabled(False)
        
    def setUpdates(self, dictionary):
        self.treeViewUpdates.clear()
        self.treeViewUpdates.setHeaderLabels(['Package', 'Version', 'Type', 'Author', 'Summary', 'Stability'])
        if dictionary != None:
            ## there is something in the dict and we need to populate the treeview
            for name in dictionary.keys(): ## move across the package names
                newChild = redRGUI.treeWidgetItem(self.treeViewUpdates, [name, dictionary[name]['Version'], 'Installed', dictionary[name]['Author'], dictionary[name]['Summary'], dictionary[name]['Stability']])
                for version in self.packageDicts[2][name]['Versions'].keys():
                    n = redRGUI.treeWidgetItem(stringList = [name, version, 'Available', self.packageDicts[2][name]['Versions'][version]['Stability'], self.packageDicts[2][name]['Versions'][version]['Date']])
                    newChild.addChild(n)
                
    def setInstalled(self, dictionary):
        self.treeViewInstalled.clear()
        self.treeViewInstalled.setHeaderLabels(['Package', 'Version', 'Author', 'Summary', 'Stability', 'Used'])
        if dictionary != None:
            ## there is something in the dict and we need to populate the treeview
            for name in dictionary.keys(): ## move across the package names
                newChild = redRGUI.treeWidgetItem(self.treeViewInstalled, [name, dictionary[name]['Version'], dictionary[name]['Author'], dictionary[name]['Summary'], dictionary[name]['Stability'], dictionary[name]['Used']])
                
    def setAvailable(self, dictionary):
        self.treeViewAvailable.clear()
        self.treeViewAvailable.setHeaderLabels(['Package', 'Version', 'Author/Stability', 'Summary/Date'])
        if dictionary != None:
            ## there is something in the dict and we need to populate the treeview
            for name in dictionary.keys(): ## move across the package names
                newChild = redRGUI.treeWidgetItem(self.treeViewAvailable, [name, 'HeadVersion', dictionary[name]['Author'], dictionary[name]['Summary'], 'Current Version'])
                for version in dictionary[name]['Versions'].keys(): ## move across all of the versions and show their name
                    n = redRGUI.treeWidgetItem(stringList = [name, version, dictionary[name]['Versions'][version]['Stability'], dictionary[name]['Versions'][version]['Date']])
                    newChild.addChild(n)
                    
    def installUpdates(self):
        ### move through the selected items in the updates page, get the RRP locations and install the rrp's for the packages.
        selectedItems = self.treeViewUpdates.selectedItems()
        
        ### make the download list
        downloadList = {}
        for item in selectedItems:  ## move across the selected items, check if it is one of the sub pakcages or not, if so; put the version number in the downloadList, otherwise put the HeadVersion in the download List.  Collect the repository also.
            name = str(item.text(0))
            ## check if main package or not
            if str(item.text(2)) == 'Installed': ## it's already installed so get the head version
                ## pull the headVersion
                headVersion = self.packageDicts[2][name]['HeadVersion']
                repository = self.packageDicts[2][name]['Repository']
            else:
                headVersion = str(item.text(1))
                repository = self.packageDicts[2][name]['Repository']
                
            if name in downloadList:
                mb = QMessageBox("Install Package Question", "You already have a version of this set to download.\nDo you want to replace\n\n"+str(downloadList[name]['HeadVersion'])+"\n\nwith\n\n"+str(headVersion), QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton)
                if mb.exec_() == QMessageBox.Ok:
                    downloadList[name] = {'HeadVersion':headVersion, 'Repository':repository}
                    
            else:
                downloadList[name] = {'HeadVersion':headVersion, 'Repository':repository}
        mb = QMessageBox("Install Package Question", "Are you sure that you want to install these packages?\n\n"+"\n".join(downloadList.keys()), QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton)
        if mb.exec_() != QMessageBox.Ok:
            return
        ## resolve the packages
        for name in downloadList.keys():  # move across all of the packages and download
            if not self.packageManager.resolveRRPDependencies([downloadList[name]['HeadVersion']], downloadList[name]['Repository'], dontAsk = True):  ## the user has already committed so we go ahead
                QMessageBox.information(None, "Install Package Information", "There was a problem with getting package "+name+".\nI'm going to get the rest of the packages but just wanted to let you know.\nYou can always try to download again if you lost the internet connection.", QMessageBox.Ok)
    def uninstallPackages(self):
        ## collect the packages that are selected.  Make sure that base isn't in the uninstall list.  Ask the user if he is sure that the files should be uninstalled, uninstall the packages (remove the files).
        selectedItems = self.treeViewInstalled.selectedItems()
        uninstallList = []
        for item in selectedItems:
            name = str(item.text(0))
            if name == 'base':  ## special case of trying to delete base.
                QMessageBox.information(self, "Deleting Base", "You are not allowed to delete base.", QMessageBox.Ok)
                continue
            uninstallList.append(name)
            
        mb = QMessageBox("Uninstall Pakcages", "Are you sure that you want to uninstall these packages?\n\n"+"\n".join(uninstallList), QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton)
        if mb.exec_() != QMessageBox.Ok:
            return
            
        import shutil
        for name in uninstallList:
            shutil.rmtree(os.path.join(redREnviron.directoryNames['libraryDir'], name), True)
            ### remove the package from the packages xml!!!
    def installNewPackage(self):
        selectedItems = self.treeViewAvailable.selectedItems()
        downloadList = {}
        for item in selectedItems:
            name = str(item.text(0))
            if str(item.text(1)) == 'HeadVersion': ## it's already installed so get the head version
                ## pull the headVersion
                headVersion = self.packageDicts[2][name]['HeadVersion']
                repository = self.packageDicts[2][name]['Repository']
            else:
                headVersion = str(item.text(1))
                repository = self.packageDicts[2][name]['Repository']
                
            if name in downloadList:
                mb = QMessageBox("Install Package Question", "You already have a version of this set to download.\nDo you want to replace\n\n"+str(downloadList[name]['HeadVersion'])+"\n\nwith\n\n"+str(headVersion), QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton)
                if mb.exec_() == QMessageBox.Ok:
                    downloadList[name] = {'HeadVersion':headVersion, 'Repository':repository}
                    
            else:
                downloadList[name] = {'HeadVersion':headVersion, 'Repository':repository}
        
        mb = QMessageBox("Install Package Question", "Are you sure that you want to install these packages?\n\n"+"\n".join(downloadList.keys()), QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton)
        if mb.exec_() != QMessageBox.Ok:
            return
        ## resolve the packages
        for name in downloadList.keys():  # move across all of the packages and download
            if not self.packageManager.resolveRRPDependencies([downloadList[name]['HeadVersion']], downloadList[name]['Repository'], dontAsk = True):  ## the user has already committed so we go ahead
                QMessageBox.information(None, "Install Package Information", "There was a problem with getting package "+name+".\nI'm going to get the rest of the packages but just wanted to let you know.\nYou can always try to download again if you lost the internet connection.", QMessageBox.Ok)