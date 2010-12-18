## <log Module.  This module (not a class) will contain and provide access to widget icons, lines, widget instances, and other log.  Accessor functions are provided to retrieve these objects, create new objects, and distroy objects.>

import redREnviron, os, traceback, sys
from datetime import tzinfo, timedelta, datetime, time
#import logging

#
#Red-R output writers
_outputDockWriter = None
_outputWindowWriter = None

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
NOTSET	 = 0	

logLevels = [CRITICAL,ERROR,WARNING,INFO,DEBUG]
logLevelsName = ['CRITICAL','ERROR','WARNING','INFO','DEBUG']
logLevelsByLevel = dict(zip(logLevels,logLevelsName))
logLevelsByName = dict(zip(logLevelsName,logLevels))



def setOutputManager(lvl,manager):
    if lvl =='dock':
        global _outputDockWriter
        _outputDockWriter = manager
    elif lvl=='window':
        global _outputWindowWriter
        _outputWindowWriter = manager
        

    
def log(table, logLevel = INFO, comment ='', source='logFun'):   
    #lh.defaultSysOutHandler.write('error type %s, debug mode %s\n' % (logLevel, redREnviron.settings['debugMode']))
    # lh.defaultSysOutHandler.write(str(logLevelsByName.get(redREnviron.settings['outputVerbosity'],0)) + ' ' + str(redREnviron.settings['outputVerbosity']) + '\n')
    
    # if table == STDOUT:
        # lh.defaultSysOutHandler.write(comment)
        # return
    
    if logLevel < logLevels[redREnviron.settings['outputVerbosity']]:
        return
    
    if logLevel == DEBUG and source !='print':
        comment = comment.rstrip('\n') + '\n'
    
    if table == R:
        comment = getSafeString(comment)
        
    if logLevels[redREnviron.settings['outputVerbosity']] == DEBUG and source !='print':        
        stack = traceback.format_stack()
        # if stack < 3:
            # lh.defaultSysOutHandler.write(comment)
            # return
    else:
        stack = None
    
    logOutput(table, logLevel, stack, comment)
        
def getSafeString(s):
    return unicode(s).replace("<", "&lt;").replace(">", "&gt;")

def formatException(type=None, value=None, tracebackInfo=None, errorMsg = None, plainText=False):
    if not tracebackInfo:
        (type,value, tracebackInfo) =  sys.exc_info()
    
    # tbList = traceback.format_exception(type,value,tracebackInfo)
    # return '\n'.join(tbList)
    # """
    t = datetime.today().isoformat(' ')
    text =  '<br>'*2 + '#'*60 + '<br>'
    if errorMsg:
        text += '<b>' + errorMsg + '</b><br>'
    text += "Unhandled exception of type %s occured at %s:<br>Traceback:<br>" % ( getSafeString(type.__name__), t)
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
    # """
    
def logOutput(table, logLevel, stack, comment):
    if logLevel !=DEBUG:
        string = '<div style="color:#0000FF">%s:%s </div>: ' %  (tables.get(table,'NOTABLE'),logLevelsByLevel.get(logLevel,'NOSET'))
        if stack:
            string+='%s || ' % (getSafeString(stack[-3]))
        
        string += '%s<br>' % (comment) 
        # if redREnviron.settings['debugMode']:
            # string = '<br>' + string
    else:
        string = comment 
        
    if _outputDockWriter:
        _outputDockWriter(table,logLevel,string)
    if _outputWindowWriter:
        _outputWindowWriter(table,logLevel,string)
    
    # if not (_outputWindowWriter and _outputDockWriter):
        # lh.defaultSysOutHandler.write(string)

    if redREnviron.settings["writeLogFile"]:
        lh.logFile.write(unicode(string).encode('Latin-1') + "<br>\n")
        

class LogHandler():
    def __init__(self):
        self.defaultSysOutHandler = sys.stdout
        sys.stdout = self
        sys.excepthook = self.exceptionHandler
        if redREnviron.settings['writeLogFile']:
            self.logFile = open(os.path.join(redREnviron.directoryNames['canvasSettingsDir'], "outputLog.html"), "w") # create the log file

    def write(self, text):
        # tb = traceback.format_stack()
        # self.defaultSysOutHandler.write('in write' + text + "\n")
        # self.defaultSysOutHandler.write('################\n' + '\n'.join(tb))
        # return
        #if not redREnviron.settings['debugMode']: return
        log(REDRCORE, DEBUG, getSafeString(text),source='print')

    def exceptionHandler(self, type, value, tracebackInfo):
        log(REDRCORE,CRITICAL,formatException(type,value,tracebackInfo),source='exception')
        
lh = LogHandler()
