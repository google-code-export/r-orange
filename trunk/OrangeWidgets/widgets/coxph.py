"""
<name>Cox Proportional Hazards</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Performs Cox Proportional Hazards on a collection of data with event times, event status, and a set of grouping variables.  This widget can perform complex comparisons inculding interactions.</description>
<RFunctions>survival:coxph</RFunctions>
<tags>Survival</tags>
<icon>icons/survival.png</icon>
"""
from OWRpy import * 
import redRGUI 
import SurvivalClasses
class coxph(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["coxph"])
        self.data = {}
        self.loadSettings() 
        self.RFunctionParam_data = ''
        self.inputs = [("data", RvarClasses.RVariable, self.processdata)]
        self.outputs = [("coxph Output", SurvivalClasses.SurvFit)]
        
        self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
        hbox = redRGUI.widgetBox(self.controlArea, orientation = 'horizontal')
        lbox = redRGUI.widgetBox(hbox)
        box = redRGUI.tabWidget(lbox)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.RFunctionParamformula =  redRGUI.RFormulaEntry(lbox)
        self.survTime = redRGUI.comboBox(self.RFunctionParamformula.extrasBox, label = 'Time')
        self.RFunctionParamrobust_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "robust:", text = 'FALSE')
        self.RFunctionParamweights_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "weights:", text = '')
        
        self.RFunctionParamy_lineEdit =  redRGUI.lineEdit(self.advancedTab,  label = "y:", text = 'TRUE')
        self.RFunctionParamx_lineEdit =  redRGUI.lineEdit(self.advancedTab,  label = "x:", text = 'FALSE')
        self.RFunctionParammodel_lineEdit =  redRGUI.lineEdit(self.advancedTab,  label = "model:", text = 'FALSE')
        self.RFunctionParammethod_comboBox = redRGUI.comboBox(self.standardTab, label = "method:", items = ['efron', 'breslow', 'exact'])
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        redRGUI.button(self.controlArea, "Report", callback = self.sendReport)
        self.RoutputWindow = redRGUI.textEdit(hbox, label = "RoutputWindow")
    def processdata(self, data):
        self.require_librarys(["survival"]) 
        if data:
            self.RFunctionParam_data=data["data"]
            self.data = data.copy()
            colnames = self.R('colnames('+self.RFunctionParam_data+')')
            self.survTime.update(colnames)
            self.RFunctionParamformula.update(colnames)
            self.commitFunction()
    def commitFunction(self):
        if str(self.RFunctionParam_data) == '': return
        if str(self.survTime.currentText())== '': return
        formulaOutput = self.RFunctionParamformula.Formula()
        if not formulaOutput: return
        if str(self.survTime.currentText()) == formulaOutput[0]: return
        if formulaOutput[0] == '' or formulaOutput[1] =='': return
        injection = []
        injection.append('formula = Surv('+str(self.survTime.currentText())+','+formulaOutput[0]+')~'+formulaOutput[1])
        if str(self.RFunctionParamrobust_lineEdit.text()) != '':
            string = 'robust='+str(self.RFunctionParamrobust_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamweights_lineEdit.text()) != '':
            string = 'weights='+str(self.RFunctionParamweights_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamy_lineEdit.text()) != '':
            string = 'y='+str(self.RFunctionParamy_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamx_lineEdit.text()) != '':
            string = 'x='+str(self.RFunctionParamx_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParammodel_lineEdit.text()) != '':
            string = 'model='+str(self.RFunctionParammodel_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParammethod_comboBox.currentText()) != '':
            string = 'method=\''+str(self.RFunctionParammethod_comboBox.currentText())+'\''
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['coxph']+'<-coxph(data='+str(self.RFunctionParam_data)+','+inj+')')
        self.R('txt<-capture.output('+self.Rvariables['coxph']+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
        self.data["data"] = self.Rvariables["coxph"]
        self.rSend("coxph Output", self.data)
    def compileReport(self):
        self.reportSettings("Input Settings",[("data", self.RFunctionParam_data)])
        self.reportSettings('Function Settings', [('robust',str(self.RFunctionParamrobust_lineEdit.text()))])
        self.reportSettings('Function Settings', [('singular_ok',str(self.RFunctionParamsingular_ok_lineEdit.text()))])
        self.reportSettings('Function Settings', [('weights',str(self.RFunctionParamweights_lineEdit.text()))])
        self.reportSettings('Function Settings', [('formula',str(self.RFunctionParamformula_lineEdit.text()))])
        self.reportSettings('Function Settings', [('y',str(self.RFunctionParamy_lineEdit.text()))])
        self.reportSettings('Function Settings', [('x',str(self.RFunctionParamx_lineEdit.text()))])
        self.reportSettings('Function Settings', [('model',str(self.RFunctionParammodel_lineEdit.text()))])
        self.reportSettings('Function Settings', [('method',str(self.RFunctionParammethod_lineEdit.text()))])
        self.reportRaw(self.Rvariables["coxph"])
    def sendReport(self):
        self.compileReport()
        self.showReport()
