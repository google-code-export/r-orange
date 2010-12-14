from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.groupBox import groupBox

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class radioButtons(widgetState,QWidget):
    def __init__(self,widget,label='Radio Button', displayLabel=True, includeInReports=True,
    buttons=None,toolTips = None, setChecked = None,
    orientation='vertical',callback = None, **args):
        
        QWidget.__init__(self,widget)
        widgetState.__init__(self,widget,label,includeInReports,**args)
        
        self.controlArea.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.label = label
        

        if displayLabel:
            self.box = groupBox(self.controlArea,label=label,orientation=orientation)
            self.controlArea.layout().addWidget(self.box)
        else:
            self.box = widgetBox(self.controlArea,orientation=orientation)

        # if orientation=='vertical':
            # self.box.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,
            # QSizePolicy.MinimumExpanding))
        # else:
            # self.box.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,
            # QSizePolicy.Preferred))
            
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
        else: return unicode(button.text())
    
    def disable(self,buttons):
        for i in self.buttons.buttons():
            if i.text() in buttons: i.setDisabled(True)

    def enable(self,buttons):
        for i in self.buttons.buttons():
            if i.text() in buttons: i.setEnabled(True)
    def getSettings(self):
        #print 'radioButtons getSettings' + self.getChecked()
        r = {'checked': self.getChecked()}
        return r
    def loadSettings(self,data):
        #print 'radioButtons loadSettings' + data
        self.setChecked(data['checked'])
        
    def getReportText(self, fileDir):
        r = {self.widgetName:{'includeInReports': self.includeInReports, 'text': self.getChecked()}}
        return r


