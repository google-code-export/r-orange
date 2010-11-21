from redRGUI import widgetState

from libraries.base.qtWidgets.webViewBox import webViewBox
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class SearchDialog(QDialog,widgetState):
    def __init__(self, caption = 'Search Dialog', url = '', icon = None, orientation = 'horizontal'):
        widgetState.__init__(self,None, 'SearchDialog',includeInReports=False)
        QDialog.__init__(self)
        
        self.setWindowTitle(caption)
        try:
            if isinstance(orientation, QLayout):
                self.setLayout(orientation)
            elif orientation == 'horizontal' or not orientation:
                self.setLayout(QHBoxLayout())
            else:
                self.setLayout(QVBoxLayout())
        except:
            self.setLayout(QVBoxLayout())
        self.thisLayout = self.layout()
        self.webView = webViewBox(self,label='Search Dialog', displayLabel=False)
        self.setMinimumSize(600, 400)
        if url and url != '':
            self.webView.load(QUrl(url))
        
        if icon:
            self.setWindowIcon(icon)
            
    def updateUrl(self, url):
        self.webView.load(QUrl(url))
        
        