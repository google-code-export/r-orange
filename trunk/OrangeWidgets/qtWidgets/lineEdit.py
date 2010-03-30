from redRGUI import widgetState

from widgetBox import widgetBox
from widgetLabel import widgetLabel
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class lineEdit(QLineEdit,widgetState):
    def __init__(self,widget,text='', label=None,orientation='horizontal', toolTip = None,  callback = None, **args):
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
        self.setMaximumWidth(175)
        self.setMinimumWidth(175)
        self.setText(text)
        if callback:
            QObject.connect(self, SIGNAL('returnPressed()'), callback)
    def getSettings(self):
        #print 'in get settings' + self.text()
        r = {'text': self.text()}
        r.update(self.getState())
        # print r
        return r
    def loadSettings(self,data):
        try:
            #print 'called load' + str(value)     
            self.setText(unicode(data['text']))
            #self.setEnabled(data['enabled'])
            self.setState(data)
        except:
            print 'Loading of lineEdit encountered an error.'