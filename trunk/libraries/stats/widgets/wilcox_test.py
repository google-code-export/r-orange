"""
<name>Wilcoxon Test</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Performs one and two sample Wilcoxon tests on vectors of data, the latter is also known as 'Mann-Whitney' test.  This widget accepts 'vectors' which may be created by the Row or Column selectors or the List selector widget.</description>
<tags>Non Parametric</tags>
<icon>stats.png</icon>
<RFunctions>stats:wilcox.test</RFunctions>
"""
from OWRpy import * 
import OWGUI 
import redRGUI
from libraries.base.signalClasses.RVariable import RVariable as redRRVariable
from libraries.base.signalClasses.RVector import RVector as redRRVector

from libraries.base.qtWidgets.textEdit import textEdit
from libraries.base.qtWidgets.button import button
class wilcox_test(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["wilcox.test"])
         
        self.RFunctionParam_x = ''
        self.RFunctionParam_y = ''
        self.inputs.addInput('id0', 'x', redRRVector, self.processx)
        self.inputs.addInput('id1', 'y', redRRVector, self.processy)

        self.outputs.addOutput('id0', 'wilcox.test Output', redRRVariable)

        
        button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = textEdit(self.controlArea)
        
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            self.commitFunction()
    def processy(self, data):
        if data:
            self.RFunctionParam_y=data.getData()
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
    def getReportText(self, fileDir):
        text = 'The wilkox test was performed on the incoming data X and Y.  A summary of the results is listed below:\n\n'
        text += str(self.RoutputWindow.toPlainText())+'\n\n'
        return text
