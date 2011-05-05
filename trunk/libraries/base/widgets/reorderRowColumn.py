"""
<name>Reorder Rows or Columns</name>
"""
from OWRpy import * 
import redR
from libraries.base.qtWidgets.button import button as redRButton
from libraries.base.qtWidgets.shuffleBox import shuffleBox as redRShuffleBox
from libraries.base.qtWidgets.radioButtons import radioButtons as redRRadioButtons
import libraries.base.signalClasses as signals

class reorderRowColumn(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_data = ''
        self.setRvariableNames(["shuffledData"])
        self.inputs.addInput("data", "Data Table", signals.RDataFrame.RDataFrame, self.processdata)
        self.outputs.addOutput('id0', "Data Table", signals.RDataFrame.RDataFrame)
        self.RFunctionParam_rowcolselector = redRRadioButtons(self.controlArea, label = 'Table Component', buttons = ['Column', 'Row'], setChecked = 'Row', callback = self.setNewOrderList)
        self.RFunctionParam_newOrder = redRShuffleBox(self.controlArea, label = 'Revised Order (Must Commit!!)')
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processdata(self, data):
        if data:
            self.RFunctionParam_data=data.getData()
            self.setNewOrderList()
        else:
            self.RFunctionParam_data=''
    def setNewOrderList(self):
        if self.RFunctionParam_data == '': return
        if self.RFunctionParam_rowcolselector.getChecked() == 'Row':
            self.RFunctionParam_newOrder.update(self.R('rownames(%s)' % self.RFunctionParam_data, wantType = redR.LIST))
        elif self.RFunctionParam_rowcolselector.getChecked() == 'Column':
            self.RFunctionParam_newOrder.update(self.R('colnames(%s)' % self.RFunctionParam_data, wantType = redR.LIST))
    def commitFunction(self):
        if unicode(self.RFunctionParam_data) == '': 
            self.status.setText('No data to work with')
            return
        if self.RFunctionParam_rowcolselector.getChecked() == 'Row':
            self.R('%s<-%s[c("%s"),]' % (self.Rvariables['shuffledData'], self.RFunctionParam_data, '","'.join(self.RFunctionParam_newOrder.listItems.values())), wantType = redR.NOCONVERSION)
        elif self.RFunctionParam_rowcolselector.getChecked() == 'Column':
            self.R('%s<-%s[,c("%s")]' % (self.Rvariables['shuffledData'], self.RFunctionParam_data, '","'.join(self.RFunctionParam_newOrder.listItems.values())), wantType = redR.NOCONVERSION)
        
        newData = signals.RDataFrame.RDataFrame(self, data = self.Rvariables['shuffledData'])
        self.rSend('id0', newData)
        
    