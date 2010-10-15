from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox as redRWidgetBox

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class widgetLabel(QLabel,widgetState):
    def __init__(self,widget,label = '', icon=None, wordWrap=False):
        QLabel.__init__(self,widget)
        # if icon:
            # icon = QIcon(icon)
            # box = redRWidgetBox(widget,orientation='horizontal')
            # box.layout().addWidget(icon)
            # box.layout().addWidget(self)
        # else:
        widget.layout().addWidget(self)
        if icon:
            label = "<img style='margin-left:5px' src=\"%s\" /> %s" % (icon, label)
        self.setText(label)
        self.setWordWrap(wordWrap)
    def text(self):
        return str(QLabel.text(self).toAscii())
    def getSettings(self):
        # print 'in widgetLabel getSettings'
        r = {'text':self.text()}
        # print r
        return r
    def loadSettings(self,data):
        # print 'in widgetLabel loadSettings'
        # print data
        self.setText(data['text'])
        

