from redRGUI import widgetState
from RSession import Rcommand
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

class Rtable(widgetState,QTableWidget):
    def __init__(self,widget,Rdata=None, rows = 0, columns = 0, 
    sortable=False, selectionMode = -1, addToLayout = 1,callback=None):
        QTableWidget.__init__(self,rows,columns,widget)

        self.R = Rcommand
        #table.__init__(self,widget,sortable=sortable,selectionMode = selectionMode,addToLayout=addToLayout)
        self.sortIndex = None
        self.oldSortingIndex = None
        self.Rdata = None
        if widget and addToLayout and widget.layout():
            widget.layout().addWidget(self)
        elif widget and addToLayout:
            try:
                widget.addWidget(self)
            except: # there seems to be no way to add this widget
                pass
        if selectionMode != -1:
            self.setSelectionMode(selectionMode)
                
        if Rdata:
            self.setRTable(Rdata)
        if sortable:
            self.setSortingEnabled(True)
            self.connect(self.horizontalHeader(), SIGNAL("sectionClicked(int)"), self.sort)
        if callback:
            QObject.connect(self, SIGNAL('cellClicked(int, int)'), callback)

        self.setRTable(Rdata)
    
    def sort(self, index):
        if index == self.oldSortingIndex:
            order = self.oldSortingOrder == Qt.AscendingOrder and Qt.DescendingOrder or Qt.AscendingOrder
        else:
            order = Qt.AscendingOrder
        self.oldSortingIndex = index
        self.oldSortingOrder = order

    def setRTable(self,Rdata, setRowHeaders = 1, setColHeaders = 1):
        print 'in Rtable set'
        if not Rdata:
            return

        self.setHidden(True)
        self.Rdata = Rdata
        dims = self.R('dim('+Rdata+')')
        #rowCount = self.R('length('+Rdata+'[,1])')
        #columnCount = self.R('length('+Rdata+'[1,])')
        self.setRowCount(dims[0])
        self.setColumnCount(dims[1])
        tableData = self.R('as.matrix('+Rdata+')', wantType = 'list', listOfLists = True)
        for j in range(0, int(dims[1])):
            for i in range(0, int(dims[0])):
                if dims[0] == 1: # there is only one row
                    ci = QTableWidgetItem(str(tableData[j]))
                # elif dims[1] == 1: # there is only one colum
                    # ci = QTableWidgetItem(str(tableData[i]))
                else:
                    ci = QTableWidgetItem(str(tableData[i][j])) # need to catch the case that there might not be multiple rows or columns
                self.setItem(i, j, ci)
        colnames = self.R('colnames(' +self.Rdata+ ')', wantType = 'list')
        for i in range(len(colnames)):
            colnames[i] = colnames[i] + ' (' + str(i+1) +')'
        rownames = self.R('rownames(' +self.Rdata+')', wantType = 'list')
        if setColHeaders: self.setHorizontalHeaderLabels(colnames)
        if setRowHeaders: self.setVerticalHeaderLabels(rownames)
        self.setHidden(False)
    def getSettings(self):
        r = {'Rdata': self.Rdata,
        'selection':[[i.row(),i.column()] for i in self.selectedIndexes()]}
        if self.oldSortingIndex != None:
            r['sortIndex'] = self.oldSortingIndex
            r['order'] = self.oldSortingOrder

        print r
        return r
    def loadSettings(self,data):
        print data
        self.setRTable(data['Rdata'])
        
        if 'sortIndex' in data.keys():
            self.sortByColumn(data['sortIndex'],data['order'])
        if 'selection' in data.keys() and len(data['selection']):
            for i in data['selection']:
                self.setItemSelected(self.item(i[0],i[1]),True)
            
            
        
  