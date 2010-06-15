"""
<name>Summary</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>base:summary</RFunctions>
<tags>R</tags>
<icon>RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class summary(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Summary", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["summary"])
        self.data = {}
         
        self.RFunctionParam_object = ''
        self.inputs = [("object", signals.RVariable, self.processobject)]
        
        self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
        box = redRGUI.tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        
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
        injection = []
        inj = ','.join(injection)
        self.R(self.Rvariables['summary']+'<-summary(object='+str(self.RFunctionParam_object)+','+inj+')')
        self.R('txt<-capture.output('+self.Rvariables['summary']+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
