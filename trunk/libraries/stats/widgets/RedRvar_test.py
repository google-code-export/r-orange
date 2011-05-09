"""
<name>F Test</name>
<RFunctions>stats:var.test</RFunctions>
<tags>Stats</tags>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 


class RedRvar_test(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["var.test"])
        self.data = {}
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'y', signals.base.RVector, self.processy)
        self.inputs.addInput('id1', 'x', signals.base.RVector, self.processx)

        
        self.RFunctionParamalternative_comboBox = redRGUI.base.comboBox(self.controlArea, label = "alternative:", items = ["two.sided","less","greater"])
        self.RFunctionParamratio_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "ratio:", text = '1')
        self.RFunctionParamconf_level_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = 'Confidence Interval:', text = '0.95')
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
        self.RoutputWindow = redRGUI.base.textEdit(self.controlArea, label = "RoutputWindow")
    def processy(self, data):
        if not self.require_librarys(["stats"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_y=data.getData()
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_y=''
    def processx(self, data):
        if not self.require_librarys(["stats"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_x=data.getData()
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_y) == '': return
        if unicode(self.RFunctionParam_x) == '': return
        injection = []
        string = 'alternative='+unicode(self.RFunctionParamalternative_comboBox.currentText())+''
        injection.append(string)
        if unicode(self.RFunctionParamratio_lineEdit.text()) != '':
            string = 'ratio='+unicode(self.RFunctionParamratio_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamconf_level_lineEdit.text()) != '':
            try:
                float(self.RFunctionParamconf_level_lineEdit.text())
                string = 'conf.level = '+unicode(self.RFunctionParamconf_level_lineEdit.text())
                injection.append(string)
            except:
                self.status.setText('Confidence Interval not a number')
        inj = ','.join(injection)
        self.R(self.Rvariables['var.test']+'<-var.test(y='+unicode(self.RFunctionParam_y)+',x='+unicode(self.RFunctionParam_x)+','+inj+')')
        self.R('txt<-capture.output('+self.Rvariables['var.test']+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
