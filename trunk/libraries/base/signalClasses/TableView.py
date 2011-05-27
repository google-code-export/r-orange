"""Table View signal class.  This is a holder signal class that should be reimplimented in other signals.  The table view signal class can return table views to the view data table widget."""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class TableView():
    def __init__(self, **kwargs):
        pass

    def getTableModel(self, widget, filterable = True, sortable = True):
        
        raise Exception("This is a dummy class, no table model can be returned from this class.  The developer must impliment a table model for the requested signal class.")
        #return MyTableModel(widget)


class BlankTableModel(QAbstractTableModel): 
    def __init__(self,parent): 
        QAbstractTableModel.__init__(self,parent)
        pass

        
        
    def getSummary(self):
        """Required, reimpliment to return a string representing the data."""
        return ''
        
    def clearFiltering(self):
        """Required, reimpliment to clear filtering criteria."""
        pass

    def flags(self,index):
        """Required, reimpliment to set flags for each item in the index, this can be quite complicated if you want..."""
        if self.editable:
            return (Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
        else:
            return (Qt.ItemIsSelectable | Qt.ItemIsEnabled)
 
    def rowCount(self, parent):
        """Required, reimpliment to return the current number of rows in the filtered data."""
        return 1
    def columnCount(self, parent): 
        """Required, reimpliment to return the current number of columns in the filtered data."""
        return 1

    def data(self, index, role): 
        """Required, reimpliment to return a QVariant representing the data in the index requested."""
        return QVariant() 

    def headerData(self, col, orientation, role):
        """Required, reimpliment to return a QVariant representing the header data for the requested column (col)."""
        return QVariant()
    

    def sort(self, Ncol, order):
        """Required, reimpliment to apply sorting to the column requested.  Logic can be implimented to pass if sorting is not allowed."""
        if self.editable: return
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        ### reset the table for sorting
        self.emit(SIGNAL("layoutChanged()"))