from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.groupBox import groupBox

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class checkBox(widgetState,QWidget):
    def __init__(self,widget,label = None, displayLabel= True, includeInReports=True,
    buttons = None,toolTips = None, setChecked=None,
    orientation='vertical',callback = None):
        
        if toolTips and len(toolTips) != len(buttons):
            raise RuntimeError('Number of buttons and toolTips must be equal')
 
        QWidget.__init__(self,widget)
        widgetState.__init__(self,widget,label,includeInReports)
        
        self.controlArea.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.controlArea.layout().addWidget(self)

        if displayLabel:
            self.box = groupBox(self.controlArea,label=label,orientation=orientation)
            # self.layout().addWidget(self.box)
        else:
            self.box = widgetBox(self.controlArea,orientation=orientation)
        
        # if orientation=='vertical':
            # self.box.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,
            # QSizePolicy.MinimumExpanding))
        # else:
            # self.box.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,
            # QSizePolicy.Preferred))
            
        self.label = label
        self.buttons = QButtonGroup(self.box)
        self.buttons.setExclusive(False)
        if buttons:
            for i,b in zip(range(len(buttons)),buttons):
                w = QCheckBox(b,self.box)
                # if toolTips:
                    # w.setToolTip(toolTips[i])
                self.buttons.addButton(w,i)
                self.box.layout().addWidget(w)

        if callback:
            QObject.connect(self.buttons, SIGNAL('buttonClicked(int)'), callback)
        if setChecked:
            self.setChecked(setChecked)
    def setSizePolicy(self, h,w):
        # self.controlArea.setSizePolicy(h,w)
        # QWidget.setSizePolicy(self,h,w)
        self.box.setSizePolicy(h,w)
            
    def setChecked(self,ids):
        for i in self.buttons.buttons():
            if unicode(i.text()) in ids: i.setChecked(True)
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
            if i.isChecked(): checked.append(unicode(i.text()))
        return checked
    def buttonAt(self,ind):
        return unicode(self.buttons.button(ind).text())
        
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
        # print '@@@@@@@@@@@@@@@@@@@@@@@', r
        #t = 'The following items were checked in %s:\n\n%s\n\n' % (self.label, self.getChecked())
        return r

