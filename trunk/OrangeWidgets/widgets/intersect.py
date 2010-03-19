"""
<name>Intersect</name>
<description>Shows data in a spreadsheet.</description>
<tags>Data Manipulation</tags>
<RFunctions>base:intersect</RFunctions>
<icon>icons/datatable.png</icon>
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
        
        self.help.setHtml('<small>Returns the intersection (common elements) between two vectors.  Elements of data tables can be converted to vectors by selecting their column in Row Col Picker or their rownames in Rownames.</small>')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        redRGUI.button(self.bottomAreaLeft, "Report", callback = self.sendReport)
        self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "Intersect Output")
        self.resize(500, 200)
    def processy(self, data):
        if data:
            self.RFunctionParam_y=data["data"]
            self.data = data.copy()
            self.commitFunction()
        else:
            self.RFunctionParam_y = ''
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data["data"]
            self.data = data.copy()
            self.commitFunction()
        else:
            self.RFunctionParam_x = ''
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
