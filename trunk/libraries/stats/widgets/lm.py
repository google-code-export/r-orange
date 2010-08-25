"""
<name>Linear Model</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Makes a linear model given a data table and a formula.  The data table should be in a 'melted' form (Melt DF should help with this).  This model can viewed using ANOVA-LM</description>
<tags>Parametric</tags>
<icon>stats.png</icon>
<RFunctions>stats:lm</RFunctions>
"""
from OWRpy import * 
import redRGUI, redRGUI
import libraries.plotting.signalClasses.RPlotAttribute as rpa
import libraries.stats.signalClasses.RLMFit as rlm
import libraries.base.signalClasses.RDataFrame as rdf
from libraries.base.qtWidgets.RFormulaEntry import RFormulaEntry
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.widgetBox import widgetBox
class lm(OWRpy): 
    settingsList = ['RFunctionParam_data', 'RFunctionParam_formula', 'modelFormula', 'sentItems']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, wantGUIDialog = 1)
        self.setRvariableNames(["lm"])
        self.RFunctionParam_formula = ""
        self.RFunctionParam_data = ''
        self.modelFormula = ''
        self.processingComplete = 0
        
        self.inputs = [("data", rdf.RDataFrame, self.processdata)]
        self.outputs = [("lm Output", rlm.RLMFit), ('lm plot attribute', rpa.RPlotAttribute)]
        
        #GUI
        
        box = widgetBox(self.GUIDialog, orientation = 'horizontal')
        paramBox = groupBox(self.GUIDialog, 'Parameters')
        formulaBox = widgetBox(self.controlArea)
        self.RFunctionParam_subset = lineEdit(paramBox, 'NULL', label = "subset:")
        self.RFunctionParam_qr = lineEdit(paramBox, 'TRUE', label = "qr:")

        self.RFunctionParam_singular_ok = lineEdit(paramBox, 'TRUE', label = "singular_ok:")
        self.RFunctionParam_y = lineEdit(paramBox, 'FALSE', label = "y:")
        self.RFunctionParam_weights = lineEdit(paramBox, "", label = "weights:")
        self.RFunctionParam_offset = lineEdit(paramBox, "", label = "offset:")
        self.RFunctionParam_contrasts = lineEdit(paramBox, "NULL", label = "contrasts:")
        self.RFunctionParam_x = lineEdit(paramBox, "FALSE", label = "x:")
        self.RFunctionParam_model = lineEdit(paramBox, "TRUE", label = "model:")
        self.RFunctionParam_method = lineEdit(paramBox, "qr", label = "method:")
        
        #start formula entry section

        buttonsBox = widgetBox(formulaBox, "Commands")
        self.formulEntry = RFormulaEntry(buttonsBox)
        
        
        self.processButton = button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        #self.processButton.setEnabled(False)
        self.status.setText('Data Not Connected Yet')
    def processdata(self, data):
        if data:
            self.RFunctionParam_data=data.getData()
            names = self.R('colnames('+self.RFunctionParam_data+')')
            self.formulEntry.update(names)
            self.status.setText('Data Connected')
        else:
            self.formulEntry.clear()
            self.RFunctionParam_data = ''
            self.status.setText('Data Connection Failed. Please Reconnect')
    def commitFunction(self):
        if self.RFunctionParam_data == '': 
            self.status.setText('No data')
            return
        self.RFunctionParam_formula = self.formulEntry.Formula()[0] + ' ~ ' + self.formulEntry.Formula()[1]

        
        self.R(self.Rvariables['lm']+'<-lm(data='+str(self.RFunctionParam_data)+',subset='+str(self.RFunctionParam_subset.text())+',qr='+str(self.RFunctionParam_qr.text())+',formula='+str(self.RFunctionParam_formula)+',singular_ok='+str(self.RFunctionParam_singular_ok.text())+',y='+str(self.RFunctionParam_y.text())+',weights='+str(self.RFunctionParam_weights.text())+',offset='+str(self.RFunctionParam_offset.text())+',contrasts='+str(self.RFunctionParam_contrasts.text())+',x='+str(self.RFunctionParam_x.text())+',model='+str(self.RFunctionParam_model.text())+',method="'+str(self.RFunctionParam_method.text())+'")')
        newData = rlm.RLMFit(data = self.Rvariables['lm'])
        self.rSend("lm Output", newData)
        
        newPlotAtt = rpa.RPlotAttribute(data = 'abline('+self.Rvariables['lm']+')')
        self.rSend('lm plot attribute', newPlotAtt)
        
    def getReportText(self, fileDir):
        return 'Generates a linear model fit to attached data and a linear model plot attribute.  The data fit was generated based on the following formula:\n\n%s\n\nOther parameters are as follows:\n\n%s\n\n' % (self.formulEntry.Formula()[0] + ' ~ ' + self.formulEntry.Formula()[1], '(data='+str(self.RFunctionParam_data)+',subset='+str(self.RFunctionParam_subset.text())+',qr='+str(self.RFunctionParam_qr.text())+',formula='+str(self.RFunctionParam_formula)+',singular_ok='+str(self.RFunctionParam_singular_ok.text())+',y='+str(self.RFunctionParam_y.text())+',weights='+str(self.RFunctionParam_weights.text())+',offset='+str(self.RFunctionParam_offset.text())+',contrasts='+str(self.RFunctionParam_contrasts.text())+',x='+str(self.RFunctionParam_x.text())+',model='+str(self.RFunctionParam_model.text())+',method="'+str(self.RFunctionParam_method.text())+'")')
        
