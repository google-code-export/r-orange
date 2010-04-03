"""
<name>Linear Model</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Makes a linear model given a data table and a formula.  The data table should be in a 'melted' form (Melt DF should help with this).  This model can viewed using ANOVA-LM</description>
<tags>Stats, Parametric</tags>
<icon>icons/stats.png</icon>
<RFunctions>stats:lm</RFunctions>
"""
from OWRpy import * 
import redRGUI, redRGUI
class lm(OWRpy): 
    settingsList = ['RFunctionParam_data', 'RFunctionParam_formula', 'modelFormula', 'sentItems']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1, wantGUIDialog = 1)
        self.setRvariableNames(["lm"])
        self.RFunctionParam_formula = ""
        self.RFunctionParam_data = ''
        self.modelFormula = ''
        self.processingComplete = 0
        self.loadSettings()
        self.inputs = [("data", RvarClasses.RVariable, self.processdata)]
        self.outputs = [("lm Output", RvarClasses.RVariable)]
        
        #GUI
        
        box = redRGUI.widgetBox(self.GUIDialog, orientation = 'horizontal')
        paramBox = redRGUI.groupBox(self.GUIDialog, 'Parameters')
        formulaBox = redRGUI.widgetBox(self.controlArea)
        self.RFunctionParam_subset = redRGUI.lineEdit(paramBox, 'NULL', label = "subset:")
        self.RFunctionParam_qr = redRGUI.lineEdit(paramBox, 'TRUE', label = "qr:")

        self.RFunctionParam_singular_ok = redRGUI.lineEdit(paramBox, 'TRUE', label = "singular_ok:")
        self.RFunctionParam_y = redRGUI.lineEdit(paramBox, 'FALSE', label = "y:")
        self.RFunctionParam_weights = redRGUI.lineEdit(paramBox, "", label = "weights:")
        self.RFunctionParam_offset = redRGUI.lineEdit(paramBox, "", label = "offset:")
        self.RFunctionParam_contrasts = redRGUI.lineEdit(paramBox, "NULL", label = "contrasts:")
        self.RFunctionParam_x = redRGUI.lineEdit(paramBox, "FALSE", label = "x:")
        self.RFunctionParam_model = redRGUI.lineEdit(paramBox, "TRUE", label = "model:")
        self.RFunctionParam_method = redRGUI.lineEdit(paramBox, "qr", label = "method:")
        
        #start formula entry section

        buttonsBox = redRGUI.widgetBox(formulaBox, "Commands")
        self.formulEntry = redRGUI.RFormulaEntry(buttonsBox)
        
        
        self.processButton = redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        #self.processButton.setEnabled(False)
        self.status.setText('Data Not Connected Yet')
    def processdata(self, data):
        if data and data['data']:
            self.RFunctionParam_data=data["data"]
            names = self.R('colnames('+self.RFunctionParam_data+')')
            self.formulEntry.update(names)
            self.status.setText('Data Connected')
        else:
            self.formulEntry.clear()
            self.RFunctionParam_data = ''
            self.status.setText('Data Connection Failed. Please Reconnect')
    def commitFunction(self):
        if self.RFunctionParam_data == '': return
        self.RFunctionParam_formula = self.formulEntry.Formula()[0] + ' ~ ' + self.formulEntry.Formula()[1]

        
        self.R(self.Rvariables['lm']+'<-lm(data='+str(self.RFunctionParam_data)+',subset='+str(self.RFunctionParam_subset.text())+',qr='+str(self.RFunctionParam_qr.text())+',formula='+str(self.RFunctionParam_formula)+',singular_ok='+str(self.RFunctionParam_singular_ok.text())+',y='+str(self.RFunctionParam_y.text())+',weights='+str(self.RFunctionParam_weights.text())+',offset='+str(self.RFunctionParam_offset.text())+',contrasts='+str(self.RFunctionParam_contrasts.text())+',x='+str(self.RFunctionParam_x.text())+',model='+str(self.RFunctionParam_model.text())+',method="'+str(self.RFunctionParam_method.text())+'")')
        self.rSend("lm Output", {"data":self.Rvariables["lm"]})
        self.status.setText('Data Processed and Sent')
