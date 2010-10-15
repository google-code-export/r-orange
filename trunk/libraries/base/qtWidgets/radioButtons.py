from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.groupBox import groupBox

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class radioButtons(widgetBox,widgetState):
    def __init__(self,widget,label=None, buttons=None,toolTips = None, setChecked = None,
    orientation='vertical',callback = None, **args):
        
        widgetBox.__init__(self,widget,orientation=orientation)
        self.label = label
        if label:
            self.box = groupBox(self,label=label,orientation=orientation)
            self.layout().addWidget(self.box)
        else:
            self.box = self
            
        self.buttons = QButtonGroup(self.box)
        for i,b in zip(range(len(buttons)),buttons):
            w = QRadioButton(b)
            if toolTips:
                w.setToolTip(toolTips[i])
            self.buttons.addButton(w)
            self.box.layout().addWidget(w)

        if callback:
            QObject.connect(self.buttons, SIGNAL('buttonClicked(int)'), callback)

        if setChecked:
            self.setChecked(setChecked)
        
    def addButton(self,text,toolTip=None):
        w = QRadioButton(text)
        if toolTip:
            w.setToolTip(toolTip)
        self.buttons.addButton(w)
        self.box.layout().addWidget(w)
    def setChecked(self,id):
        for i in self.buttons.buttons():
            if i.text() == id: i.setChecked(True)
            else: i.setChecked(False)
    def getChecked(self):
        button = self.buttons.checkedButton()
        if button == 0 or button == None or button.isEnabled()==False: return 0
        else: return str(button.text().toAscii())
    
    def disable(self,buttons):
        for i in self.buttons.buttons():
            if i.text() in buttons: i.setDisabled(True)

    def enable(self,buttons):
        for i in self.buttons.buttons():
            if i.text() in buttons: i.setEnabled(True)

    def hide(self):
        self.box.hide()
    def show(self):
        self.box.show()
        
    def getSettings(self):
        #print 'radioButtons getSettings' + self.getChecked()
        r = {'checked': self.getChecked()}
        return r
    def loadSettings(self,data):
        #print 'radioButtons loadSettings' + data
        self.setChecked(data['checked'])
        
    def getReportText(self, fileDir):
        if not self.label:
            label = "RadioButton with No Label"
        else:
            label = self.label
        r = {'label': label, 'text': self.getChecked()}

        #text = '%s with the following element selected:\n\n' % (self.label, self.getChecked())
        return r


