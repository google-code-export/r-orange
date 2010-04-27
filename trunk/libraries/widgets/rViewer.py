"""
<name>View R Output</name>
<author>Kyle R. Covington</author>
<description>Shows the output of an R variable, equivalent to typing the variable name in the R Executor</description>
<tags>R</tags>
<icon>icons/rexecutor.png</icon>
<priority>10</priority>
"""
from OWRpy import * 
import redRGUI
class rViewer(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        
        self.RFunctionParam_data = None
        self.loadSettings()
        self.inputs = [("data", signals.RVariable, self.processdata)]
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
            self.RFunctionParam_data=data["data"]
            self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_data = ''
            self.data = None
            self.commitFunction()

    
    def commitFunction(self):
        if not self.RFunctionParam_data:
            self.RoutputWindow.setHtml('No data connected to show.')
            return
        if self.data.getClass_data() in ['data.frame', 'matrix'] and 'Show All Rows' not in self.showAll.getChecked() and 'Show All Columns' not in self.showAll.getChecked():
            dims = self.data.getDims_data()
            if dims[0] > 5 and dims[1] > 5:
                text = self.data.getFullOutput(subsetting = '[1:5, 1:5]')
            elif dims[0] > 5:
                text = self.data.getFullOutput(subsetting = '[1:5,]')
            elif dims[1] > 5:
                text = self.data.getFullOutput(subsetting = '[,1:5]')
            else:
                text = self.data.getFullOutput(subsetting = '')
        elif self.data.getClass_data() in ['data.frame', 'matrix'] and 'Show All Rows' not in self.showAll.getChecked():
            dims = self.data.getDims_data()
            if dims[0] > 5:
                text = self.data.getFullOutput(subsetting = '[1:5,]')#only need to see the first 5 rows of the data.
            else:
                text = self.data.getFullOutput(subsetting = '')
        elif self.R('class('+self.RFunctionParam_data+')') in ['data.frame', 'matrix'] and 'Show All Columns' not in self.showAll.getChecked():
            dims = self.R('dim('+self.RFunctionParam_data+')')
            if dims[1] > 5:
                text = self.data.getFullOutput(subsetting = '[,1:5]')#only need to see the first 5 cols of the data.
            else:
                text = self.data.getFullOutput(subsetting = '')
        else:
            text = self.data.getFullOutput(subsetting = '')
        self.RoutputWindow.clear()
        
        self.RoutputWindow.setHtml('<pre>'+text+'</pre>')
