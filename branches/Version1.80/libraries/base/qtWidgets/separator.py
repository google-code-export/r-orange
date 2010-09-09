from redRGUI import widgetState
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class separator(QWidget,widgetState):
    def __init__(self,widget,width=8, height=8):
        QWidget.__init__(self,widget)
        if widget.layout():
            widget.layout().addWidget(self)       
        self.setFixedSize(width, height)


