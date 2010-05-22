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
        
        self.dataList = {}
        self.setRvariableNames(["view"])
        self.Rvariables['view'] = self.Rvariables['view'].split('.')[0]  # need to get rid of the .XX at the end of system time.
        self.inputs = [('Main SQLite Table', signals.rsqlitedataframe.SQLiteTable, self.gotMainTable), ('SQLite Table', signals.rsqlitedataframe.SQLiteTable, self.gotTable, 'Multiple')]
        self.outputs = [('SQLite Table', signals.rsqlitedataframe.SQLiteTable)]
        self.recentFiles=['Select File']
        self.database = None  # database will be obtained from the connection.  Queries neen not be done on the table that is recieved but it would make more sense if this were to happen
        
        ### GUI ###
        mainBox = redRGUI.widgetBox(self.controlArea, orientation = 'horizontal')
        leftBox1 = redRGUI.widgetBox(mainBox, orientation = 'vertical')
        rightBox1 = redRGUI.widgetBox(mainBox, orientation = 'vertical')
        rightBox1.setMaximumWidth(150)
        statementBox = redRGUI.groupBox(leftBox1, label = 'Statement', orientation = 'horizontal')
        self.statementLineEdit = redRGUI.lineEdit(statementBox, width = -1, toolTip = 'Place your SQL statement here the actual statement that will be returned is \'CREATE VIEW XXX AS mystatement\'', callback = self.runStatement)
        submitButton = redRGUI.button(statementBox, 'Commit Statement', callback = self.runStatement)
        infoArea = redRGUI.groupBox(leftBox1, label = 'Info:')
        self.infoA = redRGUI.widgetLabel(infoArea, 'No data connected')
        self.infoB = redRGUI.widgetLabel(infoArea, "")
        outputBox = redRGUI.groupBox(leftBox1, label = 'Sample of Output')
        self.outputTextArea = redRGUI.textEdit(outputBox)
        self.outputTextArea.setLineWrapMode(QTextEdit.NoWrap)
        ### Table Info Section ###
        ## Table Names ##
        self.tableListBox = redRGUI.listBox(rightBox1, label = 'Tables', toolTip = 'Tables available in this database.  Click one to see the column names.', callback = self.resetTableNames)
        self.columnNameListBox = redRGUI.listBox(rightBox1, label = 'Column Names', toolTip = 'Column names available in this table.', callback = self.addColumnToQuery)
    def gotMainTable(self, data):
        if data:
            self.mainData = data
            self.infoA.setText('Incoming table name is '+self.mainData.getData())
            ## scan the current table, easiest way to do that is to run a command with a query to select *
            self.statementLineEdit.setText('select * from '+self.mainData.getData())
            self.runStatement()
            self.statementLineEdit.clear()
            self.resetTableNames()
        else:
            self.mainData = None
    def gotTable(self, data, id):
        print id, ' ID ##############'
        ## set the data to the widget need to set 
        if data:
            self.dataList[id[0].widgetID] = data
            self.addTableToDataBase(data)
        else:
            del self.dataList[id]
    def resetTableNames(self):
        if self.mainData == None:
            self.status.setText('Can\'t show table names when no main table exists.  Please resend data.')
            return
            
        conn = sqlite3.connect(self.mainData.getDatabase())  # make the main connection
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM SQLITE_MASTER WHERE type="table" OR type ="view"')
        info = []
        for row in cursor:  # collect the info for all of the tables and the views.
            info.append(str(row[1])+', '+ str(row[0]))
        
        conn.close()
        self.tableListBox.update(info)
        self.resetColumnNameListBox()
    def resetColumnNameListBox(self):
        items = self.tableListBox.selectedItems()
        if len(items) == 0:
            self.status.setText('No items selected, can\'t show column names.')
            return
        tableName = str(items[0].text()).split(',')[0]
        
        if self.mainData == None:
            self.status.setText('Can\'t show table names when no main table exists.  Please resend data.')
            return
            
        conn = sqlite3.connect(self.mainData.getDatabase())  # make the main connection
        cursor = conn.cursor()
        
        cursor.execute('PRAGMA table_info('+tableName+')')
        
        colInfo = []
        for row in cursor:
            colInfo.append(str(row[1])+', '+str(row[2]))
            
        self.columnNameListBox.update(colInfo)
        conn.close()
    def addColumnToQuery(self):
        ## add a column to the query statement
        tableItems = self.tableListBox.selectedItems()
        tableName = str(tableItems[0].text()).split(',')[0]
        nameItems = self.columnNameListBox.selectedItems()
        nameName = str(nameItems[0].text()).split(',')[0]
        self.statementLineEdit.insert(tableName+'.'+nameName)
    def addTableToDataBase(self, data):
        ## copy the structure of a table into an attached database.
        if self.mainData == None:
            self.status.setText('Can\'t move table when no main table exists.  Please resend data.')
            return
            
        conn = sqlite3.connect(self.mainData.getDatabase())  # make the main connection
        cursor = conn.cursor()
        
        ## attach the data for the new table
        dbName = os.path.split(data.getItem('database'))[1].split('.')[0]
        cursor.execute('ATTACH DATABASE "'+data.getItem('database')+'" AS '+dbName)  ## now the database is attached, we need to copy this structure so we can make a view that will be persistent.
        
        cursor.execute('PRAGMA table_info('+data.getData()+')')
        colnames = cursor.fetchall()  # now we know all of the column names and attributes
        columnInfo = []
        for c in colnames:
            columnInfo.append(str(c[1])+' '+str(c[2]))
        columnNames = []
        for c in colnames:
            columnNames.append(str(c[1]))
        try:
            cursor.execute('DROP TABLE IF EXISTS '+data.getData()+'_2')
        except:
            print 'Error occured in dropping the table.'
        cursor.execute('CREATE TABLE '+data.getData()+'_2 ('+','.join(columnInfo)+')')  ## now we have made a new table.  This will be the table that we use to reference the orriginal table.  Required to work across multiple databases.  We don't really work acros multiple databases but copy data from one to another.
        
        cursor.execute('INSERT INTO '+data.getData()+'_2 ('+','.join(columnNames)+') SELECT * FROM '+dbName+'.'+data.getData())
        conn.commit()
        conn.close()
        self.resetTableNames()
    def runStatement(self):
        if self.mainData == None:
            self.status.setText('No Main Data connected')
            return
        self.outputTextArea.clear()
        
        databaseName = self.mainData.getDatabase()
        statement = str(self.statementLineEdit.text())
        conn = sqlite3.connect(databaseName)
        cursor = conn.cursor()
        print str(self.dataList)
        if len(self.dataList) > 0:
            for key in self.dataList.keys():
                database = self.dataList[key]
                
                if 'local|' in database.getItem('database'):
                    databaseName = os.path.join(qApp.canvasDlg.tempDir, database.getItem('database').split('|')[1])
                else:
                    databaseName = database.getItem('database')
                    
                dbName = os.path.split(databaseName)[1].split('.')[0]
                query = 'ATTACH "'+str(databaseName)+'" AS '+dbName
                print query
                cursor.execute(query)
                self.outputTextArea.insertHtml('Added database: '+dbName+'<br>')
        cursor.execute('DROP VIEW IF EXISTS '+self.Rvariables['view'])
        try:
            cursor.execute('CREATE VIEW '+self.Rvariables['view']+' AS '+statement)  # execute the statement
        except Exception as inst:
            self.outputTextArea.clear()
            self.outputTextArea.insertHtml('Error occured during processing, please check that the query is formatted correctly.')
            self.outputTextArea.insertHtml(str(inst))
            conn.commit()
            conn.close()
            return
        conn.commit()
        conn.close()
        newData = signals.rsqlitedataframe.SQLiteTable(data = self.Rvariables['view'], database = self.mainData.database) # set the new data
        self.rSend('SQLite Table', newData)  # send the data
        self.updateScan()
        
    def updateScan(self):
        #if self.rowNamesCombo.count() == 0:
        if 'local|' in self.mainData.database:
            database = os.path.join(qApp.canvasDlg.tempDir, self.mainData.database.split('|')[1])
        else:
            database = self.mainData.database
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info('+str(self.Rvariables['view'])+')')
        colnames = cursor.fetchall()
        cursor.execute("SELECT * from "+str(self.Rvariables['view'])+" LIMIT 10")
        data = cursor.fetchall()  # collect the first N lines of the data so that we can put it into the scan area.
        conn.close()
        txt = self.html_table(colnames,data)
        
        self.outputTextArea.insertHtml(txt)
        
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
        