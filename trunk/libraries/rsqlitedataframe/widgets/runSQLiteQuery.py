## basic sqlite statement evaluator.  This widget allows one to execute specific sql statements on a recieved database and generate an sql view.  Essentially always running CREATE VIEW widgetname AS statement.
"""
<name>Run SQLite Query</name>
<description>Runs the query 'QUERY', sets a new view as the result of that query and then sends it through the output slot.</description>
<tags>Data Input, SQLite</tags>
<icon>icons/readfile.png</icon>
<priority>10</priority>
"""

from OWRpy import *
import redRGUI
import sqlite3 
import re, os
class runSQLiteQuery(OWRpy):
    
    globalSettingsList = ['recentFiles','path']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "SQLite Quert", wantMainArea = 0, resizingEnabled = 1)
        
        self.data = None
        self.setRvariableNames(["view"])
        self.Rvariables['view'] = self.Rvariables['view'].split('.')[0]  # need to get rid of the .XX at the end of system time.
        self.loadSettings()
        self.inputs = [('SQLite Table', signals.rsqlitedataframe.SQLiteTable, self.gotTable)]
        self.outputs = [('SQLite Table', signals.rsqlitedataframe.SQLiteTable)]
        self.recentFiles=['Select File']
        self.database = None  # database will be obtained from the connection.  Queries neen not be done on the table that is recieved but it would make more sense if this were to happen
        
        ### GUI ###
        
        statementBox = redRGUI.groupBox(self.controlArea, label = 'Statement', orientation = 'horizontal')
        self.statementLineEdit = redRGUI.lineEdit(statementBox, toolTip = 'Place your SQL statement here the actual statement that will be returned is \'CREATE VIEW XXX AS mystatement\'')
        submitButton = redRGUI.button(statementBox, 'Commit Statement', callback = self.runStatement)
        infoArea = redRGUI.groupBox(self.controlArea, label = 'Info:')
        self.infoA = redRGUI.widgetLabel(infoArea, 'No data connected')
        outputBox = redRGUI.groupBox(self.controlArea, label = 'Sample of Output')
        self.outputTextArea = redRGUI.textEdit(outputBox)
        
    def gotTable(self, data):
        ## set the data to the widget need to set 
        if data:
            self.data = data
            self.infoA.setText('Incoming table name is '+self.data.data)
        else:
            self.data = None
            self.infoA.setText('No data connected')
    def runStatement(self):
        if self.data == None: return
        statement = str(self.statementLineEdit.text())
        if 'local|' in self.data.database:
            database = os.path.join(qApp.canvasDlg.tempDir, self.data.database.split('|')[1])
        else:
            database = self.data.database
            
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        cursor.execute('CREATE VIEW '+self.Rvariables['view']+' AS '+statement)  # execute the statement
        
        newData = signals.rsqlitedataframe.SQLiteTable(data = self.Rvariables['view'], database = self.data.database) # set the new data
        self.rSend('SQLite Table', newData)  # send the data
        self.updateScan()
        
    def updateScan(self):
        #if self.rowNamesCombo.count() == 0:
        if 'local|' in self.data.database:
            database = os.path.join(qApp.canvasDlg.tempDir, self.data.database.split('|')[1])
        else:
            database = self.data.database
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info('+str(self.Rvariables['view'])+')')
        colnames = cursor.fetchall()
        self.outputTextArea.clear()
        cursor.execute("SELECT * from "+str(self.Rvariables['view'])+" LIMIT 10")
        data = cursor.fetchall()  # collect the first N lines of the data so that we can put it into the scan area.
        conn.commit()
        conn.close()
        txt = self.html_table(colnames,data)
        
        self.outputTextArea.setText(txt)
        
    def html_table(self,colnames,data):
        s = '<table border="1" cellpadding="3">'
        s+= '  <tr>'
        for c in colnames:
            s += '<td><b>'+str(c[1])+'</b></td>'
        s+= '</tr>'
        
        for r in data:
            s += '<tr>'
            for d in r:
                s += '<td>'+str(d)+'</td>'
            s += '</tr>'
        s+= '</table>'
        return s
        