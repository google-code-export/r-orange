from redRGUI import widgetState
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from SQLiteSession import *

class table(widgetState,QTableWidget):
    def __init__(self,widget,data=None, rows = 0, columns = 0, sortable = False, selectionMode = -1, addToLayout = 1, callback = None):
        QTableWidget.__init__(self,rows,columns,widget)
        self.sortIndex = None
        self.oldSortingIndex = None
        self.data = None
        self.dataTable = None
        ### should turn this into a function as all widgets use it to some degree
        if widget and addToLayout and widget.layout():
            widget.layout().addWidget(self)
        elif widget and addToLayout:
            try:
                widget.addWidget(self)
            except: # there seems to be no way to add this widget
                pass
                
        ###
        if selectionMode != -1:
            self.setSelectionMode(selectionMode)
        if data:
            self.setTable(data)
        if sortable:
            self.setSortingEnabled(True)
            self.connect(self.horizontalHeader(), SIGNAL("sectionClicked(int)"), self.sort)
        if callback:
            QObject.connect(self, SIGNAL('cellClicked(int, int)'), callback)
        self.sqlite = SQLiteHandler('local|SavedObjects.db')
    def setTable(self, data, keys = None):
        print 'in table set'
        if data==None:
            print 'No data to place in table'
            return
        if not keys:
            keys = [str(key) for key in data.keys()]
        self.setHidden(True)
        self.dataTable = self.sqlite.dictToTable(data)
        qApp.setOverrideCursor(Qt.WaitCursor)
        #print data
        self.clear()
        self.setRowCount(len(data[data.keys()[0]]))
        self.setColumnCount(len(data.keys()))

        self.setHorizontalHeaderLabels(keys)
        if 'row_names' in data.keys(): ## special case if the keyword row_names is present we want to populate the rownames of the table
            self.setVerticalHeaderLabels([str(item) for item in data['row_names']])
        n = 0
        for key in keys:
            m = 0
            for item in data[key]:
                newitem = QTableWidgetItem(str(item))
                self.setItem(m, n, newitem)
                m += 1
            n += 1
        
        self.setHidden(False)
        qApp.restoreOverrideCursor()

    def sort(self, index):
        if index == self.oldSortingIndex:
            order = self.oldSortingOrder == Qt.AscendingOrder and Qt.DescendingOrder or Qt.AscendingOrder
        else:
            order = Qt.AscendingOrder
        self.oldSortingIndex = index
        self.oldSortingOrder = order
        
    def getSettings(self):
        try:
            r = {'data': self.dataTable,'selection':[[i.row(),i.column()] for i in self.selectedIndexes()]}
            if self.oldSortingIndex:
                r['sortIndex'] = self.oldSortingIndex
                r['order'] = self.oldSortingOrder
            
        except Exception as inst:
            print r
            print inst
            r = {'data':None}
        return r
    def loadSettings(self,data):
        self.setTable(self.sqlite.tableToDict(data['data']))
        
        if 'sortIndex' in data.keys():
            self.sortByColumn(data['sortIndex'],data['order'])
        if 'selection' in data.keys() and len(data['selection']):
            for i in data['selection']:
                self.setItemSelected(self.item(i[0],i[1]),True)

    def delete(self):
        sip.delete(self)