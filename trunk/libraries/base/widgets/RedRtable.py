"""
<name>Convert To Table/Prop Table</name>
<tags>Data Manipulation</tags>
"""
from OWRpy import * 
from libraries.base.qtWidgets.lineEdit import lineEdit as redRlineEdit 
from libraries.base.qtWidgets.radioButtons import radioButtons as redRradioButtons 
from libraries.base.qtWidgets.comboBox import comboBox as redRcomboBox 
from libraries.base.qtWidgets.checkBox import checkBox as redRcheckBox 
from libraries.base.qtWidgets.textEdit import textEdit as redRtextEdit 
import libraries.base.signalClasses as signals

class RedRtable(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["table", "propTable"])
        self.data = {}
        self.RFunctionParam_data = ''
        self.inputs.addInput("data", "Data Table", signals.RDataFrame.RDataFrame, self.processdata)
        self.outputs.addOutput("table Output","Table Output", signals.RDataFrame.RDataFrame)
        self.outputs.addOutput("propTable", "Prob Table Output", signals.RDataFrame.RDataFrame)
        
        self.commit = redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,processOnInput=True)
        
        self.RoutputWindow = redRtextEdit(self.controlArea, label = "R Output Window")
    def processdata(self, data):
        if data:
            self.RFunctionParam_data=data.getData()
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_data=''
    def commitFunction(self):
        if str(self.RFunctionParam_data) == '': return
        self.R(self.Rvariables['table']+'<-table(data='+str(self.RFunctionParam_data)+')', wantType = 'NoConversion')
        self.R('txt<-capture.output('+self.Rvariables['table']+')', wantType = 'NoConversion')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.R(self.Rvariables['propTable']+'<-prop.table('+self.Rvariables['table']+')', wantType = 'NoConversion')
        self.R('txt<-capture.output('+self.Rvariables['propTable']+')', wantType = 'NoConversion')
        tmp2 = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertPlainText(tmp+'\n\n'+tmp2)
        newData = signals.RDataFrame.RDataFrame(data = 'as.data.frame('+self.Rvariables["table"]+')', parent = 'as.data.frame('+self.Rvariables["table"]+')') # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("table Output", newData)
        newDataProp = signals.RDataFrame.RDataFrame(data = 'as.data.frame('+self.Rvariables['propTable']+')', parent = 'as.data.frame('+self.Rvariables['propTable']+')')
        self.rSend('propTable', newDataProp)