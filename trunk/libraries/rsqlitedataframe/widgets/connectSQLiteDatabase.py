## SQLite database interface initiator.  Sort of a misnomer but I can't think of a better name.  Basically what we want to do is to allow the user to set an arbitrary database on disk and set it into the Red-R schema.  This will simply connect to a database and allow the user to select one of the tables in that database and send it into the Red-R schema as a SQLiteTable

"""
<name>Connect to SQLite Database</name>
<description>Reads files from a text file and brings them into RedR in the form of an SQLite structure.  These files should be like a table and should have values that are separated either by a tab, space, or comma.  You can use the scan feature to scan a small part of your data and make sure that it is in the correct format.  You can also set a column to represent the row names of your data.  This is encouraged if you have row names as some widgets rely on row names to help them function.  By specifying a column as a rownames column that column will have the reserved word of Rownames no matter what the column name is in the data table that you are reading.  SQLite tables can be connected to any RDataFrame or RList accepting widget.</description>
<tags>Data Input, SQLite</tags>
<RFunctions>utils:read.table</RFunctions>
<icon>icons/readfile.png</icon>
<priority>10</priority>
"""

from OWRpy import *
import redRGUI 

import re, os
import sqlite3
class connectSQLiteDatabase(OWRpy):
    
    globalSettingsList = ['recentFiles','path']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "SQLite Database Connector", wantMainArea = 0, resizingEnabled = 1)

        self.recentFiles=['Select File']
        self.database = None
        self.path = os.path.abspath('/')
        
        
        #set R variable names        
        
        self.setRvariableNames(['dataframe_org','dataframe_final','filename', 'parent'])
        self.inputs = None
        self.outputs = [("SQLite Data Table", signals.rsqlitedataframe.SQLiteTable)]
        
        #### GUI ####
        area = redRGUI.widgetBox(self.controlArea,orientation='horizontal')
        options = redRGUI.widgetBox(area,orientation='vertical')
        box = redRGUI.groupBox(options, label="Load File", addSpace = True, orientation='horizontal')
        ### set file area
        button = redRGUI.button(box, label = 'Browse', callback = self.browseFile)
        self.dbinfo = redRGUI.widgetLabel(box, '')  # put the name of the database here
        ### set table area
        self.tableNames = redRGUI.listBox(self.controlArea, label = 'Available Tables:', toolTip = 'A list of available tables that can be selected.  The selected table will be sent into the schema.', callback = self.selectTable)
        
    def browseFile(self): 
        fn = QFileDialog.getOpenFileName(self, "Open File", self.path,
        "Database (*.db);; All Files (*.*)")
        if fn.isEmpty(): return
        self.dbinfo.setText(str(fn))
        self.database = str(fn)
        self.scanNewFile()  # scans the database and picks out the table names for sending to the send function.
        
    def scanNewFile(self):
        ## establish connection and cursor
        conn = sqlite3.connect(os.path.abspath(self.database))
        cursor = conn.cursor()
        
        ## query the database for the tables.
        
        cursor.execute('SELECT * FROM (SELECT * FROM SQLITE_MASTER UNION ALL SELECT * FROM SQLITE_TEMP_MASTER) WHERE type="table" OR type ="view"')
        info = []
        for row in cursor:  # collect the info for all of the tables and the views.
            info.append(str(row[1])+', '+ str(row[0]))
        
        conn.close() # close the connection, no need to commit anything
        
        self.tableNames.update(info)  # place the table names into the tableNames listBox
        
    def selectTable(self):
        ## place the table from the database into an SQLiteTable object
        ## get the table name
        table = str(self.tableNames.selectedItems()[0].text()).split(',')[0]
        
        newData = signals.rsqlitedataframe.SQLiteTable(data = table, database = self.database)
        self.rSend("SQLite Data Table", newData)
    
        