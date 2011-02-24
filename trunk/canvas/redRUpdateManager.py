from libraries.base.qtWidgets.dialog import dialog as redRdialog
from libraries.base.qtWidgets.treeWidgetItem import treeWidgetItem as redRtreeWidgetItem
from libraries.base.qtWidgets.button import button as redRbutton
from libraries.base.qtWidgets.textEdit import textEdit as redRtextEdit
from libraries.base.qtWidgets.tabWidget import tabWidget as redRtabWidget
from libraries.base.qtWidgets.treeWidget import treeWidget as redRtreeWidget
from libraries.base.qtWidgets.widgetBox import widgetBox as redRwidgetBox
from libraries.base.qtWidgets.webViewBox import webViewBox as redRwebViewBox

## package manager class redRPackageManager.  Contains a dlg for the package manager which reads xml from the red-r.org website and compares it with a local package system on the computer

import os, sys, redREnviron, urllib2, zipfile, traceback, shutil
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
import xml.dom.minidom
import redRGUI, re , redRLog
import xml.etree.ElementTree as etree
from datetime import date
if sys.platform =='win32':
   import win32api, win32process
   from win32com.shell import shell, shellcon
   
import redRi18n
# def _(a):
    # return a
_ = redRi18n.Coreget_()

class updateManager(QMainWindow):
    def __init__(self,app,schema=None):
        QMainWindow.__init__(self)
        self.main = redRwidgetBox(None)
        self.setCentralWidget(self.main)
        self.schema = schema
        self.app = app
        self.version = redREnviron.version['REDRVERSION']
        self.repository = redREnviron.settings['updatesRepository']
        self.updateFile = os.path.join(redREnviron.directoryNames['canvasSettingsDir'],'red-RUpdates.xml')
        if os.path.exists(self.updateFile):
            self.availableUpdate = self.parseUpdatesXML(self.updateFile)
        #qApp.processEvents()
    def checkForUpdate(self, auto=True):
        today = date.today()
        if not redREnviron.checkInternetConnection():
            return

        if redREnviron.settings['lastUpdateCheck'] != 0:
            diff =  today - redREnviron.settings['lastUpdateCheck']
            if int(diff.days) < 7 and auto:
                    return
        url =redREnviron.settings['updatesRepository'] +'/currentVersion.xml'
        print 'theurl:', url
        print 'thesavefile', self.updateFile
        try:
            f = urllib2.urlopen(url)
            output = open(self.updateFile,'wb')
            output.write(f.read())
            output.close()
            
        except:
            redREnviron.settings['updateAvailable'] = False
            redRLog.log(redRLog.REDRCORE,redRLog.ERROR,'Could not find updates from web.')
            
        redREnviron.settings['lastUpdateCheck'] = today
        redREnviron.saveSettings()
        
        self.availableUpdate = self.parseUpdatesXML(self.updateFile)
        print 'avaliable', self.availableUpdate
        
        if (self.availableUpdate['redRVersion'] == redREnviron.version['REDRVERSION'] 
        and self.availableUpdate['SVNVersion'] > redREnviron.version['SVNVERSION']):
            print auto, self.availableUpdate['SVNVersion'] in redREnviron.settings['ignoredUpdates']
            if auto and self.availableUpdate['SVNVersion'] in redREnviron.settings['ignoredUpdates']:
                redREnviron.settings['updateAvailable'] = False
            else: 
                redREnviron.settings['updateAvailable'] = True
        else: 
            redREnviron.settings['updateAvailable'] = False
        
        print 'is available', redREnviron.settings['updateAvailable']
        redREnviron.saveSettings()
    
    def showUpdateDialog(self,auto=False):
        print 'in showUpdateDialog'
        html = _("<h2>Red-R %s</h2><h4>Revision:%s; Date: %s</h4><br>%s") % (
        self.availableUpdate['redRVersion'],self.availableUpdate['SVNVersion'],
        self.availableUpdate['date'],self.availableUpdate['changeLog']) 
        
        print 'in createDialog'
        width = 350
        height = 350
        changeLogBox = redRwebViewBox(self.main,label=_('Update'),displayLabel=False)
        changeLogBox.setMinimumWidth(width)
        changeLogBox.setMinimumHeight(width)
        changeLogBox.setHtml(html)
        
        buttonArea2 = redRwidgetBox(self.main,orientation = 'horizontal', alignment=Qt.AlignRight)
        redRbutton(buttonArea2, label = _('Update'), callback = self.accept)
        redRbutton(buttonArea2, label = _('Ignore Update'), callback = self.ignore)
        redRbutton(buttonArea2, label = _('Cancel'), callback = self.reject)
        
        
        desktop = self.app.desktop()
        deskH = desktop.screenGeometry(desktop.primaryScreen()).height()
        deskW = desktop.screenGeometry(desktop.primaryScreen()).width()
        h = max(0, deskH/2 - height/2)  # if the window is too small, resize the window to desktop size
        w = max(0, deskW/2 - width/2)
        self.move(w,h+2)
        self.show()
        print 'end createDialog'
        
    #parse the xml from the website and create a dict of avaliable updates
    #each os that a section in the xml
    def parseUpdatesXML(self,fileName):
        try:
            f = open(fileName, 'r')
            updatesXML = xml.dom.minidom.parse(f)
            f.close()
            
            update = {}
            update['redRVersion'] = self.getXMLText(updatesXML.getElementsByTagName('redRVersion')[0].childNodes)
            
            if sys.platform=="win32":
                updatesNode = updatesXML.getElementsByTagName('win32')[0]
            elif sys.platform=="darwin":
                updatesNode = updatesXML.getElementsByTagName('mac')[0]
            elif sys.platform == 'linux2':
                updatesNode = updatesXML.getElementsByTagName('linux')[0]
            if updatesNode and updatesNode != None:
                if redREnviron.version['TYPE'] =='compiled':
                    update['url'] = self.getXMLText(updatesNode.getElementsByTagName('compiled')[0].childNodes)
                elif redREnviron.version['TYPE'] =='src':
                    update['url'] = self.getXMLText(updatesNode.getElementsByTagName('src')[0].childNodes)
                else:
                    raise Exception('Unknown type')
                update['SVNVersion'] = self.getXMLText(updatesNode.getElementsByTagName('SVNVersion')[0].childNodes)
                update['date'] = self.getXMLText(updatesNode.getElementsByTagName('date')[0].childNodes)
                update['changeLog'] = self.getXMLText(updatesNode.getElementsByTagName('changeLog')[0].childNodes)

            return update
        except:
            redRLog.log(redRLog.REDRCORE,redRLog.ERROR,'Red-R update information cannot be downloaded.')
            redRLog.log(redRLog.REDRCORE,redRLog.DEBUG,redRLog.formatException())

    def getXMLText(self, nodelist):
        rc = ''
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
                
        rc = str(rc).strip()
        return rc

    def accept(self):
        print 'accept'
        self.downloadUpdate(self.availableUpdate)
        redREnviron.settings['updateAvailable'] = False
        redREnviron.saveSettings()
        
    def reject(self):
        print 'reject'
        self.app.exit(0)
    
    def ignore(self):
        print 'ignore'
        redREnviron.settings['ignoredUpdates'] += self.availableUpdate['SVNVersion']
        redREnviron.settings['updateAvailable'] = False
        redREnviron.saveSettings()
        self.app.exit(0)
        

    def downloadUpdate(self,update):
        print 'downloadUpdate'
        url = update['url']
        file = os.path.join(redREnviron.directoryNames['downloadsDir'],
        os.path.basename(update['url']))
        
        # self.execUpdate(file)
        # return
        print url, file
        self.progressBar = QProgressDialog(self.schema)
        self.progressBar.setCancelButtonText(QString())
        self.progressBar.setWindowTitle('Downloading...')
        self.progressBar.setLabelText('Downloading...')
        self.progressBar.setMaximum(100)
        i = 0
        self.progressBar.setValue(i)
        self.progressBar.show()
        self.manager = QNetworkAccessManager(self.schema)
        reply = self.manager.get(QNetworkRequest(QUrl(url)))
        
        self.manager.connect(reply,SIGNAL("downloadProgress(qint64,qint64)"), self.updateProgress)
        
        self.manager.connect(self.manager,SIGNAL("finished(QNetworkReply*)"),
        lambda reply: self.replyFinished(reply, file,self.execUpdate))
        # self.downloadFile(url,file,finishedFun=self.closeAndUpdate, progressFun=self.updateProgress)
    
    def updateProgress(self, read,total):
        self.progressBar.setValue(round((float(read) / float(total))*100))
        qApp.processEvents()
       
    #file is the downloaded installer file
    #run the installer and exit red-r 
    #the installer should run independantly and make all the changes needed for the os
    def execUpdate(self,file):
        
        installDir = os.path.split(os.path.abspath(redREnviron.directoryNames['redRDir']))[0]
        ######## WINDOWS ##############
        if sys.platform =='win32':
            cmd = "%s /D=%s" % (file,installDir)
            try:
                shell.ShellExecuteEx(shellcon.SEE_MASK_NOCLOSEPROCESS,0,'open',file,"/D=%s" % installDir,
                redREnviron.directoryNames['downloadsDir'],0)
                # win32process.CreateProcess('Red-R update',cmd,'','','','','','','')
            except:
                redRLog.log(redRLog.REDRCORE, redRLog.ERROR,redRLog.formatException())
                mb = QMessageBox(_("Error"), _("There was an Error in updating Red-R."), 
                    QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, 
                    QMessageBox.NoButton, QMessageBox.NoButton, self.schema)
                mb.exec_()
        
        ######## MAC ##############
        elif sys.platform =='darwin':
            cmd = '%s %s %s %s' % (os.path.join(redREnviron.directoryNames['redRDir'],'MacOS','python'), 
            os.path.join(redREnviron.directoryNames['redRDir'],'redRMacUpdater.py'), file, installDir)
            print cmd
            r = QProcess.startDetached(cmd)
            
        else:
            raise Exception('Add Linux specific installer code')
            
        self.app.exit(1)

        
    def replyFinished(self, reply,file,finishedFun):
        self.reply = reply
        output = open(file,'wb')
        alltext = self.reply.readAll()
        output.write(alltext)
        output.close()
        if finishedFun:
            finishedFun(file)


            
