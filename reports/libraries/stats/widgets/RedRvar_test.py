"""
<name>F Test</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Perform the F test on two vectors</description>
<RFunctions>stats:var.test</RFunctions>
<tags>Stats</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RVector import RVector as redRRVector

from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.textEdit import textEdit
class RedRvar_test(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["var.test"])
        self.data = {}
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'y', redRRVector, self.processy)
        self.inputs.addInput('id1', 'x', redRRVector, self.processx)

        
        self.RFunctionParamalternative_comboBox = comboBox(self.controlArea, label = "alternative:", items = ["two.sided","less","greater"])
        self.RFunctionParamratio_lineEdit = lineEdit(self.controlArea, label = "ratio:", text = '1')
        self.RFunctionParamconf_level_lineEdit = lineEdit(self.controlArea, label = 'Confidence Interval:', text = '0.95')
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = textEdit(self.controlArea, label = "RoutputWindow")
    def processy(self, data):
        if not self.require_librarys(["stats"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_y=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_y=''
    def processx(self, data):
        if not self.require_librarys(["stats"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if str(self.RFunctionParam_y) == '': return
        if str(self.RFunctionParam_x) == '': return
        injection = []
        string = 'alternative='+str(self.RFunctionParamalternative_comboBox.currentText())+''
        injection.append(string)
        if str(self.RFunctionParamratio_lineEdit.text()) != '':
            string = 'ratio='+str(self.RFunctionParamratio_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamconf_level_lineEdit.text()) != '':
            try:
                float(self.RFunctionParamconf_level_lineEdit.text())
                string = 'conf.level = '+str(self.RFunctionParamconf_level_lineEdit.text())
                injection.append(string)
            except:
                self.status.setText('Confidence Interval not a number')
        inj = ','.join(injection)
        self.R(self.Rvariables['var.test']+'<-var.test(y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+','+inj+')')
        self.R('txt<-capture.output('+self.Rvariables['var.test']+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
