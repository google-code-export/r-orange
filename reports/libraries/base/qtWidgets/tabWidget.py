from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class tabWidget(QTabWidget,widgetState):
    def __init__(self,widget):
        
        widgetState.__init__(self, 'tabWidget',includeInReports=True)
        QTabWidget.__init__(self,widget)
        if widget.layout():
            widget.layout().addWidget(self)
        self.tabs = {}
        
    def createTabPage(self, name, widgetToAdd = None, canScroll = False):
        #print 'start: ' + name
        if widgetToAdd == None:
            # print 'make widgetBox'
            widgetToAdd = widgetBox(self, addToLayout = 0, margin = 4)
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
    def getSettings(self):
        r= {'currentIndex': self.currentIndex()}
        return r
    def loadSettings(self,data):
        #print 'called load' + str(value)
        self.setCurrentIndex(data['currentIndex'])
        
    def getReportText(self,fileDir):
        reportData = []
        for name, tab in self.tabs.items():
            children = tab.children()
            for i in children:
                if isinstance(i, widgetState) and i.includeInReports:
                    d = i.getReportText(fileDir)
                    if type(d) is list:
                        for k in range(len(d)):
                            d[k]['container'] = name
                        reportData = reportData + d
                    elif d:
                        d['container'] = name
                        reportData.append(d)
            
        
        return reportData
