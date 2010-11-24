## <log Module.  This module (not a class) will contain and provide access to widget icons, lines, widget instances, and other log.  Accessor functions are provided to retrieve these objects, create new objects, and distroy objects.>
    # Copyright (C) 2010 Kyle R Covington

    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.

    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.

    # You should have received a copy of the GNU General Public License
    # along with this program.  If not, see <http://www.gnu.org/licenses/>.
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import SQLiteSession, redREnviron, os, traceback, sys
from datetime import tzinfo, timedelta, datetime, time
_logDB = redREnviron.directoryNames['logDB']
handler = SQLiteSession.SQLiteHandler(defaultDB = _logDB)
#_tables = []
_sessionID = redREnviron.settings['id']
_outputManager = None
_exceptionManager = None
if 'minSeverity' not in redREnviron.settings.keys():
    redREnviron.settings['minSeverity'] = 5
if 'debug' not in redREnviron.settings.keys():
    redREnviron.settings['debug'] = False
def setExceptionManager(em):
    global _exceptionManager
    _exceptionManager = em
PYTHON = 1
R = 2
GENERAL =3


def setOutputManager(om):
    global _outputManager
    _outputManager = om
def getSessionID():
    global _sessionID
    return _sessionID
def log(table, severity, errorType = 2, comment = ""):
    global _tables
    if comment in ['', '\n', '\t']: return
    
    if type(table) == int:
        if table == 1:
            table = 'Python'
        elif table == 2:
            table = 'R'
        elif table == 3:
            table = 'General'
    if type(errorType) == int:
        if errorType == 1:
            errorType = 'Error'
        elif errorType == 2:
            errorType = 'Comment'
        elif errorType == 3:
            errorType = 'Message'
        elif errorType == 4:
            errorType = 'Warning'
    tb = traceback.format_stack()
    if tb < 3:
        lh.defaultSysOutHandler.write(comment)
        return
    if table not in [0, 10]:
        
        handler.execute(query = "INSERT INTO All_Output (OutputDomain, TimeStamp, Session, Severity, ErrorType, Comment, Trackback) VALUES (\"%s\", \"%s\", \"%s\", %s, \"%s\", \"%s\", \"%s\")" % (table, datetime.today().isoformat(' '), _sessionID, severity, errorType, comment, unicode('</br>'.join(tb)).replace('\"', '')))
        
        if severity >= redREnviron.settings['minSeverity'] or (errorType == 'Error' and severity >= redREnviron.settings['exceptionLevel']):
            logOutput('<br /><div style="color:#FF0000">%s level %s:</div><br /> %s <br /><strong>%s</strong>' % (errorType, severity, tb[-3], toHtmlSafe(comment)))
    elif table == 0:
        logOutput('<br /><div style="color:#0000FF">%s level %s:</div><br /> %s <br /><strong>%s</strong>' % (errorType, severity, tb[-3], toHtmlSafe(comment)))
    elif table == 10 and redREnviron.settings['debugMode']:
        logOutput('<br /><div style="color:#2554C7">%s level %s:</div><br /> %s <br /><strong>%s</strong>' % (errorType, severity, tb[-3], toHtmlSafe(comment)))
    elif table == 20:
        lh.defaultSysOutHandler.write(comment)
def getHistory(widgetFile):
    widgets = []
    result = handler.execute(query = "SELECT * FROM ConnectionHistory WHERE OutWidget == \"%s\"" % widgetFile)
    for row in result:
        widgets.append(row[1])
def logConnection(outWidgetFile, inWidgetFile):
    handler.execute(query = "INSERT INTO ConnectionHistory (OutWidget, InWidget) VALUES (\"%s\", \"%s\")" % (outWidgetFile, inWidgetFile))
def logException(string):
    global _exceptionManager
    if _exceptionManager:
        cursor = QTextCursor( _exceptionManager.exceptionText.textCursor())                
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      
        _exceptionManager.exceptionText.setTextCursor(cursor)                             
        
        _exceptionManager.exceptionText.insertHtml(string + '<br />')                              
def logOutput(string):
    global _outputManager
    if _outputManager:
        cursor = QTextCursor( _outputManager.printOutput.textCursor())                
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)      
        _outputManager.printOutput.setTextCursor(cursor)                             
        
        _outputManager.printOutput.insertHtml(string + '<br/>')
def toHtmlSafe(string):
    newString = string.replace('<', '&lt;').replace('>', '&gt;')
    return newString
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
        self.catchOutput(1)
    def catchOutput(self, catch):
        if catch:    sys.stdout = self
        else:         sys.stdout = self.defaultSysOutHandler
    
    def safe_unicode(self,obj):
        try:
            return unicode(obj)
        except UnicodeEncodeError:
            # obj is unicode
            return unicode(obj).encode('unicode_escape')
    
    def write(self, text):
        #sys.stdout.write(text)
        if not redREnviron.settings['debugMode']: return
        import re, log
        m = re.search('^(\|(#+)\|\s?)(.*)',text)

        if m:
            log.log(3, len(m.group(2)), 2, text)
        else:
            log.log(3, 1, 2, text)
lh = LogHandler()
initializeTables()