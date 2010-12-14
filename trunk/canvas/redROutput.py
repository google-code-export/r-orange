from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import string
import time as ti
from datetime import tzinfo, timedelta, datetime, time
import traceback, redRExceptionHandling
import os.path, os
import redREnviron, redRLog, SQLiteSession
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
        self.errorDB = redRLog.logDB()
        self.errorHandler = SQLiteSession.SQLiteHandler(defaultDB = self.errorDB)
        
        self.textOutput = QTextEdit(self)
        self.textOutput.setReadOnly(1)
        self.textOutput.zoomIn(1)
        self.allOutput = ''
        
        self.setLayout(QVBoxLayout())
        wb = redRwidgetBox(self)
        self.tw = redRTabWidget(wb)
        self.outputExplorer = self.tw.createTabPage('General Outputs')
        self.topWB = redRwidgetBox(self.outputExplorer, orientation = 'horizontal')
        self.tableCombo = redRComboBox(self.topWB, label = 'Table:', items = ['All'] + [row[0] for row in self.errorHandler.execute('SELECT DISTINCT OutputDomain FROM All_Output')], callback = self.processTable)
        #self.tableCombo.update(self.errorHandler.getTableNames())
        self.minSeverity = redRComboBox(self.topWB, label = 'Minimum Severity:', items = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], callback = self.processTable)
        self.maxRecords = redRLineEdit(self.topWB, label = 'Maximum Records:', text = '100')
        self.typeCombo = redRComboBox(self.topWB, label = 'Output Type:', items = ['No Filter', 'Error', 'Comment', 'Message', 'Warning'], callback = self.processTable)
        redRbutton(self.topWB, label = 'Refresh', callback = self.refresh)
        self.sessionID = redRradiobuttons(self.topWB, label = 'Session ID', displayLabel = False, buttons = ['Current Session Only', 'All Sessions'], setChecked = 'Current Session Only', callback = self.processTable)
        redRbutton(self, label = 'Update View', callback = self.processTable)
        redRbutton(self.topWB, label = 'Clear DB', callback = self.clearDataBase)
        self.outputExplorer.layout().addWidget(self.textOutput)
        self.outputExplorer.layout().setMargin(2)
        self.setWindowTitle("Output Window")
        self.setWindowIcon(QIcon( os.path.join(redREnviron.directoryNames["canvasDir"], "icons", "output.png")))
        self.exceptionTracker = self.tw.createTabPage('Exceptions')
        self.exceptionText = redRTextEdit(self.exceptionTracker, label = 'Exception Text', displayLabel = False)

        
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
    
    def outputManager(self, table, severity, errorType, tb, comment):
        # if errorType == log.ERROR and redREnviron.settings["focusOnCatchException"]:
            # qApp.canvasDlg.menuItemShowOutputWindow()
        
        string = '<div style="color:#0000FF">%s:%s:%s: </div>' %  (redRLog.tables[table],redRLog.errorTypes[errorType], severity)
        if redREnviron.settings['debugMode']:
            string+='\t%s' % tb[-3]
            
        string +='\t<b>%s</b>' % (self.getSafeString(comment))
        
        cursor = QTextCursor( self.canvasDlg.printOutput.textCursor())                
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      
        self.canvasDlg.printOutput.setTextCursor(cursor)                             
        self.canvasDlg.printOutput.insertHtml('%s<br>' % string)
    
    def setStatusBarEvent(self, text):
        
        if text == "" or text == None:
            self.canvasDlg.statusBar.showMessage("")
            return
        elif text == "\n": return
        text = unicode(text)
        text = text.replace("<nobr>", ""); text = text.replace("</nobr>", "")
        text = text.replace("<b>", ""); text = text.replace("</b>", "")
        text = text.replace("<i>", ""); text = text.replace("</i>", "")
        text = text.replace("<br>", ""); text = text.replace("&nbsp", "")
        self.canvasDlg.statusBar.showMessage("Last event: " + unicode(text), 5000)
        
    def showExceptionTab(self):
        self.tw.setCurrentIndex(1)
    def refresh(self):
        self.tableCombo.update(['All'] + [row[0] for row in self.errorHandler.execute('SELECT DISTINCT OutputDomain FROM All_Output')])
        #print self.errorHandler.getTableNames()
        
    def processTable(self):
        inj = []
        if unicode(self.typeCombo.currentText()) != 'No Filter':
            inj.append('ErrorType == \"%s\"' % self.typeCombo.currentText())
        if unicode(self.tableCombo.currentText()) != 'All':
            inj.append('OutputDomain == \"%s\"' % self.tableCombo.currentText())
        inj.append('Severity >= %s' % unicode(self.minSeverity.currentText()))
        query = "SELECT * FROM All_Output WHERE "+" AND ".join(inj)+" ORDER BY k DESC LIMIT %s" % (self.maxRecords.text())
        response = self.errorHandler.execute(query = query)
        #print query

            
        self.showTable(response)
    def clearDataBase(self):
        redRLog.clearDB()
    def showTable(self, response):
        htmlText = self.toHTMLTable(response)
        self.textOutput.clear()
        self.textOutput.insertHtml(htmlText)
    def toHTMLTable(self, response):
        
        s = '<h2>%s</h2>' % self.tableCombo.currentText()
        s+= '<table border="1" cellpadding="3">'
        s+= '  <tr><td><b>'
        s+= '    </b></td><td><b>'.join(['Log ID', 'Output Category', 'Time Stamp', 'Session ID', 'Severity', 'Message Type', 'Message', 'Traceback'])
        s+= '  </b></td></tr>'
        
        for row in response:
            s+= '  <tr><td>'
            s+= '    </td><td>'.join([unicode(i) for i in row])
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
        return
        if catch:    sys.stdout = self
        else:         sys.stdout = self.defaultSysOutHandler

    def clear(self):
        self.textOutput.clear()
        self.exceptionText.clear()

    # print text produced by warning and error widget calls
    def widgetEvents(self, text, eventVerbosity = 1):
        if redREnviron.settings["outputVerbosity"] >= eventVerbosity:
            if text != None:
                self.write(unicode(text))
            self.setStatusBarEvent(QString(text))

    # simple printing of text called by print calls
    def safe_unicode(self,obj):
        try:
            return unicode(obj)
        except UnicodeEncodeError:
            # obj is unicode
            return unicode(obj).encode('unicode_escape')

    def write(self, text):
        return

    def flush(self):
        pass
    
    def getSafeString(self, s):
        return unicode(s).replace("<", "&lt;").replace(">", "&gt;")

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
        try:
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
                
            else:
                return
        except: pass
    def exceptionHandler(self, type, value, tracebackInfo):
        print 'Exception Occured, please see the output for more details.\n'
        if redREnviron.settings["focusOnCatchException"]:
            self.canvasDlg.menuItemShowOutputWindow()

        text = redRExceptionHandling.formatException(type,value,tracebackInfo)
        redRLog.log(3,9,1,text)
        
        t = datetime.today().isoformat(' ')
        toUpload = {}
        #toUpload['time'] = t
        toUpload['errorType'] = self.getSafeString(type.__name__)
        toUpload['traceback'] = text
        #toUpload['file'] = os.path.split(traceback.extract_tb(tracebackInfo, 10)[0][0])[1]
        
        if redREnviron.settings["printExceptionInStatusBar"]:
            self.setStatusBarEvent("Unhandled exception of type %s occured at %s. See output window for details." % ( unicode(type) , t))

        
        cursor = QTextCursor(self.exceptionText.textCursor())                # clear the current text selection so that
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      # the text will be appended to the end of the
        self.exceptionText.setTextCursor(cursor)                             # existing text
        self.exceptionText.insertHtml(text)                                  # then append the text
        cursor = QTextCursor(self.exceptionText.textCursor())                # clear the current text selection so that
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      # the text will be appended to the end of the
        self.exceptionText.setTextCursor(cursor)
        
        if redREnviron.settings["writeLogFile"]:
            self.logFile.write(unicode(text) + "<br>\n")
        
        self.uploadException(toUpload)

        
