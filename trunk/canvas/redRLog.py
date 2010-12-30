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
DEVEL	 = 0	

logLevels = [CRITICAL,ERROR,WARNING,INFO,DEBUG,DEVEL]
logLevelsName = ['CRITICAL','ERROR','WARNING','INFO','DEBUG','DEVEL']
logLevelsByLevel = dict(zip(logLevels,logLevelsName))
logLevelsByName = dict(zip(logLevelsName,logLevels))



def setOutputManager(lvl,manager):
    if lvl =='dock':
        global _outputDockWriter
        _outputDockWriter = manager
    elif lvl=='window':
        global _outputWindowWriter
        _outputWindowWriter = manager
        

    
def log(table, logLevel = INFO, comment ='', widget=None):   
    #lh.defaultSysOutHandler.write('error type %s, debug mode %s\n' % (logLevel, redREnviron.settings['debugMode']))
    # lh.defaultSysOutHandler.write(str(logLevelsByName.get(redREnviron.settings['outputVerbosity'],0)) + ' ' + str(redREnviron.settings['outputVerbosity']) + '\n')
    
    # if table == STDOUT:
        # lh.defaultSysOutHandler.write(comment)
        # return
    if redREnviron.settings["writeLogFile"]:
        lh.logFile.write(unicode(comment).encode('Latin-1')+'<br>')
        
    if logLevel < logLevels[redREnviron.settings['outputVerbosity']]:
        return

        
    if logLevels[redREnviron.settings['outputVerbosity']] <= DEBUG:
        stack = traceback.format_stack()
        # if stack < 3:
            # lh.defaultSysOutHandler.write(comment)
            # return
    else:
        stack = None
    
    formatedLogOutput(table, logLevel, stack, comment,widget)
    
def logOutput(table, logLevel, comment,html=False):
    if _outputDockWriter:
        _outputDockWriter(table,logLevel,comment,html)
    if _outputWindowWriter:
        _outputWindowWriter(table,logLevel,comment,html)
    
    # if not (_outputWindowWriter and _outputDockWriter):
        # lh.defaultSysOutHandler.write(string)


def formatedLogOutput(table, logLevel, stack, comment, widget=None):
    # if logLevel == DEBUG:
        # comment = comment.rstrip('\n') + '<br>'
    
    if table == R:
        comment = getSafeString(comment)
    if logLevel == CRITICAL:
        color = '#FF0000'
    else:
        color = "#0000FF"
    string = '<div style="color:%s">%s:%s </div>: ' %  (color, tables.get(table,'NOTABLE'),logLevelsByLevel.get(logLevel,'NOSET'))
    if stack:
        string+='%s || ' % (getSafeString(stack[-3]))
    
    string += '%s<br>' % (comment) 
    logOutput(table, logLevel, string,html=True)
          
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
    
def moveLogFile(newFile):
    lh.logFile.close()
    # if os.path.exists(newFile):
        # os.remove(newFile)
    # os.rename(lh.currentLogFile, newFile)
    lh.logFile = open(newFile, "w")
    # lh.currentLogFile = newFile
def closeLogFile():
    lh.logFile.close()
    os.remove(redREnviron.settings['logFile'])
    
class LogHandler():
    def __init__(self):
        self.defaultSysOutHandler = sys.stdout
        sys.stdout = self
        sys.excepthook = self.exceptionHandler
        # self.currentLogFile = redREnviron.settings['logFile']
        if redREnviron.settings['writeLogFile']:
            self.logFile = open(redREnviron.settings['logFile'], "w") # create the log file

    #ONLY FOR DEVEL print statements
    def write(self, text):
        # tb = traceback.format_stack()
        # self.defaultSysOutHandler.write('in write' + str(logLevels[redREnviron.settings['outputVerbosity']]) + "\n")
        # self.defaultSysOutHandler.write('################\n' + '\n'.join(tb))
        # return
        if logLevels[redREnviron.settings['outputVerbosity']] != DEVEL:
            return
        if redREnviron.settings["writeLogFile"]:
            self.logFile.write(unicode(text).encode('Latin-1'))
            
        logOutput(REDRCORE,DEVEL, text,html=False)

    def exceptionHandler(self, type, value, tracebackInfo):
        log(REDRCORE,CRITICAL,formatException(type,value,tracebackInfo))
        
lh = LogHandler()
