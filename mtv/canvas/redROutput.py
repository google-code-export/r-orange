# Author: Gregor Leban (gregor.leban@fri.uni-lj.si) modified by Kyle R Covington and Anup Parikh
# Description:
#     print system output and exceptions into a window. Enables copy/paste
#
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import string
import time as ti
from datetime import tzinfo, timedelta, datetime, time
import traceback, redRExceptionHandling
import os.path, os
import redREnviron, log, SQLiteSession
from libraries.base.qtWidgets.button import button as redRbutton
from libraries.base.qtWidgets.checkBox import checkBox as redRcheckBox
from libraries.base.qtWidgets.widgetBox import widgetBox as redRwidgetBox
from libraries.base.qtWidgets.dialog import dialog as redRdialog
from libraries.base.qtWidgets.widgetLabel import widgetLabel as redRwidgetLabel
from libraries.base.qtWidgets.comboBox import comboBox as redRComboBox
from libraries.base.qtWidgets.radioButtons import radioButtons as redRradiobuttons
from libraries.base.qtWidgets.tabWidget import tabWidget as redRTabWidget
from libraries.base.qtWidgets.textEdit import textEdit as redRTextEdit
from libraries.base.qtWidgets.lineEdit import lineEdit as redRLineEdit

class OutputWindow(QDialog):
    def __init__(self, canvasDlg, *args):
        QDialog.__init__(self, None, Qt.Window)
        self.canvasDlg = canvasDlg
        
        self.defaultExceptionHandler = sys.excepthook
        self.defaultSysOutHandler = sys.stdout

        self.logFile = open(os.path.join(redREnviron.directoryNames['canvasSettingsDir'], "outputLog.html"), "w") # create the log file
        ### error logging setup ###
        self.errorDB = log.logDB()
        self.errorHandler = SQLiteSession.SQLiteHandler(defaultDB = self.errorDB)
        
        self.textOutput = QTextEdit(self)
        self.textOutput.setReadOnly(1)
        self.textOutput.zoomIn(1)
        self.allOutput = ''
        
        self.setLayout(QVBoxLayout())
        wb = redRwidgetBox(self)
        tw = redRTabWidget(wb)
        self.outputExplorer = tw.createTabPage('General Outputs')
        self.topWB = redRwidgetBox(self.outputExplorer, orientation = 'horizontal')
        self.tableCombo = redRComboBox(self.topWB, label = 'Table:', items = ['All_Output, table'], callback = self.processTable)
        self.tableCombo.update(self.errorHandler.getTableNames())
        self.minSeverity = redRComboBox(self.topWB, label = 'Minimum Severity:', items = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], callback = self.processTable)
        self.maxRecords = redRLineEdit(self.topWB, label = 'Maximum Records:', text = '100')
        self.typeCombo = redRComboBox(self.topWB, label = 'Output Type:', items = ['No Filter', 'Error', 'Comment', 'Message', 'Warning'], callback = self.processTable)
        #redRbutton(self.topWB, label = 'Refresh', callback = self.refresh)
        self.sessionID = redRradiobuttons(self.topWB, buttons = ['Current Session Only', 'All Sessions'], setChecked = 'Current Session Only', callback = self.processTable)
        redRbutton(self, label = 'Update View', callback = self.processTable)
        redRbutton(self.topWB, label = 'Clear DB', callback = self.clearDataBase)
        self.outputExplorer.layout().addWidget(self.textOutput)
        self.outputExplorer.layout().setMargin(2)
        self.setWindowTitle("Output Window")
        self.setWindowIcon(QIcon(canvasDlg.outputPix))
        self.exceptionTracker = tw.createTabPage('Exceptions')
        self.exceptionText = redRTextEdit(self.exceptionTracker)

        
        self.unfinishedText = ""
        
        w = h = 500
        if redREnviron.settings.has_key("outputWindowPos"):
            desktop = qApp.desktop()
            deskH = desktop.screenGeometry(desktop.primaryScreen()).height()
            deskW = desktop.screenGeometry(desktop.primaryScreen()).width()
            w, h, x, y = redREnviron.settings["outputWindowPos"]
            if x >= 0 and y >= 0 and deskH >= y+h and deskW >= x+w: 
                self.move(QPoint(x, y))
            else: 
                w = h = 500
        self.resize(w, h)
        self.lastTime = ti.time()
        self.hide()
        log.setOutputManager(self)
    def refresh(self):
        self.tableCombo.update(self.errorHandler.getTableNames())
        #print self.errorHandler.getTableNames()
        
    def processTable(self):
        if str(self.typeCombo.currentText()) != 'No Filter':
            if str(self.sessionID.getChecked()) == 'Current Session Only':
                response = self.errorHandler.execute(query = "SELECT * FROM %s WHERE Session == \"%s\" AND Severity >= %s AND ErrorType == \"%s\" ORDER BY k DESC LIMIT %s" % (str(self.tableCombo.currentText()).split(',')[0], log.getSessionID(), str(self.minSeverity.currentText()), str(self.typeCombo.currentText()), self.maxRecords.text()))
            else:
                response = self.errorHandler.execute(query = "SELECT * FROM %s WHERE Severity >= %s AND ErrorType == \"%s\" ORDER BY k DESC LIMIT %s" % (str(self.tableCombo.currentText()).split(',')[0], str(self.minSeverity.currentText()), str(self.typeCombo.currentText()), self.maxRecords.text()))
        else:
            if str(self.sessionID.getChecked()) == 'Current Session Only':
                response = self.errorHandler.execute(query = "SELECT * FROM %s WHERE Session == \"%s\" AND Severity >= %s ORDER BY k DESC LIMIT %s" % (str(self.tableCombo.currentText()).split(',')[0], log.getSessionID(), str(self.minSeverity.currentText()), self.maxRecords.text()))
            else:
                
                response = self.errorHandler.execute(query = "SELECT * FROM %s WHERE Severity >= %s ORDER BY k DESC LIMIT %s" % (str(self.tableCombo.currentText()).split(',')[0], str(self.minSeverity.currentText()), self.maxRecords.text()))
            
        self.showTable(response)
    def clearDataBase(self):
        log.clearDB()
    def showTable(self, response):
        htmlText = self.toHTMLTable(response)
        self.textOutput.clear()
        self.textOutput.insertHtml(htmlText)
    def toHTMLTable(self, response):
        
        s = '<h2>%s</h2>' % self.tableCombo.currentText()
        s+= '<table border="1" cellpadding="3">'
        s+= '  <tr><td><b>'
        s+= '    </b></td><td><b>'.join(['Log ID', 'Time Stamp', 'Session ID', 'Severity', 'Error Type', 'Message'])
        s+= '  </b></td></tr>'
        
        for row in response:
            s+= '  <tr><td>'
            s+= '    </td><td>'.join([str(i) for i in row])
            s+= '  </td></tr>'
        s+= '</table>'
        return s
    def stopCatching(self):
        self.catchException(0)
        self.catchOutput(0)

    def showEvent(self, ce):
        ce.accept()
        QDialog.showEvent(self, ce)
        settings = redREnviron.settings
        if settings.has_key("outputWindowPos"):
            w, h, x, y = settings["outputWindowPos"]
            self.move(QPoint(x, y))
            self.resize(w, h)
        
    def hideEvent(self, ce):
        redREnviron.settings["outputWindowPos"] = (self.width(), self.height(), self.pos().x(), self.pos().y())
        ce.accept()
        QDialog.hideEvent(self, ce)
                
    def closeEvent(self,ce):
        redREnviron.settings["outputWindowPos"] = (self.width(), self.height(), self.pos().x(), self.pos().y())
        if getattr(self.canvasDlg, "canvasIsClosing", 0):
            self.catchException(0)
            self.catchOutput(0)
            ce.accept()
            QDialog.closeEvent(self, ce)
        else:
            self.hide()

    def catchException(self, catch):
        if catch: sys.excepthook = self.exceptionHandler
        else:     sys.excepthook = self.defaultExceptionHandler

    def catchOutput(self, catch):
        if catch:    sys.stdout = self
        else:         sys.stdout = self.defaultSysOutHandler

    def clear(self):
        self.textOutput.clear()
        self.exceptionText.clear()

    # print text produced by warning and error widget calls
    def widgetEvents(self, text, eventVerbosity = 1):
        if redREnviron.settings["outputVerbosity"] >= eventVerbosity:
            if text != None:
                self.write(str(text))
            self.canvasDlg.setStatusBarEvent(QString(text))

    # simple printing of text called by print calls
    def safe_str(self,obj):
        try:
            return str(obj)
        except UnicodeEncodeError:
            # obj is unicode
            return unicode(obj).encode('unicode_escape')

    def write(self, text):
        text = self.safe_str(text)
        # if text[-1:] == "\n":
        
        self.allOutput += text.replace("\n", "<br>\n")
        # else:
            # self.allOutput += text + "\n"

        # if redREnviron.settings["writeLogFile"]:
            # log.log(3, 1, 2, text.replace("\n", "<br>\n"))
            
        #if not redREnviron.settings['debugMode']: return 
        
        import re
        m = re.search('^(\|(#+)\|\s?)(.*)',text)
        
        
        if redREnviron.settings["focusOnCatchOutput"]:
            self.canvasDlg.menuItemShowOutputWindow()

        # cursor = QTextCursor(self.exceptionText.textCursor())                
        # cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      
        # self.exceptionText.setTextCursor(cursor)                             
        # if re.search('#'*60 + '<br>',text):
            # self.exceptionText.insertHtml(text)                              
        # else:
            # self.exceptionText.insertPlainText(text)                              
        # cursor = QTextCursor(self.exceptionText.textCursor())                
        # cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      
        
        if m:
            log.log(3, len(m.group(2)), 2, text)
        else:
            log.log(3, 1, 2, text)
            
        if text[-1:] == "\n":
            if redREnviron.settings["printOutputInStatusBar"]:
                self.canvasDlg.setStatusBarEvent(self.unfinishedText + text)
            self.unfinishedText = ""
        else:
            self.unfinishedText += text
            
        # if ti.time() - self.lastTime > 10:
            # self.processTable()

    def flush(self):
        pass
    
    def getSafeString(self, s):
        return str(s).replace("<", "&lt;").replace(">", "&gt;")

    def uploadYes(self):
        self.msg.done(1)

    def uploadNo(self):
        self.msg.done(0)
    def rememberResponse(self):
        if 'Remember my Response' in self.remember.getChecked():
            self.checked = True
            redREnviron.settings['askToUploadError'] = 0

        else:
            self.checked = False
        
    def uploadException(self,err):
        import httplib,urllib
        import sys,pickle,os, re
        #print redREnviron.settings['askToUploadError'], 'askToUploadError'
        #print redREnviron.settings['uploadError'], 'uploadError'
        if not redREnviron.settings['askToUploadError']:
            res = redREnviron.settings['uploadError']
        else:
            self.msg = redRdialog(parent=self,title='Red-R Error')
            
            error = redRwidgetBox(self.msg,orientation='vertical')
            redRwidgetLabel(error, label='Do you wish to report the Error Log?')
            buttons = redRwidgetBox(error,orientation='horizontal')

            redRbutton(buttons, label = 'Yes', callback = self.uploadYes)
            redRbutton(buttons, label = 'No', callback = self.uploadNo)
            self.checked = False
            self.remember = redRcheckBox(error,buttons=['Remember my Response'],callback=self.rememberResponse)
            res = self.msg.exec_()
            redREnviron.settings['uploadError'] = res
        #print res
        if res == 1:
            #print 'in res'
            err['version'] = redREnviron.version['SVNVERSION']
            err['type'] = redREnviron.version['TYPE']
            err['redRversion'] = redREnviron.version['REDRVERSION']
            #print err['traceback']
            
            
            ##err['output'] = self.allOutput
            if os.name == 'nt':
                err['os'] = 'Windows'
            # else:
                # err['os'] = 'Not Specified'
            if redREnviron.settings['canContact']:
                err['email'] = redREnviron.settings['email']
            # else:
                # err['email'] = 'None; no contact'
            #err['id'] = redREnviron.settings['id']
            #print err, 'Error'
            params = urllib.urlencode(err)
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            conn = httplib.HTTPConnection("localhost",80)
            conn.request("POST", "/errorReport.php", params,headers)
            #print err
            # response = conn.getresponse()
            # print response.status, response.reason
            # data = response.read()
            # print data
            # conn.close()
        else:
            return
        
    def exceptionHandler(self, type, value, tracebackInfo):
        if redREnviron.settings["focusOnCatchException"]:
            self.canvasDlg.menuItemShowOutputWindow()

        text = redRExceptionHandling.formatException(type,value,tracebackInfo)
        log.log(3,9,1,text)
        
        t = datetime.today().isoformat(' ')
        toUpload = {}
        #toUpload['time'] = t
        toUpload['errorType'] = self.getSafeString(type.__name__)
        toUpload['traceback'] = text
        toUpload['file'] = os.path.split(traceback.extract_tb(tracebackInfo, 10)[0][0])[1]
        
        if redREnviron.settings["printExceptionInStatusBar"]:
            self.canvasDlg.setStatusBarEvent("Unhandled exception of type %s occured at %s. See output window for details." % ( str(type) , t))

        
        cursor = QTextCursor(self.exceptionText.textCursor())                # clear the current text selection so that
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      # the text will be appended to the end of the
        self.exceptionText.setTextCursor(cursor)                             # existing text
        self.exceptionText.insertHtml(text)                                  # then append the text
        cursor = QTextCursor(self.exceptionText.textCursor())                # clear the current text selection so that
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      # the text will be appended to the end of the
        self.exceptionText.setTextCursor(cursor)
        
        if redREnviron.settings["writeLogFile"]:
            self.logFile.write(str(text) + "<br>\n")
        
        self.uploadException(toUpload)

        
