from redRGUI import widgetState # the great irony is that this widget does not need a widget state
from PyQt4.QtCore import *
from PyQt4.QtGui import *

        
class widgetBoxNoLabel(QWidget):
    def __init__(self,widget, name = '', orientation=QVBoxLayout(), addSpace=False, sizePolicy = None, margin = -1, spacing = -1, flat = 0, addToLayout = 1):
        QWidget.__init__(self,widget)
        
        if widget.layout():
            widget.layout().addWidget(self)
        
        if margin == -1: margin = 0
        try:
            if isinstance(orientation, QLayout):
                self.setLayout(orientation)
            elif orientation == 'horizontal' or not orientation:
                self.setLayout(QHBoxLayout())
            else:
                self.setLayout(QVBoxLayout())
        except:
            self.setLayout(QVBoxLayout())
            
        if self.layout() == 0 or self.layout() == None:
            self.setLayout(QVBoxLayout())
        if sizePolicy:
            self.setSizePolicy(sizePolicy)

        if spacing == -1: spacing = 4
        self.layout().setSpacing(spacing)
        if margin != -1:
            self.layout().setMargin(margin)

        if addSpace and isinstance(addSpace, int):
            separator(widget, 0, addSpace)
        elif addSpace:
            separator(widget)
