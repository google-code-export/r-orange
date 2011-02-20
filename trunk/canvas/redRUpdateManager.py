from libraries.base.qtWidgets.dialog import dialog as redRdialog
from libraries.base.qtWidgets.treeWidgetItem import treeWidgetItem as redRtreeWidgetItem
from libraries.base.qtWidgets.button import button as redRbutton
from libraries.base.qtWidgets.textEdit import textEdit as redRtextEdit
from libraries.base.qtWidgets.tabWidget import tabWidget as redRtabWidget
from libraries.base.qtWidgets.treeWidget import treeWidget as redRtreeWidget
from libraries.base.qtWidgets.widgetBox import widgetBox as redRwidgetBox
from libraries.base.qtWidgets.webViewBox import webViewBox as redRwebViewBox

## package manager class redRPackageManager.  Contains a dlg for the package manager which reads xml from the red-r.org website and compares it with a local package system on the computer

import os, sys, redREnviron, urllib2, zipfile, traceback
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
        #self.urlOpener = urllib2.FancyURLopener()
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
        print url
        try:
            f = urllib2.urlopen(url)
            output = open(self.updateFile,'wb')
            output.write(f.read())
            output.close()
        except:
            redREnviron.settings['updateAvailable'] = False
            return 
            
        redREnviron.settings['lastUpdateCheck'] = today
        redREnviron.saveSettings()
        
        self.availableUpdate = self.parseUpdatesXML(self.updateFile)
        if (self.availableUpdate['redRVerion'] == redREnviron.version['REDRVERSION'] 
        and self.availableUpdate['SVNVersion'] > redREnviron.version['SVNVERSION']):
            redREnviron.settings['updateAvailable'] = True
        else: 
            redREnviron.settings['updateAvailable'] = False
    
    def showUpdateDialog(self,auto=False):
        print 'in showUpdateDialog'
        html = _("<h2>Red-R %s</h2><h4>Revision:%s; Date: %s</h4><br>%s") % (
        self.availableUpdate['redRVerion'],self.availableUpdate['SVNVersion'],
        self.availableUpdate['date'],self.availableUpdate['changeLog']) 
        wasUpdated=self.createDialog(html,True)
        
        return wasUpdated
        # elif not avaliable and not auto:
            # self.createDialog(_('You have the most current version of Red-R %s.') % self.version,False)

    def parseUpdatesXML(self,fileName):
        try:
            f = open(fileName, 'r')
            updatesXML = xml.dom.minidom.parse(f)
            f.close()
            # updatesXML = xml.dom.minidom.parseString(xml)
            update = {}
            update['redRVerion'] = self.getXMLText(updatesXML.getElementsByTagName('redRVerion')[0].childNodes)
            update['SVNVersion'] = self.getXMLText(updatesXML.getElementsByTagName('SVNVersion')[0].childNodes)
            update['date'] = self.getXMLText(updatesXML.getElementsByTagName('date')[0].childNodes)
            update['changeLog'] = self.getXMLText(updatesXML.getElementsByTagName('changeLog')[0].childNodes)
            if sys.platform=="win32":
                updatesNode = updatesXML.getElementsByTagName('win32')[0]
            elif sys.platform=="darwin":
                updatesNode = updatesXML.getElementsByTagName('mac')[0]
            elif sys.platform == 'linux2':
                updatesNode = updatesXML.getElementsByTagName('linux2')[0]
            if updatesNode and updatesNode != None:
                update['compiledFileName'] = self.getXMLText(updatesNode.getElementsByTagName('compiled')[0].childNodes)
                update['developerFileName'] = self.getXMLText(updatesNode.getElementsByTagName('src')[0].childNodes)
            return update
        except:
            return {}

    def getXMLText(self, nodelist):
        rc = ''
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
                
        rc = str(rc).strip()
        return rc

    def createDialog(self,html,avaliable):
        print 'in createDialog'
        width = 350
        height = 350
        changeLogBox = redRwebViewBox(self.main,label=_('Update'),displayLabel=False)
        changeLogBox.setMinimumWidth(width)
        changeLogBox.setMinimumHeight(width)
        changeLogBox.setHtml(html)
        
        buttonArea2 = redRwidgetBox(self.main,orientation = 'horizontal', 
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed),alignment=Qt.AlignRight)
        if avaliable:
            redRbutton(buttonArea2, label = _('Close Red-R and Update'), callback = self.accept)
        redRbutton(buttonArea2, label = _('Cancel'), callback = self.reject)
        
        
        desktop = self.app.desktop()
        deskH = desktop.screenGeometry(desktop.primaryScreen()).height()
        deskW = desktop.screenGeometry(desktop.primaryScreen()).width()
        h = max(0, deskH/2 - height/2)  # if the window is too small, resize the window to desktop size
        w = max(0, deskW/2 - width/2)
        self.move(w,h+2)
        self.show()
        print 'end createDialog'
        
    def accept(self):
        print 'accept'
        self.downloadUpdate(self.availableUpdate)
        redREnviron.settings['updateAvailable'] = False
        
    def reject(self):
        print 'reject'
        self.app.exit(0)
        
    def showNoUpdates(self):
        UpdatePopup = redRdialog(self.schema, title = _('Update Manager'))
        UpdatePopup.setMinimumWidth(350)
        UpdatePopup.setMinimumHeight(350)
        changeLogBox = redRwebViewBox(UpdatePopup)
        changeLogBox.setHtml(_('You have the most current version of Red-R %s.') % self.version)
        
        buttonArea2 = redRwidgetBox(UpdatePopup,orientation = 'horizontal', 
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed),alignment=Qt.AlignRight)
        
        redRbutton(buttonArea2, label = _('Done'), callback = UpdatePopup.reject)
        UpdatePopup.exec_()    
    def showNoInternet(self):
        UpdatePopup = redRdialog(self.schema, title = _('Update Manager'))
        UpdatePopup.setMinimumWidth(350)
        UpdatePopup.setMinimumHeight(350)
        changeLogBox = redRwebViewBox(UpdatePopup)
        changeLogBox.setHtml(_('No Internet Connection.'))
        
        buttonArea2 = redRwidgetBox(UpdatePopup,orientation = 'horizontal', 
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed),alignment=Qt.AlignRight)
        
        redRbutton(buttonArea2, label = _('Done'), callback = UpdatePopup.reject)
        UpdatePopup.exec_()
    def showUpdateAvaliable(self,update):
        UpdatePopup = redRdialog(self.schema, title = _('Update Manager'))
        
        changeLogBox = redRwebViewBox(UpdatePopup)
        changeLogBox.setMinimumWidth(350)
        changeLogBox.setMinimumHeight(350)
        html = _("<h2>Red-R %s</h2><h4>Revision:%s; Date: %s</h4>") % (
        update['redRVerion'],update['SVNVersion'],update['date']) 

        changeLogBox.setHtml(html +'<br>' +update['changeLog'])
        
        buttonArea2 = redRwidgetBox(UpdatePopup,orientation = 'horizontal', 
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed),alignment=Qt.AlignRight)
        
        redRbutton(buttonArea2, label = 'Close Red-R and Update', callback = UpdatePopup.accept)
        redRbutton(buttonArea2, label = _('Cancel'), callback = UpdatePopup.reject)
        if UpdatePopup.exec_() == QDialog.Accepted:
            self.downloadUpdate(update)
        
    def downloadUpdate(self,update):
        if redREnviron.version['TYPE'] =='compiled':
            url = update['compiledFileName']
            file = os.path.join(redREnviron.directoryNames['downloadsDir'],
            os.path.basename(update['compiledFileName']))
        else:
            url = update['developerFileName']
            file = os.path.join(redREnviron.directoryNames['downloadsDir'],
            os.path.basename(update['developerFileName']))
        
        # self.execUpdate(file)
        # return
        # print url, file
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
       
    def execUpdate(self,file):
        installDir = os.path.split(os.path.abspath(redREnviron.directoryNames['redRDir']))[0]
        # print installDir
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
        
        
        self.app.exit(1)

    def closeAndUpdate(self,file):
        qApp.canvasDlg.closeEvent(QCloseEvent(),postCloseFun=lambda:self.execUpdate(file))
        
    def replyFinished(self, reply,file,finishedFun):
        self.reply = reply
        output = open(file,'wb')
        alltext = self.reply.readAll()
        output.write(alltext)
        output.close()
        if finishedFun:
            finishedFun(file)

