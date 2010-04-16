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
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["pamr.cv"])
        self.RFunctionParam_folds = "NULL"
        self.RFunctionParam_nfold = "NULL"
        self.require_librarys(["pamr"]) 
        self.loadSettings() 
        self.RFunctionParam_data = ''
        self.RFunctionParam_fit = ''
        self.inputs = [("data", RvarClasses.RVariable, self.processdata),("fit", RvarClasses.RVariable, self.processfit)]
        self.outputs = [("pamr.cv Output", RvarClasses.RVariable)]
        
        self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
        box = redRGUI.tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.RFunctionParamfolds_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "folds:")
        self.RFunctionParamnfold_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "nfold:")
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        redRGUI.button(self.controlArea, "Report", callback = self.sendReport)
    def processdata(self, data):
        if data:
            self.RFunctionParam_data=data["data"]
            self.commitFunction()
    def processfit(self, data):
        if data:
            self.RFunctionParam_fit=data["data"]
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
        self.rSend("pamr.cv Output", {"data":self.Rvariables["pamr.cv"]})
    def compileReport(self):
        self.reportSettings("Input Settings",[("data", self.RFunctionParam_data)])
        self.reportSettings("Input Settings",[("fit", self.RFunctionParam_fit)])
        self.reportSettings('Function Settings', [('folds',str(self.RFunctionParam_folds))])
        self.reportSettings('Function Settings', [('nfold',str(self.RFunctionParam_nfold))])
        self.reportRaw(self.Rvariables["pamr.cv"])
    def sendReport(self):
        self.compileReport()
        self.showReport()
