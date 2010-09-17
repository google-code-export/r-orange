from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox as redRWidgetBox

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class statusLabel(QLabel,widgetState):
    def __init__(self,widget,label = '', wordWrap=True):
        QLabel.__init__(self,widget)
        # if icon:
            # icon = QIcon(icon)
            # box = redRWidgetBox(widget,orientation='horizontal')
            # box.layout().addWidget(icon)
            # box.layout().addWidget(self)
        # else:
        
        widget.layout().addWidget(self)
        self.status = 0
        self.setText(label)
        self.setWordWrap(wordWrap)
        
    def getSettings(self):
        # print 'in widgetLabel getSettings'
        r = {'text':self.text(),'status':self.status}
        print r
        return r
    def loadSettings(self,data):
        # print 'in widgetLabel loadSettings'
        print data
        self.setText(data['text'])
        self.setStatus(data['status'])
    def getReportText(self, fileDir):
        return ''
        
    def setText(self, string):
        # self.setStyleSheet("QLabel { background-color: #ffff00 }")
        QLabel.setText(self, string)
        qApp.processEvents()    
    def setStatus(self, statusInt):
        self.status = statusInt
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
        elif statusInt == 4: ## Data Processing    
            self.setStyleSheet("QLabel { background-color: #ffff00 }")
            QLabel.setText(self, 'Data Processing...')
        elif statusInt == 5: ## Data Processing Complete
            self.setStyleSheet("QLabel { background-color: #ffff00 }")
            QLabel.setText(self, 'Data Processing Complete')
        

        qApp.processEvents()    