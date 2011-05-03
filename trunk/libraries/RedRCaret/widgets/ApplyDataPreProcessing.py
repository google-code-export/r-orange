"""
<name>Apply Data PreProcessing (Caret)</name>
"""
from OWRpy import * 
from libraries.base.qtWidgets.lineEdit import lineEdit as redRlineEdit 
from libraries.base.qtWidgets.radioButtons import radioButtons as redRradioButtons 
from libraries.base.qtWidgets.comboBox import comboBox as redRcomboBox 
from libraries.base.qtWidgets.checkBox import checkBox as redRcheckBox 
from libraries.base.qtWidgets.textEdit import textEdit as redRtextEdit 
import libraries.base.signalClasses as signals
import libraries.RedRCaret.signalClasses as caret
class ApplyDataPreProcessing(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.require_librarys(["caret"])
        self.setRvariableNames(['processedData'])
        self.data = {}
        self.RFunctionParam_y = ''
        self.RFunctionParam_classes = ''
        self.RFunctionParam_preprocessModel = ''
        self.inputs.addInput("y", "Input Caret Data", caret.CaretData.CaretData, self.processy)
        self.inputs.addInput('preprocess', 'PreProcessed Model', signals.RModelFit.RModelFit, self.processList)
        self.outputs.addOutput("applyPreprocessData","Processed Data", caret.CaretData.CaretData)

        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processy(self, data):
        
        if data:
            self.RFunctionParam_y=data.getData()
            self.RFunctionParam_classes = data.getClasses()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_y=''
    def processList(self, data):
        ## takes a data list of partitions, we split into in list and not in list
        if data:
            self.RFunctionParam_preprocessModel = data.getData()
            self.commitFunction()
        else:
            self.RFunctionParam_preprocessModel = ''
    def commitFunction(self):
        if self.RFunctionParam_y == '':
            self.status.setText('No data to work with')
            return
        if self.RFunctionParam_preprocessModel == '':
            self.status.setText('No model to work with')
            return
            
        self.R('%s<-predict(%s, %s)' % (self.Rvariables['processedData'], self.RFunctionParam_preprocessModel, self.RFunctionParam_y), wantType = 'NoConversion')
        
        newData = caret.CaretData.CaretData(self, data = self.Rvariables['processedData'], classes = self.RFunctionParam_classes)
        
        self.rSend('applyPreprocessData', newData)
        