"""comboBox, a selectable box for choosing from one of several values.

The comboBox always has an element selected as currentText().  This is accessible using currentId() also.  The constructor takes a list of key value pairs to set the available options.
"""

from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from OrderedDict import OrderedDict
import redRLog
import redRi18n
_ = redRi18n.get_(package = 'base')
class comboBox(QComboBox,widgetState):
    def __init__(self,widget,label=None, displayLabel=True, includeInReports=True, 
    items=None, editable=False, orientation='horizontal',callback = None, toolTip = None):
        
        widgetState.__init__(self,widget,label,includeInReports)
        QComboBox.__init__(self,self.controlArea)
        
        if displayLabel:
            self.hb = widgetBox(self.controlArea,orientation=orientation)
            lb = widgetLabel(self.hb, label)
            self.hb.layout().addWidget(self)
            self.hasLabel = True
            self.hb.layout().setAlignment(lb,Qt.AlignRight)
            lb.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        else:
            self.controlArea.layout().addWidget(self)
            self.hasLabel = False
        self.label = label
        
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        
        self.items = OrderedDict()
        self.setEditable(editable)

        if items:
            self.addItems(items)

        if callback:
            QObject.connect(self, SIGNAL('activated(int)'), callback)
        if toolTip:
            self.setToolTip(toolTip)
    def getSettings(self):            
        """Standard getSettings"""
        r = {'items':self.items,
             'current':self.currentIndex()}
        return r
    
    def loadSettings(self,data):
        """Standard loadSettings"""
        # print _('in comboBox load')
        # print data

        self.update(data['items'])
        self.setCurrentIndex(data['current'])
    
    def currentId(self):
        """Returns the current ID"""
        try:
            return self.items.keys()[self.currentIndex()]
        except:
            return None
    def currentItem(self):
        """Returns the current key value pair"""
        return {self.items.keys()[self.currentIndex()]:self.items.values()[self.currentIndex()]}
    def setCurrentId(self,id):
        """Sets the current ID, the ID's value will apear in the comboBox"""
        try:
            self.setCurrentIndex(self.items.keys().index(id))
        except:
            pass
    def addItems(self,items):
        """Adds items to the comboBox, new items will appear after old ones"""
        if type(items) in [dict,OrderedDict]:
            for k,v in items.items():
                self.addItem(k,v)
        elif type(items) in [list]:
            if len(items) > 0 and type(items[0]) is tuple:
                for k,v in items:
                    self.addItem(k,v)
            else:
                for v in items:
                    self.addItem(v,v)
            # redRLog.log(redRLog.REDRCORE,redRLog.DEBUG,_('In listBox should not use list'))
        else:
            raise Exception(_('In comboBox, addItems takes a list, dict or OrderedDict'))
    
    def update(self, items):
        """Clears the comboBox and adds new items, sets the current ID to the previously selected ID if found in the items"""
        current = self.currentId()
        self.clear()
        self.addItems(items)
        self.setCurrentId(current)
        
    def clear(self):
        """Removes all items from the comboBox"""
        QComboBox.clear(self)
        self.items = OrderedDict()
    def addItem(self,id,item):
        """Adds a single item"""
        QComboBox.addItem(self,item)
        self.items[id] = item
            
    def getReportText(self, fileDir):
        """Standard getReportText"""
        r = {self.widgetName:{'includeInReports': self.includeInReports, 'text': self.currentText()}}
        #return '%s set to %s' % (self.label, self.currentText())
        return r
