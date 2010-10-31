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
    
import SQLiteSession, redREnviron, os
_logDB = os.path.join(redREnviron.directoryNames['canvasSettingsDir'], "log.db")
handler = SQLiteSession.SQLiteHandler(defaultDB = _logDB)

def log(table, severity, errorType = 2, comment = ""):
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
    handler.execute(query = "INSERT INTO %s (Severity, ErrorType, Comment) VALUES (%s, \"%s\", \"%s\")" % (table, severity, errorType, comment))
    handler.execute(query = "INSERT INTO %s (Severity, ErrorType, Comment) VALUES (%s, \"%s\", \"%s\")" % ('All_Output', severity, errorType, comment))
    
def logDB():
    return _logDB
def clearDB():
    for t in ['All_Output', 'General', 'R', 'Python']:
        handler.setTable(table = t, colNames = "(\"k\" INTEGER PRIMARY KEY AUTOINCREMENT, \"Severity\", \"ErrorType\", \"Comment\")", force = True)
def initializeTables():
    for t in ['All_Output', 'General', 'R', 'Python']:
        handler.setTable(table = t, colNames = "(\"k\" INTEGER PRIMARY KEY AUTOINCREMENT, \"Severity\", \"ErrorType\", \"Comment\")")
        
initializeTables()