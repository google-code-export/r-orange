from redRGUI import widgetState
from widgetBox import widgetBox
from widgetLabel import widgetLabel

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class textEdit(QTextEdit,widgetState):
    def __init__(self,widget,html='',label=None,orientation='vertical'):
        QTextEdit.__init__(self,widget)
        
        if label:
            hb = widgetBox(widget,orientation=orientation)
            widgetLabel(hb, label)
            hb.layout().addWidget(self)
        else:
            widget.layout().addWidget(self)
        self.insertHtml(html)

    def sizeHint(self):
        return QSize(10,10)
    def setCursorToEnd(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
    def getSettings(self):
        # print 'in textEdit getSettings'
        r = {'text': self.toHtml()}
        r.update(self.getState())
        # print r['text']
        return r
    def loadSettings(self,data):
        # print 'in textEdit loadSettings'
        #print data
        #print '##################################\n<br>'
        # print data['text']
        self.clear()
        self.insertHtml(data['text'])
        # self.setEnabled(data['enabled'])
        self.setState(data)

        
