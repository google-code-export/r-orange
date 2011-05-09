"""
<name>Linear Model</name>
<tags>Parametric</tags>
<icon>stats.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI

class lm(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, wantGUIDialog = 1, **kwargs)
        self.setRvariableNames(["lm"])
        self.RFunctionParam_formula = ""
        self.RFunctionParam_data = ''
        self.modelFormula = ''
        self.processingComplete = 0
        
        self.inputs.addInput('id0', 'data', signals.base.RDataFrame, self.processdata)

        self.outputs.addOutput('id0', 'lm Output', signals.stats.RLMFit)
        self.outputs.addOutput('id1', 'lm plot attribute', signals.plotting.RPlotAttribute)

        
        #GUI
        
        box = redRGUI.base.widgetBox(self.GUIDialog, orientation = 'horizontal')
        paramBox = redRGUI.base.groupBox(self.GUIDialog, 'Parameters')
        formulaBox = redRGUI.base.widgetBox(self.controlArea)
        self.RFunctionParam_subset = redRGUI.base.lineEdit(paramBox, 'NULL', label = "subset:")
        self.RFunctionParam_qr = redRGUI.base.lineEdit(paramBox, 'TRUE', label = "qr:")

        self.RFunctionParam_singular_ok = redRGUI.base.lineEdit(paramBox, 'TRUE', label = "singular_ok:")
        self.RFunctionParam_y = redRGUI.base.lineEdit(paramBox, 'FALSE', label = "y:")
        self.RFunctionParam_weights = redRGUI.base.lineEdit(paramBox, "", label = "weights:")
        self.RFunctionParam_offset = redRGUI.base.lineEdit(paramBox, "", label = "offset:")
        self.RFunctionParam_contrasts = redRGUI.base.lineEdit(paramBox, "NULL", label = "contrasts:")
        self.RFunctionParam_x = redRGUI.base.lineEdit(paramBox, "FALSE", label = "x:")
        self.RFunctionParam_model = redRGUI.base.lineEdit(paramBox, "TRUE", label = "model:")
        self.RFunctionParam_method = redRGUI.base.lineEdit(paramBox, "qr", label = "method:")
        
        #start formula entry section

        buttonsBox = redRGUI.base.widgetBox(formulaBox, "Commands")
        self.formulEntry = redRGUI.base.RFormulaEntry(buttonsBox,label='Formula',displayLabel=False)
        
        
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
        #self.processButton.setEnabled(False)
        self.status.setText('Data Not Connected Yet')
    def processdata(self, data):
        if data:
            self.RFunctionParam_data=data.getData()
            names = self.R('colnames('+self.RFunctionParam_data+')')
            self.formulEntry.update(names)
            self.status.setText('Data Connected')
            if self.commit.processOnInput():
                self.commitFunction()

        else:
            self.formulEntry.clear()
            self.RFunctionParam_data = ''
            self.status.setText('Data Connection Failed. Please Reconnect')
    def commitFunction(self):
        if self.RFunctionParam_data == '': 
            self.status.setText('No data')
            return
        if self.formulEntry.Formula()[0] == '' or self.formulEntry.Formula()[1] == '':
            self.status.setText('Please select valid formula parameters')
            return
        self.RFunctionParam_formula = self.formulEntry.Formula()[0] + ' ~ ' + self.formulEntry.Formula()[1]

        
        self.R(self.Rvariables['lm']+'<-lm(data='+unicode(self.RFunctionParam_data)+',subset='+unicode(self.RFunctionParam_subset.text())+',qr='+unicode(self.RFunctionParam_qr.text())+',formula='+unicode(self.RFunctionParam_formula)+',singular_ok='+unicode(self.RFunctionParam_singular_ok.text())+',y='+unicode(self.RFunctionParam_y.text())+',weights='+unicode(self.RFunctionParam_weights.text())+',offset='+unicode(self.RFunctionParam_offset.text())+',contrasts='+unicode(self.RFunctionParam_contrasts.text())+',x='+unicode(self.RFunctionParam_x.text())+',model='+unicode(self.RFunctionParam_model.text())+',method="'+unicode(self.RFunctionParam_method.text())+'")', wantType = 'NoConversion')
        newData = signals.stats.RLMFit(self, data = self.Rvariables['lm'])
        self.rSend("id0", newData)
        
        newPlotAtt = signals.plotting.RPlotAttribute(self, data = 'abline('+self.Rvariables['lm']+')')
        self.rSend("id1", newPlotAtt)
        
