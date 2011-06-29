
## package manager class redRPackageManager.  Contains a dlg for the package manager which reads xml from the red-r.org website and compares it with a local package system on the computer

import os, sys, redREnviron, urllib2, zipfile, traceback, redRLog
from datetime import date

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

import xml.dom.minidom
import redRQTCore, re 
import orngRegistry
import pprint
import xml.etree.ElementTree as etree
import redRi18n
# def _(a):
    # return a
_ = redRi18n.Coreget_()
repository = 'http://www.red-r.org/repository/Red-R-' + redREnviron.version['REDRVERSION'] 
## moves through the local package file and returns a dict of packages with version, stability, update date, etc
def getAvailablePackages():
    file = os.path.join(redREnviron.directoryNames['canvasSettingsDir'],'red-RPackages.xml')
    if not os.path.isfile(file):
        self.createAvailablePackagesXML()
    packages = readXML(file)
    if packages == None: 
        self.createAvailablePackagesXML()
    
    packageDict = {}
    for package in packages.firstChild.childNodes:
        if package.nodeType !=package.ELEMENT_NODE:
            continue
        p = orngRegistry.parsePackageXML(package)
        packageDict[p['Name']] =  p
    
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(packageDict)        
    return packageDict
        
def getInstalledPackages():
    """Accessory function used by this and other modules to check for available packages on this installation and on the repository.  
    
    Returns a dict of packages with version, stability and updat date.
    """
    packageDict = {}
    for package in os.listdir(redREnviron.directoryNames['libraryDir']): 
        if not (os.path.isdir(os.path.join(redREnviron.directoryNames['libraryDir'], package)) 
        and os.path.isfile(os.path.join(redREnviron.directoryNames['libraryDir'],package,'package.xml'))):
            continue

        packageXML = readXML(os.path.join(redREnviron.directoryNames['libraryDir'],package,'package.xml'))
        
        packageDict[package] = orngRegistry.parsePackageXML(packageXML)
        
    
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(packageDict)
    return packageDict
        
def readXML(fileName):
    with open(fileName, 'r') as f:
        #print fileName
        mainTabs = xml.dom.minidom.parse(f)
    
    return mainTabs
    
def updatePackagesFromRepository(auto=True):
    print 'updatePackagesFromRepository', auto
    today = date.today()
    if not redREnviron.checkInternetConnection():
        return

    if redREnviron.settings['lastUpdateCheckPackages'] != 0:
        diff =  today - redREnviron.settings['lastUpdateCheckPackages']
        if int(diff.days) < 7 and auto:
                return 
    
    url = repository + '/packages.xml'
    file = os.path.join(redREnviron.directoryNames['canvasSettingsDir'],'red-RPackages.xml')
    print url
    try:
        f = urllib2.urlopen(url)
        output = open(file,'wb')
        output.write(f.read())
        output.close()  
        
        redREnviron.settings['lastUpdateCheckPackages'] = today
        redREnviron.saveSettings()
    except:
        redRLog.log(redRLog.REDRCORE,redRLog.ERROR,'Could not updated package repository from web.')
## packageManager class handles package functions such as resolving rrp's resolving dependencies, appending packages to the package xml or any function that remotely has to do with handling packages
class packageManager(redRQTCore.dialog):
    def __init__(self,canvas):
        # self.urlOpener = urllib.FancyURLopener()
        self.repository = 'http://www.red-r.org/repository/Red-R-' + redREnviron.version['REDRVERSION'] 
        self.version = redREnviron.version['REDRVERSION']
        self.availablePackages = self.getPackages()
        redRQTCore.dialog.__init__(self,canvas, title = _('Package Manager'))
        self.canvas = canvas
        self.setMinimumWidth(700)
        
        ## GUI ##
        self.controlArea = redRQTCore.widgetBox(self)
        #### layout of the tabsArea
        self.treeViewUpdates = redRQTCore.treeWidget(self.controlArea, label=_('Package List'), displayLabel=False, 
        callback = self.updateItemClicked)

        # holds the tree view of all of the packages that need updating
        self.treeViewUpdates.setHeaderLabels([
        _('Package'), 
        _('Status'),
        _('Local'),
        _('Repository'),
        _('Author'), 
        _('Summary') 
        #_('Current Version'), _('Current Version Stability'), _('New Version'), _('New Version Stability')
        ])
        
          
        #self.treeViewUpdates.setSelectionModel(QItemSelectModel.Rows)
        self.treeViewUpdates.setSelectionMode(QAbstractItemView.SingleSelection)
        self.infoViewUpdates = redRQTCore.textEdit(self.controlArea, label=_('Update Info'), displayLabel=False)  ## holds the         
        #### buttons and the like
        buttonArea2 = redRQTCore.widgetBox(self,orientation = 'horizontal')
        redRQTCore.button(buttonArea2, _('Install'), callback = self.installUpdates)
        redRQTCore.button(buttonArea2, _('Delete'), callback = self.uninstallPackages)
        redRQTCore.widgetBox(buttonArea2, sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed),
        orientation = 'horizontal')
        redRQTCore.button(buttonArea2, label = _('Update Repository'), callback = self.updateFromRepository)
        redRQTCore.button(buttonArea2, label = _('Done'), callback = self.accept)        
    def resolveRDependencies(self, packageList):
        import RSession
        packageList = [x.strip() for x in packageList]
        RSession.install_libraries(packageList)

    def installRRP(self,packageName,filename):
        """Installs the RRP zip file as the new package.  The old package is removed first then the new downloaded package is unzipped into it's place.  
        
        
        """
        installDir = os.path.join(redREnviron.directoryNames['libraryDir'], packageName)
        #print _('installDir'), installDir
        import shutil
        import compileall
        try:
            shutil.rmtree(installDir,ignore_errors=True)  ## remove the old dir for copying
            redRLog.log(redRLog.REDRCORE, redRLog.DEVEL, 'shutil remove complete')
            os.mkdir(installDir) ## make the directory to store the zipfile into
            redRLog.log(redRLog.REDRCORE, redRLog.DEVEL, 'os mkdir complete')
            zfile = zipfile.ZipFile(filename, "r" )
            zfile.extractall(installDir)
            zfile.close()
            redRLog.log(redRLog.REDRCORE, redRLog.DEVEL, 'zip file extraction complete')
            
            ## now process the requires for R
            
            pack = readXML(os.path.join(installDir, 'package.xml'))
            packageInfo = orngRegistry.parsePackageXML(pack)
            redRLog.log(redRLog.REDRCORE, redRLog.DEVEL, 'package xml parsing complete')
            import RSession
            md = QMessageBox()
            md.setText(_('Please wait while we install the R packages for this Red-R package'))
            md.show()
            if 'RLibraries' in packageInfo.keys():
                if not RSession.require_librarys(packageInfo['RLibraries']):
                    redRLog.log(redRLog.REDRCORE, redRLog.INFO, _('Installing package %(PACKAGENAME)s aborted by user.') % {'PACKAGENAME':packageName})
                    shutil.rmtree(installDir,ignore_errors=True)
                    return
            md.hide()
            redRLog.log(redRLog.REDRCORE, redRLog.DEVEL, 'R library installation complete')
            redRLog.log(redRLog.REDRCORE, redRLog.INFO, _('Installing package %(PACKAGENAME)s') % {'PACKAGENAME':packageName})
            compileall.compile_dir(installDir) # compile the directory for later importing.
            redRLog.log(redRLog.REDRCORE, redRLog.DEVEL, 'package installation complete')
        except Exception as inst:
            redRLog.log(redRLog.REDRCORE, redRLog.CRITICAL, _('There was an error installing %(PACKAGENAME)s. %(ERROR)s') % {'PACKAGENAME':packageName, 'ERROR':unicode(inst)})
            redRLog.log(redRLog.REDRCORE, redRLog.DEBUG,redRLog.formatException())
            if redREnviron.settings['outputVerbosity'] > 0:
                mb = QMessageBox(_("Package Installation Error"),_('There was an error installing %(PACKAGENAME)s. %(ERROR)s') % {'PACKAGENAME':packageName, 'ERROR':unicode(inst)}, QMessageBox.Information, 
                QMessageBox.Ok | QMessageBox.Default,
                QMessageBox.NoButton, 
                QMessageBox.NoButton, 
                self.canvas)
                mb.exec_()            
        
        md = QMessageBox()
        md.setText(_('Please wait while we generate the documentation for these files.\nThis might take a while so don\'t worry.'))
        md.show()
        redRLog.log(redRLog.REDRCORE, redRLog.DEVEL, 'Creating package documentation')
        import subprocess
        p = subprocess.Popen('python createDoc.py %s' % redREnviron.directoryNames['redRDir'], cwd = os.path.join(redREnviron.directoryNames['redRDir'], 'doc'), stdout=subprocess.PIPE, shell=True).communicate()[0]
        redRLog.log(redRLog.REDRCORE, redRLog.DEVEL, p)
        md.hide()
        
        md = QMessageBox()
        md.setText(_('We are refreshing the canvas after loading all of those files.\nInstallation is almost done.'))
        md.show()
        self.canvas.toolbarFunctions.reloadWidgets()
        self.loadPackagesLists()
        md.hide()
    # read and parse the package xml file
    # return dict
    def getPackageInfo(self,filename):
        zfile = zipfile.ZipFile(filename, "r" )
        f = zfile.open('package.xml')
        xmlStr = f.read()
        f.close()
        packageXML = xml.dom.minidom.parseString(xmlStr)
        package = orngRegistry.parsePackageXML(packageXML)
        return package
    # take a dict with package name as key and value a dict containing key 'installed' 
    # if value of 'installed' key is true do nothing and return else install 
    def downloadPackages(self,packages,window=None, force = False):
        if not redREnviron.checkInternetConnection():
            return False
        if not window:
            window  = self.canvas
        OK = True
        for package,status in packages.items():
            if status['installed'] and not force: continue
            if not package in self.sitePackages: continue
            self.progressBar = QProgressDialog(window)
            self.progressBar.setCancelButtonText(QString())
            self.progressBar.setWindowTitle(_('Installing Packages'))
            self.progressBar.setLabelText(_('Installing Packages ...'))
            self.progressBar.setMaximum(100)
            i = 0
            self.progressBar.setValue(i)
            self.progressBar.show()
            self.progressBar.setValue(i)
            self.progressBar.setLabelText(_('Installing: %s') % package)
            packageName = unicode(package+'-'+self.sitePackages[package]['Version']['Number']+'.zip')
            url = unicode(self.repository+'/'+package+'/'+packageName)
            file = os.path.join(redREnviron.directoryNames['downloadsDir'], unicode(packageName))
            try:
                self.manager = QNetworkAccessManager(window)
                reply = self.manager.get(QNetworkRequest(QUrl(url)))
                self.manager.connect(reply,SIGNAL("downloadProgress(qint64,qint64)"), self.updateProgress)
                self.manager.connect(self.manager,SIGNAL("finished(QNetworkReply*)"),
                lambda reply: self.replyFinished(reply, package, file, self.installRRP))
            except:
                redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
                OK=False
                self.progressBar.hide()

        return OK
    def updateProgress(self, read,total):
        self.progressBar.setValue(round((float(read) / float(total))*100))
        qApp.processEvents()
        
    def replyFinished(self, reply,package, file,finishedFun):
        self.reply = reply
        output = open(file,'wb')
        alltext = self.reply.readAll()
        output.write(alltext)
        output.close()
        if finishedFun:
            finishedFun(package,file)

    # take a dict with package name as key and value a dict containing key 'installed' 
    # return a a dict with the same structure including all the required packages
    def getDependencies(self,packages):
        # print 'in getDependencies', packages
        deps = {}
        for name, package in packages.items():
            if (name in self.sitePackages.keys() and len(self.sitePackages[name]['Dependencies'])):
                for dep in self.sitePackages[name]['Dependencies']:
                    if (dep in self.localPackages.keys()): 
                        installed=True
                    else:
                        installed=False
                    t = {}
                    t[dep] = {'Version':self.sitePackages[dep]['Version']['Number'], 'installed':installed}
                    deps.update(t)
                    deps.update(self.getDependencies(t))

        return deps
    
    # takes an xml node and returns the text 
    def getXMLText(self, nodelist):
        rc = ''
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
                
        rc = unicode(rc).strip()
        return rc
        
    # downloads the packages.xml file from repository
    # The file is stored in the canvasSettingsDir/red-RPackages.xml
    def updatesAvailable(self,auto=True):
        self.updatePackagesFromRepository(auto)
        packages = self.getPackages()
        if 'Out of date' in [x['status'] for x in packages.values()]:
            return True
        else: 
            return False
            
    def updatePackagesFromRepository(self, auto=True):
        return updatePackagesFromRepository(auto = True)
        #print 'updatePackagesFromRepository', auto
        #today = date.today()
        #if not redREnviron.checkInternetConnection():
            #return

        #if redREnviron.settings['lastUpdateCheckPackages'] != 0:
            #diff =  today - redREnviron.settings['lastUpdateCheckPackages']
            #if int(diff.days) < 7 and auto:
                    #return 
        
        #url = self.repository + '/packages.xml'
        #file = os.path.join(redREnviron.directoryNames['canvasSettingsDir'],'red-RPackages.xml')
        #print url
        #try:
            #f = urllib2.urlopen(url)
            #output = open(file,'wb')
            #output.write(f.read())
            #output.close()  
            
            #redREnviron.settings['lastUpdateCheckPackages'] = today
            #redREnviron.saveSettings()
        #except:
            #redRLog.log(redRLog.REDRCORE,redRLog.ERROR,'Could not updated package repository from web.')
             
        #return self.getPackages()
        
    # runs through all the installed packages and creates red-RPackages.xml file
    # The file is stored in the canvasSettingsDir until overwritten by updatePackagesFromRepository function
    def createAvailablePackagesXML(self):
        xml = '<packages>'
        for package in os.listdir(redREnviron.directoryNames['libraryDir']): 
            if (os.path.isdir(os.path.join(redREnviron.directoryNames['libraryDir'], package)) 
            and os.path.isfile(os.path.join(redREnviron.directoryNames['libraryDir'],package,'package.xml'))):
                f = open(os.path.join(redREnviron.directoryNames['libraryDir'],package,'package.xml'),'r')
                xml = xml + '\n' + f.read()
                f.close()
        
        f = open(os.path.join(redREnviron.directoryNames['canvasSettingsDir'],'red-RPackages.xml'),'w')
        f.write(xml + '\n</packages>')
        f.close()
        # print 'asdfasdfsd', xml
    ## moves through the local package file and returns a dict of packages with version, stability, update date, etc
    def getAvailablePackages(self):
        return getAvailablePackages()
        # file = os.path.join(redREnviron.directoryNames['canvasSettingsDir'],'red-RPackages.xml')
        # if not os.path.isfile(file):
            # self.createAvailablePackagesXML()
        # packages = readXML(file)
        # if packages == None: 
            # self.createAvailablePackagesXML()
        
        # packageDict = {}
        # for package in packages.firstChild.childNodes:
            # if package.nodeType !=package.ELEMENT_NODE:
                # continue
            # p = orngRegistry.parsePackageXML(package)
            # packageDict[p['Name']] =  p
        
        ##pp = pprint.PrettyPrinter(indent=4)
        ##pp.pprint(packageDict)        
        # return packageDict
        
    ## returns a tuple of dicts (packages needed updates, installed packages, and packages available on the repository)
    
    def getPackages(self):
        self.localPackages = getInstalledPackages()
        self.sitePackages = self.getAvailablePackages()
        # print self.sitePackages
        if self.sitePackages in [None, {}]:
            #return (None, self.localPackages, None)
            self.sitePackages = self.localPackages
        
        self.availablePackages = {}
        
        ## loop through the package names and see what should be upgraded.
        for name,remotePackage in self.sitePackages.items():
            # this package must not be on Red-R.org any more.
            self.availablePackages[name] = {}
            self.availablePackages[name]['new'] = remotePackage
            if name in self.localPackages.keys():
                localPackage = self.localPackages[name]
                self.availablePackages[name]['current'] = localPackage
                if float(localPackage['Version']['Number']) < float(remotePackage['Version']['Number']):
                    self.availablePackages[name]['status'] = 'Out of date'
                else:
                    self.availablePackages[name]['status'] = 'Current'
            else:
                self.availablePackages[name]['status'] = 'New'
                
        for name,localPackage in self.localPackages.items():
            if name not in self.availablePackages.keys():
                self.availablePackages[name] = {}
                self.availablePackages[name]['status'] = 'Local only'
                self.availablePackages[name]['current'] = localPackage
                self.availablePackages[name]['new'] = localPackage

        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(self.updatePackages)        

        return self.availablePackages
 
    def updateItemClicked(self, item1, item2):
        if item1:
            self.infoViewUpdates.setHtml(self.availablePackages[unicode(item1.text(0))]['new']['Description'])
    #### get the pakcages that are on Red-R.org  we ask before we do this and record the xml so we only have to get it once.
    def updateFromRepository(self):
        self.updatePackagesFromRepository(auto=False)
        self.loadPackagesLists()
    def loadPackagesLists(self,force=True):    
        self.getPackages()
        self.setUpdates(self.availablePackages)

        
    def exec_(self):
        # mb = QMessageBox("Update Package Repository", "Update package repository for Red-R.org?", 
        # QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, 
        # QMessageBox.No | QMessageBox.Escape, QMessageBox.NoButton, qApp.canvasDlg)
        # if mb.exec_() == QMessageBox.Ok:
        self.updatePackagesFromRepository(auto=True)
        self.loadPackagesLists(force=False)
        redRQTCore.dialog.exec_(self)
        
    def setUpdates(self, packages):
        self.treeViewUpdates.clear()
        if not packages:
            return 
        for name,package in packages.items(): ## move across the package names
            if 'current' in package.keys():
                current = package['current']
            if 'new' in package.keys():
                new = package['new']
                
            color = 'white'
            line = [name,package['status']]
            if package['status'] == 'Out of date':
                line += [
                '%s (%s)' % (current['Version']['Number'],current['Version']['Stability']),
                '%s (%s)' % (new['Version']['Number'],new['Version']['Stability'])               
                ]
                color='red'
            elif package['status'] in ['Current']:
                line += [
                '%s (%s)' % (current['Version']['Number'],current['Version']['Stability']),
                '%s (%s)' % (new['Version']['Number'],new['Version']['Stability'])               
                ]
            elif package['status'] in ['Local only']:
                line += [
                '%s (%s)' % (current['Version']['Number'],current['Version']['Stability']),
                ''
                ]
            elif package['status'] in ['New']:
                line += [
                '',
                '%s (%s)' % (new['Version']['Number'],new['Version']['Stability'])
                ]
            
            line += [new['Author'], new['Summary']]
            
            newChild = redRQTCore.treeWidgetItem(self.treeViewUpdates, line,bgcolor=QColor(color))
            
    def installAllPakcages(self):
        """Install all packages on the repository, this is if you just want to get everything."""
        downloadList = {}
        for package, value in self.availablePackages.items():
            if value['status'] == 'Local only': continue
            downloadList[package] = {'Version':'force', 'installed':False}
        
        self.askToInstall(downloadList, _("Are you sure that you want to install all available packages?"))
        
    # takes user selected list of packages from the available packages menu and installed them and all the dependencies
    def installNewPackage(self):
        selectedItems = self.treeViewAvailable.selectedItems()
        if len(selectedItems) ==0: return
        downloadList = {}
        for item in selectedItems:  
            name = unicode(item.text(0))
            downloadList[name] = {'Version':unicode(item.text(3)), 'installed':False}

        self.askToInstall(downloadList, _("Are you sure that you want to install these packages?"))
        
    def installUpdates(self):
        ### move through the selected items in the updates page, get the RRP locations and install the rrp's for the packages.
        selectedItems = self.treeViewUpdates.selectedItems()
        if len(selectedItems) ==0: return
        ### make the download list
        downloadList = {}
        for item in selectedItems:  
            name = unicode(item.text(0))
            self.availablePackages[name]
            downloadList[name] = {'Version':self.availablePackages[name]['new']['Version']['Number'], 'installed':False}
        # print downloadList
        self.askToInstall(downloadList,"Are you sure that you want to install these packages?")
                
    def uninstallPackages(self):
        ## collect the packages that are selected.  Make sure that base isn't in the uninstall list.  Ask the user if he is sure that the files should be uninstalled, uninstall the packages (remove the files).
        selectedItems = self.treeViewUpdates.selectedItems()
        if len(selectedItems) ==0: return

        uninstallList = []
        for item in selectedItems:
            name = unicode(item.text(0))
            if name == 'base':  ## special case of trying to delete base.
                QMessageBox.information(self, _("Deleting Base"), _("You are not allowed to delete base."), QMessageBox.Ok)
                continue
            uninstallList.append(name)
        if len(uninstallList) ==0: return
        
        mb = QMessageBox(_("Uninstall Packages"), _("Are you sure that you want to uninstall these packages?\n\n")+
        "\n".join(uninstallList), QMessageBox.Information, 
        QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton,self)
        
        if mb.exec_() != QMessageBox.Ok:
            return
            
        import shutil
        for name in uninstallList:
            shutil.rmtree(os.path.join(redREnviron.directoryNames['libraryDir'], name), True)
        
        self.canvas.toolbarFunctions.reloadWidgets()
        self.loadPackagesLists(force=False)
    
    # Lists all packages that will be downloaded and installed
    # asks for permission to perform the actions
    def askToInstall(self,packages,msg):
        deps = self.getDependencies(packages)
        mainStr = []
        depStr = []
        for package,version in packages.items():
            if not version['installed']:
                mainStr.append(package + '-' + version['Version'])
            
        for package,version in deps.items():
            if not version['installed'] and package not in packages.keys():
                depStr.append(package + '-' + version['Version'])
            
        
        msg = msg + _("\nRepository: Red-R.org\nPackages:\n-- ") + "\n-- ".join(mainStr)
        if len(depStr) > 0:
            msg = msg + _("\n With dependencies:\n-- ") + "\n-- ".join(depStr)
            
        mb = QMessageBox(_("Install Packages"), msg, 
        QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, 
        QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton,self)
        if mb.exec_() != QMessageBox.Ok:
            return

        ## resolve the packages
        packages.update(deps)
        #print packages
        results = self.downloadPackages(packages,window=self)
        
        #self.tabsArea.setCurrentIndex(1)
    
    

    # install file form file. Takes package rrp location and parses the xml file to dependencies
    # installs the local rrp file as well as all the required dependencies if they exist in the repository
    def installPackageFromFile(self,filename):
        try:
            package = self.getPackageInfo(filename)
            
            if package['Name'] in self.localPackages.keys() and self.localPackages[package['Name']]['Version']['Number'] == package['Version']['Number']: 
                mb = QMessageBox(_("Install Package"), 'Package "%s" is already installed. Do you want to remove the current version and continue installation?' % package['Name'], 
                QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, 
                QMessageBox.No | QMessageBox.Escape, QMessageBox.NoButton,self)
                if mb.exec_() != QMessageBox.Ok:
                    return

                
            downloadList = {}
            downloadList[package['Name']] = {'Version':unicode(package['Version']['Number']), 'installed':False}
            deps = self.getDependencies(downloadList)
            #print deps
            notFound = []
            download = {}
            for name,version in deps.items():
                if name in self.availablePackages.keys() and version['Version'] == self.availablePackages[name]['Version']['Number']:
                    download[name] = version
                else:
                    notFound.append(name)
            if len(notFound) > 0:
                mb = QMessageBox.warning(self,_("Install Package"), 
                _('The following packages are required but not found in the Red-R.org repository. Installation will not proceed.\n\n--')+
                '\n--'.join(notFound),
                QMessageBox.Ok)
                return
            else:
                msg = _("Are you sure that you want to install this package and its dependencies?\nRepository: Red-R.org\nPackage:\n--") + package['Name']
                if len(download.keys()) > 0:
                    msg = msg + _("\n With dependencies:\n--") + "\n--".join(deps.keys())
                    
                mb = QMessageBox(_("Install Package"), msg, 
                QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, 
                QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton,self)
                if mb.exec_() != QMessageBox.Ok:
                    return
            #print filename
            self.installRRP(package['Name'], filename)
            if len(download.keys()) > 0:
                results = self.downloadPackages(download,window=self)
            else: #need to do this to refresh the widget tree
                self.canvas.toolbarFunctions.reloadWidgets()
        except Exception as inst:
            mb = QMessageBox.warning(self,_("Install Package"), 
                _('The following error occurred during the installation of your package.\nPlease contact the package maintainer to report this error.\n\n')+unicode(inst),
                QMessageBox.Ok)
            raise Exception, unicode(inst)
     
