## <log Module.  This module (not a class) will contain and provide access to widget icons, lines, widget instances, and other log.  Accessor functions are provided to retrieve these objects, create new objects, and distroy objects.>

import SQLiteSession, redREnviron, os, traceback, sys
from datetime import tzinfo, timedelta, datetime, time

_logDB = redREnviron.directoryNames['logDB']
handler = SQLiteSession.SQLiteHandler(defaultDB = _logDB)
_sessionID = redREnviron.settings['id']
_outputManager = None
_exceptionManager = None
if 'minSeverity' not in redREnviron.settings.keys():
    redREnviron.settings['minSeverity'] = 5
if 'debug' not in redREnviron.settings.keys():
    redREnviron.settings['debug'] = False

    
# def setExceptionManager(em):
    # global _exceptionManager
    # _exceptionManager = em
##Error Tables
PYTHON = 1
R = 2
GENERAL =3
DEBUG = 10

##Error Type
ERROR = 1
COMMENT = 2
MESSAGE = 3
WARNING = 4

errorTypes = {ERROR:'Error', COMMENT: 'Comment', MESSAGE: 'Message', WARNING: 'Warning'}
tables = {PYTHON: 'Python', R:'R',GENERAL:'General',DEBUG:'Debug'}

def setOutputManager(om):
    global _outputManager
    _outputManager = om

def getSessionID():
    global _sessionID
    return _sessionID
def log(table, severity, errorType = COMMENT, comment = ""):
    #if comment in ['', '\n', '\t']: return
    
    if table == DEBUG and redREnviron.settings['debugMode']:
        logOutput(table,severity, errorType, None, comment)
        return
    elif table == 20:
        lh.defaultSysOutHandler.write(comment)
        return
            
    if redREnviron.settings['debugMode']:        
        tb = traceback.format_stack()
        if tb < 3:
            lh.defaultSysOutHandler.write(comment)
            return
    else:
        tb = None
    
    if table not in [0, DEBUG]:
        handler.execute(query = "INSERT INTO All_Output (OutputDomain, TimeStamp, Session, Severity, ErrorType, Comment, Trackback) VALUES (\"%s\", \"%s\", \"%s\", %s, \"%s\", \"%s\", \"%s\")" % (
        table, datetime.today().isoformat(' '), _sessionID, severity, errorType, comment, unicode('</br>'.join(tb)).replace('\"', '')))
        
        if severity >= redREnviron.settings['minSeverity'] or (errorType == ERROR and severity >= redREnviron.settings['exceptionLevel']):
            logOutput(table,severity, errorType, tb, comment)
    elif table == 0:
        logOutput(table,severity, errorType, tb, comment)
        
def getHistory(widgetFile):
    widgets = []
    result = handler.execute(query = "SELECT * FROM ConnectionHistory WHERE OutWidget == \"%s\"" % widgetFile)
    for row in result:
        widgets.append(row[1])
def logConnection(outWidgetFile, inWidgetFile):
    handler.execute(query = "INSERT INTO ConnectionHistory (OutWidget, InWidget) VALUES (\"%s\", \"%s\")" % (outWidgetFile, inWidgetFile))
def logOutput(table, severity, errorType, tb, comment):
    if not tb:
        tb = ['','','','']
    global _outputManager
    if _outputManager:
        _outputManager(table, severity, errorType, tb, comment)
    else:
        string = '%s level %s\t%s\t%s' % (errorType, severity, tb[-3], comment)
        lh.defaultSysOutHandler.write(string)
def logDB():
    return _logDB
def clearDB():
    handler.setTable(table = 'All_Output', colNames = "(\"k\" INTEGER PRIMARY KEY AUTOINCREMENT, \"OutputDomain\", \"TimeStamp\", \"Session\", \"Severity\", \"ErrorType\", \"Comment\", \"Trackback\")", force = True)
def initializeTables():
    handler.setTable(table = 'All_Output', colNames = "(\"k\" INTEGER PRIMARY KEY AUTOINCREMENT, \"OutputDomain\", \"TimeStamp\", \"Session\", \"Severity\", \"ErrorType\", \"Comment\", \"Trackback\")")
    handler.setTable(table = 'ConnectionHistory', colNames = "(\"k\" INTEGER PRIMARY KEY AUTOINCREMENT, \"OutWidget\", \"InWidget\")")

class LogHandler():
    def __init__(self):
        self.defaultSysOutHandler = sys.stdout
        sys.stdout = self
        sys.excepthook = self.exceptionHandler

    def safe_unicode(self,obj):
        try:
            return unicode(obj)
        except UnicodeEncodeError:
            # obj is unicode
            return unicode(obj).encode('unicode_escape')
    
    def write(self, text):
        
        # tb = traceback.format_stack()
        # self.defaultSysOutHandler.write('in write' + text + "\n")
        
        # self.defaultSysOutHandler.write('################\n' + '\n'.join(tb))
        # return
        if not redREnviron.settings['debugMode']: return

        # logOutput(DEBUG,1, 2, None, text)
        log(DEBUG, 1, 2, text)
    
    def exceptionHandler(self, type, value, tracebackInfo):        
        #text = redRExceptionHandling.formatException(type,value,tracebackInfo)
        log(3,9,1)
    


lh = LogHandler()
initializeTables()