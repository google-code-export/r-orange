"""
<name>Apply Data PreProcessing (Caret)</name>
"""
from OWRpy import * 
import redRGUI, signals
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
        self.inputs.addInput('preprocess', 'PreProcessed Model', signals.base.RModelFit, self.processList)
        self.outputs.addOutput("applyPreprocessData","Processed Data", caret.CaretData.CaretData)

        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
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
        