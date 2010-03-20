"""
<name>R viewer</name>
<author>Kyle R. Covington</author>
<description>Shows the output of an R variable, equivalent to typing the variable name in the R Executor</description>
<tags>R</tags>
<icon>icons/rexecutor.png</icon>
<priority>10</priority>
"""
from OWRpy import * 
import OWGUI 
import RRGUI 
import redRGUI
class rViewer(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        
        self.RFunctionParam_data = None
        self.loadSettings()
        self.inputs = [("data", RvarClasses.RVariable, self.processdata)]
        self.showAll = redRGUI.checkBox(self.controlArea, buttons = ['Show All'])
        OWGUI.button(self.bottomAreaRight, self, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRGUI.textEdit(self.controlArea)
    
    def processdata(self, data):
        if data:
            self.RFunctionParam_data=data["data"]
            self.commitFunction()

    
    def commitFunction(self):
        if not self.RFunctionParam_data:
            self.RoutputWindow.setHtml('No data connected to show.')
            return
        if self.R('class('+self.RFunctionParam_data+')') in ['data.frame', 'matrix'] and 'Show All' not in self.showAll.getChecked():
            self.R('txt<-capture.output('+self.RFunctionParam_data+'[1:5,])') #only need to see the first 5 rows of the data.
        else:
            self.R('txt<-capture.output('+self.RFunctionParam_data+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.setHtml('<pre>'+tmp+'</pre>')
