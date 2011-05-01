## TRUE FALSE button, only one checkbox and the function returns either 'TRUE' if checked or 'FALSE' if not.

from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.groupBox import groupBox
from OrderedDict import OrderedDict
import redRReports,redRLog

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRi18n
_ = redRi18n.get_(package = 'base')
class TFCheckBox(widgetState,QWidget):
    def __init__(self,widget,label = None, displayLabel= True, includeInReports=True,
    toolTip = None, setChecked=False,
    orientation='vertical',callback = None):
        QWidget.__init__(self,widget)
        widgetState.__init__(self,widget,label,includeInReports)
        

        self.controlArea.layout().addWidget(self)

        self.box = widgetBox(self.controlArea,orientation=orientation)
        
        self.controlArea.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.box.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,
        QSizePolicy.Preferred))
        
        # if orientation=='vertical':
            # self.box.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,
            # QSizePolicy.MinimumExpanding))
        # else:
            # self.box.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,
            # QSizePolicy.Preferred))
            
        self.label = label
        self.items = OrderedDict()
        self.buttons = QButtonGroup(self.box)
        self.buttons.setExclusive(False)
        self.addButton('TRUE', label, toolTip)


        if callback:
            QObject.connect(self.buttons, SIGNAL('buttonClicked(int)'), callback)
        if setChecked:
            self.setChecked('TRUE')

    def addButton(self,id, text,toolTip=None):
        self.items[id] = text
        w = QCheckBox(text)
        if toolTip:
            w.setToolTip(toolTip)
        self.buttons.addButton(w,self.items.keys().index(id))
        self.box.layout().addWidget(w)
                    
    def setSizePolicy(self, h,w):
        # self.controlArea.setSizePolicy(h,w)
        # QWidget.setSizePolicy(self,h,w)
        self.box.setSizePolicy(h,w)
            
    def setChecked(self,ids):
        for i in self.buttons.buttons():
            id = self.buttons.id(i)
            if unicode(self.items.keys()[id]) in ids: i.setChecked(True)
            else: i.setChecked(False)
        
    def checked(self):
        if 'TRUE' in self.getCheckedIds(): return 'TRUE'
        else: return 'FALSE'

    def getChecked(self):
        return self.getCheckedItems().values()
        # checked = []
        # for i in self.buttons.buttons():
            # if i.isChecked(): checked.append(unicode(i.text()))
        # return checked
    def getCheckedIds(self):
        return self.getCheckedItems().keys()
        # checked = []
        # for i in self.buttons.buttons():
            # if i.isChecked(): checked.append(self.items.keys()[i.id()])
        # return checked
        
    def getCheckedItems(self):
        checked = {}
        for i in self.buttons.buttons():
            id = self.buttons.id(i)
            if i.isChecked(): checked[self.items.keys()[id]] = self.items[self.items.keys()[id]]
        return checked
        
    def getUnchecked(self):
        unChecked = []
        for i in self.buttons.buttons():
            if not i.isChecked(): unChecked.append(unicode(i.text()))
        return unChecked
    
    def buttonAt(self,ind):
        return unicode(self.buttons.button(ind).text())
                
    def getSettings(self):
        #print _('radioButtons getSettings') + self.getChecked()
        r = {'items':self.items, 'checked': self.getCheckedIds()}
        return r
    def loadSettings(self,data):
        #print _('radioButtons loadSettings') + data
        #self.addButtons(data['items'])
        self.setChecked(data['checked'])
        
    def getReportText(self, fileDir):
        selected = self.getChecked()

        if len(selected):
            text='Checked: ' + ', '.join(selected)
        else:
            text= _('Nothing Checked')
        r = {self.widgetName:{'includeInReports': self.includeInReports, 'text': text}}
        # print '@@@@@@@@@@@@@@@@@@@@@@@', r
        #t = 'The following items were checked in %s:\n\n%s\n\n' % (self.label, self.getChecked())
        return r

