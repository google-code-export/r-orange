"""
<name>Rank</name>
<tags>Data Manipulation</tags>
"""
from OWRpy import * 
import redRGUI, signals
import OWGUI 
import redRGUI 

import redRi18n
_ = redRi18n.get_(package = 'base')
class rank(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["rank"])
        self.RFunctionParam_ties_method = ''
        #self.RFunctionParam_na_last = "TRUE"
         
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', _('x'), signals.base.RList, self.processx)

        self.outputs.addOutput('id0', _('rank Output'), signals.base.RMatrix)
        
        
        
        #self.help.setHtml('<small>This Widget ranks elements in a vector and returns a ranked vector.</small>')
        self.RFunctionParamties_method_comboBox = redRGUI.base.comboBox(self.controlArea, label = _("How to handle ties:"), 
        items = [_('average'), _('first'), _('random'), _('max'), _('min')])
        
        self.columns = redRGUI.base.listBox(self.controlArea, label = _('Dataset:'), callback = self.onSelect)
        
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, _("Commit"), callback = self.commitFunction,
        processOnInput=True, processOnChange=True)
    def processx(self, data):
        if not data:
            self.RFunctionParam_x = ''
            self.columns.clear()
            return
            
        self.RFunctionParam_x=data.getData()
        columns = self.R('names('+self.RFunctionParam_x+')',wantType='list')
        #print columns
        self.columns.update(columns)

        if self.commit.processOnInput():
            self.commitFunction()
            
    def onSelect(self):
        if self.commit.processOnChange():
            self.commitFunction()

    def commitFunction(self):
        selectCols = self.columns.selectedIds()
        if self.RFunctionParam_x == '' and not len(selectCols) !=1: 
            self.status.setText(_('No data'))
            return
        
        injection = []
        if self.RFunctionParamties_method_comboBox.currentText() != '':
            string = 'ties.method="'+str(self.RFunctionParamties_method_comboBox.currentText())+'"'
            injection.append(string)
        
        
        inj = ','.join(injection)
        self.R(self.Rvariables['rank']+'<-rank(x=%s$%s,%s, na.last = TRUE)' % (self.RFunctionParam_x,selectCols[0],inj), 
        wantType = 'NoConversion')
        newData = signals.base.RMatrix(self, data = 'as.matrix('+self.Rvariables['rank']+')')
        self.rSend("id0", newData)

