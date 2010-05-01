"""
<name>ANOVA-LM</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Performs ANOVA on a linear model, usually made using the LM widget.  Returns an output of the ANOV comparison.</description>
<tags>Parametric, Stats</tags>
<icon>icons/stats.png</icon>
<RFunctions>stats:anova, stats:lm, stats:anova.lm</RFunctions>
"""
from OWRpy import * 
import OWGUI 
import redRGUI
class anova_lm(OWRpy): 
    settingsList = ['RFunctionParam_object']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.RFunctionParam_object = ''
        self.loadSettings()
        self.inputs = [("object", signals.RVariable, self.processobject)]
        
        box = redRGUI.groupBox(self.controlArea, "Output")
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRGUI.textEdit(box)
        #box.layout().addWidget(self.RoutputWindow)
    def onLoadSavedSession(self):
        self.commitFunction()
    def processobject(self, data):
        if data:
            self.RFunctionParam_object=data["data"]
            self.commitFunction()
        else: self.RFunctionParam_object = ''
    def commitFunction(self):
        if self.RFunctionParam_object == '': return
        self.R('txt<-capture.output('+'anova.lm(object='+str(self.RFunctionParam_object)+'))')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
