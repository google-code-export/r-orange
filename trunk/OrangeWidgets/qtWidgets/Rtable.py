from table import table
from RSession import RSession
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

class Rtable(table):
    def __init__(self,widget,Rdata=None, rows = 0, columns = 0,sortable=False, selectionMode = -1, addToLayout = 1):
        self.R = RSession()
        table.__init__(self,widget,sortable=sortable,selectionMode = selectionMode,addToLayout=addToLayout)

        if Rdata:
            self.setRTable(Rdata)
    
    def setRTable(self,Rdata, setRowHeaders = 1, setColHeaders = 1):
        print 'in Rtable set'
        self.setHidden(True)
        self.Rdata = Rdata
        dims = self.R.R('dim('+Rdata+')')
        #rowCount = self.R.R('length('+Rdata+'[,1])')
        #columnCount = self.R.R('length('+Rdata+'[1,])')
        self.setRowCount(dims[0])
        self.setColumnCount(dims[1])
        tableData = self.R.R('as.matrix('+Rdata+')', wantType = 'list', listOfLists = True)
        for j in range(0, int(dims[1])):
            for i in range(0, int(dims[0])):
                if dims[0] == 1: # there is only one row
                    ci = QTableWidgetItem(str(tableData[j]))
                # elif dims[1] == 1: # there is only one colum
                    # ci = QTableWidgetItem(str(tableData[i]))
                else:
                    ci = QTableWidgetItem(str(tableData[i][j])) # need to catch the case that there might not be multiple rows or columns
                self.setItem(i, j, ci)
        colnames = self.R.R('colnames(' +self.Rdata+ ')', wantType = 'list')
        for i in range(len(colnames)):
            colnames[i] = colnames[i] + ' (' + str(i+1) +')'
        rownames = self.R.R('rownames(' +self.Rdata+')', wantType = 'list')
        if setColHeaders: self.setHorizontalHeaderLabels(colnames)
        if setRowHeaders: self.setVerticalHeaderLabels(rownames)
        self.setHidden(False)
    def getSettings(self):
        r = table.getSettings(self)
        del r['data']
        r['Rdata'] = self.Rdata
        return r
    def loadSettings(self,data):
        #print data
        self.setRTable(data['Rdata'])
        
        if 'sortIndex' in data.keys():
            # print 'aaaaaaaaa###############'
            self.sortByColumn(data['sortIndex'],data['order'])
        #print 'aaaaaaaaatable#########################'
        if 'selection' in data.keys() and len(data['selection']):
            # print 'table#########################'
            for i in data['selection']:
                # print i
                self.setItemSelected(self.item(i[0],i[1]),True)
            
                #self.selectRow(i[0])
            
        
  