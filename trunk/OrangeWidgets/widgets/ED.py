"""
<name>ED, EC, ID</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>drc:ED</RFunctions>
<tags>Dose Response</tags>
<icon>icons/drc.PNG</icon>
"""
from OWRpy import * 
import redRGUI 

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
        self.data = {}
        
        
        self.RFunctionParam_respLev = "50"
        self.RFunctionParam_type = 0
        self.RFunctionParam_display = "TRUE"
        self.loadSettings() 
        self.RFunctionParam_object = ''
        self.inputs = [("object", RvarClasses.RVariable, self.processobject)]
        self.outputs = [("ED Output", RvarClasses.RDataFrame)]
        
        box = redRGUI.tabWidget(self.controlArea, None, self)
        self.standardTab = redRGUI.createTabPage(box, "standardTab", self, "Standard")
        self.advancedTab = redRGUI.createTabPage(box, "advancedTab", self, "Advanced")
        self.RFUnctionParamlogBase_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamlogBase_lineEdit", self, "RFunctionParam_logBase", label = "logBase:")
        self.RFunctionParamreference_comboBox = redRGUI.comboBox(self.advancedTab, "RFunctionParamreference_comboBox", self, "RFunctionParam_reference", label = "reference:", items = ['control', 'upper'])
        self.RFUnctionParamlevel_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamlevel_lineEdit", self, "RFunctionParam_level", label = "level:")
        self.RFunctionParamci_comboBox = redRGUI.comboBox(self.advancedTab, "RFunctionParamci_comboBox", self, "RFunctionParam_ci", label = "ci:", items = ['none', 'delta', 'fls', 'tfls'])
        self.RFUnctionParamod_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamod_lineEdit", self, "RFunctionParam_od", label = "od:")
        self.RFUnctionParambound_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParambound_lineEdit", self, "RFunctionParam_bound", label = "bound:")
        
        
        self.RFUnctionParamrespLev_lineEdit =  redRGUI.lineEdit(self.standardTab, "RFUnctionParamrespLev_lineEdit", self, "RFunctionParam_respLev", label = "Levels:")
        self.RFunctionParamtype_comboBox = redRGUI.comboBox(self.standardTab, "RFunctionParamtype_comboBox", self, "RFunctionParam_type", label = "type:", items = ['relative', 'absolute'])
        self.RFUnctionParamdisplay_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamdisplay_lineEdit", self, "RFunctionParam_display", label = "display:")
        redRGUI.button(self.controlArea, self, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRGUI.textEdit("RoutputWindow", self)
        self.standardTab.layout().addWidget(self.RoutputWindow)
    def processobject(self, data):
        self.require_librarys(["drc"]) 
        if data and 'data' in data:
            self.RFunctionParam_object=data["data"]
            self.data = data.copy()
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
        self.data['data'] = self.Rvariables["ED"]
        self.rSend("ED Output", self.data)
