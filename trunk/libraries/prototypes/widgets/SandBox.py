"""
<name>SandBox</name>
<description></description>
<tags>Prototypes</tags>
<priority>9010</priority>
"""

from OWRpy import *
import OWGUI,glob,imp, time
import redRGUI
import signals
from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.webViewBox import webViewBox
from PyQt4.QtWebKit import *

import redRi18n
_ = redRi18n.get_(package = 'base')

QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)

class SandBox(OWRpy):
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.lineEditText = ''
        #self.require_librarys(['BARD'])
        ### GUI ###
        
        #self.webBox = webViewBox(self.controlArea, label = 'Web Box')
        #self.webBox.setHtml('This is a simple test. <object type="application/x-pdf" data="file:///home/covingto/Documents/DNA%20Gel.pdf" width = "500" height = "400"></object>')
        a = redRGUI.base.widgetLabel(self.controlArea ,_(
"""Thanks for setting up Red-R.<br>
<ul>
<li>Whats new in Red-R 1.85: <a href="http://red-r.org/downloads/changelog">Change Log</a></li>
<li>Take a tour with the Red-R 1.85 <a href="http://red-r.org/downloads/changelog">screencast</a></li>
<li><a href="http://red-r.org/documentation">Red-R Documentation</a></li>
<li>Additional functionality: <a href="http://red-r.org/redrpackages">Red-R Packages</a></li>
</ul>
"""))
        a.setOpenExternalLinks(True)
        a.setWordWrap(True)
        a.setFixedWidth(350)