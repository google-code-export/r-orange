"""
<name>Summary</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>base:summary</RFunctions>
<tags>R</tags>
<icon>RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals
class summary(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Summary", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["summary"])
        self.data = {}
         
        self.RFunctionParam_object = ''
        self.inputs = [("object", signals.RVariable.RVariable, self.processobject)]
        self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "RoutputWindow")
    def processobject(self, data):
        if not self.require_librarys(["base"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_object=data.getData()
            self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_object=''
    def commitFunction(self):
        if str(self.RFunctionParam_object) == '': return
        self.R('txt<-capture.output(summary(object='+str(self.RFunctionParam_object)+'))')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
