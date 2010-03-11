"""
<name>Transpose</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Transposes a data table and sends.</description>
<tags>Data Manipulation</tags>
<RFunctions>utils:t</RFunctions>
<icon>icons/rexecutor.png</icon>
<priority>2040</priority>
"""
from OWRpy import * 
import OWGUI 
import redRGUI
class t(OWRpy): 
    settingsList = ['sentItems']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["t", 't_cm_'])
        self.RFunctionParam_x = ''
        self.data={}
        self.loadSettings()
        
        self.inputs = [("x", RvarClasses.RDataFrame, self.processx)]
        self.outputs = [("t Output", RvarClasses.RDataFrame)]
        
        #box = redRGUI.widgetBox(self.controlArea, "Widget Box")
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data["data"]
            self.data = data.copy()
            self.commitFunction()
    def commitFunction(self):
        if self.x == '': return
        
        self.R(self.Rvariables['t']+'<-as.data.frame(t(x='+str(self.RFunctionParam_x)+'))')
        self.R(self.Rvariables['t_cm_']+'<-data.frame(row.names = rownames('+self.Rvariables['t']+'))')
        
        self.data['data'] = self.Rvariables['t']
        self.data['cm'] = self.Rvariables['t_cm_']
        self.data['parent'] = self.Rvariables['t']
        self.rSend("t Output", self.data)
