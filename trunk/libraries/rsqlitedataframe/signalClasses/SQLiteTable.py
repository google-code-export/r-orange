from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RDataFrame import *
import time, sqlite3


class SQLiteTable(RDataFrame):
    def __init__(self, data, database, connection = None, parent = None, checkVal = True):
        RDataFrame.__init__(self, data = data, parent = parent, checkVal = False)
        ##  Need to set some specific parameters for SQLiteTable objects.  Such as the database and other stuff
        
        self.database = database
        self.newDataName = 'dataFrameConversion_'+str(time.time()) # put this here because we may make many connections from this output and we only want one dataFrameConversion_ in R
        if connection == None:
            pass
            ## make the connection
        else:
            self.connection = connection
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
        self.require_librarys(['RSQLite']) # require the sqlite package
        ## convert the data table to a database.  This will actually run the current sql query which will likely inherit from some kind of view
        self.R('m<-dbDriver("SQLite")')
        print self.database
        self.R('con<-dbConnect(m, dbname=\''+self.database+'\')')
        
        
        self.R(self.newDataName+'<-dbGetQuery(con, statement=\'select * from '+self.data+'\')')
        self.R('dbDisconnect(con)')  # close the connection
        # it would be really nice if in this we could ask the user to pick the column for the column name
        
        
        # convert the classes of the columns to something reasonable like numeric or factor
        conn = sqlite3.connect(self.database)
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
        
        newData = RDataFrame(data = self.newDataName)
        return newData
        
        
        
    