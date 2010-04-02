from redRGUI import widgetState
from widgetBox import widgetBox
from widgetLabel import widgetLabel
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtWebKit

class webViewBox(QtWebKit.QWebView,widgetState):
    def __init__(self,widget,label=None,url=None,orientation='vertical'):
        QtWebKit.QWebView.__init__(self,widget)
        
        if label:
            hb = widgetBox(widget,orientation=orientation)
            widgetLabel(hb, label)
            hb.layout().addWidget(self)
        else:
            widget.layout().addWidget(self)
        
        self.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.connect(self, SIGNAL('linkClicked(QUrl)'), self.followLink)
        if url:
            try:
                self.load(QUrl(url))
            except: pass 
    
    def followLink(self, url):
        self.load(QUrl(url))

    def sizeHint(self):
        return QSize(10,10)

        
