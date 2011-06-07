"""Web View Box

The web view box allows the user to see web pages displayed in a box.  This is similar to the web views that many users will be fammiliar with.  If a url is supplied as a string that url will be loaded at construction time.  If followHere is set to True, hyperlinks will be loaded in this web view, otherwise hyperlinks will be loaded in a new tab of the default web browser on the system.

"""


from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4 import QtWebKit
import redRi18n
QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)
_ = redRi18n.get_(package = 'base')
class webViewBox(QtWebKit.QWebView,widgetState):
    def __init__(self,widget,label=None, displayLabel=True, url=None,orientation='vertical', followHere = False, **kwargs):
        kwargs.setdefault('includeInReports', True)
        kwargs.setdefault('sizePolicy', QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        widgetState.__init__(self,widget,label, **kwargs)
        QtWebKit.QWebView.__init__(self,self.controlArea)
        # factory = QtWebKit.QWebPluginFactory()
        # self.page().setPluginFactory(factory)
        self.controlArea.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        if displayLabel:
            hb = widgetBox(self.controlArea,orientation=orientation)
            widgetLabel(hb, label)
            hb.layout().addWidget(self)
        else:
            self.controlArea.layout().addWidget(self)
    
        self.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        if not followHere:
            self.connect(self, SIGNAL('linkClicked(QUrl)'), self.followLink)
        if url:
            try:
                self.load(QUrl(url))
            except: pass 
    
    def followLink(self, url):
        import webbrowser
        #print unicode(url)
        #print url.toString()
        webbrowser.open_new_tab(url.toString())


