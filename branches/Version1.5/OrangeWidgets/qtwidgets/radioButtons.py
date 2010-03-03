from redRGUI import widgetState
from widgetBox import widgetBox
from groupBox import groupBox

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class radioButtons(widgetBox,widgetState):
    def __init__(self,widget,label=None,buttons=None,orientation='vertical',callback = None, **args):
        widgetBox.__init__(self,widget,orientation=orientation)
        #widget.layout().addWidget(self)
        if(len(buttons) > 1):
            self.box = groupBox(self,label=label,orientation=orientation)
            self.layout().addWidget(self.box)
            self.buttons = QButtonGroup(self.box)
            
            
            for i in buttons:
                w = QRadioButton(i)
                self.buttons.addButton(w)
                self.box.layout().addWidget(w)
        else:
            self.buttons = QButtonGroup(self)
            
            w = QRadioButton(buttons[0])
            self.buttons.addButton(w)
            self.layout().addWidget(w)
        if callback:
            
            QObject.connect(self.buttons, SIGNAL('buttonClicked(int)'), callback)
        # if label:
            # QGroupBox.__init__(self,title,widget)
        # else:
            # QGroupBox.__init__(self,widget)
       
        # widget.layout().addWidget(self)
        # self.setLayout(QVBoxLayout())
        # self.buttons = QButtonGroup(self)
        
        # for i in buttons:
            # w = QRadioButton(i)
            # self.buttons.addButton(w)
            # self.layout().addWidget(w)
        # print 'aaaaaaaaaaaaa'
        # if callback:
            # print callback
            # QObject.connect(self.buttons, SIGNAL('buttonClicked(int)'), callback)
        
    def setChecked(self,id):
        for i in self.buttons.buttons():
            if i.text() == id: i.setChecked(True)
    def getChecked(self):
        button = self.buttons.checkedButton()
        if button == 0 or button == None: return 0
        else: return button.text()
      
    def getSettings(self):
        #print 'radioButtons getSettings' + self.getChecked()
        r = {'checked': self.getChecked()}
        r.update(self.getState())
        return r
    def loadSettings(self,data):
        #print 'radioButtons loadSettings' + data
        self.setChecked(data['checked'])
        self.setState()


