"""
<name>ED</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<tags>Dose Response</tags>
<icon>icons/drc.PNG</icon>
"""
from OWRpy import * 
import OWGUI 
import RRGUI 
class ED(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["ED"])
        self.RFunctionParam_logBase = "NULL"
        self.RFunctionParam_reference = 0
        self.RFunctionParam_level = '0.95'
        self.RFunctionParam_ci = 2
        self.RFunctionParam_od = "FALSE"
        self.RFunctionParam_bound = "TRUE"
        
        
        self.RFunctionParam_respLev = "50"
        self.RFunctionParam_type = 0
        self.RFunctionParam_display = "TRUE"
        self.loadSettings() 
        self.RFunctionParam_object = ''
        self.inputs = [("object", RvarClasses.RVariable, self.processobject)]
        self.outputs = [("ED Output", RvarClasses.RDataFrame)]
        
        box = RRGUI.tabWidget(self.controlArea, None, self)
        self.standardTab = RRGUI.createTabPage(box, "standardTab", self, "Standard")
        self.advancedTab = RRGUI.createTabPage(box, "advancedTab", self, "Advanced")
        self.RFUnctionParamlogBase_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamlogBase_lineEdit", self, "RFunctionParam_logBase", label = "logBase:")
        self.RFunctionParamreference_comboBox = RRGUI.comboBox(self.advancedTab, "RFunctionParamreference_comboBox", self, "RFunctionParam_reference", label = "reference:", items = ['control', 'upper'])
        self.RFUnctionParamlevel_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamlevel_lineEdit", self, "RFunctionParam_level", label = "level:")
        self.RFunctionParamci_comboBox = RRGUI.comboBox(self.advancedTab, "RFunctionParamci_comboBox", self, "RFunctionParam_ci", label = "ci:", items = ['none', 'delta', 'fls', 'tfls'])
        self.RFUnctionParamod_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamod_lineEdit", self, "RFunctionParam_od", label = "od:")
        self.RFUnctionParambound_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParambound_lineEdit", self, "RFunctionParam_bound", label = "bound:")
        
        
        self.RFUnctionParamrespLev_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamrespLev_lineEdit", self, "RFunctionParam_respLev", label = "respLev:")
        self.RFunctionParamtype_comboBox = RRGUI.comboBox(self.standardTab, "RFunctionParamtype_comboBox", self, "RFunctionParam_type", label = "type:", items = ['relative', 'absolute'])
        self.RFUnctionParamdisplay_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamdisplay_lineEdit", self, "RFunctionParam_display", label = "display:")
        OWGUI.button(self.controlArea, self, "Commit", callback = self.commitFunction)
        self.RoutputWindow = RRGUI.textEdit("RoutputWindow", self)
        self.standardTab.layout().addWidget(self.RoutputWindow)
    def processobject(self, data):
        self.require_librarys(["drc"]) 
        if data:
            self.RFunctionParam_object=data["data"]
            self.commitFunction()
    def commitFunction(self):
        if self.RFunctionParam_object == '': return
        if self.RFunctionParam_respLev == '': return
        injection = []
        if self.RFunctionParam_logBase != '':
            string = 'logBase='+str(self.RFunctionParam_logBase)
            injection.append(string)
        if self.RFunctionParam_reference != '':
            string = 'reference="'+str(self.RFunctionParamreference_comboBox.currentText())+'"'
            injection.append(string)
        if self.RFunctionParam_level != '':
            string = 'level='+str(self.RFunctionParam_level)
            injection.append(string)
        if self.RFunctionParam_ci != '':
            string = 'ci="'+str(self.RFunctionParamci_comboBox.currentText())+'"'
            injection.append(string)
        if self.RFunctionParam_od != '':
            string = 'od='+str(self.RFunctionParam_od)
            injection.append(string)
        if self.RFunctionParam_bound != '':
            string = 'bound='+str(self.RFunctionParam_bound)
            injection.append(string)
        if self.RFunctionParam_respLev != '':
            string = 'respLev=c('+str(self.RFunctionParam_respLev)+')'
            injection.append(string)
        if self.RFunctionParam_type != '':
            string = 'type="'+str(self.RFunctionParamtype_comboBox.currentText())+'"'
            injection.append(string)
        if self.RFunctionParam_display != '':
            string = 'display='+str(self.RFunctionParam_display)
            injection.append(string)
        inj = ','.join(injection)
        self.R('txt<-capture.output('+self.Rvariables['ED']+'<-ED(object='+str(self.RFunctionParam_object)+','+inj+'))')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
        self.rSend("ED Output", {"data":self.Rvariables["ED"]})
