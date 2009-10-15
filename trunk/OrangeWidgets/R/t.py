"""
<name>Transpose</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Transposes a data table and sends.</description>
<tags>Data Manipulation</tags>
<icon>icons/RExecutor.png</icon>
<priority>2040</priority>
"""
from OWRpy import * 
import OWGUI 
import RRGUI
class t(OWRpy): 
    settingsList = ['sentItems']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["t"])
        self.RFunctionParam_x = ''
        self.loadSettings()
        self.inputs = [("x", RvarClasses.RDataFrame, self.processx)]
        self.outputs = [("t Output", RvarClasses.RDataFrame)]
        
        box = RRGUI.widgetBox(self.controlArea, None, None, "Widget Box")
        RRGUI.button(box, None, self, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data["data"]
            self.commitFunction()
    def commitFunction(self):
        if self.x == '': return
        self.R(self.Rvariables['t']+'<-as.data.frame(t(x='+str(self.RFunctionParam_x)+'))')
        self.rSend("t Output", {"data":self.Rvariables["t"]})
