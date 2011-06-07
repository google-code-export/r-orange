"""
custom message dialog that is called with exec_ (a Qt funciton).  
This dialog will take any redRGUI qtwidget as its child.
"""
from redRGUI import widgetState

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRi18n
_ = redRi18n.get_(package = 'base')

class dialog(QDialog,widgetState):
    def __init__(self, parent = None, layout = 'vertical',title=None, callback = None):
        kwargs.setdefault('includeInReports', True)
        kwargs.setdefault('sizePolicy', QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        widgetState.__init__(self, self, 'dialog',**kwargs)
        QDialog.__init__(self,parent)

        if title:
            self.setWindowTitle(title)
        if layout == 'horizontal':
            self.setLayout(QHBoxLayout())
        else:
            self.setLayout(QVBoxLayout())
        if callback:
            QObject.connect(self, SIGNAL('accepted()'), callback)
            QObject.connect(self, SIGNAL('rejected()'), callback)