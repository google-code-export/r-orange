"""
<name>cbind</name>
<RFunctions>base:cbind</RFunctions>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame

from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.button import button
class RedRcbind(OWRpy): 
    globalSettingsList = ['sendOnSelect']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["cbind"])
        self.data = {}
        self.RFunctionParam_a = ''
        self.RFunctionParam_b = ''
        self.inputs.addInput('id0', 'a', redRRDataFrame, self.processa)
        self.inputs.addInput('id1', 'b', redRRDataFrame, self.processb)

        self.outputs.addOutput('id0', 'cbind Output', redRRDataFrame)

        
        self.RFunctionParamdeparse_level_lineEdit = lineEdit(self.controlArea, label = "deparse_level:", text = '1')
        
        buttonBox = widgetBox(self.controlArea,orientation='horizontal',alignment=Qt.AlignRight)
        self.sendOnSelect = checkBox(buttonBox,buttons=['Calculate on data Input'], 
        toolTips=['Calculate variance on data input.'])
        redRCommitButton(buttonBox, "Commit", callback = self.commitFunction)
        
        
    def processa(self, data):
        if not self.require_librarys(["base"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_a=data.getData()
            #self.data = data
            if 'Calculate on data Input' in self.sendOnSelect.getChecked():
                self.commitFunction()
                
        else:
            self.RFunctionParam_a=''
    def processb(self, data):
        if not self.require_librarys(["base"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_b=data.getData()
            #self.data = data
            if 'Calculate on data Input' in self.sendOnSelect.getChecked():
                self.commitFunction()
        else:
            self.RFunctionParam_b=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_a) == '': return
        if unicode(self.RFunctionParam_b) == '': return
        injection = []
        if unicode(self.RFunctionParamdeparse_level_lineEdit.text()) != '':
            string = 'deparse.level='+unicode(self.RFunctionParamdeparse_level_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['cbind']+'<-cbind('+unicode(self.RFunctionParam_a)+','+unicode(self.RFunctionParam_b)+','+inj+')', wantType = 'NoConversion')
        newData = redRRDataFrame(data = self.Rvariables["cbind"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("id0", newData)
