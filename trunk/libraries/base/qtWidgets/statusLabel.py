from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox as redRWidgetBox

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class statusLabel(QLabel,widgetState):
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
    def getSettings(self):
        # print 'in widgetLabel getSettings'
        r = {'text':self.text()}
        # print r
        return r
    def loadSettings(self,data):
        # print 'in widgetLabel loadSettings'
        # print data
        self.setText(data['text'])
    def getReportText(self, fileDir):
        return ''
        
    def setText(self, string):
        self.setStyleSheet("QLabel { background-color: #ffff00 }")
        QLabel.setText(self, string)
        
    def setStatus(self, statusInt):
        if statusInt == 0: ## No valid data
            self.setStyleSheet("QLabel { background-color: #ff0000 }")
            QLabel.setText(self, 'No Data To Process')
        elif statusInt == 1: ## New data not processed
            self.setStyleSheet("QLabel { background-color: #0000ff }")
            QLabel.setText(self, 'New Data Received, Not Processed')
        elif statusInt == 2: ## data sent
            self.setStyleSheet("QLabel { background-color: #00ff00 }")
            QLabel.setText(self, 'Data Processed And Sent')
        elif statusInt == 3: ## Error
            self.setStyleSheet("QLabel { background-color: #ff0000 }")
            QLabel.setText(self, 'Error')

