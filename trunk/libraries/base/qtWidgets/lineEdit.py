from redRGUI import widgetState

from widgetBox import widgetBox
from widgetLabel import widgetLabel
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class lineEdit(QLineEdit,widgetState):
    def __init__(self,widget,text='', label=None,orientation='horizontal', toolTip = None,  width = 0, callback = None, **args):
        QLineEdit.__init__(self,widget)
        if widget:
            if label:
                self.hb = widgetBox(widget,orientation=orientation)
                widgetLabel(self.hb, label)
                if width != -1:
                    sb = widgetBox(self.hb)
                    sb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.hb.layout().addWidget(self)
                self.hasLabel = True
            else:
                widget.layout().addWidget(self)
                self.hasLabel = False
        if toolTip: self.setToolTip(toolTip)
        if width == 0:
            self.setMaximumWidth(175)
            self.setMinimumWidth(175)
        elif width == -1:
            pass
        else:
            self.setMaximumWidth(width)
            self.setMinimumWidth(width)
        self.setText(text)
        # self.setText('asdf')
        if callback:
            QObject.connect(self, SIGNAL('returnPressed()'), callback)
    def getSettings(self):
        #print 'in get settings' + self.text()
        r = {'text': self.text()}
        # print r
        return r
    def hide(self):
        if self.hasLabel:
            self.hb.hide()
        else:
            QLineEdit.hide(self)
    def show(self):
        if self.hasLabel:
            self.hb.show()
        else:
            QLineEdit.show(self)
    def loadSettings(self,data):
        try:
            #print 'called load' + str(value)     
            self.setText(unicode(data['text']))
            #self.setEnabled(data['enabled'])
        except:
            print 'Loading of lineEdit encountered an error.'