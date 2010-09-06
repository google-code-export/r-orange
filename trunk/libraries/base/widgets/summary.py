"""
<name>Summary</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>base:summary</RFunctions>
<tags>R</tags>
<icon>RExecutor.png</icon>
<inputWidgets></inputWidgets>
<outputWidgets>base_RDataTable, base_ListSelector, base_DataExplorer</outputWidgets>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RVariable import RVariable as redRRVariable

from libraries.base.qtWidgets.textEdit import textEdit
class summary(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["summary"])
        self.data = {}
         
        self.RFunctionParam_object = ''
        self.inputs.addInput('id0', 'R Variable Object', redRRVariable, self.processobject)

        self.RoutputWindow = textEdit(self.controlArea, label = "RoutputWindow")
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
    def getReportText(self, fileDir):
        text = 'Summary of attached data:\n\n'
        text += str(self.RoutputWindow.toPlainText())+'\n\n'
        return text
