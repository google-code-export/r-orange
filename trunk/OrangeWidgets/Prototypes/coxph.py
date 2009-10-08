"""
<name>coxph</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
import RRGUI 
class coxph(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["coxph"])
        self.RFunctionParam_formula = ""
        self.RFunctionParam_init = ""
        self.RFunctionParam_weights = ""
        self.RFunctionParam_robust = "FALSE"
        self.RFunctionParam_y = "TRUE"
        self.RFunctionParam_x = "FALSE"
        self.RFunctionParam_model = "FALSE"
        self.RFunctionParam_method = 0
        self.loadSettings() 
        self.RFunctionParam_data = ''
        self.inputs = [("data", RvarClasses.RVariable, self.processdata)]
        self.outputs = [("coxph Output", RvarClasses.RVariable)]
        
        box = OWGUI.widgetBox(self.controlArea, "Widget Box")
        self.RFUnctionParamformula_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParamformula_lineEdit", self, "RFunctionParam_formula", label = "formula:")
        self.RFUnctionParaminit_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParaminit_lineEdit", self, "RFunctionParam_init", label = "init:")
        self.RFUnctionParamweights_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParamweights_lineEdit", self, "RFunctionParam_weights", label = "weights:")
        self.RFUnctionParamrobust_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParamrobust_lineEdit", self, "RFunctionParam_robust", label = "robust:")
        self.RFUnctionParamy_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParamy_lineEdit", self, "RFunctionParam_y", label = "y:")
        self.RFUnctionParamx_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParamx_lineEdit", self, "RFunctionParam_x", label = "x:")
        self.RFUnctionParammodel_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParammodel_lineEdit", self, "RFunctionParam_model", label = "model:")
        self.RFunctionParammethod_comboBox = RRGUI.comboBox(box, "RFunctionParammethod_comboBox", self, "RFunctionParam_method", label = "method:", items = ['efron', 'breslow', 'exact'])
        OWGUI.button(box, self, "Commit", callback = self.commitFunction)
        self.RoutputWindow = RRGUI.textEdit("RoutputWindow", self)
        box.layout().addWidget(self.RoutputWindow)
    def processdata(self, data):
        self.require_librarys(["survival"]) 
        if data:
            self.RFunctionParam_data=data["data"]
            self.commitFunction()
    def commitFunction(self):
        if self.RFunctionParam_data == '': return
        if self.RFunctionParam_formula == '': return
        if self.RFunctionParam_method == 0:
            meth = 'efron'
        elif self.RFunctionParam_method == 1:
            meth = 'breslow'
        elif self.RFunctionParam_method == 2:
            meth = 'exact'
        self.R(self.Rvariables['coxph']+'<-coxph(data='+str(self.RFunctionParam_data)+',formula='+str(self.RFunctionParam_formula)+',init='+str(self.RFunctionParam_init)+',weights='+str(self.RFunctionParam_weights)+',robust='+str(self.RFunctionParam_robust)+',y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+',model='+str(self.RFunctionParam_model)+',method="'+str(meth)+'")')
        self.R('txt<-capture.output('+self.Rvariables['coxph']+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
        self.rSend("coxph Output", {"data":self.Rvariables["coxph"]})
