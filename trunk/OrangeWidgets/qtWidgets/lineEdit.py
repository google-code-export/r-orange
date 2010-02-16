from redRGUI import widgetState

from widgetBoxNoLabel import widgetBoxNoLabel
from widgetLabel import widgetLabel
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class lineEdit(QLineEdit,widgetState):
    def __init__(self,widget,text='', label=None,orientation='vertical', **args):
        QLineEdit.__init__(self,widget)
        if label:
            hb = widgetBoxNoLabel(widget,orientation=orientation)
            widgetLabel(hb, label)
            hb.layout().addWidget(self)
        else:
            widget.layout().addWidget(self)
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
