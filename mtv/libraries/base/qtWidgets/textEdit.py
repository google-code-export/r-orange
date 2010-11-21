from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.button import button

import redRReports
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class textEdit(QTextEdit,widgetState):
    def __init__(self,widget,html='',label=None, orientation='vertical', editable=True,printable=True):
        QTextEdit.__init__(self,widget)
        self.label = label
        self.hb = widgetBox(widget,orientation=orientation)
        if label:
            widgetLabel(self.hb, label)
        self.hb.layout().addWidget(self)
        wb = widgetBox(self.hb, orientation = 'horizontal')
        if printable:
            button(wb, "Print", self.printMe)
            
        if not editable:
            self.setReadOnly(True)
        self.insertHtml(html)
        button(wb, "Clear", callback = self.clear)
        
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
    def toPlainText(self):
        return unicode(QTextEdit.toPlainText(self).toAscii())
    def show(self):
        if self.label:
            self.hb.show()
        else:
            QTextEdit.show(self)
    def getReportText(self,fileDir):
        if not self.label:
            label = "TextBox with No Label"
        else:
            label = self.label
        return {'label': label, 'text': redRReports.createLitralBlock(self.toPlainText())}
        
    def printMe(self):
        printer = QPrinter()
        printDialog = QPrintDialog(printer)
        if printDialog.exec_() == QDialog.Rejected: 
            print 'Printing Rejected'
            return
        self.print_(printer)
        
