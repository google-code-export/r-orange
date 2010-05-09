from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RDataFrame import *
import time


class SQLiteTable(RDataFrame):
    def __init__(self, data, database, connection = None, parent = None, checkVal = True):
        RDataFrame.__init__(self, data = data, parent = parent, checkVal = False)
        ##  Need to set some specific parameters for SQLiteTable objects.  Such as the database and other stuff
        
        self.database = database
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
        self.R('con<-dbConnect(m, dbname=\''+self.database+'\')')
        
        newDataName = 'dataFrameConversion_'+str(time.time())
        self.R(newDataName+'<-dbGetQuery(con, statement=\'select * from '+self.data+'\')')
        self.R('dbDisconnect(con)')  # close the connection
        newData = RDataFrame(data = newDataName)
        return newData
        
        
        
    