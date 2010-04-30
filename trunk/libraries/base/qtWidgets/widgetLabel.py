from redRGUI import widgetState
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class widgetLabel(QLabel,widgetState):
    def __init__(self,widget,label = ''):
        QLabel.__init__(self,widget)
        widget.layout().addWidget(self)
        self.setText(label)
    def getSettings(self):
        # print 'in widgetLabel getSettings'
        r = {'text':self.text()}
        # print r
        return r
    def loadSettings(self,data):
        # print 'in widgetLabel loadSettings'
        # print data
        self.setText(data['text'])
    
        

