from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.button import button

import redRReports
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class textEdit(QTextEdit,widgetState):
    def __init__(self,widget,html='',label=None, displayLabel=True,includeInReports=True, 
    orientation='vertical', alignment=None, editable=True, printable=False,**args):

        widgetState.__init__(self, label, **args)

        QTextEdit.__init__(self,widget)
        self.label = label
        if displayLabel:
            self.hb = groupBox(widget,label=label,orientation=orientation)
        else:
            self.hb = widgetBox(widget,orientation=orientation)

        self.hb.layout().addWidget(self)
        if alignment:
            widget.layout().setAlignment(self.hb,alignment)
        if printable:
            button(self.hb, "Print", self.printMe)
            
        if not editable:
            self.setReadOnly(True)
        self.insertHtml(html)
        

    def hide(self):
        self.hb.hide()
    def show(self):
        self.hb.show()
            
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
    def toPlainText(self):
        return str(QTextEdit.toPlainText(self).toAscii())
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
        
