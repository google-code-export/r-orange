"""
<name>Effective Dose</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>drc:ED</RFunctions>
<tags>Dose Response</tags>
<icon>icons/drc.PNG</icon>
"""
from OWRpy import * 
import redRGUI 
class ED(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["ED"])
        self.data = {}
        self.require_librarys(["drc"]) 
        self.loadSettings() 
        self.RFunctionParam_object = ''
        self.inputs = [("object", RvarClasses.RVariable, self.processobject)]
        self.outputs = [("ED Output", RvarClasses.RVariable)]
        
        self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
        self.standardTab = redRGUI.widgetBox(self.controlArea)

        self.RFunctionParamrespLev_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "Response Level:", text = '50', toolTip = 'The response level.  For example for ED50 use 50.\nIf you desire more than one response level separate them by commas ex: 50, 90, 95.')
        self.RFunctionParamci_lineEdit =  redRGUI.comboBox(self.standardTab,  label = "Confidence Function:", items = ['none', 'delt', 'fls', 'tfls'])
        
        self.RFunctionParamlevel_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "Confidence Interval:", text = '0.95', toolTip = 'The confidence interval to use with the Confidence Function.')
        self.RFunctionParamtype_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "type:", text = '')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "RoutputWindow")
    def processobject(self, data):
        
        if data:
            self.RFunctionParam_object=data["data"]
            self.data = data.copy()
            self.commitFunction()
    def commitFunction(self):
        if str(self.RFunctionParam_object) == '': return
        if str(self.RFunctionParamrespLev_lineEdit.text()) == '': return
        injection = []
        if str(self.RFunctionParamrespLev_lineEdit.text()) != '':
            string = 'respLev=c('+str(self.RFunctionParamrespLev_lineEdit.text())+')'
            injection.append(string)
        if str(self.RFunctionParamci_lineEdit.currentText()) != 'none':
            string = 'ci=\''+str(self.RFunctionParamci_lineEdit.currentText())+'\''
            injection.append(string)
        if str(self.RFunctionParamtype_lineEdit.text()) != '':
            string = 'type=\''+str(self.RFunctionParamtype_lineEdit.text())+'\''
            injection.append(string)
        if str(self.RFunctionParamlevel_lineEdit.text()) != '':
            string = 'level='+str(self.RFunctionParamlevel_lineEdit.text())
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['ED']+'<-ED(object='+str(self.RFunctionParam_object)+','+inj+')')
        self.R('txt<-capture.output('+self.Rvariables['ED']+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
        
        newData = self.data.copy()
        newData.data = self.Rvariables["ED"]
        self.rSend("ED Output", newData)
    
