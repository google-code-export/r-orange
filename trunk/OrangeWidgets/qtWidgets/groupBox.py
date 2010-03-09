#from redRGUI import widgetState,separator
import redRGUI
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class groupBox(QGroupBox,redRGUI.widgetState):
    def __init__(self,widget, label = None, orientation='vertical', addSpace=False, sizePolicy = None, margin = -1, spacing = -1, flat = 0):
        if label:
            QGroupBox.__init__(self,label)
        else:
            QGroupBox.__init__(self)
       
        
        widget.layout().addWidget(self)

        if orientation == 'horizontal' or not orientation:
            self.setLayout(QHBoxLayout())
        else:
            self.setLayout(QVBoxLayout())
        #if sizePolicy: self.setSizePolicy(sizePolicy, sizePolicy)
        #else: 
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        if spacing == -1: spacing = 4
        self.layout().setSpacing(spacing)
        if margin != -1:
            self.layout().setMargin(margin)
        else:
            self.layout().setMargin(4)
        if addSpace and isinstance(addSpace, int):
            redRGUI.separator(widget, 0, addSpace)
        elif addSpace:
            redRGUI.separator(widget)
    def getSettings(self):
        return self.getState()
    def loadSettings(self,data):
        self.setState()

        

        

