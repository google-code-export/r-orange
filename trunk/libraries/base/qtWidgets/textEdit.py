from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.button import button

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class textEdit(QTextEdit,widgetState):
    def __init__(self,widget,html='',label=None, orientation='vertical', editable=True):
        QTextEdit.__init__(self,widget)
        self.label = label
        if label:
            self.hb = widgetBox(widget,orientation=orientation)
            widgetLabel(self.hb, label)
            self.hb.layout().addWidget(self)
            button(self.hb, "Print", self.printMe)
        else:
            widget.layout().addWidget(self)
            button(widget, "Print", self.printMe)
            
        if not editable:
            self.setReadOnly(True)
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
    def getReportText(self, fileDir):
        return self.toPlainText()+'\n\n'
        
    def printMe(self):
        printer = QPrinter()
        printDialog = QPrintDialog(printer)
        if printDialog.exec_() == QDialog.Rejected: 
            print 'Printing Rejected'
            return
        self.print_(printer)
        
