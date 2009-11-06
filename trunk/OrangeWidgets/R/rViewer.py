"""
<name>R viewer</name>
<author>Kyle R. Covington</author>
<description>Shows the output of an R variable, equivalent to typing the variable name in the R Executor</description>
<tags>R, Data Manipulation</tags>
<icon>icons/RExecutor.PNG</icon>
<priority>10</priority>
"""
from OWRpy import * 
import OWGUI 
import RRGUI 
class rViewer(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        
        self.loadSettings()
        self.inputs = [("data", RvarClasses.RVariable, self.processdata)]
        
        OWGUI.button(self.controlArea, self, "Commit", callback = self.commitFunction)
        self.RoutputWindow = RRGUI.textEdit("RoutputWindow", self)
        self.controlArea.layout().addWidget(self.RoutputWindow)
    
    def processdata(self, data):
        if data:
            self.RFunctionParam_data=data["data"]
            self.commitFunction()

    
    def commitFunction(self):
        self.R('txt<-capture.output('+self.RFunctionParam_data+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
