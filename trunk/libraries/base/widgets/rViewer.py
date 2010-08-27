"""
<name>View R Output</name>
<author>Kyle R. Covington</author>
<description>Shows the output of an R variable, equivalent to typing the variable name in the R Executor.</description>
<tags>R</tags>
<icon>rexecutor.png</icon>
<priority>10</priority>
"""
from OWRpy import * 
import redRGUI
from libraries.base.signalClasses.RVariable import RVariable as redRRVariable
from libraries.base.qtWidgets.textEdit import textEdit
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.checkBox import checkBox
class rViewer(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        
        self.RFunctionParam_data = None
        
        self.inputs.addInput('id0', 'R Variable Data', redRRVariable, self.processdata)

        self.showAll = checkBox(self.bottomAreaRight, 
        buttons = ['String', 'Show All'],orientation="horizontal", setChecked = 'String')
        button(self.bottomAreaRight, label="Commit", callback = self.commitFunction)
        button(self.bottomAreaLeft, label="Print", callback = self.printViewer)
        self.RoutputWindow = textEdit(self.controlArea)
    
    def printViewer(self):
        thisPrinter = QPrinter()
        printer = QPrintDialog(thisPrinter)
        if printer.exec_() == QDialog.Rejected:
            print 'Printing Rejected'
            return
        self.RoutputWindow.print_(thisPrinter)
    def processdata(self, data):
        if data:
            self.RFunctionParam_data=data.getData()
            self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_data = ''
            self.data = None
            self.commitFunction()

    
    def commitFunction(self):
        if not self.data: return
        self.RoutputWindow.clear()
        text = ''
        if 'String' in self.showAll.getChecked():
            text += self.R('paste(capture.output(str('+str(self.data.getData())+')), collapse = \'\\n\')')
            text += '\n'
        text += '\n'
        if 'Show All' in self.showAll.getChecked():
            text += self.R('paste(capture.output('+str(self.data.getData())+'), collapse = \'\\n\')')
        self.RoutputWindow.setHtml('<pre>'+str(text)+'</pre>')
    def getReportText(self, fileDir):
        text = 'The following was displayed in the rViewer widget:\n\n'
        text += str(self.RoutputWindow.toPlainText())+'\n\n'
        return text
