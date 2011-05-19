"""Widget Box

A box to put other widgets into.  Boxes are set up with a layout that places new widgets into the widget in either a horizontal or vertical alignment.

"""

from redRGUI import widgetState
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redREnviron, os
import redRi18n
_ = redRi18n.get_(package = 'base')
class widgetBox(QWidget,widgetState):
    def __init__(self,widget, orientation='vertical', addSpace=False, includeInReports=True,
    sizePolicy = None, margin = -1, spacing = -1, addToLayout = 1, alignment=Qt.AlignTop, helpButton = False):

        widgetState.__init__(self,widget, _('WidgetBox'),includeInReports)
        QWidget.__init__(self,self.controlArea)
            
        self.controlArea.layout().addWidget(self)
        # self.setFlat(flat)
        # if widget and widget.layout():
            # widget.layout().addWidget(self)
        
        try:
            if isinstance(orientation, QLayout):
                self.setLayout(orientation)
            elif orientation == 'horizontal' or not orientation:
                self.setLayout(QHBoxLayout())
            elif orientation == 'grid':
                self.setLayout(QGridLayout())
            else:
               self.setLayout(QVBoxLayout())
        except:
            self.setLayout(QVBoxLayout())
            
        if self.layout() == 0 or self.layout() == None:
            self.setLayout(QVBoxLayout())
        if helpButton:
            icon = QPixmap(os.path.join(redREnviron.directoryNames['redRDir'], 'canvas', 'icons', 'information.png'))
            tlabel = QLabel()
            tlabel.setPixmap(icon)
            self.layout().addWidget(tlabel)

            
        self.controlArea.layout().setAlignment(alignment)            

        if spacing == -1: spacing = 4
        self.layout().setSpacing(spacing)
        if margin == -1: margin = 0
        if margin != -1:
            self.layout().setMargin(margin)
        if widget:
            if addSpace and isinstance(addSpace, int):
                separator(self.controlArea, 0, addSpace)
            elif addSpace:
                separator(self.controlArea)
        if sizePolicy:
            self.setSizePolicy(sizePolicy)
    
    def layout(self):
        """Returns the layout of the box."""
        return QWidget.layout(self)
    
    def delete(self):
        sip.delete(self)
  
