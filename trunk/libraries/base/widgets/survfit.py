"""
<name>Survival Fit</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Generates a survival fit of either a data table or a fit model.  This widget can be connected to a plotting widget for generating survival curves.</description>
<RFunctions>survival:survfit</RFunctions>
<tags>Survival</tags>
<icon>icons/survival.png</icon>
"""
from OWRpy import * 
import redRGUI 
class survfit(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1, wantGUIDialog = 1)
        
        self.setRvariableNames(["survfit"])
        self.data = {}
        self.loadSettings() 
        self.RFunctionParam_data = ''
        self.inputs = [("data", signals.RVariable, self.processdata), ('Model Fit', signals.RModelFit, self.processfit)]
        self.outputs = [("survfit Output", signals.RSurvFit)]
        
        self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
        formulaBox = redRGUI.widgetBox(self.controlArea)
        self.times = redRGUI.comboBox(formulaBox, label = 'Times', toolTip = 'The event times.')
        self.event = redRGUI.comboBox(formulaBox, label = 'Events', toolTip = 'The event status. 1 means an event occurred\nwhile 0 means there was no event at the end time.')
        self.groupings = redRGUI.comboBox(formulaBox, label = 'Groupings', toolTip = 'The column that specifies the groupings of the data.\nThis is optional.')
        self.RFunctionParamweights_lineEdit =  redRGUI.lineEdit(self.GUIDialog,  label = "weights:", text = '', toolTip = 'The weights applied to the data, should be in the form c(weight1, weight2, ...).')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processfit(self, data):
        self.require_librarys(['survival'])
        if data:
            self.times.clear()
            self.event.clear()
            self.groupings.clear()
            self.data = data.copy()
            self.R(self.Rvariables['survfit']+'<-survfit('+data['data']+')')
            self.out = signals.RModelFit(data=self.Rvariables["survfit"])
            self.rSend("survfit Output", self.out)
    def processdata(self, data):
        self.require_librarys(["survival"]) 
        if data:
            self.RFunctionParam_data=data["data"]
            colnames = self.R('colnames('+self.RFunctionParam_data+')')
            self.groupings.update(colnames)
            self.times.update(colnames)
            self.event.update(colnames)
            self.data = data.copy()
            self.commitFunction()
    def commitFunction(self):
        if str(self.RFunctionParam_data) == '': return
        if str(self.times.currentText()) == str(self.event.currentText()): return
        if str(self.times.currentText()) == '' or str(self.event.currentText()) == '': return
        injection = []
        formula = 'formula = Surv('+str(self.times.currentText())+','+str(self.event.currentText())+')'
        if str(self.groupings.currentText()) != '':
            formula += '~'+str(self.groupings.currentText())
        injection.append(formula)
        self.formula = formula
        if str(self.RFunctionParamweights_lineEdit.text()) != '':
            string = 'weights='+str(self.RFunctionParamweights_lineEdit.text())
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['survfit']+'<-survfit(data='+str(self.RFunctionParam_data)+','+inj+')')
        self.out = signals.RSurvFit(data=self.Rvariables["survfit"])
        self.rSend("survfit Output", self.out)

