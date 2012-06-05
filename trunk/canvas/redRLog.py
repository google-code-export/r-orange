"""redRLog

Handles the standard output and error and redirects it to the various output managers. 

"""

import redREnviron, os, traceback, sys, redR
from datetime import tzinfo, timedelta, datetime
#
#Red-R output writers
_outputWriter = {}
_logTriggers = {}
# _outputDockWriter = None
# _outputWindowWriter = None
# _outputWindow = None

##Error Tables
REDRCORE = 1
R = 2
REDRWIDGET =3

tables = {REDRCORE: 'REDRCORE', R:'R',REDRWIDGET:'REDRWIDGET'}


##Error Type
CRITICAL = 50
ERROR	 = 40	
WARNING	 = 30	
INFO	 = 20	
DEBUG	 = 10	
DEVEL	 = 0	

logLevels = [CRITICAL,ERROR,WARNING,INFO,DEBUG,DEVEL]
logLevelsName = ['CRITICAL','ERROR','WARNING','INFO','DEBUG','DEVEL']
logLevelsByLevel = dict(zip(logLevels,logLevelsName))
logLevelsByName = dict(zip(logLevelsName,logLevels))

#print 'loading defs'

def setLogTrigger(name,manager,level):
    """Create a trigger for a certain level. Given a log entry of some level, execute manager."""
    global _logTriggers
    _logTriggers[name] = {'level':level,'trigger':manager}

def removeOutputManager(name):
    """Remove a log output manager"""
    if name in _outputWriter.keys():
        del _outputWriter[name]
def setOutputManager(name,manager,level=None):
    """Add log output manager"""
    global _outputWriter
    _outputWriter[name] = {'level':level,'writer':manager}
    
def log(table, logLevel = INFO, comment ='', widget=None, html=True):   
    """Create a log entry."""
    if redREnviron.settings['displayTraceback']:
        stack = traceback.format_stack()
    else:
        stack = None

    formattedLog = formatedLogOutput(table, logLevel, stack, comment, html)    

    logOutput(table, logLevel, formattedLog,html=True)
    logTrigger(table, logLevel)
    if logLevel >= ERROR:
        errorSubmitter(table, logLevel, comment)

def logTrigger(table,logLevel):
    """Execute log trigger with level > logLevel."""
    global _logTriggers
    for trigger in _logTriggers.values():
        if logLevel >= logLevels[logLevels.index(trigger['level'])]:
            trigger['trigger'](table,logLevel)

def logOutput(table, logLevel, comment,html=False):
    """Execute all log writers."""
    global _outputWriter
    # print logLevel, logLevels[redREnviron.settings['outputVerbosity']]
    for writer in _outputWriter.values():
        #print writer
        if writer['level']:
            if logLevel >= logLevels[logLevels.index(writer['level'])]:
                # print 'asdfasdf', writer['level'], logLevels[logLevels.index(writer['level'])]
                writer['writer'](table,logLevel,comment,html)
        else:
            if logLevel >= logLevels[redREnviron.settings['outputVerbosity']]:
                writer['writer'](table,logLevel,comment,html)
    
def formatedLogOutput(table, logLevel, stack, comment, html):
    """Format Log entry for output."""
    """Format Log entry for output."""
    # if logLevel == DEBUG:
        # comment = comment.rstrip('\n') + '<br>'
    
    if not html:
        comment = getSafeString(comment)
    if logLevel == CRITICAL:
        color = '#FF0000'
    else:
        color = "#0000FF"
    string = '<span style="color:%s">%s:%s </span>: ' %  (color, tables.get(table,'NOTABLE'),logLevelsByLevel.get(logLevel,'NOSET'))
    if stack and len(stack) >= 3:
        string += '%s || ' % (getSafeString(stack[-3]))
    else:
        string += unicode(stack)
    string += '%s<br>' % (comment) 
    return string
    
def getSafeString(s):
    """Escape log strings for HTML."""
    try:
        return unicode(s, errors='ignore').replace("<", "&lt;").replace(">", "&gt;").encode('ascii', 'ignore')
    except Exception as inst:
        print unicode(inst)
        return unicode(s).encode('ascii', 'ignore') ## can't convert the string so we just return it and hope for the best.

def formatException(type=None, value=None, tracebackInfo=None, errorMsg = None, plainText=False):
    """Format Exception for output."""
    if not tracebackInfo:
        (type,value, tracebackInfo) =  sys.exc_info()
    
    t = datetime.today().isoformat(' ')
    text =  '<br>'*2 + '#'*60 + '<br>'
    if errorMsg:
        text += '<b>' + errorMsg + '</b><br>'
    text += "Unhandled exception of type %s occured at %s:<br>Traceback:<br>" % ( getSafeString(type.__name__), t)
    list = traceback.extract_tb(tracebackInfo, 10)
    space = "&nbsp; "
    totalSpace = space
    for i in range(len(list)):
        # print list[i]
        (file, line, funct, code) = list[i]
        #print _('code'), code
        
        (dir, filename) = os.path.split(file)
        text += "" + totalSpace + "File: <b>" + filename + "</b>, line %4d" %(line) + " in <b>%s</b><br>" % (getSafeString(funct))
        if code != None:
            if not plainText:
                code = code.replace('<', '&lt;') #convert for html
                code = code.replace('>', '&gt;')
                code = code.replace("\t", "\x5ct") # convert \t to unicode \t
            text += "" + totalSpace + "Code: " + code + "<br>"
        totalSpace += space
    
    lines = traceback.format_exception_only(type, value)
    for line in lines[:-1]:
        text += "" + totalSpace + getSafeString(line) + "<br>"
    text += "<b>" + totalSpace + getSafeString(lines[-1]) + "</b><br>"
    
    text +=  '#'*60 + '<br>'*2
    if plainText:
        text = re.sub('<br>','\n',text)
        text = re.sub('&nbsp;','',text)
        
        text = re.sub("</?[^\W].{0,10}?>", "", text)
        return text
    else:
        return text
    
    
class LogHandler():
    """Captures standard out and error and redirects to logging system.

    Redirects the standard out and error to output writers. Also manages the default output writing to log files. Setting output log files and removing old log files.
    """
    def __init__(self):
        ########## system specific, resetting except hook kills linux #########
        ##### if linux  #######
        self.defaultStdout = sys.stdout
        self.defaultExceptionHandler = sys.excepthook
        sys.stdout = self
        sys.excepthook = self.exceptionHandler
  
        # self.currentLogFile = redREnviron.settings['logFile']
        self.clearOldLogs()
        # create the log file
        self.logFilename = "outputLog_%s.html" % redREnviron.settings['id']
        self.openLogFile()
        
    def moveLogFile(self,oldDir, newDir):
        # print 'aaaaaaaaaaa', oldDir,newDir
        if not self.logFile: return
        self.logFile.close()
        os.rename(os.path.join(oldDir,self.logFilename), os.path.join(newDir,self.logFilename))
        self.logFile = open(os.path.join(newDir,self.logFilename), "a")
    def openLogFile(self):
        self.logFile = open(os.path.join(redREnviron.settings['logsDir'],self.logFilename),"w")

    def closeLogFile(self):
        if self.logFile:
            self.logFile.close()
            removeOutputManager('file')
            #os.remove(redREnviron.settings['logFile'])
        
    def closeLogger(self):
        if sys.platform == 'win32':
            sys.stdout = self.defaultStdout
    
    def showLogFile(self):
        ## open a browser to show the log file.
        import webbrowser
        webbrowser.open(unicode(os.path.join(redREnviron.settings['logsDir'],self.logFilename)))
        
    def clearOldLogs(self):
        ## check the mod date for all of the logs in the log directory and remove those that are older than the max number of days.
        import glob
        import time
        for f in glob.glob(redREnviron.settings['logsDir']+'/*.html'):
            if int(redREnviron.settings['keepForXDays']) > -1 and time.time() - os.path.getmtime(f) > 60*60*24*int(redREnviron.settings['keepForXDays']):
                try:
                    os.remove(f)
                    #print 'file %s removed\n' % f
                except Exception as inst:
                    print unicode(inst)
    
    
    #ONLY FOR DEVEL print statements
    def writetoFile(self,table,logLevel,comment,html):
        if not redREnviron.settings["writeLogFile"]: return
        
        if not self.logFile:
            self.openLogFile()
        
        self.logFile.write(unicode(comment).encode('Latin-1')+'<br>')
    
    def flush(self):
        pass
    def write(self, text):
        try:
            import redREnviron
            global logOutput
            try:
                if logLevels[redREnviron.settings['outputVerbosity']] != DEVEL:
                    return
            except Exception as inst:
                logOutput(REDRCORE, DEVEL, text = unicode(inst))
                return
            logOutput(REDRCORE,DEVEL, text,html=False)
            if logLevels[redREnviron.settings['outputVerbosity']] == DEVEL:
                self.defaultStdout.write(text)
        except: pass
    def exceptionHandler(self, type, value, tracebackInfo):
        
        log(REDRCORE,CRITICAL,formatException(type,value,tracebackInfo))
        if logLevels[redREnviron.settings['outputVerbosity']] == DEVEL or redR.LOADING:
            self.defaultExceptionHandler(type, value, tracebackInfo)
        
fileLogger = LogHandler()
setOutputManager('file',fileLogger.writetoFile,level=DEVEL)

###########################
### Error Submission ######
###########################

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import string
import time as ti
from datetime import tzinfo, timedelta, datetime, time
import redRi18n
import httplib,urllib
import re

def errorSubmitter(table, level, string):
    global tables
    global logLevelsByLevel
    a = redRSubmitErrors()
    a.uploadException({'errorType':'%s.%s' % (tables[table],logLevelsByLevel[level]),'traceback':string})
    
class redRSubmitErrors():
    def __init__(self):
        pass
        
    def uploadYes(self):
        self.msg.done(1)

    def uploadNo(self):
        self.msg.done(0)
    def rememberResponse(self):
        if _('Remember my Response') in self.remember.getChecked():
            self.checked = True
            redREnviron.settings['askToUploadError'] = 0

        else:
            self.checked = False
        
    def uploadException(self,err):
        """Upload an exception to the website"""
        try:
            """Ask if the error can be uploaded.  Unless the user doesn't want to be bothered with asking."""
            if not redREnviron.settings['askToUploadError']:
                res = redREnviron.settings['uploadError']
            else:
                import redRQTCore
                self.msg = redRQTCore.dialog(parent=qApp.canvasDlg,title='Red-R Error')
                
                error = redRQTCore.widgetBox(self.msg,orientation='vertical')
                redRQTCore.widgetLabel(error, label='Do you wish to report the Error Log?')
                buttons = redRQTCore.widgetBox(error,orientation='horizontal')

                redRQTCore.button(buttons, label = _('Yes'), callback = self.uploadYes)
                redRQTCore.button(buttons, label = _('No'), callback = self.uploadNo)
                self.checked = False
                self.remember = redRQTCore.checkBox(error,label='response', displayLabel=None,
                buttons=[_('Remember my Response')],callback=self.rememberResponse)
                res = self.msg.exec_()
                redREnviron.settings['uploadError'] = res
            
            """If errors can be uploaded then send them"""
            if res == 1:
                # print 'in res'
                err['version'] = redREnviron.version['SVNVERSION']
                err['type'] = redREnviron.version['TYPE']
                err['redRversion'] = redREnviron.version['REDRVERSION']
                if os.name == 'nt':
                    err['os'] = 'Windows'
                if redREnviron.settings['canContact']:
                    err['email'] = redREnviron.settings['email']
                params = urllib.urlencode(err)
                headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
                conn = httplib.HTTPConnection("red-r.org",80)
                conn.request("POST", "/errorReport.php", params,headers)
                log(REDRCORE, INFO, '<strong>Error data posted to the server</strong>')
            else:
                return
        except: 
            pass