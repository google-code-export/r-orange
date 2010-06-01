"""
<name>Intersect</name>
<description>Shows data in a spreadsheet.</description>
<tags>Data Manipulation</tags>
<RFunctions>base:intersect</RFunctions>
<icon>datatable.png</icon>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import redRGUI 
class intersect(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Intersect", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["intersect"])
        self.data = {}
         
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.inputs = [("y", signals.RVector, self.processy),("x", signals.RVector, self.processx)]
        self.outputs = [("intersect Output", signals.RVector)]
        
        self.help.setHtml('<small>Returns the intersection (common elements) between two vectors.  Elements of data tables can be converted to vectors by selecting their column in Row Col Picker or their rownames in Rownames. Associated data of X will be sent forward and the data of Y will be lost to downstream widgets.</small>')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "Intersect Output")
        self.resize(500, 200)
    def processy(self, data):
        if data:
            self.RFunctionParam_y=data.getData()
            self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_y = ''
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data.copy()
            self.commitFunction()
        else:
            self.RFunctionParam_x = ''
    def commitFunction(self):
        if str(self.RFunctionParam_y) == '': 
            self.status.setText('No Y data exists')
            return
        if str(self.RFunctionParam_x) == '': 
            self.status.setText('No X data exists')
            return
        self.R(self.Rvariables['intersect']+'<-intersect(y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+')')
        self.R('txt<-capture.output('+self.Rvariables['intersect']+')')
        
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse =" \n")')
        self.RoutputWindow.insertHtml('<br><br><pre>Shared elements between your inputs:\n'+str(tmp)+'</pre>')        
        newData = signals.RVector(data = self.Rvariables["intersect"])
        
        self.rSend("intersect Output", newData)

