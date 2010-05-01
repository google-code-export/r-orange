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
        self.setRvariableNames(["t"])
        self.RFunctionParam_x = ''
        self.data={}
        self.loadSettings()
        
        self.inputs = [("x", signals.RDataFrame, self.processx)]
        self.outputs = [("t Output", signals.RDataFrame)]
        
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
        
        newData = signals.RDataFrame(data = self.Rvariables['t'])
        newData.dictAttrs = self.data.dictAttrs.copy()
        self.rSend("t Output", newData)
