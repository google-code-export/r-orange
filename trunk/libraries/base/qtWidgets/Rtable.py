from redRGUI import widgetState
from RSession import Rcommand
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

class Rtable(widgetState,QTableView):
    def __init__(self,widget,Rdata=None, rows = 0, columns = 0, 
    sortable=False, selectionMode = -1, addToLayout = 1,callback=None):
        QTableView.__init__(self,widget)

        self.R = Rcommand
        self.sortIndex = None
        self.oldSortingIndex = None
        self.Rdata = None
        self.parent = widget
        
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

        

    def setRTable(self,Rdata, setRowHeaders = 1, setColHeaders = 1):
        #print Rdata
        self.Rdata = Rdata
        self.tm = MyTableModel(Rdata,self) 
        self.setModel(self.tm)


    def sort(self, index):
        if index == self.oldSortingIndex:
            order = self.oldSortingOrder == Qt.AscendingOrder and Qt.DescendingOrder or Qt.AscendingOrder
        else:
            order = Qt.AscendingOrder
        self.oldSortingIndex = index
        self.oldSortingOrder = order


    def getSettings(self):
        r = {'Rdata': self.Rdata,
        'selection':[[i.row(),i.column()] for i in self.selectedIndexes()]}
        if self.oldSortingIndex != None:
            r['sortIndex'] = self.oldSortingIndex
            r['order'] = self.oldSortingOrder

        return r
    def loadSettings(self,data):
        print data
        self.setRTable(data['Rdata'])
        
        if 'sortIndex' in data.keys():
            self.sortByColumn(data['sortIndex'],data['order'])
        if 'selection' in data.keys() and len(data['selection']):
            for i in data['selection']:
                self.setItemSelected(self.item(i[0],i[1]),True)

class MyTableModel(QAbstractTableModel): 
    def __init__(self, Rdata, parent=None): 
        """ datain: a list of lists
            headerdata: a list of strings
        """
        self.R = Rcommand
        print parent
        QAbstractTableModel.__init__(self,parent) 
        self.Rdata = Rdata
        self.colnames = self.R('colnames(' +Rdata+ ')', wantType = 'list')
        self.colnames.insert(0,'Row Names')
        #self.rownames = self.R('rownames(' +Rdata+')', wantType = 'list')
        
        self.arraydata =  self.R('as.matrix(cbind(rownames(' +Rdata+'),'+Rdata+'))', wantType = 'list', listOfLists = True)
        
    def rowCount(self, parent): 
        return len(self.arraydata) 
 
    def columnCount(self, parent): 
        return len(self.arraydata[0]) 
 
    def data(self, index, role): 
        if not index.isValid(): 
            return QVariant() 
        elif role != Qt.DisplayRole: 
            return QVariant() 
        return QVariant(self.arraydata[index.row()][index.column()]) 

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.colnames[col])
        # elif orientation == Qt.Vertical and role == Qt.DisplayRole:     
            # return QVariant(self.rownames[col])
        return QVariant()

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        import operator
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()

        self.emit(SIGNAL("layoutChanged()"))

  