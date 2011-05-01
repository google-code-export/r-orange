"""
<name>View Python Dict</name>
<tags>R</tags>
"""
from OWRpy import * 
import redRGUI
from libraries.base.signalClasses.RVariable import RVariable as redRRVariable
from libraries.base.qtWidgets.textEdit import textEdit
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.checkBox import checkBox as redRCheckBox
from libraries.base.signalClasses.StructuredDict import StructuredDict
import redRi18n
_ = redRi18n.get_(package = 'base')
class pyDict(OWRpy): 
    globalSettingsList = ['commit','showAll']

    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        
        self.RFunctionParam_data = None
        self.data = None
        
        self.inputs.addInput('id0', _('R Variable Data'), StructuredDict, self.processdata)

        self.RoutputWindow = textEdit(self.controlArea,label=_('Output'), editable=False)
        

        self.commit = redRCommitButton(self.bottomAreaRight, label=_("Commit"), callback = self.commitFunction, 
        processOnInput=True)
        
        #button(self.bottomAreaLeft, label=_("Print"), callback = self.printViewer)
        
    
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
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_data = ''
            self.data = None
            self.commitFunction()

    
    def commitFunction(self):
        if not self.data: return
        self.RoutputWindow.clear()
        ## the keys:
        keys = self.RFunctionParam_data.keys()
        self.RoutputWindow.insertPlainText('\t'.join(keys) + '\n')
        for i in range(len(self.RFunctionParam_data[keys[0]])):
            self.RoutputWindow.insertPlainText('\t'.join([str(self.RFunctionParam_data[k][i]) for k in keys]) + '\n')
        
        
