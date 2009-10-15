"""
<name>Wilcoxon Test</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Performs one and two sample Wilcoxon tests on vectors of data, the latter is also known as 'Mann-Whitney' test.  This widget accepts 'vectors' which may be created by the Row or Column selectors or the List selector widget.</description>
<tags>NonParametric</tags>
<icon>icons/stats.PNG</icon>
"""
from OWRpy import * 
import OWGUI 
import RRGUI 

class wilcox_test(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["wilcox.test"])
        self.loadSettings() 
        self.RFunctionParam_x = ''
        self.RFunctionParam_y = ''
        self.inputs = [("x", RvarClasses.RVector, self.processx), ('y', RvarClasses.RVector, self.processy)]
        self.outputs = [("wilcox.test Output", RvarClasses.RVariable)]
        
        box = RRGUI.tabWidget(self.controlArea, None, self)
        self.standardTab = RRGUI.createTabPage(box, "standardTab", self, "Standard")
        self.advancedTab = RRGUI.createTabPage(box, "advancedTab", self, "Advanced")
        OWGUI.button(self.controlArea, self, "Commit", callback = self.commitFunction)
        self.RoutputWindow = RRGUI.textEdit("RoutputWindow", self)
        self.controlArea.layout().addWidget(self.RoutputWindow)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data["data"]
            self.commitFunction()
    def processy(self, data):
        if data:
            self.RFunctionParam_y=data["data"]
            self.commitFunction()
    def commitFunction(self):
        if self.RFunctionParam_x == '': return
        injection = []
        if self.RFunctionParam_y != '':
            injection.append(str('y='+str(self.RFunctionParam_y)))
        inj = ','.join(injection)
        self.R('txt<-capture.output('+self.Rvariables['wilcox.test']+'<-wilcox.test(x='+str(self.RFunctionParam_x)+','+inj+'))')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
        self.rSend("wilcox.test Output", {"data":self.Rvariables["wilcox.test"]})
