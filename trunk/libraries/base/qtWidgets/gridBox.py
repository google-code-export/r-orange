"""Grid Box

A grid layout that allows the developer to set items in a grid.  Each grid cell is actually a widgetBox with it's own layout.
"""

from redRGUI import widgetState
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libraries.base.qtWidgets.widgetBox import *
import redRi18n
_ = redRi18n.get_(package = 'base')
class gridBox(QWidget,widgetState):
    def __init__(self,widget, addToLayout = 1, alignment=Qt.AlignTop, spacing = -1, margin = -1,**kwargs):
        kwargs.setdefault('includeInReports', True)
        kwargs.setdefault('sizePolicy', QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        widgetState.__init__(self,widget, _('GridBox'),**kwargs)
        QWidget.__init__(self,self.controlArea)
        
        self.controlArea.layout().addWidget(self)
        
        self.setLayout(QGridLayout())
        
        self.controlArea.layout().setAlignment(alignment)            
        if spacing == -1: spacing = 4
        self.layout().setSpacing(spacing)
        if margin == -1: margin = 0
        self.layout().setMargin(margin)
        self.widgetArray = {}
    def cell(self, row, col):
        """Returns the widgetBox at the cell indicated.  If the cell does not exist yet, it is generated."""
        ## return the widgetbox in the specified cell
        if (row, col) not in self.widgetArray.keys():
            self.widgetArray[(row, col)] = widgetBox(None)
            self.layout().addWidget(self.widgetArray[(row, col)], row, col)
        return self.widgetArray[(row, col)]