from redRGUI import widgetState
from widgetBox import widgetBox
from groupBox import groupBox

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class checkBox(widgetBox,widgetState):
    def __init__(self,widget,label=None,buttons = None,toolTips = None, setChecked=None,
    orientation='vertical',callback = None, **args):
        
        widgetBox.__init__(self,widget,orientation=orientation)
            
        if label:
            self.box = groupBox(self,label=label,orientation=orientation)
            self.layout().addWidget(self.box)
        else:
            self.box = self
            
        self.buttons = QButtonGroup(self.box)
        self.buttons.setExclusive(False)
        for i,b in zip(range(len(buttons)),buttons):
            w = QCheckBox(b)
            if toolTips:
                w.setToolTip(toolTips[i])
            self.buttons.addButton(w)
            self.box.layout().addWidget(w)

        if callback:
            QObject.connect(self.buttons, SIGNAL('buttonClicked(int)'), callback)
        if setChecked:
            self.setChecked(setChecked)
            
    def setChecked(self,ids):
        for i in self.buttons.buttons():
            if i.text() in ids: i.setChecked(True)
    def getChecked(self):
        checked = []
        for i in self.buttons.buttons():
            if i.isChecked(): checked.append(i.text())

        return checked
      
    def getSettings(self):
        # print 'radioButtons getSettings' + self.getChecked()
        r = {'checked': self.getChecked()}
        return r
    def loadSettings(self,data):
        # print 'radioButtons loadSettings'
        # print data
        self.setChecked(data['checked'])
        
        # return
        
        

