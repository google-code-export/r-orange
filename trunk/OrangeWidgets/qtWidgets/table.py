from redRGUI import widgetState
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class table(widgetState,QTableWidget):
    def __init__(self,widget,data=None, rows = 0, columns = 0, sortable = False, selectionMode = -1, addToLayout = 1):
        QTableWidget.__init__(self,rows,columns,widget)
        self.sortIndex = None
        self.oldSortingIndex = None
        self.data = None
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
        
    def setTable(self, data):
        print 'in table set'
        if data==None:
            return
        self.setHidden(True)
        self.data = data
        qApp.setOverrideCursor(Qt.WaitCursor)
        #print data
        self.clear()
        self.setRowCount(len(data[data.keys()[0]]))
        self.setColumnCount(len(data.keys()))

        n = 0
        for key in data:
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
    
        r = {'data': self.data,'selection':[[i.row(),i.column()] for i in self.selectedIndexes()]}
        if self.oldSortingIndex:
            r['sortIndex'] = self.oldSortingIndex
            r['order'] = self.oldSortingOrder
            
        # print r
        return r
    def loadSettings(self,data):
        self.setTable(data['data'])
        if 'sortIndex' in data.keys():
            self.sortByColumn(data['sortIndex'],data['order'])
        #print 'aaaaaaaaatable#########################'
        if 'selection' in data.keys() and len(data['selection']):
            for i in data['selection']:
                self.setItemSelected(self.item(i[0],i[1]),True)

    def delete(self):
        sip.delete(self)