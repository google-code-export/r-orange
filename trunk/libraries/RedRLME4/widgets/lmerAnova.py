### lmer anova, just like anova, actually runs the anova command, but comparing two lmer fits.

"""
<name>LMER Anova</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>stats:anova</RFunctions>
<tags>Parametric</tags>
<icon>stats.png</icon>
"""
from OWRpy import * 
import redRGUI 
class lmerAnova(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "LMER Anova", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["anova"])
        self.data = None
        self.data2 = None
        self.RFunctionParam_model = ''
        self.RFunctionParam_data = ''
        self.RFunctionParam_data2 = ''
        self.inputs = [("data", signals.RedRLME4.RLme4ModelFit, self.processdata), ("data2", signals.RedRLME4.RLme4ModelFit, self.processdata2)]
        
        self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "RoutputWindow")

    def processdata(self, data):
         
        if data:
            self.RFunctionParam_data=data.getData()
            self.data = data
            #self.data = data.copy()
            self.commitFunction()
        else:
            self.RFunctionParam_data=''

    def processdata2(self, data):
         
        if data:
            self.RFunctionParam_data2=data.getData()
            self.data2 = data
            #self.data = data.copy()
            self.commitFunction()
        else:
            self.data2 = None
            self.RFunctionParam_data2=''
    def commitFunction(self):
        if str(self.RFunctionParam_data) == '': 
            self.status.setText('No data')
            return
        if str(self.RFunctionParam_data2) == '': 
            self.status.setText('No data')
            return
        if self.data2 and self.data.getDataParent() != self.data2.getDataParent():
            self.status.setText('Data not of the same parent, incompatable models')
            return
        if self.data2:
            self.R(self.Rvariables['anova']+'<-anova('+str(self.RFunctionParam_data)+','+str(self.RFunctionParam_data2)+')')
        else:
            self.R(self.Rvariables['anova']+'<-anova('+str(self.RFunctionParam_data)+')')
        self.R('txt<-capture.output('+self.Rvariables['anova']+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertPlainText(tmp)
        
