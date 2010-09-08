"""
<name>Intersect</name>
<description>Use the Set Operations widget.</description>
<tags>Deprecated</tags>
<RFunctions>base:intersect</RFunctions>
<icon>datatable.png</icon>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.qtWidgets.textEdit import textEdit
from libraries.base.qtWidgets.button import button
class intersect(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["intersect"])
        self.data = {}
         
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'y', redRRVector, self.processy)
        self.inputs.addInput('id1', 'x', redRRVector, self.processx)

        self.outputs.addOutput('id0', 'intersect Output', redRRVector)

        
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = textEdit(self.controlArea, label = "Intersect Output")
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
        newData = redRRVector(data = self.Rvariables["intersect"])
        
        self.rSend("id0", newData)
    def getReportText(self, fileDir):
        return 'Sends the intersecting element, those that are the same, in the two incomming data vectors.\n\n'

