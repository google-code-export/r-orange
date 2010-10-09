"""
<name>Transpose</name>
<tags>Data Manipulation</tags>
"""
from OWRpy import * 

from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.signalClasses.RMatrix import RMatrix as redRRMatrix

from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.checkBox import checkBox as redRCheckBox

class t(OWRpy): 
    globalSettingsList = ['commitOnInput']

    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["t"])
        self.RFunctionParam_x = ''
        self.data={}
        
        
        self.inputs.addInput('id0', 'Input Data Table or Matrix', [redRRDataFrame, redRRMatrix], self.processx)

        self.outputs.addOutput('id0', 'Transposed Data Table', redRRDataFrame)

        
        self.commitOnInput = redRCheckBox(self.bottomAreaRight, buttons = ['Commit on Selection'],
        toolTips = ['Whenever this selection changes, send data forward.'], setChecked='Commit on Selection')

        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            self.data = data
            if 'Commit on Selection' in self.commitOnInput.getChecked():
                self.commitFunction()
    def commitFunction(self):
        if self.x == '': return
        
        self.R(self.Rvariables['t']+'<-as.data.frame(t(x='+str(self.RFunctionParam_x)+'))')
        
        newData = redRRDataFrame(data = self.Rvariables['t'])
        newData.dictAttrs = self.data.dictAttrs.copy()
        self.rSend("id0", newData)
    def getReportText(self, fileDir):
        text = 'Data transposed and sent to downstream widgets.\n\n'
        return text