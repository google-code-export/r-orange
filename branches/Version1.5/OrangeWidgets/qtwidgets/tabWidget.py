from redRGUI import widgetState
from widgetBox import widgetBox
from widgetBoxNoLabel import widgetBoxNoLabel
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class tabWidget(QTabWidget,widgetState):
    def __init__(self,widget):
        QTabWidget.__init__(self,widget)
        if widget.layout():
            widget.layout().addWidget(self)
    
    def createTabPage(self, name, widgetToAdd = None, canScroll = False):
        print 'start: ' + name
        if widgetToAdd == None:
            print 'make widgetBox'
            widgetToAdd = widgetBoxNoLabel(self, addToLayout = 0, margin = 4)
        if canScroll:
            scrollArea = QScrollArea() 
            self.addTab(scrollArea, name)
            scrollArea.setWidget(widgetToAdd)
            scrollArea.setWidgetResizable(1) 
            scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
            scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        else:
            print 'add'
            self.addTab(widgetToAdd, name)
        return widgetToAdd 
    def getSettings(self):
        r= {'currentIndex': self.currentIndex()}
        r.update(self.getState())
        return r
    def loadSettings(self,data):
        #print 'called load' + str(value)
        self.setCurrentIndex(data['currentIndex'])
        self.setState(data)

