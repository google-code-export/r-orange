"""
<name>survdiff</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<tags>Survival</tags>
"""
from OWRpy import * 
import OWGUI 
import RRGUI 
class survdiff(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["survdiff"])
        self.RFunctionParam_subset = ""
        self.RFunctionParam_formula = ""
        self.RFunctionParam_rho = "0"
        self.RFunctionParam_na_action = ""
        self.loadSettings() 
        self.RFunctionParam_data = ''
        self.inputs = [("data", RvarClasses.RVariable, self.processdata)]
        self.outputs = [("survdiff Output", RvarClasses.RVariable)]
        
        box = RRGUI.tabWidget(self.controlArea, None, self)
        self.standardTab = RRGUI.createTabPage(box, "standardTab", self, "Standard")
        self.advancedTab = RRGUI.createTabPage(box, "advancedTab", self, "Advanced")
        self.RFUnctionParamsubset_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamsubset_lineEdit", self, "RFunctionParam_subset", label = "subset:")
        self.RFUnctionParamformula_lineEdit =  RRGUI.lineEdit(self.standardTab, "RFUnctionParamformula_lineEdit", self, "RFunctionParam_formula", label = "formula:")
        self.RFUnctionParamrho_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamrho_lineEdit", self, "RFunctionParam_rho", label = "rho:")
        self.RFUnctionParamna_action_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamna_action_lineEdit", self, "RFunctionParam_na_action", label = "na_action:")
        OWGUI.button(self.controlArea, self, "Commit", callback = self.commitFunction)
        self.RoutputWindow = RRGUI.textEdit("RoutputWindow", self)
        self.controlArea.layout().addWidget(self.RoutputWindow)
    def processdata(self, data):
        self.require_librarys(["survival"]) 
        if data:
            self.RFunctionParam_data=data["data"]
            self.commitFunction()
            if 'formula' in data:
                self.RFunctionParam_formula = data['formula']
    def commitFunction(self):
        if self.RFunctionParam_data == '': return
        if self.RFunctionParam_formula == '': return
        injection = []
        if self.RFunctionParam_subset != '':
            string = 'subset='+str(self.RFunctionParam_subset)
            injection.append(string)
        if self.RFunctionParam_formula != '':
            string = 'formula='+str(self.RFunctionParam_formula)
            injection.append(string)
        if self.RFunctionParam_rho != '':
            string = 'rho='+str(self.RFunctionParam_rho)
            injection.append(string)
        if self.RFunctionParam_na_action != '':
            string = 'na_action='+str(self.RFunctionParam_na_action)
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['survdiff']+'<-survdiff(data='+str(self.RFunctionParam_data)+','+inj+')')
        self.rSend("survdiff Output", {"data":self.Rvariables["survdiff"], "formula":self.RFunctionParam_formula})
