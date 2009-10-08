"""
<name>survfit</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
import RRGUI 
class survfit(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["survfit"])
        self.RFunctionParam_subset = ""
        self.RFunctionParam_formula = ""
        self.RFunctionParam_weights = ""
        self.RFunctionParam_na_action = ""
        self.loadSettings() 
        self.RFunctionParam_data = ''
        self.inputs = [("data", RvarClasses.RVariable, self.processdata)]
        self.outputs = [("survfit Output", RvarClasses.RVariable)]
        
        box = OWGUI.widgetBox(self.controlArea, "Widget Box")
        self.RFUnctionParamsubset_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParamsubset_lineEdit", self, "RFunctionParam_subset", label = "subset:")
        self.RFUnctionParamformula_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParamformula_lineEdit", self, "RFunctionParam_formula", label = "formula:")
        self.RFUnctionParamweights_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParamweights_lineEdit", self, "RFunctionParam_weights", label = "weights:")
        self.RFUnctionParamna_action_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParamna_action_lineEdit", self, "RFunctionParam_na_action", label = "na_action:")
        OWGUI.button(box, self, "Commit", callback = self.commitFunction)
    def processdata(self, data):
        self.require_librarys(["survival"]) 
        if data:
            self.RFunctionParam_data=data["data"]
            self.commitFunction()
    def commitFunction(self):
        if self.RFunctionParam_data == '': return
        if self.RFunctionParam_formula == '': return
        self.R(self.Rvariables['survfit']+'<-survfit(data='+str(self.RFunctionParam_data)+',formula='+str(self.RFunctionParam_formula)+',weights='+str(self.RFunctionParam_weights)+')')
        self.rSend("survfit Output", {"data":self.Rvariables["survfit"]})
