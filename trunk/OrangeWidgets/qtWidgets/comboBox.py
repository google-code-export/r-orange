from redRGUI import widgetState
from widgetBox import widgetBox
from widgetLabel import widgetLabel


from PyQt4.QtCore import *
from PyQt4.QtGui import *

class comboBox(QComboBox,widgetState):
    def __init__(self,widget,label=None, items=None, orientation='horizontal',callback = None, callback2 = None, **args):
        
        QComboBox.__init__(self,widget)
        if label:
            hb = widgetBox(widget,orientation=orientation)
            widgetLabel(hb, label)
            hb.layout().addWidget(self)
        else:
            widget.layout().addWidget(self)
        
        if items:
            self.addItems([unicode(i) for i in items])
        # print callback
        if callback:
            # print callback
            QObject.connect(self, SIGNAL('activated(int)'), callback)
            
        if callback2: # more overload for other functions
            QObject.connect(self, SIGNAL('activated(int)'), callback2)

    def getSettings(self):
        items = []
        # print 'in comboBox get'

        for i in range(0,self.count()):
            items.append(self.itemText(i))
        
        r = {'items':items,'current':self.currentIndex()}
        r.update(self.getState())
        return r
        
    def loadSettings(self,data):
        # print 'in comboBox load'
        # print data
        try:
            self.clear()
            self.addItems([unicode(i) for i in data['items']])
            self.setCurrentIndex(data['current'])
            self.setState(data)
            #self.setEnabled(data['enabled'])
        except:
            print 'Loading of comboBox encountered an error.'
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
        current = self.currentText()
        self.clear()
        self.addRItems(items)
        index = self.findText(current)
        if index != -1:
            self.setCurrentIndex(index)
    
