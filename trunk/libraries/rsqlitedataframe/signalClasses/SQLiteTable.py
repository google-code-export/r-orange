from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RDataFrame import *
import time, sqlite3, os


class SQLiteTable(RDataFrame):
    def __init__(self, data, database, parent = None, checkVal = True):
        RDataFrame.__init__(self, data = data, parent = parent, checkVal = False)
        ##  Need to set some specific parameters for SQLiteTable objects.  Such as the database and other stuff
        if parent:  # sets the parent (ideally a real table in the database) of the data that you have here.  This may not be used that much, especially if you merge things, but you have it anyway if you need it.
            self.parent = parent
        else:
            self.parent = data
        self.database = database
        self.newDataName = 'dataFrameConversion_'+str(time.time()) # put this here because we may make many connections from this output and we only want one dataFrameConversion_ in R
        
    def saveSettings(self):
        return {'package': self.__package__, 'class':str(self.__class__), 'data':self.data, 'database': self.database, 'newDataName': self.newDataName}
    def loadSettings(self, settings):
        self.data = settings['data']
        self.database = settings['database']
        self.newDataName = settings['newDataName']
    def convertToClass(self, varClass):
        if varClass == RList:
            return self._convertToList()
        elif varClass == RVariable:
            return self._convertToDataFrame()
        elif varClass == RDataFrame:
            return self._convertToDataFrame()
        elif varClass == SQLiteTable:
            return self.copy()
        else:
            raise Exception
    def _convertToList(self):
        #self.R('list_of_'+self.data+'<-as.list('+self.data+')')
        dfData = self._convertToDataFrame()
        
        newData = RList(data = 'as.list('+dfData.data+')')
        return newData
    def _convertToDataFrame(self):
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
        self.R('m<-dbDriver("SQLite")')
        print database
        self.R('con<-dbConnect(m, dbname=\''+database+'\')')
        
        
        self.R(self.newDataName+'<-dbGetQuery(con, statement=\'select * from '+self.data+'\')')
        self.R('dbDisconnect(con)')  # close the connection
        # it would be really nice if in this we could ask the user to pick the column for the column name
        
        
        # convert the classes of the columns to something reasonable like numeric or factor
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        cursor.execute('PRAGMA table_info('+self.data+')')
        types = []
        for row in cursor:
            types.append((row[1], row[2]))
        conn.close()
        for type in types:
            if type[1] in ['text']:
                self.R(self.newDataName+'$'+str(type[0])+'<-as.factor('+self.newDataName+'$'+str(type[0])+')')
            elif type[1] in ['real']:
                self.R(self.newDataName+'$'+str(type[0])+'<-as.numeric('+self.newDataName+'$'+str(type[0])+')')
        
        ## allow the user to set rownames???
        
        
        newData = RDataFrame(data = self.newDataName)
        return newData
        
        
        
    