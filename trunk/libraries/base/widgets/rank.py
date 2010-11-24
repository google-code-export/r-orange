"""
<name>Rank</name>
<tags>Data Manipulation</tags>
"""
from OWRpy import * 
import OWGUI 
import redRGUI 
from libraries.base.signalClasses.RList import RList as redRRList
from libraries.base.signalClasses.RMatrix import RMatrix as redRRMatrix

from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.listBox import listBox
class rank(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["rank"])
        self.RFunctionParam_ties_method = ''
        #self.RFunctionParam_na_last = "TRUE"
         
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'x', redRRList, self.processx)

        self.outputs.addOutput('id0', 'rank Output', redRRMatrix)
        
        
        
        #self.help.setHtml('<small>This Widget ranks elements in a vector and returns a ranked vector.</small>')
        self.RFunctionParamties_method_comboBox = comboBox(self.controlArea, label = "ties_method:", 
        items = ['average', 'first', 'random', 'max', 'min'])
        
        self.columns = listBox(self.controlArea, label = 'Dataset A:', callback = self.onSelect)
        
        self.commit = redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True, processOnChange=True)
    def processx(self, data):
        if not data:
            self.RFunctionParam_x = ''
            self.columns.clear()
            return
            
        self.RFunctionParam_x=data.getData()
        columns = self.R('names('+self.RFunctionParam_x+')',wantType='list')
        print columns
        self.columns.update(columns)

        if self.commit.processOnInput():
            self.commitFunction()
            
    def onSelect(self):
        if self.commit.processOnChange():
            self.commitFunction()

    def commitFunction(self):
        if self.columns.selectedItems():
            col = self.columns.selectedItems()[0].text()
        else:
            col = None

        if self.RFunctionParam_x == '' and not col: 
            self.status.setText('No data')
            return
        
        injection = []
        if self.RFunctionParamties_method_comboBox.currentText() != '':
            string = 'ties.method="'+str(self.RFunctionParamties_method_comboBox.currentText())+'"'
            injection.append(string)
        
        
        inj = ','.join(injection)
        self.R(self.Rvariables['rank']+'<-rank(x='+unicode(self.RFunctionParam_x)+','+inj+', na.last = TRUE)')
        newData = redRRMatrix(data = 'as.matrix('+self.Rvariables['rank']+')')
        self.rSend("id0", newData)
        
    def getReportText(self, fileDir):
        return 'Data was ranked.\n\n'

