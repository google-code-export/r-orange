from redRGUI import widgetState
from widgetBox import widgetBox
from widgetLabel import widgetLabel

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class textEdit(QTextEdit,widgetState):
    def __init__(self,widget,html='',label=None,orientation='vertical'):
        QTextEdit.__init__(self,widget)
        self.label = label
        if label:
            self.hb = widgetBox(widget,orientation=orientation)
            widgetLabel(self.hb, label)
            self.hb.layout().addWidget(self)
        else:
            widget.layout().addWidget(self)
        self.insertHtml(html)

    def hide(self):
        if self.hb:
            self.hb.hide()
        else:
            QTextEdit.hide(self)
    def sizeHint(self):
        return QSize(10,10)
    def setCursorToEnd(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
    def getSettings(self):
        # print 'in textEdit getSettings'
        r = {'text': self.toHtml()}
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
    def hide(self):
        if self.label:
            self.hb.hide()
        else:
            QTextEdit.hide(self)
    def show(self):
        if self.label:
            self.hb.show()
        else:
            QTextEdit.show(self)

        
