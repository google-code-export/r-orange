"""Text Edit

This is a text area into which data can be placed or entered.  Developers will generally wish to simply fill these boxes with data from a function that would be cumbersome to place into a label (like when you want to scroll).

Use the functions insertHtml() or insertPlainText() to insert strings into the textEdit.  Use the function clear() to clear the textEdit and the function setCursorToEnd() to set the cursor to the end of the viewable text.

"""


from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.button import button

import RSession

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRi18n
_ = redRi18n.get_(package = 'base')
class textEdit(QTextEdit,widgetState):
    def __init__(self,widget,html='',label=None, displayLabel=True, orientation='vertical', alignment=None, editable=True, printable=False,clearable=False,**kwargs):
        kwargs.setdefault('includeInReports', True)
        kwargs.setdefault('sizePolicy', QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        widgetState.__init__(self,widget, label,**kwargs)

        QTextEdit.__init__(self,self.controlArea)
        self.label = label
        if displayLabel:
            self.hb = groupBox(self.controlArea,label=label,orientation=orientation)
        else:
            self.hb = widgetBox(self.controlArea,orientation=orientation)

        self.hb.layout().addWidget(self)
        if alignment:
            self.controlArea.layout().setAlignment(self.hb,alignment)
        if printable:
            button(self.hb, _("Print"), self.printMe)
        if clearable:
            button(self.hb, _("Clear"), callback = self.clear)
        if not editable:
            self.setReadOnly(True)
        self.setFontFamily('Courier')
        self.insertHtml(html)
        
        
    def sizeHint(self):
        return QSize(1,1)
    def setCursorToEnd(self):
        """Places the cursor to the end of the document.  Required if you want to add text and there is the possibility that the user moved the cursor somewhere."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
    def getSettings(self):
        # print _('in textEdit getSettings')
        r = {'text': unicode(self.toHtml())}
        # print r['text']
        
        #print r
        
        return r
    def loadSettings(self,data):
        print 'Loading text edit data %s' % unicode(data)
        self.clear()
        
        self.insertHtml(data['text'])
        # self.setEnabled(data['enabled'])
    def toPlainText(self):
        return unicode(QTextEdit.toPlainText(self))
    def getReportText(self,fileDir):
        limit = min(100000,len(self.toPlainText()))
        return {self.widgetName:{'includeInReports': self.includeInReports, 'type': 'litralBlock',
        'text': self.toPlainText()[0:limit], 'numChrLimit': limit}}
        
    def printMe(self):
        """Prints the current text in the textEdit to the printer."""
        printer = QPrinter()
        printDialog = QPrintDialog(printer)
        if printDialog.exec_() == QDialog.Rejected: 
            print _('Printing Rejected')
            return
        self.print_(printer)
        
    def captureOutput(self, s):
        tmp = RSession.Rcommand('paste(capture.output(%s), collapse ="\n")' % s)
        self.insertHtml('<br><pre>'+tmp+'</pre><br><br>')