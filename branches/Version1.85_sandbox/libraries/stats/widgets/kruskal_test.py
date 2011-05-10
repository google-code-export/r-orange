"""
<name>Kruskal</name>
<description>Performs the Kruskal Walis test on data.</description>
<author>Generated using Widget Maker written by Kyle R. Covington</author>

<icon>stats.png</icon>
<tags>Non Parametric</tags>
<RFunctions>stats:kruskal.test</RFunctions>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
class kruskal_test(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
         
        self.RFunctionParam_data = ''
        self.inputs.addInput('id0', 'data', signals.base.RVariable, self.processdata)


        self.RFunctionParamformula =  redRGUI.base.RFormulaEntry(self.controlArea)
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRGUI.base.textEdit(self.controlArea, label = "RoutputWindow")
    def processdata(self, data):
        if not self.require_librarys(["stats"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        self.RoutputWindow.clear()
        self.status.setText('New data recieved')
        if data:
            self.RFunctionParam_data=data.getData()
            self.data = data
            self.RFunctionParamformula.update(self.R('colnames('+self.RFunctionParam_data+')'))
            self.commitFunction()
        else:
            self.RFunctionParam_data = ''
            self.RFunctionParamformula.clear()
    def commitFunction(self):
        if unicode(self.RFunctionParam_data) == '': 
            self.status.setText('No data')
            return
        formulaOutput = self.RFunctionParamformula.Formula()
        if formulaOutput == None or formulaOutput[0] == '' or formulaOutput[1] == '': 
            self.status.setText('Bad formula construction')
            return
        injection = []
        string = formulaOutput[0]+ ' ~ ' + formulaOutput[1]
        injection.append(string)

        inj = ','.join(injection)
        self.R('txt<-capture.output(kruskal.test('+inj+', data='+unicode(self.RFunctionParam_data)+'))')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<pre>'+tmp+'</pre>')
        self.status.setText('Data sent')
