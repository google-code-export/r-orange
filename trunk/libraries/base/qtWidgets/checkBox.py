"""checkBox

A labeled collection of checkboxes.  Boxes can either be checked or not and they act independently.
"""
from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.groupBox import groupBox
from OrderedDict import OrderedDict
import redRReports,redRLog

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRi18n
_ = redRi18n.get_(package = 'base')
class checkBox(widgetState,QWidget):
    def __init__(self,widget,label = None, displayLabel= True, includeInReports=True,
    buttons = None,toolTips = None, setChecked=None,
    orientation='vertical',callback = None):
        """Constructor, common parameters will be widget, label, buttons (a list or list-tuple of key values for buttons), toolTips (a list of toolTips for the buttons), and setChecked (a list of keys to check from the buttons)"""
        if toolTips and len(toolTips) != len(buttons):
            raise RuntimeError(_('Number of buttons and toolTips must be equal'))
 
        QWidget.__init__(self,widget)
        widgetState.__init__(self,widget,label,includeInReports)
        

        self.controlArea.layout().addWidget(self)

        if displayLabel:
            self.box = groupBox(self.controlArea,label=label,orientation=orientation)
            # self.layout().addWidget(self.box)
        else:
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
        if buttons:
            self.addButtons(buttons)


        if callback:
            QObject.connect(self.buttons, SIGNAL('buttonClicked(int)'), callback)
        if setChecked:
            self.setChecked(setChecked)

    def addButtons(self,buttons):
        """Internal function to add buttons.  Can be called by end developer but should be extensively tested to ensure the desired functionality"""
        if type(buttons) in [dict,OrderedDict]:
            for k,v in buttons.items():
                self.addButton(k,v)
        elif type(buttons) in [list]:
            if len(buttons) > 0 and type(buttons[0]) is tuple:
                for k,v in buttons:
                    self.addButton(k,v)
            else:
                for v in buttons:
                    self.addButton(v,v)

            # redRLog.log(redRLog.REDRCORE,redRLog.DEBUG,_('In radioButtons should not use list'))
        else:
            raise Exception(_('In radioButtons, addButtons takes a list, dict or OrderedDict'))

    def addButton(self,id, text,toolTip=None):
        """Internal function called by addButtons"""
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
        """Sets the keys listed in ids to checked"""
        for i in self.buttons.buttons():
            id = self.buttons.id(i)
            if unicode(self.items.keys()[id]) in ids: i.setChecked(True)
            else: i.setChecked(False)
    
    def checkAll(self):
        """Checks all of the buttons"""
        for i in self.buttons.buttons():
            i.setChecked(True)
    def uncheckAll(self):
        """Unchecks all of the buttons"""
        for i in self.buttons.buttons():
            i.setChecked(False)
    def clear(self):
        """Removes all buttons from the widget.  Should be called before an end developer calls addButtons"""
        self.items = {}
        for i in self.buttons.buttons():
            self.removeButton(i)
    def getChecked(self):
        """Returns a list of checked button's labels"""
        return self.getCheckedItems().values()
        
    def getCheckedIds(self):
        """Returns a list of checked button's IDs"""
        return self.getCheckedItems().keys()
        
    def getCheckedItems(self):
        """Returns a dict of checked keys and labels"""
        checked = {}
        for i in self.buttons.buttons():
            id = self.buttons.id(i)
            if i.isChecked(): checked[self.items.keys()[id]] = self.items[self.items.keys()[id]]
        return checked
    def getUncheckedItems(self):
        """Returns a dict of unchecked keys and labels"""
        checked = {}
        for i in self.buttons.buttons():
            id = self.buttons.id(i)
            if not i.isChecked(): checked[self.items.keys()[id]] = self.items[self.items.keys()[id]]
        return checked
    def getUnchecked(self):
        """Same as getChecked but reversed"""
        return self.getUncheckedItems.values()
    def getUncheckedIds(self):
        """Same as getCheckedIds but reversed"""
        return self.getUncheckedItems.keys()
    
    def buttonAt(self,ind):
        """Returns the button at a given index"""
        return unicode(self.buttons.button(ind).text())
                
    def getSettings(self):
        """Called by :mod:`widgetSettings` to get settings"""
        #print _('radioButtons getSettings') + self.getChecked()
        r = {'items':self.items, 'checked': self.getCheckedIds()}
        return r
    def loadSettings(self,data):
        """Called by :mod:`widgetSettings` to set settings"""
        #print _('radioButtons loadSettings') + data
        #self.addButtons(data['items'])
        self.setChecked(data['checked'])
        
    def getReportText(self, fileDir):
        """Returns report text for report generator"""
        selected = self.getChecked()

        if len(selected):
            text='Checked: ' + ', '.join(selected)
        else:
            text= _('Nothing Checked')
        r = {self.widgetName:{'includeInReports': self.includeInReports, 'text': text}}
        # print '@@@@@@@@@@@@@@@@@@@@@@@', r
        #t = 'The following items were checked in %s:\n\n%s\n\n' % (self.label, self.getChecked())
        return r

