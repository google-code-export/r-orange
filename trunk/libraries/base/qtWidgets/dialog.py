### custom message dialog that is called with exex_ (a Qt funciton).  This dialog will take any redRGUI qtwidget as its child.

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class dialog(QDialog):
    def __init__(self, parent = None, layout = 'vertical'):
        QDialog.__init__(self)
        
        if layout == 'horizontal':
            self.setLayout(QHBoxLayout())
        else:
            self.setLayout(QVBoxLayout())