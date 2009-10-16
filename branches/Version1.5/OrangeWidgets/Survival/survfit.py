"""
<name>Survival Fit</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Generates a survival fit object</description>
<icon>icons/survival.png</icon>
<tags>Survival</tags>
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
        self.RFunctionParam_time = 0
        self.RFunctionParam_event = 0
        self.modelFormula = ''
        self.handled = 0
        self.processingComplete = 0
        self.ableToCommit = 0
        self.loadSettings() 
        self.RFunctionParam_data = ''
        self.inputs = [("data", RvarClasses.RVariable, self.processdata)]
        self.outputs = [("survfit Output", RvarClasses.RVariable)]
        
        tw = RRGUI.tabWidget(self.controlArea, None, self)
        self.standardPage = RRGUI.createTabPage(tw, "standardPage", self, "Standard")
        self.advancedTab = RRGUI.createTabPage(tw, "advancedTab", self, "Advanced")
        #box = OWGUI.widgetBox(self.standardPage, "Widget Box")
        self.RFUnctionParamsubset_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamsubset_lineEdit", self, "RFunctionParam_subset", label = "subset:")
        #self.RFUnctionParamformula_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParamformula_lineEdit", self, "RFunctionParam_formula", label = "formula:")
        self.RFUnctionParamweights_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamweights_lineEdit", self, "RFunctionParam_weights", label = "weights:")
        self.RFUnctionParamna_action_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamna_action_lineEdit", self, "RFunctionParam_na_action", label = "na_action:")
        OWGUI.button(self.controlArea, self, "Commit", callback = self.commitFunction)
        
        #formula section
        box = OWGUI.widgetBox(self.standardPage, "Formula Variables")
        
        self.phenoVarListBox = RRGUI.listBox(box, 'phenoVarListBox', self, callback = self.phenoVarListBoxItemClicked, tooltip = 'The column of the classes of the samples.')
        buttonsBox = OWGUI.widgetBox(self.standardPage, "Commands")
        
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
        # self.splitCanvas.addWidget(box)
        # self.splitCanvas.addWidget(buttonsBox)
    def clearModel(self):
        self.modelFormula = ''
        self.modelText.setText('')
        self.phenoVarListBox.setEnabled(True)
        self.plusButton.setEnabled(False)
        self.colonButton.setEnabled(False)
        self.starButton.setEnabled(False)
        
    def processdata(self, data):
        self.require_librarys(["survival"]) 
        if data:
            self.RFunctionParam_data=data["data"]
            
            names = self.R('colnames('+self.RFunctionParam_data+')')
            self.RFunctionParam_timeBox.clear()
            self.RFunctionParam_eventBox.clear()
            self.phenoVarListBox.clear()    
            for name in names:
                self.RFunctionParam_timeBox.addItem(name)
                self.RFunctionParam_eventBox.addItem(name)
                self.phenoVarListBox.addItem(name)
            self.commitFunction()

    def commitFunction(self):
        if self.RFunctionParam_data == '': return
        print 'data is '+self.RFunctionParam_data
        if self.RFunctionParam_timeBox.itemText(self.RFunctionParam_time) != self.RFunctionParam_eventBox.itemText(self.RFunctionParam_event) or self.modelFormula == '':
            formula = 'Surv('+self.RFunctionParam_timeBox.itemText(self.RFunctionParam_time) + ',' + self.RFunctionParam_eventBox.itemText(self.RFunctionParam_event) + ')~' + self.modelFormula
            print formula
        else: return
        if self.handled == 0: return
        if self.ableToCommit == 0:
            QMessageBox.information(self, 'Orange Canvas','Model formula is of incorrect type.  Formula will be cleared, please reenter.',  QMessageBox.Ok + QMessageBox.Default)
            self.clearModel
            return
        
        
        self.RFunctionParam_formula = formula
        self.R(self.Rvariables['survfit']+'<-survfit(data='+str(self.RFunctionParam_data)+',formula='+str(self.RFunctionParam_formula)+',weights='+str(self.RFunctionParam_weights)+')')
        self.rSend("survfit Output", {"data":self.Rvariables["survfit"], 'formula':self.RFunctionParam_formula, 'rawdata':self.RFunctionParam_data})
        self.processingComplete = 1
        
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
