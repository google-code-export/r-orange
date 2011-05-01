from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRi18n
_ = redRi18n.get_(package = 'base')
class tabWidget(QTabWidget,widgetState):
    def __init__(self,widget, position = QTabWidget.North):
        
        widgetState.__init__(self,widget, 'tabWidget',includeInReports=True)
        QTabWidget.__init__(self,self.controlArea)
        self.controlArea.layout().addWidget(self)
        
        self.tabs = {}
        self.setTabPosition(position)
    def createTabPage(self, name, widgetToAdd = None, canScroll = False, orientation = 'horizontal'):
        #print 'start: ' + name
        if widgetToAdd == None:
            # print _('make widgetBox')
            widgetToAdd = widgetBox(self, addToLayout = 0, margin = 4, orientation = orientation)
        if canScroll:
            scrollArea = QScrollArea() 
            self.addTab(scrollArea, name)
            scrollArea.setWidget(widgetToAdd)
            scrollArea.setWidgetResizable(1) 
            scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
            scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        else:
            #print 'add'
            self.addTab(widgetToAdd, name)
        self.tabs[name] = widgetToAdd
        
        return widgetToAdd
    def currentTab(self):
        return self.tabs.keys()[self.currentIndex()]
    def removeTab(self, name):
        QTabWidget.removeTab(self, self.tabs.keys().index(name))
    def getSettings(self):
        r= {'currentIndex': self.currentIndex()}
        return r
    def loadSettings(self,data):
        #print 'called load' + unicode(value)
        self.setCurrentIndex(data['currentIndex'])
        
    def getReportText(self,fileDir):
        reportData = {}
        for name, tab in self.tabs.items():
            children = tab.children()
            for i in children:
                if isinstance(i, widgetState):
                    d = i.getReportText(fileDir)
                    if type(d) is dict:
                        for k,v in d.items():
                            d[k]['container'] = name
                        reportData.update(d)
            
        
        return reportData
