from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.groupBox import groupBox

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class checkBox(widgetState):
    def __init__(self,widget,label = None, displayLabel= True, includeInReports=True,
    buttons = None,toolTips = None, setChecked=None,
    orientation='vertical',callback = None, **args):
        
        widgetState.__init__(self,widget,label,includeInReports,**args)

        if displayLabel:
            self.box = groupBox(self.controlArea,label=label,orientation=orientation)
        else:
            self.box = widgetBox(self.controlArea,orientation=orientation)
            
        self.label = label
        self.buttons = QButtonGroup(self.box)
        self.buttons.setExclusive(False)
        if buttons:
            for i,b in zip(range(len(buttons)),buttons):
                w = QCheckBox(b)
                if toolTips:
                    w.setToolTip(toolTips[i])
                self.buttons.addButton(w,i)
                self.box.layout().addWidget(w)

        if callback:
            QObject.connect(self.buttons, SIGNAL('buttonClicked(int)'), callback)
        if setChecked:
            self.setChecked(setChecked)
            
    def setChecked(self,ids):
        for i in self.buttons.buttons():
            if str(i.text().toAscii()) in ids: i.setChecked(True)
            else: i.setChecked(False)
    def checkAll(self):
        for i in self.buttons.buttons():
            i.setChecked(True)
    def uncheckAll(self):
        for i in self.buttons.buttons():
            i.setChecked(False)
        
    def getChecked(self):
        checked = []
        for i in self.buttons.buttons():
            if i.isChecked(): checked.append(str(i.text().toAscii()))
        return checked
    def buttonAt(self,ind):
        return str(self.buttons.button(ind).text().toAscii())
        
    def getSettings(self):
        # print 'radioButtons getSettings' + self.getChecked()
        r = {'checked': self.getChecked()}
        return r
    def loadSettings(self,data):
        print 'checkBox loadSettings'
        print data
        self.setChecked(data['checked'])
        
        # return
        
    def getReportText(self, fileDir):
        selected = self.getChecked()

        if len(selected):
            text='Checked: ' + ', '.join(selected)
        else:
            text= 'Nothing Checked'
        r = {self.widgetName:{'includeInReports': self.includeInReports, 'text': text}}
        print '@@@@@@@@@@@@@@@@@@@@@@@', r
        #t = 'The following items were checked in %s:\n\n%s\n\n' % (self.label, self.getChecked())
        return r

