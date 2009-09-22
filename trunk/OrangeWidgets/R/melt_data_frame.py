"""
<name>melt.data.frame</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
class melt_data_frame(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["melt.data.frame"])
        self.RFunctionParam_na_rm = "!preserve.na"
        self.RFunctionParam_measure_var = ""
        self.RFunctionParam_variable_name = "variable"
        self.RFunctionParam_preserve_na = "TRUE"
        self.RFunctionParam_id_var = ""
        self.RFunctionParam_data = ''
        self.inputs = [("data", RvarClasses.RDataFrame, self.processdata)]
        self.outputs = [("melt.data.frame Output", RvarClasses.RDataFrame)]
        
        box = OWGUI.widgetBox(self.controlArea, "Widget Box")
        OWGUI.lineEdit(box, self, "RFunctionParam_na_rm", label = "na_rm:")
        OWGUI.lineEdit(box, self, "RFunctionParam_measure_var", label = "measure_var:")
        OWGUI.lineEdit(box, self, "RFunctionParam_variable_name", label = "variable_name:")
        OWGUI.lineEdit(box, self, "RFunctionParam_preserve_na", label = "preserve_na:")
        OWGUI.lineEdit(box, self, "RFunctionParam_id_var", label = "id_var:")
        OWGUI.button(box, self, "Commit", callback = self.commitFunction)
    def processdata(self, data):
        if data:
            self.require_librarys(['reshape'])
            self.RFunctionParam_data=data["data"]
            self.commitFunction()
    def commitFunction(self):
        if self.RFunctionParam_data == '': return
        self.R(self.Rvariables['melt.data.frame']+'<-melt.data.frame(data='+str(self.RFunctionParam_data)+',na_rm='+str(self.RFunctionParam_na_rm)+',measure_var='+str(self.RFunctionParam_measure_var)+',variable_name="'+str(self.RFunctionParam_variable_name)+'",preserve_na='+str(self.RFunctionParam_preserve_na)+',id_var='+str(self.RFunctionParam_id_var)+')')
        self.rSend("melt.data.frame Output", {"data":self.Rvariables["melt.data.frame"]})
