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
import os.path, os, redRGUI, redREnviron

class OutputWindow(QDialog):
    def __init__(self, canvasDlg, *args):
        QDialog.__init__(self, None, Qt.Window)
        self.canvasDlg = canvasDlg

        self.textOutput = QTextEdit(self)
        self.textOutput.setReadOnly(1)
        self.textOutput.zoomIn(1)
        self.allOutput = ''
        
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.textOutput)
        self.layout().setMargin(2)
        self.setWindowTitle("Output Window")
        self.setWindowIcon(QIcon(canvasDlg.outputPix))

        self.defaultExceptionHandler = sys.excepthook
        self.defaultSysOutHandler = sys.stdout

        self.logFile = open(os.path.join(redREnviron.directoryNames['canvasSettingsDir'], "outputLog.html"), "w") # create the log file
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
            
        self.hide()

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

    # print text produced by warning and error widget calls
    def widgetEvents(self, text, eventVerbosity = 1):
        if redREnviron.settings["outputVerbosity"] >= eventVerbosity:
            if text != None:
                self.write(str(text))
            self.canvasDlg.setStatusBarEvent(QString(text))

    # simple printing of text called by print calls
    def write(self, text):
            
        # if text[-1:] == "\n":
        self.allOutput += text.replace("\n", "<br>\n")
        # else:
            # self.allOutput += text + "\n"

        if redREnviron.settings["writeLogFile"]:
            self.logFile.write(text.replace("\n", "<br>\n"))
            
        if not redREnviron.settings['debugMode']: return 
        
        import re
        m = re.search('^(\|(#+)\|\s?)(.*)',text)
        if redREnviron.settings['outputVerbosity'] ==0:
            if m:
                text = str(m.group(3))
            
        elif m and len(m.group(2)) >= redREnviron.settings['outputVerbosity']:
            # text = '\n len:' + str(len(m.group(2))) + '\n outputVerbosity:' + str(redREnviron.settings['outputVerbosity']+1) + '\n output:'+ str(m.group(3)) + "\n print:" + str(len(m.group(2)) >= (redREnviron.settings['outputVerbosity'])+1)
            text = str(m.group(3)) + "\n"
        else:
            return

        
        if redREnviron.settings["focusOnCatchOutput"]:
            self.canvasDlg.menuItemShowOutputWindow()


        
        cursor = QTextCursor(self.textOutput.textCursor())                # clear the current text selection so that
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      # the text will be appended to the end of the
        self.textOutput.setTextCursor(cursor)                             # existing text
        self.textOutput.insertPlainText(text)                                  # then append the text
        cursor = QTextCursor(self.textOutput.textCursor())                # clear the current text selection so that
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      # the text will be appended to the end of the
        if text[-1:] == "\n":
            if redREnviron.settings["printOutputInStatusBar"]:
                self.canvasDlg.setStatusBarEvent(self.unfinishedText + text)
            self.unfinishedText = ""
        else:
            self.unfinishedText += text
            

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
        import sys,pickle,os

        if not redREnviron.settings['askToUploadError']:
            res = redREnviron.settings['uploadError']
        else:
            self.msg = redRGUI.dialog(parent=self,title='Red-R Error')
            
            error = redRGUI.widgetBox(self.msg,orientation='vertical')
            redRGUI.widgetLabel(error, label='Do you wish to report the Error Log?')
            buttons = redRGUI.widgetBox(error,orientation='horizontal')

            redRGUI.button(buttons, label = 'Yes', callback = self.uploadYes)
            redRGUI.button(buttons, label = 'No', callback = self.uploadNo)
            self.checked = False
            self.remember = redRGUI.checkBox(error,buttons=['Remember my Response'],callback=self.rememberResponse)
            res = self.msg.exec_()
            redREnviron.settings['uploadError'] = res
            
        if res == 1:
            err['version'] = redREnviron.version['SVNVERSION']
            err['type'] = redREnviron.version['TYPE']
            err['output'] = self.allOutput
            err['os'] = os.name
            params = urllib.urlencode(err)
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            conn = httplib.HTTPConnection("www.red-r.org",80)
            conn.request("POST", "/errorReport.php", params,headers)
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
        # print 'exceptionHandler'
        # traceback.extract_tb(tracebackInfo)
        # print type, value
        #traceback.print_exception(type,value,tracebackInfo)
        toUpload = {}
        t = datetime.today().isoformat(' ')
        text = "Unhandled exception of type %s occured at %s:<br>Traceback:<br>\n" % ( self.getSafeString(type.__name__), t)

        toUpload['time'] = t
        toUpload['errorType'] = self.getSafeString(type.__name__)

        
        if redREnviron.settings["printExceptionInStatusBar"]:
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
            text += "" + totalSpace + "File: <b>" + filename + "</b>, line %4d" %(line) + " in <b>%s</b><br>\n" % (self.getSafeString(funct))
            if code != None:
                code = code.replace('<', '&lt;') #convert for html
                code = code.replace('>', '&gt;')
                code = code.replace("\t", "\x5ct") # convert \t to unicode \t
                text += "" + totalSpace + "Code: " + code + "<br>\n"
            totalSpace += space
        #print '-'*60, text
        lines = traceback.format_exception_only(type, value)
        for line in lines[:-1]:
            text += "" + totalSpace + self.getSafeString(line) + "<br>\n"
        text += "<b>" + totalSpace + self.getSafeString(lines[-1]) + "</b><br>\n"

        toUpload['traceback'] = text
        
        
        cursor = QTextCursor(self.textOutput.textCursor())                # clear the current text selection so that
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      # the text will be appended to the end of the
        self.textOutput.setTextCursor(cursor)                             # existing text
        self.textOutput.insertHtml(text)                                  # then append the text
        cursor = QTextCursor(self.textOutput.textCursor())                # clear the current text selection so that
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      # the text will be appended to the end of the

        if redREnviron.settings["writeLogFile"]:
            self.logFile.write(str(text) + "<br>\n")
        
        self.uploadException(toUpload)

        
def printException():
    import sys, traceback
    print '-'*60
    traceback.print_exc(file=sys.stdout)
    print '-'*60        
