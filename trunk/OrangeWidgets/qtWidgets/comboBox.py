from redRGUI import widgetState
from widgetBox import widgetBox
from widgetLabel import widgetLabel

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class comboBox(QComboBox,widgetState):
    def __init__(self,widget,label=None, items=None, orientation='vertical',callback = None, **args):
        
        QComboBox.__init__(self,widget)
        if label:
            hb = widgetBox(widget,orientation=orientation)
            widgetLabel(hb, label)
            hb.layout().addWidget(self)
        else:
            widget.layout().addWidget(self)
        if items:
            self.addItems([unicode(i) for i in items])
        # print callback
        if callback:
            # print callback
            QObject.connect(self, SIGNAL('activated(int)'), callback)

    def getSettings(self):
        items = []
        for i in range(0,self.count()):
            items.append(self.itemText(i))
        
        r = {'items':items,'current':self.currentIndex(),'enabled':self.isEnabled()}
        return r
        
    def loadSettings(self,data):
        self.clear()
        self.addItems([unicode(i) for i in data['items']])
        self.setCurrentIndex(data['current'])
        self.setEnabled(data['enabled'])

        
