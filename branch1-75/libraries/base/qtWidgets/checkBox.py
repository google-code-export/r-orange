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
        self.label = label
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
            if str(i.text()) in ids: i.setChecked(True)
            else: i.setChecked(False)
    def getChecked(self):
        checked = []
        for i in self.buttons.buttons():
            if i.isChecked(): checked.append(str(i.text()))

        return checked
    def hide(self):
        self.box.hide()
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
        print 'getting report for checkBox'
        t = ''
        if self.label:
            t += str(self.label)+': '

        t += '</br><table border = "1"><tr><th>Items</th><th>Checked</th></tr>'
        for i in self.buttons.buttons():
            t += '<tr><td>'+str(i.text())+'</td><td>'
            if i.isChecked():
                t += 'X'
            t += '</td></tr>'
        t += '</table></br>'
        return t

