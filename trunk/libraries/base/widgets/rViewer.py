"""
<name>View R Output</name>
<author>Kyle R. Covington</author>
<description>Shows the output of an R variable, equivalent to typing the variable name in the R Executor</description>
<tags>R</tags>
<icon>rexecutor.png</icon>
<priority>10</priority>
"""
from OWRpy import * 
import redRGUI
import libraries.base.signalClasses.RVariable as rvar
class rViewer(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "RViewer", wantMainArea = 0, resizingEnabled = 1)
        
        self.RFunctionParam_data = None
        
        self.inputs = [("data", rvar.RVariable, self.processdata)]
        self.showAll = redRGUI.checkBox(self.bottomAreaRight, 
        buttons = ['Show All Rows', 'Show All Columns'],orientation="horizontal")
        redRGUI.button(self.bottomAreaRight, label="Commit", callback = self.commitFunction)
        redRGUI.button(self.bottomAreaLeft, label="Print", callback = self.printViewer)
        self.RoutputWindow = redRGUI.textEdit(self.controlArea)
    
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
        try:
            text = self.data.showSummary()
        except Exception, msg:
            print str(msg), 'Show Summary must not exist in this signal type'
            text = self.R('paste(capture.output(str('+str(self.data.getData())+')), collapse = \'\\n\')')
        self.RoutputWindow.setHtml('<pre>'+str(text)+'</pre>')
