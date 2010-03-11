"""
<name>intersect</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import redRGUI 
class intersect(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["intersect"])
        self.data = {}
        self.loadSettings() 
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.inputs = [("y", RvarClasses.RVector, self.processy),("x", RvarClasses.RVector, self.processx)]
        self.outputs = [("intersect Output", RvarClasses.RVector)]
        
        self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        redRGUI.button(self.controlArea, "Report", callback = self.sendReport)
        self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "RoutputWindow")
        self.resize(500, 200)
    def processy(self, data):
        if data:
            self.RFunctionParam_y=data["data"]
            self.data = data.copy()
            self.commitFunction()
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data["data"]
            self.data = data.copy()
            self.commitFunction()
    def commitFunction(self):
        if str(self.RFunctionParam_y) == '': return
        if str(self.RFunctionParam_x) == '': return
        self.R(self.Rvariables['intersect']+'<-intersect(y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+')')
        self.R('txt<-capture.output('+self.Rvariables['intersect']+')')
        
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse =" \n")')
        self.RoutputWindow.insertHtml('<br><br><pre>Shared elements between your inputs:\n'+str(tmp)+'</pre>')
        self.data["data"] = self.Rvariables["intersect"]
        self.rSend("intersect Output", self.data)
    def compileReport(self):
        self.reportSettings("Input Settings",[("y", self.RFunctionParam_y)])
        self.reportSettings("Input Settings",[("x", self.RFunctionParam_x)])
        self.reportRaw(self.Rvariables["intersect"])
    def sendReport(self):
        self.compileReport()
        self.showReport()
