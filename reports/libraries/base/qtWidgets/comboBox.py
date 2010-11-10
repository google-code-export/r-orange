from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class comboBox(QComboBox,widgetState):
    def __init__(self,widget,label=None, displayLabel=True, includeInReports=True, 
    items=None, itemIds=None,editable=False,
    orientation='horizontal',callback = None, callback2 = None, **args):
        
        widgetState.__init__(self,widget,label,includeInReports)
        QComboBox.__init__(self,self.controlArea)
        
        if displayLabel:
            self.hb = widgetBox(self.controlArea,orientation=orientation)
            widgetLabel(self.hb, label)
            self.hb.layout().addWidget(self)
            self.hasLabel = True
        else:
            self.controlArea.layout().addWidget(self)
            self.hasLabel = False
        self.label = label

        self.ids = [] 
        
        if items:
            self.addItems([i for i in items],itemIds)
        #if editable:
        self.setEditable(editable)
        
        if callback:
            QObject.connect(self, SIGNAL('activated(int)'), callback)
            
        if callback2: # more overload for other functions
            QObject.connect(self, SIGNAL('activated(int)'), callback2)

    def getSettings(self):
        items = []
        # print 'in comboBox get'

        for i in range(0,self.count()):
            items.append(self.itemText(i))
            
        r = {'items':items,
             'current':self.currentIndex(), 
             'ids':self.ids}
        return r
    
    def loadSettings(self,data):
        # print 'in comboBox load'
        # print data
        try:
            self.clear()
            if 'ids' in data.keys():
                self.addItems([i for i in data['items']],data['ids'])
            else:
                self.addItems([i for i in data['items']])
            self.setCurrentIndex(data['current'])
            
            #self.setEnabled(data['enabled'])
        except:
            print 'Loading of comboBox encountered an error.'
            import traceback,sys
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60        
    def currentId(self):
        return self.ids[self.currentIndex()]
    def addItems(self,items,ids=None):
        
        if ids:
            for item, id in zip(items,ids):
                self.addItem(item,id)
        else:
            for i in items:
                self.addItem(i)
        # if ids:
            # self.ids = self.ids + ids
        # else:
            # self.ids = self.ids + range(self.count(), self.count() + len(items))
    def currentText(self):
        return str(QComboBox.currentText(self).toAscii())
        
    def addItem(self,item,id=None):
        QComboBox.addItem(self,item)
        if id:
            self.ids.append(id)
        else:
            self.ids.append(self.count())
            
    def addRItems(self, items):
        if items:
            if type(items) == type(''):
                self.addItems([items])
            elif type(items) == type([]):
                self.addItems(items)
        else:
            print str(items)
            print 'Items failed to add'
    def update(self, items):
        print 'Updating comboBox with the following items', items
        current = self.currentText()
        self.clear()
        self.addRItems(items)
        index = self.findText(current)
        if index != -1:
            self.setCurrentIndex(index)
    def getReportText(self, fileDir):

        r = {self.widgetName:{'includeInReports': self.includeInReports, 'text': self.currentText()}}
        #return '%s set to %s' % (self.label, self.currentText())
        return r
