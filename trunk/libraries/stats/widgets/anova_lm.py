"""
<name>ANOVA-LM</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Performs ANOVA on a linear model, usually made using the LM widget.  Returns an output of the ANOV comparison.</description>
<tags>Parametric</tags>
<icon>stats.png</icon>
<RFunctions>stats:anova, stats:lm, stats:anova.lm</RFunctions>
"""
from OWRpy import * 
import OWGUI 
import redRGUI
from libraries.base.signalClasses.RLMFit import RLMFit as redRRLMFit
from libraries.base.qtWidgets.textEdit import textEdit
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.groupBox import groupBox
class anova_lm(OWRpy): 
    settingsList = ['RFunctionParam_object']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.RFunctionParam_object = ''
        self.saveSettingsList.extend(['RFunctionParam_object'])
        self.inputs.addInput('id0', 'object', redRRLMFit, self.processobject)

        
        box = groupBox(self.controlArea, "Output")
        button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = textEdit(box)
        #box.layout().addWidget(self.RoutputWindow)
    def onLoadSavedSession(self):
        self.commitFunction()
    def processobject(self, data):
        if data:
            self.RFunctionParam_object=data.getData()
            self.commitFunction()
        else: self.RFunctionParam_object = ''
    def commitFunction(self):
        if self.RFunctionParam_object == '': return
        self.R('txt<-capture.output('+'anova.lm(object='+str(self.RFunctionParam_object)+'))')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertPlainText(tmp)
    def getReportText(self, fileDir):
        text = 'ANOVA-LM analysis performted.  The following is a summary of the results:\n\n'
        text += str(self.RoutputWindow.toPlainText())+'\n\n'
        return text
