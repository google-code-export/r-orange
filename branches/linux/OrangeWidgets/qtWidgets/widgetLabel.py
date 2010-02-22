from redRGUI import widgetState
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class widgetLabel(QLabel,widgetState):
    def __init__(self,widget,text):
        QLabel.__init__(self,widget)
        try:
            print 'this widget has a layout' + str(widget.layout())
            widget.layout().addWidget(self)
        except:
            widget.addWidget(self)
        self.setText(text)
    def getSettings(self):
        # print 'in widgetLabel getSettings'
        r = {'text':self.text()}
        r.update(self.getState())
        # print r
        return r
    def loadSettings(self,data):
        # print 'in widgetLabel loadSettings'
        # print data
        self.setText(data['text'])
        self.setState(data)
    
        

