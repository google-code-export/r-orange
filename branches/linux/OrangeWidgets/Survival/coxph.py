"""
<name>Cox</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Performs Cox proportional hazards analysis and generates a Cox model.  The Cox model can be used to validate the proportional hazards of the data.</description>
<icon>icons/survival.png</icon>
<tags>Survival</tags>
"""
from OWRpy import * 
import OWGUI 
import RRGUI 
import SurvivalClasses

class coxph(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["coxph"])
        self.RFunctionParam_subset = ""
        self.RFunctionParam_na_action = ""
        self.RFunctionParam_formula = ""
        self.RFunctionParam_init = ""
        self.RFunctionParam_control = ""
        self.RFunctionParam_weights = ""
        self.RFunctionParam_robust = "FALSE"
        self.RFunctionParam_y = "TRUE"
        self.RFunctionParam_x = "FALSE"
        self.RFunctionParam_model = "FALSE"
        self.RFunctionParam_method = 0
        self.modelFormula = ''
        self.handled = 0
        self.processingComplete = 0
        self.ableToCommit = 0
        self.loadSettings() 
        self.RFunctionParam_data = ''
        self.inputs = [("data", SurvivalClasses.SurvFit, self.processdata)]
        self.outputs = [("coxph Output", RvarClasses.RVariable)]
        
        box = RRGUI.tabWidget(self.controlArea, None, self)
        self.standardTab = RRGUI.createTabPage(box, "standardTab", self, "Standard")
        self.advancedTab = RRGUI.createTabPage(box, "advancedTab", self, "Advanced")
        self.RFUnctionParamsubset_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamsubset_lineEdit", self, "RFunctionParam_subset", label = "subset:")
        self.RFUnctionParamna_action_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamna_action_lineEdit", self, "RFunctionParam_na_action", label = "na_action:")
        self.RFUnctionParamformula_lineEdit =  RRGUI.lineEdit(self.standardTab, "RFUnctionParamformula_lineEdit", self, "RFunctionParam_formula", label = "formula:")
        self.RFUnctionParaminit_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParaminit_lineEdit", self, "RFunctionParam_init", label = "init:")
        self.RFUnctionParamcontrol_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamcontrol_lineEdit", self, "RFunctionParam_control", label = "control:")
        self.RFUnctionParamweights_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamweights_lineEdit", self, "RFunctionParam_weights", label = "weights:")
        self.RFUnctionParamrobust_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamrobust_lineEdit", self, "RFunctionParam_robust", label = "robust:")
        self.RFUnctionParamy_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamy_lineEdit", self, "RFunctionParam_y", label = "y:")
        self.RFUnctionParamx_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamx_lineEdit", self, "RFunctionParam_x", label = "x:")
        self.RFUnctionParammodel_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParammodel_lineEdit", self, "RFunctionParam_model", label = "model:")
        self.RFunctionParammethod_comboBox = RRGUI.comboBox(self.advancedTab, "RFunctionParammethod_comboBox", self, "RFunctionParam_method", label = "method:", items = ['efron', 'breslow', 'exact'])
        
        box = OWGUI.widgetBox(self.standardTab, "Formula Variables")
        
        self.phenoVarListBox = RRGUI.listBox(box, 'phenoVarListBox', self, callback = self.phenoVarListBoxItemClicked, tooltip = 'The column of the classes of the samples.')
        buttonsBox = OWGUI.widgetBox(self.standardTab, "Commands")
        
        self.RFunctionParam_timeBox = RRGUI.comboBox(buttonsBox, 'RFunctionParam_timeBox', self, 'RFunctionParam_time', label = 'Event Time:', tooltip = 'The column that represents the recurrence time in the data')
        self.RFunctionParam_eventBox = RRGUI.comboBox(buttonsBox, 'RFunctionParam_eventBox', self, 'RFunctionParam_event', label = 'Event Status:', tooltip = 'The column that represents the event status in the data')
        
        self.plusButton = OWGUI.button(buttonsBox, self, "And", callback = self.plusButtonClicked)
        self.plusButton.setEnabled(False)
        self.colonButton = OWGUI.button(buttonsBox, self, "Interacting With", callback = self.colonButtonClicked)
        self.colonButton.setEnabled(False)
        self.starButton = OWGUI.button(buttonsBox, self, "Together and Interacting", callback = self.starButtonClicked)
        self.starButton.setEnabled(False)
        self.processEsetButton = OWGUI.button(buttonsBox, self, "Clear", callback = self.clearModel)
        #self.processEsetButton.setEnabled(False)
        self.modelText = OWGUI.widgetLabel(buttonsBox, '')
        
        OWGUI.button(self.controlArea, self, "Commit", callback = self.commitFunction)
        self.RoutputWindow = RRGUI.textEdit("RoutputWindow", self)
        self.controlArea.layout().addWidget(self.RoutputWindow)
    def processdata(self, data):
        self.require_librarys(["survival"]) 
        if data:
            self.RFunctionParam_data=data["data"]

            if 'formula' in data:
                self.RFunctionParam_formula = data['formula']
            if 'rawdata' in data:
                self.RFunctionParam_data = data['rawdata']
            self.commitFunction()
    def commitFunction(self):
        if self.RFunctionParam_data == '': return
        if self.RFunctionParam_formula == '': return
        injection = []
        if self.RFunctionParam_subset != '':
            string = 'subset='+str(self.RFunctionParam_subset)
            injection.append(string)
        if self.RFunctionParam_na_action != '':
            string = 'na_action='+str(self.RFunctionParam_na_action)
            injection.append(string)
        if self.RFunctionParam_formula != '':
            string = 'formula='+str(self.RFunctionParam_formula)
            injection.append(string)
        if self.RFunctionParam_init != '':
            string = 'init='+str(self.RFunctionParam_init)
            injection.append(string)
        if self.RFunctionParam_control != '':
            string = 'control='+str(self.RFunctionParam_control)
            injection.append(string)
        if self.RFunctionParam_weights != '':
            string = 'weights='+str(self.RFunctionParam_weights)
            injection.append(string)
        if self.RFunctionParam_robust != '':
            string = 'robust='+str(self.RFunctionParam_robust)
            injection.append(string)
        if self.RFunctionParam_y != '':
            string = 'y='+str(self.RFunctionParam_y)
            injection.append(string)
        if self.RFunctionParam_x != '':
            string = 'x='+str(self.RFunctionParam_x)
            injection.append(string)
        if self.RFunctionParam_model != '':
            string = 'model='+str(self.RFunctionParam_model)
            injection.append(string)
        if self.RFunctionParam_method != '':
            string = 'method="'+str(self.RFunctionParammethod_comboBox.itemText(int(self.RFunctionParam_method)))+'"'
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['coxph']+'<-coxph(data='+str(self.RFunctionParam_data)+','+inj+')')
        self.R('txt<-capture.output('+self.Rvariables['coxph']+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
        self.rSend("coxph Output", {"data":self.Rvariables["coxph"]})
        
    def clearModel(self):
        self.modelFormula = ''
        self.modelText.setText('')
        self.phenoVarListBox.setEnabled(True)
        self.plusButton.setEnabled(False)
        self.colonButton.setEnabled(False)
        self.starButton.setEnabled(False)
    
    def phenoVarListBoxItemClicked(self):
        self.handled = 1
        if self.processingComplete == 1:
            self.modelFormula = ''
            self.processingComplete = 0
        element = self.phenoVarListBox.selectedItems()[0].text()
        self.modelFormula += str(element)
        self.phenoVarListBox.setEnabled(False)
        self.plusButton.setEnabled(True)
        self.colonButton.setEnabled(True)
        self.starButton.setEnabled(True)
        #self.processEsetButton.setEnabled(True)
        self.modelText.setText("Model: " + self.modelFormula)
        self.ableToCommit = 1
    def plusButtonClicked(self):
        self.modelFormula += ' + '
        self.phenoVarListBox.setEnabled(True)
        self.plusButton.setEnabled(False)
        self.colonButton.setEnabled(False)
        self.starButton.setEnabled(False)
        #self.processEsetButton.setEnabled(False)
        self.modelText.setText("Model: " + self.modelFormula)
        self.ableToCommit = 0
    def colonButtonClicked(self):
        self.modelFormula += ' : '
        self.phenoVarListBox.setEnabled(True)
        self.plusButton.setEnabled(False)
        self.colonButton.setEnabled(False)
        self.starButton.setEnabled(False)
        #self.processEsetButton.setEnabled(False)
        self.modelText.setText("Model: " + self.modelFormula)
        self.ableToCommit = 0
    def starButtonClicked(self):
        self.modelFormula += ' * '
        self.phenoVarListBox.setEnabled(True)
        self.plusButton.setEnabled(False)
        self.colonButton.setEnabled(False)
        self.starButton.setEnabled(False)
        #self.processEsetButton.setEnabled(False)
        self.modelText.setText("Model: " + self.modelFormula)
        self.ableToCommit = 0
