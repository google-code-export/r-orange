## converts an R data frame to an sqlite table.  The defaut behavior is to place the table into the local|temp.db directory though this can be changed by the user.
"""
<name>Convert DataFrame to SQLite Table</name>
<description>Converts an R data frame to an sqlite table.  The defaut behavior is to place the table into the local|temp.db directory though this can be changed by the user.</description>
<tags>SQLite</tags>
<icon>readfile.png</icon>
<priority>10</priority>
"""

from OWRpy import *
import redRGUI
import sqlite3 
import re, os
class convertDataFrameToSQLite(OWRpy):
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "SQLite Convert DataFrame", wantMainArea = 0, resizingEnabled = 1)
        
        self.data = None
        
        self.inputs = [('DataFrame', signals.RDataFrame, self.gotDataFrame)]
        self.outputs = None
        
        ###  GUI  ###  Should be very simple, just ask the user where she wants to place the database and what the table name should be.
        box = redRGUI.groupBox(self.controlArea, label = 'Database Location', orientation = 'horizontal')
        self.dbLabel = redRGUI.widgetLabel(box, 'local|temp.db')
        
        button = redRGUI.button(box, 'Set Database', callback = self.changeDatabase)
        button2 = redRGUI.button(box, 'Set Local', callback = self.setLocal)
        
        box2 = redRGUI.groupBox(self.controlArea, label = 'Table Name')
        self.tableNameLineEdit = redRGUI.lineEdit(box2)
        
        commitButton = redRGUI.button(self.bottomAreaRight, 'Commit', callback = self.commit)
    def gotDataFrame(self, data):
        if data:
            self.data = data
            self.tableNameLineEdit.setText(str(self.data.getData().replace('.', '_')))
            
        else:
            self.data = None
    
    def changeDatabase(self):
        fn = QFileDialog.getSaveFileName(self, "Set Database", os.path.abspath('/'), "Database (*.db)")
        if fn.isEmpty(): return
        self.dbLabel.setText(str(os.path.abspath(str(fn))))
        
    def setLocal(self):
        self.dbLabel.setText('local|temp.db')
        
    def commit(self):
        ## make a call in R so that we save the table
        if 'local|' in str(self.dbLabel.text()):  # convert the database if the local name is present.
            database = os.path.join(qApp.canvasDlg.tempDir, str(self.dbLabel.text()).split('|')[1])
        else:
            database = str(self.dbLabel.text())
            
        database = database.replace('\\','/')
        
        
        if not self.require_librarys(['RSQLite']):
            QMessageBox.information(self, 'SQLite Conversion','Can\'t load the RSQLite package.  Please connect to the internet to download.',  QMessageBox.Ok + QMessageBox.Default)
        self.R('m<-dbDriver("SQLite")')
        self.R('con<-dbConnect(m, dbname=\''+database+'\')')
        self.R('dbWriteTable(con, \''+str(self.tableNameLineEdit.text())+'\', '+str(self.data.data)+', overwrite = TRUE)')
        self.R('dbCommit(con)')
        self.R('dbDisconnect(con)')  # close the connection
        
        self.status.setText('Data Committed')
        