from redRGUI import widgetState

from widgetBox import widgetBox
from widgetLabel import widgetLabel
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class lineEdit(QLineEdit,widgetState):
    def __init__(self,widget,text='', label=None,orientation='horizontal', toolTip = None,  **args):
        QLineEdit.__init__(self,widget)
        
        if label:
            hb = widgetBox(widget,orientation=orientation)
            widgetLabel(hb, label)
            sb = widgetBox(hb)
            sb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            hb.layout().addWidget(self)
        else:
            widget.layout().addWidget(self)
        if toolTip: self.setToolTip(toolTip)
        self.setMaximumWidth(200)
        self.setMinimumWidth(200)
        self.setText(text)
    def getSettings(self):
        #print 'in get settings' + self.text()
        r = {'text': self.text()}
        r.update(self.getState())
        # print r
        return r
    def loadSettings(self,data):
        #print 'called load' + str(value)     
        self.setText(unicode(data['text']))
        #self.setEnabled(data['enabled'])
        self.setState(data)
