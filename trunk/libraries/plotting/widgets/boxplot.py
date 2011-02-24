"""
<name>Box Plot</name>
<tags>Plotting</tags>
<icon>boxplot.png</icon>
"""
from OWRpy import * 
import OWGUI, redRGUI
from libraries.base.signalClasses.RList import RList as redRRList
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.commitButton import commitButton as redRCommitButton
class boxplot(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'x', redRRList, self.processx)

        
        self.commit = redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,processOnInput=True)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            if self.commit.processOnInput():
                self.commitFunction()
    def commitFunction(self):
        if self.x == '': 
            self.status.setText('Do data. Can not plot')
            return
        try:
            self.R('boxplot(x=as.list('+unicode(self.RFunctionParam_x)+'), notch = TRUE)')
        except Exception as inst:
            QMessageBox.information(self,'R Error', "Plotting failed.  Try to format the data in a way that is acceptable for this widget.\nSee the documentation for help.\n%s" % inst, 
            QMessageBox.Ok + QMessageBox.Default)
            return