"""
<name>ks.test</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>stats:ks.test</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 

class RedRks_test(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
            OWRpy.__init__(self, **kwargs)
            self.setRvariableNames(["ks.test"])
            self.data = {}
            self.RFunctionParam_y = ''
            self.RFunctionParam_x = ''
            self.inputs.addInput('id0', 'y', signals.base.RVector, self.processy)
            self.inputs.addInput('id1', 'x', signals.base.RVector, self.processx)

            
            self.RFunctionParamalternative_comboBox = redRGUI.base.comboBox(self.controlArea, label = "alternative:", items = ["two.sided","less","greater"])
            self.RFunctionParamexact_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "exact:", text = 'NULL')
            redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
            self.RoutputWindow = redRGUI.base.textEdit(self.controlArea, label = "RoutputWindow")
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
            if unicode(self.RFunctionParam_y) == '': return
            if unicode(self.RFunctionParam_x) == '': return
            injection = []
            string = 'alternative=\''+unicode(self.RFunctionParamalternative_comboBox.currentText())+'\''
            injection.append(string)
            if unicode(self.RFunctionParamexact_lineEdit.text()) != '':
                    string = 'exact='+unicode(self.RFunctionParamexact_lineEdit.text())+''
                    injection.append(string)
            inj = ','.join(injection)
            self.R(self.Rvariables['ks.test']+'<-ks.test(y='+unicode(self.RFunctionParam_y)+',x='+unicode(self.RFunctionParam_x)+','+inj+')')
            self.R('txt<-capture.output('+self.Rvariables['ks.test']+')')
            self.RoutputWindow.clear()
            tmp = self.R('paste(txt, collapse ="\n")')
            self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
