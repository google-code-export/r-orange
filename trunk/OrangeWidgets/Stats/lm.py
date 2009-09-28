"""
<name>lm</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
class lm(OWRpy): 
    settingsList = ['RFunctionParam_data', 'RFunctionParam_formula', 'modelFormula', 'sentItems']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 1, resizingEnabled = 1)
        self.setRvariableNames(["lm"])
        self.RFunctionParam_subset = "NULL"
        self.RFunctionParam_qr = "TRUE"
        self.RFunctionParam_formula = ""
        self.RFunctionParam_singular_ok = "TRUE"
        self.RFunctionParam_y = "FALSE"
        self.RFunctionParam_weights = ""
        self.RFunctionParam_offset = ""
        self.RFunctionParam_contrasts = "NULL"
        self.RFunctionParam_x = "FALSE"
        self.RFunctionParam_model = "TRUE"
        self.RFunctionParam_method = "qr"
        self.RFunctionParam_data = ''
        self.modelFormula = ''
        self.processingComplete = 0
        self.loadSettings()
        self.inputs = [("data", RvarClasses.RVariable, self.processdata)]
        self.outputs = [("lm Output", RvarClasses.RVariable)]
        
        box = OWGUI.widgetBox(self.controlArea, "Widget Box")
        OWGUI.lineEdit(box, self, "RFunctionParam_subset", label = "subset:")
        OWGUI.lineEdit(box, self, "RFunctionParam_qr", label = "qr:")

        OWGUI.lineEdit(box, self, "RFunctionParam_singular_ok", label = "singular_ok:")
        OWGUI.lineEdit(box, self, "RFunctionParam_y", label = "y:")
        OWGUI.lineEdit(box, self, "RFunctionParam_weights", label = "weights:")
        OWGUI.lineEdit(box, self, "RFunctionParam_offset", label = "offset:")
        OWGUI.lineEdit(box, self, "RFunctionParam_contrasts", label = "contrasts:")
        OWGUI.lineEdit(box, self, "RFunctionParam_x", label = "x:")
        OWGUI.lineEdit(box, self, "RFunctionParam_model", label = "model:")
        OWGUI.lineEdit(box, self, "RFunctionParam_method", label = "method:")
        OWGUI.button(box, self, "Commit", callback = self.commitFunction)
        
        #start formula entry section
        self.splitCanvas = QSplitter(Qt.Vertical, self.mainArea)
        self.mainArea.layout().addWidget(self.splitCanvas)
        box = OWGUI.widgetBox(self, "Formula Variables")
        
        self.phenoVarListBox = OWGUI.listBox(box, self, callback = self.phenoVarListBoxItemClicked, tooltip = 'The column of the classes of the samples.')
        buttonsBox = OWGUI.widgetBox(self, "Commands")

        self.RFunctionParam_formulaOutcomeBox = OWGUI.comboBox(buttonsBox, self, 'RFunctionParam_formulaOutcome', label = 'Response Column:', tooltip = 'The column of the values of the classes.') #, callback = self.setRFuntionParam_FormulaOutcome)
        self.plusButton = OWGUI.button(buttonsBox, self, "And", callback = self.plusButtonClicked)
        self.plusButton.setEnabled(False)
        self.colonButton = OWGUI.button(buttonsBox, self, "Interacting With", callback = self.colonButtonClicked)
        self.colonButton.setEnabled(False)
        self.starButton = OWGUI.button(buttonsBox, self, "Together and Interacting", callback = self.starButtonClicked)
        self.starButton.setEnabled(False)
        self.processEsetButton = OWGUI.button(buttonsBox, self, "Commit", callback = self.commitFunction)
        self.processEsetButton.setEnabled(False)
        self.modelText = OWGUI.widgetLabel(buttonsBox, '')
        self.splitCanvas.addWidget(box)
        self.splitCanvas.addWidget(buttonsBox)
    # def setRFuntionParam_FormulaOutcome(self):
        # self.RFunctionParam_formulaResponse += self.RFunctionParam_formulaOutcomeBox.currentText()
        # self.FormatFormula()
        
    # def FormatFormula(self):
        # formula = ''
        # formula += self.RFunctionParam_formulaOutcomeBox.currentText()
        # formula += '~'
        # formula += self.RFunctionParam_formulaOutcome
        # self.RFunctionParam_formula = formula
    def onLoadSavedSession(self):
        
        self.commitFunction()
    
    def processdata(self, data):
        if data:
            self.RFunctionParam_data=data["data"]
            self.commitFunction()
        names = self.R('colnames('+self.RFunctionParam_data+')')
        for name in names:
            self.RFunctionParam_formulaOutcomeBox.addItem(name)
        for name in names:
            self.phenoVarListBox.addItem(name)
    def commitFunction(self):
        if self.RFunctionParam_data == '': return
        if self.RFunctionParam_formulaOutcomeBox.currentText() == None or self.RFunctionParam_formulaOutcomeBox.currentText() == '': return
        if self.modelText.text() == '': return
        model = self.modelText.text().replace('Model: ', '')
        self.RFunctionParam_formula = self.RFunctionParam_formulaOutcomeBox.currentText()+'~'+model

        
        self.R(self.Rvariables['lm']+'<-lm(data='+str(self.RFunctionParam_data)+',subset='+str(self.RFunctionParam_subset)+',qr='+str(self.RFunctionParam_qr)+',formula='+str(self.RFunctionParam_formula)+',singular_ok='+str(self.RFunctionParam_singular_ok)+',y='+str(self.RFunctionParam_y)+',weights='+str(self.RFunctionParam_weights)+',offset='+str(self.RFunctionParam_offset)+',contrasts='+str(self.RFunctionParam_contrasts)+',x='+str(self.RFunctionParam_x)+',model='+str(self.RFunctionParam_model)+',method="'+str(self.RFunctionParam_method)+'")')
        self.rSend("lm Output", {"data":self.Rvariables["lm"]})
        
    def phenoVarListBoxItemClicked(self):
        if self.processingComplete == 1:
            self.modelFormula = ''
            self.processingComplete = 0
        element = self.phenoVarListBox.selectedItems()[0].text()
        self.modelFormula += str(element)
        self.phenoVarListBox.setEnabled(False)
        self.plusButton.setEnabled(True)
        self.colonButton.setEnabled(True)
        self.starButton.setEnabled(True)
        self.processEsetButton.setEnabled(True)
        self.modelText.setText("Model: " + self.modelFormula)
    def plusButtonClicked(self):
        self.modelFormula += ' + '
        self.phenoVarListBox.setEnabled(True)
        self.plusButton.setEnabled(False)
        self.colonButton.setEnabled(False)
        self.starButton.setEnabled(False)
        self.processEsetButton.setEnabled(False)
        self.modelText.setText("Model: " + self.modelFormula)
    def colonButtonClicked(self):
        self.modelFormula += ' : '
        self.phenoVarListBox.setEnabled(True)
        self.plusButton.setEnabled(False)
        self.colonButton.setEnabled(False)
        self.starButton.setEnabled(False)
        self.processEsetButton.setEnabled(False)
        self.modelText.setText("Model: " + self.modelFormula)
    def starButtonClicked(self):
        self.modelFormula += ' * '
        self.phenoVarListBox.setEnabled(True)
        self.plusButton.setEnabled(False)
        self.colonButton.setEnabled(False)
        self.starButton.setEnabled(False)
        self.processEsetButton.setEnabled(False)
        self.modelText.setText("Model: " + self.modelFormula)
