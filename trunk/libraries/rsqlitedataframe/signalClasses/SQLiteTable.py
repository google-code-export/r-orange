from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RDataFrame import *
from StructuredDict import *
import time, sqlite3, os
import redRGUI


class SQLiteTable(RDataFrame, StructuredDict):
    def __init__(self, data, database = None, parent = None, checkVal = True):
        RDataFrame.__init__(self, data = data, parent = parent, checkVal = False)
        StructuredDict.__init__(self, data = data, parent = parent, checkVal = False)
        ##  Need to set some specific parameters for SQLiteTable objects.  Such as the database and other stuff
        if parent:  # sets the parent (ideally a real table in the database) of the data that you have here.  This may not be used that much, especially if you merge things, but you have it anyway if you need it.
            self.parent = parent
        else:
            self.parent = data
        self.database = database
        self.newDataName = 'dataFrameConversion_'+str(time.time()) # put this here because we may make many connections from this output and we only want one dataFrameConversion_ in R
        self.dialog = redRGUI.dialog()
        self.dataFrameData = None
        self.rownameList = redRGUI.listBox(self.dialog, label = 'Rownames', toolTip = 'Select a column to represent Row Names', callback = self.dialog.accept)
        
    def saveSettings(self):
        return {'package': self.__package__, 'class':str(self.__class__), 'data':self.data, 'database': self.database, 'newDataName': self.newDataName}
    def loadSettings(self, settings):
        self.data = settings['data']
        self.database = settings['database']
        self.newDataName = settings['newDataName']
    def convertToClass(self, varClass):
        if varClass == RList:
            return self._convertToList()
        elif varClass == BaseRedRVariable:
            return self
        elif varClass == RVariable:
            return self._convertToDataFrame()
        elif varClass == RDataFrame:
            return self._convertToDataFrame()
        elif varClass == SQLiteTable:
            return self
        elif varClass == StructuredDict:
            return self._convertToStructuredDict()
        elif varClass == UnstructuredDict:
            return self._convertToStructuredDict()
        else:
            raise Exception
    def getDatabase(self):
        if 'local|' in self.database:  # convert the database if the local name is present.
            database = os.path.join(qApp.canvasDlg.tempDir, self.database.split('|')[1])
        else:
            database = self.database
        return database
    def _convertToStructuredDict(self):
        ## convert to a python object that is a structured dict.
        if 'local|' in self.database:  # convert the database if the local name is present.
            database = os.path.join(qApp.canvasDlg.tempDir, self.database.split('|')[1])
        else:
            database = self.database
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info('+self.data+')')
        dictData = {}
        colnames = []
        for row in cursor:
            dictData[str(row[1])] = []  # make an empty list in the beginning.
            colnames.append(str(row[1]))
        
        cursor.execute('select * from '+self.data)
        for row in cursor: ## returns a structured tuple of values that will go into the dict.  But these values are based on rows instead of columns as the dict will be
            for i in range(len(colnames)):
                dictData[colnames[i]].append(row[i])
                
        conn.close()
        newData = StructuredDict(data = dictData, parent = self, keys = colnames)
        return newData
    def deleteSignal(self):
        print 'Delete Signal'
        if self.dataFrameData:
            self.R('if(exists("' + self.dataFrameData.getData() + '")) { rm(' + self.dataFrameData.getData() + ') }')
        
        self.dataFrameData = None
    def _convertToList(self):
        #self.R('list_of_'+self.data+'<-as.list('+self.data+')')
        if self.dataFrameData:
            return self.dataFrameData._convertToList()
        else:
            dfData = self._convertToDataFrame()
            
            newData = RList(data = 'as.list('+dfData.data+')')
            return newData
    def _convertToDataFrame(self):
        if self.dataFrameData:  ## don't reprocess if there is already a valid conversion.
            return self.dataFrameData
        ## we need to check if the database is available if not then we can't make the conversion.
        if 'local|' in self.database:  # convert the database if the local name is present.
            database = os.path.join(qApp.canvasDlg.tempDir, self.database.split('|')[1])
        else:
            database = self.database
        if not os.path.exists(database):
            if self.R('exists('+self.newDataName+')') == 'TRUE':
                QMessageBox.information(self, 'SQLite Conversion','Database '+str(database)+' does not exist on your system.\nHowever, I found the data in the Red-R session and will send this\ninstead of making a new table.',  QMessageBox.Ok + QMessageBox.Default)
                newData = RDataFrame(data = self.newDataName)
                return newData
            else:
                QMessageBox.information(self, 'SQLite Conversion','Database '+str(database)+' does not exist on your system.\nIf you got this schema from someone else this is normal.\nI\'ll make the connection but no data will be sent.',  QMessageBox.Ok + QMessageBox.Default)
                return
        database = database.replace('\\','/')
        self.require_librarys(['RSQLite']) # require the sqlite package
        ## convert the data table to a database.  This will actually run the current sql query which will likely inherit from some kind of view
        
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        cursor.execute('PRAGMA table_info('+self.data+')')
        types = []
        for row in cursor:
            types.append((row[1], row[2]))
        conn.close()
        
        ### list all of the column names and allow the user to specify one as the rowname column if desired.
        colnames = [type[0] for type in types]
        colnames.insert(0, 'No Names')
        self.rownameList.update(colnames)
        r = self.dialog.exec_() ## execute the dialog
        if r == QDialog.Accepted:
            
            rownameSelection = '\''+str(self.rownameList.selectedItems()[0].text())+'\''
        else:
            rownameSelection = 'NULL'
        self.R('m<-dbDriver("SQLite")')
        print database
        self.R('con<-dbConnect(m, dbname=\''+database+'\')')
        
        
        self.R(self.newDataName+'<-dbGetQuery(con, statement=\'select * from '+self.data+'\', row.names = '+rownameSelection+')')
        self.R('dbDisconnect(con)')  # close the connection
        # it would be really nice if in this we could ask the user to pick the column for the column name
        
        
        # convert the classes of the columns to something reasonable like numeric or factor
        
        for type in types:
            if type[1] in ['text']:
                self.R(self.newDataName+'$'+str(type[0])+'<-as.factor('+self.newDataName+'$'+str(type[0])+')')
            elif type[1] in ['real']:
                self.R(self.newDataName+'$'+str(type[0])+'<-as.numeric('+self.newDataName+'$'+str(type[0])+')')
        
        if rownameSelection != 'NULL':
            self.R('rownames('+self.newDataName+')<-'+self.newDataName+'$'+rownameSelection.strip('\''))
            self.R(self.newDataName+'<-'+self.newDataName+'[colnames('+self.newDataName+') != '+rownameSelection+',,drop = F]')
        ## allow the user to set rownames???
        
        
        self.dataFrameData = RDataFrame(data = self.newDataName)
        return self.dataFrameData
        
        
        
    