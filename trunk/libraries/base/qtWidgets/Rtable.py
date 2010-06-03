from redRGUI import widgetState
from RSession import Rcommand
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy,sip

class Rtable(widgetState,QTableView):
    def __init__(self,widget,Rdata=None, editable=False, rows=None, columns=None,
    sortable=False, selectionMode = -1, addToLayout = 1,callback=None):
        QTableView.__init__(self,widget)

        self.R = Rcommand
        self.sortIndex = None
        self.oldSortingIndex = None
        self.Rdata = None
        self.parent = widget
        self.tm=None
        self.editable=editable
        
        self.setAlternatingRowColors(True)
        
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
        self.tm = MyTableModel(Rdata,self,editable=self.editable) 
        self.setModel(self.tm)
        # self.tm.setData(self.tm.index(1,1), QColor(Qt.red), Qt.BackgroundRole);
        # d = self.itemDelegate(self.tm.index(1,1))
        # d.paint(QBrush(Qt.red))

    def columnCount(self):
        if self.tm:
            return self.tm.columnCount(self)
        else:
            return 0
    def addRow(self):
        self.tm.insertRows(self.tm.rowCount(self),1)
    def addColumn(self):
        self.tm.insertColumns(self.tm.columnCount(self),1)

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
        # print data
        if not data['Rdata']: return 
        
        self.setRTable(data['Rdata'])
        
        if 'sortIndex' in data.keys():
            self.sortByColumn(data['sortIndex'],data['order'])
        if 'selection' in data.keys() and len(data['selection']):
            for i in data['selection']:
                self.setItemSelected(self.item(i[0],i[1]),True)
    def delete(self):
        sip.delete(self)

class MyTableModel(QAbstractTableModel): 
    def __init__(self, Rdata, parent,editable=False): 
        """ datain: a list of lists
            headerdata: a list of strings
        """
        self.R = Rcommand
        self.editable = editable
        #print parent
        QAbstractTableModel.__init__(self,parent) 
        self.Rdata = Rdata
        self.colnames = self.R('colnames(' +Rdata+ ')', wantType = 'list')
        if self.colnames:
            self.colnames.insert(0,'Row Names')
        self.rownames = self.R('rownames(' +Rdata+')', wantType = 'list')
        
        self.arraydata = self.R('as.matrix(cbind(rownames(' +Rdata+'),'+Rdata+'))', wantType = 'list')
        
    def flags(self,index):
        if self.editable:
            return (Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
        else:
            return (Qt.ItemIsSelectable | Qt.ItemIsEnabled)
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

    def setData(self,index,data, role):
        print 'in setData', data, index, role
        if not index.isValid(): 
            return False
        elif role == Qt.EditRole: 
            self.arraydata[index.row()][index.column()] = data.toString()
            self.emit(SIGNAL("dataChanged()"))
            return True
        # elif role == Qt.BackgroundRole:
            # print 'in BackgroundRole'
            # d = self.itemDelegate(index)
            # d.paint(QBrush(Qt.red))
            # return True
        
        return False
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.colnames[col])
        # elif orientation == Qt.Vertical and role == Qt.DisplayRole:     
            # return QVariant(self.rownames[col])
        return QVariant()
    
    def setHeaderData(self,col,orientation,data,role):
        if orientation == Qt.Horizontal and role == Qt.EditRole:
            self.colnames[col] = data.toString()
            self.emit(SIGNAL("headerDataChanged()"))
            return True
        else:
            return False

    def insertRows(self,beforeRow,count):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.emit(SIGNAL("beginInsertRows()"))
        
        # print self.arraydata
        # print type(self.arraydata)
        # print self.arraydata.shape
        # self.arraydata.resize(self.rowCount(self)+1)
        # print self.arraydata.shape
        # print self.arraydata
        #self.arraydata = [[1,1,1,1,1],[2,2,2,2,2]]
        self.arraydata.append(['' for i in xrange(self.columnCount(self))])
        self.rownames.append('')
        #numpy.append(self.arraydata, [[''] for i in xrange(self.columnCount(self))])
        #print d
        self.emit(SIGNAL("endInsertRows()"))
        self.emit(SIGNAL("layoutChanged()"))
        return True
    def insertColumns(self,beforeColumn,count):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.emit(SIGNAL("beginInsertRows()"))

        for x in self.arraydata:
            x.append('')
        #self.arraydata.append(['' for i in xrange(self.columnCount(self))])
        self.colnames.append('')

        self.emit(SIGNAL("endInsertRows()"))
        self.emit(SIGNAL("layoutChanged()"))

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        import operator
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()

        self.emit(SIGNAL("layoutChanged()"))

    def delete(self):
        sip.delete(self)  