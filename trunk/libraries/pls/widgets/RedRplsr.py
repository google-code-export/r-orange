"""
<name>RedRplsr</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Beginning module for the pls package to generate a model fit.</description>
<RFunctions>pls:plsr</RFunctions>
<tags>PLS</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals

class RedRplsr(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "plsr", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["plsr"])
        self.data = {}
        self.RFunctionParam_data = ''
        self.inputs = [("data", signals.RDataFrame.RDataFrame, self.processdata)]
        self.outputs = [("plsr Output", signals.RModelFit.RModelFit)]
        
        self.RFunctionParamformula_lineEdit = redRGUI.lineEdit(self.controlArea, label = "formula:", text = '')
        self.RFunctionParamscale_radioButtons = redRGUI.radioButtons(self.controlArea, label = "Scale the data:", buttons = ['TRUE', 'FALSE'], setChecked = 'FALSE', orientation = 'horizontal')
        self.RFunctionParammethod_lineEdit = redRGUI.lineEdit(self.controlArea, label = "method:", text = '')
        self.RFunctionParamncomp_lineEdit = redRGUI.lineEdit(self.controlArea, label = "ncomp:", text = '10')
        self.RFunctionParamvalidation_comboBox = redRGUI.comboBox(self.controlArea, label = "validation:", items = ["none","CV","LOO"])
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processdata(self, data):
        if not self.require_librarys(["pls"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_data=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_data=''
    def commitFunction(self):
        if str(self.RFunctionParam_data) == '': return
        if str(self.RFunctionParamformula_lineEdit.text()) == '':
            self.status.setText('No Formula')
            return
        injection = []
        if str(self.RFunctionParamformula_lineEdit.text()) != '':
            string = 'formula='+str(self.RFunctionParamformula_lineEdit.text())+''
            injection.append(string)
        ## make commit function for self.RFunctionParamscale_checkBox
        if str(self.RFunctionParamscale_radioButtons.getChecked()) == 'TRUE':
            injection.append('scale = TRUE')
        else:
            injection.append('scale = FALSE')
        if str(self.RFunctionParammethod_lineEdit.text()) != '':
            string = 'method='+str(self.RFunctionParammethod_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamncomp_lineEdit.text()) != '':
            string = 'ncomp='+str(self.RFunctionParamncomp_lineEdit.text())+''
            injection.append(string)
        string = 'validation=\''+str(self.RFunctionParamvalidation_comboBox.currentText())+'\''
        injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['plsr']+'<-plsr(data='+str(self.RFunctionParam_data)+',model = TRUE, x = TRUE, y = TRUE,'+inj+')')
        newData = signals.RModelFit.RModelFit(data = self.Rvariables["plsr"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("plsr Output", newData)
