"""
<name>pamr.cv</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
import redRGUI 
class pamr_cv(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Pamr CV", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["pamr.cv"])
        self.RFunctionParam_folds = "NULL"
        self.RFunctionParam_nfold = "NULL"
        self.loadSettings() 
        self.RFunctionParam_data = ''
        self.RFunctionParam_fit = ''
        self.inputs = [("data", signals.pamr.RPAMRData, self.processdata),("fit", signals.pamr.RPAMRFit, self.processfit)]
        self.outputs = [("pamr.cv Output", signals.pamr.RPAMRCVFit)]
        
        self.help.setHtml('<small>Cross validates a PAMR fit.</small>')
        box = redRGUI.tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.RFunctionParamfolds_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "folds:")
        self.RFunctionParamnfold_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "nfold:")
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processdata(self, data):
        if not self.require_librarys(["pamr"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_data=data.getData()
            self.commitFunction()
    def processfit(self, data):
        if not self.require_librarys(["pamr"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_fit=data.getData()
            self.commitFunction()
    def commitFunction(self):
        if str(self.RFunctionParam_data) == '': return
        if str(self.RFunctionParam_fit) == '': return
        injection = []
        if str(self.RFunctionParamfolds_lineEdit.text()) != '':
            string = 'folds='+str(self.RFunctionParamfolds_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamnfold_lineEdit.text()) != '':
            string = 'nfold='+str(self.RFunctionParamnfold_lineEdit.text())
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['pamr.cv']+'<-pamr.cv(data='+str(self.RFunctionParam_data)+',fit='+str(self.RFunctionParam_fit)+','+inj+')')
        self.R('pamr.plotcv('+self.Rvariables['pamr.cv']+')')
        newData = signals.pamr.RPAMRCVFit(data = self.Rvariables['pamr.cv'])
        self.rSend("pamr.cv Output", newData)

