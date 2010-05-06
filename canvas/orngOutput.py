# Author: Gregor Leban (gregor.leban@fri.uni-lj.si) modified by Kyle R Covington and Anup Parikh
# Description:
#     print system output and exceptions into a window. Enables copy/paste
#
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import string
from datetime import tzinfo, timedelta, datetime
import traceback
import os.path, os

class OutputWindow(QDialog):
    def __init__(self, canvasDlg, *args):
        QDialog.__init__(self, None, Qt.Window)
        self.canvasDlg = canvasDlg

        self.textOutput = QTextEdit(self)
        self.textOutput.setReadOnly(1)
        self.textOutput.zoomIn(1)
        self.numberofLines = 0
        self.debugMode = 0

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.textOutput)
        self.layout().setMargin(2)
        self.setWindowTitle("Output Window")
        self.setWindowIcon(QIcon(canvasDlg.outputPix))

        self.defaultExceptionHandler = sys.excepthook
        self.defaultSysOutHandler = sys.stdout

        self.logFile = open(os.path.join(canvasDlg.canvasSettingsDir, "outputLog.html"), "w") # create the log file
        self.unfinishedText = ""
        
        w = h = 500
        if canvasDlg.settings.has_key("outputWindowPos"):
            desktop = qApp.desktop()
            deskH = desktop.screenGeometry(desktop.primaryScreen()).height()
            deskW = desktop.screenGeometry(desktop.primaryScreen()).width()
            w, h, x, y = canvasDlg.settings["outputWindowPos"]
            if x >= 0 and y >= 0 and deskH >= y+h and deskW >= x+w: 
                self.move(QPoint(x, y))
            else: 
                w = h = 500
        self.resize(w, h)
            
        self.hide()

    def stopCatching(self):
        self.catchException(0)
        self.catchOutput(0)

    def showEvent(self, ce):
        ce.accept()
        QDialog.showEvent(self, ce)
        settings = self.canvasDlg.settings
        if settings.has_key("outputWindowPos"):
            w, h, x, y = settings["outputWindowPos"]
            self.move(QPoint(x, y))
            self.resize(w, h)
        
    def hideEvent(self, ce):
        self.canvasDlg.settings["outputWindowPos"] = (self.width(), self.height(), self.pos().x(), self.pos().y())
        ce.accept()
        QDialog.hideEvent(self, ce)
                
    def closeEvent(self,ce):
        self.canvasDlg.settings["outputWindowPos"] = (self.width(), self.height(), self.pos().x(), self.pos().y())
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

    # print text produced by warning and error widget calls
    def widgetEvents(self, text, eventVerbosity = 1):
        if self.canvasDlg.settings["outputVerbosity"] >= eventVerbosity:
            if text != None:
                self.write(str(text))
            self.canvasDlg.setStatusBarEvent(QString(text))

    # simple printing of text called by print calls
    def write(self, text):
        # print text
        #return
        if '#--#' in text and self.debugMode == 0:  # a convenience function that will suppress printing of things that should be in debug this allows the user to set a flag that distinguishes printing of normal things from printing debug things.  Kind of a hack I know but it should work in most places.
            return 
        self.numberofLines += 1
        # if self.numberofLines > 1000 and not self.debugMode:
            # self.textOutput.clear()
            # self.numberofLines = 0
        Text = text #self.getSafeString(text)
        #Text = Text.replace("\n", "<br>\n")   # replace new line characters with <br> otherwise they don't get shown correctly in html output
        
        #text = "<nobr>" + text + "</nobr>"
        
        if self.canvasDlg.settings["focusOnCatchOutput"]:
            self.canvasDlg.menuItemShowOutputWindow()

        if self.canvasDlg.settings["writeLogFile"]:
            self.logFile.write(Text.replace("\n", "<br>\n"))

        
        cursor = QTextCursor(self.textOutput.textCursor())                # clear the current text selection so that
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      # the text will be appended to the end of the
        self.textOutput.setTextCursor(cursor)                             # existing text
        self.textOutput.insertPlainText(Text)                                  # then append the text
        cursor = QTextCursor(self.textOutput.textCursor())                # clear the current text selection so that
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      # the text will be appended to the end of the
        if Text[-1:] == "\n":
            if self.canvasDlg.settings["printOutputInStatusBar"]:
                self.canvasDlg.setStatusBarEvent(self.unfinishedText + text)
            self.unfinishedText = ""
        else:
            self.unfinishedText += text
            
        

    # def writelines(self, lines):
        # for line in lines:
            # self.numberofLines += 1
            # self.write(line)
            # if self.numberofLines > 1000 and not self.debugMode:
                # self.textOutput.clear()

    def flush(self):
        pass
    
    def getSafeString(self, s):
        return str(s).replace("<", "&lt;").replace(">", "&gt;")

    def uploadException(self,err):
        import httplib,urllib
        import sys,pickle
        res = QMessageBox.question(self, 'RedR Error','Do you wish to send the output to the developers?', QMessageBox.Yes, QMessageBox.No)
        #res = QMessageBox.No
        if res == QMessageBox.Yes:
            err.update(self.canvasDlg.version)
            err['template'] = ''
            
            params = urllib.urlencode(err)
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            conn = httplib.HTTPConnection("www.red-r.org",80)
            conn.request("POST", "/errorReport.php", params,headers)
            response = conn.getresponse()
            print response.status, response.reason
            data = response.read()
            print data
            conn.close()
        else:
            return
        
    def exceptionHandler(self, type, value, tracebackInfo):
        if self.canvasDlg.settings["focusOnCatchException"]:
            self.canvasDlg.menuItemShowOutputWindow()
        # print 'exceptionHandler'
        # traceback.extract_tb(tracebackInfo)
        # print type, value
        #traceback.print_exception(type,value,tracebackInfo)
        toUpload = {}
        t = datetime.today().isoformat(' ')
        text = "<nobr>Unhandled exception of type %s occured at %s:</nobr><br><nobr>Traceback:</nobr><br>\n" % ( self.getSafeString(type.__name__), t)

        toUpload['time'] = t
        toUpload['errorType'] = self.getSafeString(type.__name__)

        
        if self.canvasDlg.settings["printExceptionInStatusBar"]:
            self.canvasDlg.setStatusBarEvent("Unhandled exception of type %s occured at %s. See output window for details." % ( str(type) , t))

        

        list = traceback.extract_tb(tracebackInfo, 10)
        #print list
        space = "&nbsp; "
        totalSpace = space
        #print range(len(list))
        for i in range(len(list)):
            # print list[i]
            (file, line, funct, code) = list[i]
            #print 'code', code
            
            (dir, filename) = os.path.split(file)
            text += "<nobr>" + totalSpace + "File: <b>" + filename + "</b>, line %4d" %(line) + " in <b>%s</b></nobr><br>\n" % (self.getSafeString(funct))
            if code != None:
                code = code.replace('<', '&lt;') #convert for html
                code = code.replace('>', '&gt;')
                code = code.replace("\t", "\x5ct") # convert \t to unicode \t
                text += "<nobr>" + totalSpace + "Code: " + code + "</nobr><br>\n"
            totalSpace += space
        #print '-'*60, text
        lines = traceback.format_exception_only(type, value)
        for line in lines[:-1]:
            text += "<nobr>" + totalSpace + self.getSafeString(line) + "</nobr><br>\n"
        text += "<nobr><b>" + totalSpace + self.getSafeString(lines[-1]) + "</b></nobr><br>\n"

        toUpload['traceback'] = text
        self.uploadException(toUpload)
        
        cursor = QTextCursor(self.textOutput.textCursor())                # clear the current text selection so that
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      # the text will be appended to the end of the
        self.textOutput.setTextCursor(cursor)                             # existing text
        self.textOutput.insertHtml(text)                                  # then append the text
        cursor = QTextCursor(self.textOutput.textCursor())                # clear the current text selection so that
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      # the text will be appended to the end of the

        if self.canvasDlg.settings["writeLogFile"]:
            self.logFile.write(str(text) + "<br>\n")
