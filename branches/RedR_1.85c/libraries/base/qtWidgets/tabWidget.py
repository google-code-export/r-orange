"""Tab Widget

Place a widget area that is organized by tabs.  This widget can be quite useful if the developer plans to place several pages of options or other groupings into the widget.

"""


from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRi18n
_ = redRi18n.get_(package = 'base')
class tabWidget(QTabWidget,widgetState):
    def __init__(self,widget, position = QTabWidget.North, **kwargs):
        kwargs.setdefault('includeInReports', True)
        kwargs.setdefault('sizePolicy', QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        widgetState.__init__(self,widget, 'tabWidget',**kwargs)
        QTabWidget.__init__(self,self.controlArea)
        self.controlArea.layout().addWidget(self)
        
        self.tabs = {}
        self.setTabPosition(position)
    def createTabPage(self, name, widgetToAdd = None, canScroll = False, orientation = 'horizontal'):
        """Places a new tab into the tabWidget with the name (name).  Developers can make a widget and add that to the tab directly.  Otherwise, a widgetBox is generated with the orientation indicated in orientation.  If canScroll is set to True then the tab area will allow the user to scroll to areas that aren't visible.
        
        This function returns either the widget submitted in widgetToAdd or the widgetBox generate (likely the more useful aspect).
        """
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
        """Returns the name of the currently visible tab."""
        return self.tabs.keys()[self.currentIndex()]
    def removeTab(self, name):
        """Removes a tab from the widget."""
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
