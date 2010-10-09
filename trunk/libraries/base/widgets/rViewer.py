"""
<name>View R Output</name>
<tags>R</tags>
"""
from OWRpy import * 
import redRGUI
from libraries.base.signalClasses.RVariable import RVariable as redRRVariable
from libraries.base.qtWidgets.textEdit import textEdit
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.checkBox import checkBox as redRCheckBox

class rViewer(OWRpy): 
    globalSettingsList = ['commitOnInput','showAll']

    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        
        self.RFunctionParam_data = None
        self.data = None
        
        self.inputs.addInput('id0', 'R Variable Data', redRRVariable, self.processdata)

        self.RoutputWindow = textEdit(self.controlArea,editable=False)
        
        self.showAll = redRCheckBox(self.bottomAreaLeft, 
        buttons = ['String Representation', 'Show All'],orientation="horizontal", 
        setChecked = 'String Representation')
        
        self.commitOnInput = redRCheckBox(self.bottomAreaRight, buttons = ['Commit on Input'],
        toolTips = ['Whenever this widget gets data it should try to commit'])

        redRCommitButton(self.bottomAreaRight, label="Commit", callback = self.commitFunction)
        
        #button(self.bottomAreaLeft, label="Print", callback = self.printViewer)
        
    
    # def printViewer(self):
        # thisPrinter = QPrinter()
        # printer = QPrintDialog(thisPrinter)
        # if printer.exec_() == QDialog.Rejected:
            # print 'Printing Rejected'
            # return
        # self.RoutputWindow.print_(thisPrinter)
    def processdata(self, data):
        #print '######################in processdata', data
        if data:
            self.RFunctionParam_data=data.getData()
            self.data = data
            if 'Commit on Input' in self.commitOnInput.getChecked():
                self.commitFunction()
        else:
            self.RFunctionParam_data = ''
            self.data = None
            self.commitFunction()

    
    def commitFunction(self):
        if not self.data: return
        self.RoutputWindow.clear()
        text = ''
        if 'String Representation' in self.showAll.getChecked():
            text += self.R('paste(capture.output(str('+str(self.data.getData())+')), collapse = \'\\n\')')
            text += '\n'
        text += '\n'
        if 'Show All' in self.showAll.getChecked():
            text += self.R('paste(capture.output('+str(self.data.getData())+'), collapse = \'\\n\')')
        #text = text.replace(' ', "\t")
        self.RoutputWindow.setPlainText(str(text))
    def getReportText(self, fileDir):
        text = 'The following was displayed in the rViewer widget:\n\n'
        text += str(self.RoutputWindow.toPlainText())+'\n\n'
        return text
