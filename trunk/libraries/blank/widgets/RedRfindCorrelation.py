"""
<name>findCorrelation</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>caret:findCorrelation</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
from libraries.base.qtWidgets.lineEdit import lineEdit as redRlineEdit 
from libraries.base.qtWidgets.radioButtons import radioButtons as redRradioButtons 
from libraries.base.qtWidgets.comboBox import comboBox as redRcomboBox 
from libraries.base.qtWidgets.checkBox import checkBox as redRcheckBox 
from libraries.base.qtWidgets.textEdit import textEdit as redRtextEdit 
import libraries.base.signalClasses as signals

class RedRfindCorrelation(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.require_librarys(["caret"])
        self.setRvariableNames(["findCorrelation"])
        self.data = {}
        self.RFunctionParam_x = ''
        self.RFunctionParam_data = ''
        self.inputs.addInput("x", "Correlation Matrix", signals.RMatrix.RMatrix, self.processx)
        self.inputs.addInput("data", "Data Table / Sample List", [signals.RDataFrame.RDataFrame, signals.RList.RList], self.processdata)
        self.outputs.addOutput("findCorrelation Output","Reduced Data Table", signals.RDataFrame.RDataFrame)
        self.outputs.addOutput("findCorrelation Output List", "Reduced Data List", signals.RList.RList)
        
        self.RFunctionParamcutoff_spinBox = redRSpinBox(self.controlArea, label = "Max Correlation Coef (/100):", min = 1, max = 99, value = 90)
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRtextEdit(self.controlArea, label = "R Output Window")
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def processdata(self, data):
        if data:
            self.RFunctionParam_data=data.getData()
            self.dataClass = self.R('class('+self.RFunctionParam_data+')')
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_data=''
    def commitFunction(self):
        if str(self.RFunctionParam_x) == '': return
        if str(self.RFunctionParam_data) == '': return
        injection = []
        #if str(self.RFunctionParamcutoff_spinBox.value()) != '':
        string = ',cutoff='+str(float(self.RFunctionParamcutoff_spinBox.value())/100)+''
        injection.append(string)
        inj = ''.join(injection)
        self.R(self.Rvariables['findCorrelation']+'<-findCorrelation(x='+str(self.RFunctionParam_x)+inj+')')
        if self.dataClass == 'list':
            ## need to remove the findCorrelation from all of the class objects
            self.R(self.Rvariables['findCorrelationOutput']+'<-list()')
            for i in range(self.R('length('+self.RFunctionParam_data+')')):
                self.R(self.Rvariables['findCorrelationOutput']+'[['+str(i+1)+']]<-'+self.RFunctionParam_data+'[['+str(i + 1)+']][, -'+self.Rvariables['findCorrelation']+']')
            newData = signals.RList.RList(data = self.Rvariables['findCorrelationOutput'])
            self.rSend("findCorrelation Output List", newData)
            self.rSend("findCorrelation Output", None)
        if self.dataClass == 'data.frame':
            self.R(self.Rvariables['findCorrelationOutput']+'<-'+self.RFunctionParam_data+'[, -'+self.Rvariables['findCorrelation']+']')
            newData = signals.RDataFrame.RDataFrame(data = self.Rvariables['findCorrelationOutput'], parent = self.Rvariables['findCorrelationOutput'])
            self.rSend("findCorrelation Output", newData)
            self.rSend("findCorrelation Output List", None)
        self.RoutputWindow.clear()
        self.RoutputWindow.insertPlainText('Removed %s samples from the data.' % self.R('length('+self.Rvariables['findCorrelation']+')'))