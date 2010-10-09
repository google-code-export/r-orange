"""
<name>Row or Column Binding</name>
<tags>Prototypes</tags>
"""
from OWRpy import * 
from libraries.base.qtWidgets.lineEdit import lineEdit as redRlineEdit 
from libraries.base.qtWidgets.radioButtons import radioButtons as redRradioButtons 
from libraries.base.qtWidgets.comboBox import comboBox as redRcomboBox 
from libraries.base.qtWidgets.checkBox import checkBox as redRcheckBox 
from libraries.base.qtWidgets.textEdit import textEdit as redRtextEdit 
import libraries.base.signalClasses as signals

class RedRrbind(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["rbind"])
        self.data = {}
        self.RFunctionParam_x = ''
        self.inputs.addInput("x", "Data", [signals.RDataFrame.RDataFrame, signals.RVector.RVector], self.processx, multiple = True)
        self.outputs.addOutput("rbind Output","Joined Data", signals.RDataFrame.RDataFrame)
        self.bindingMode = redRRadioButtons(self.controlArea, label = 'Binding Mode:', buttons = ['Row', 'Column'], setChecked = 'Row')
        self.RFunctionParamdeparse_level_lineEdit = redRlineEdit(self.controlArea, label = "Deparse Level:", text = '1')
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processx(self, data, id):
        
        if data:
            self.data[id] = data.getData()
            
            #self.data = data
            self.commitFunction()
        else:
            del self.data[id]
    def commitFunction(self):
        if len(self.data) < 2: return
        injection = []
        if str(self.RFunctionParamdeparse_level_lineEdit.text()) != '':
            string = 'deparse.level='+str(self.RFunctionParamdeparse_level_lineEdit.text())+''
            injection.append(string)
        inj = ''.join(injection)
        if str(self.bindingMode.getChecked()) == 'Row':
            function = 'rbind'
        else:
            function = 'cbind'
        self.R(self.Rvariables['rbind']+'<-'+function+'('+','.join([i for k, i in self.data.items()])+','+inj+')')
        newData = signals.RDataFrame.RDataFrame(data = self.Rvariables["rbind"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("rbind Output", newData)