"""
<name>Partition/Resample/Fold (Caret)</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Creates a data partition, a resample of the data or a fold depending on the selections in the function box.  Partition, partitions the data into groups, resample generates a bootstrap resampling of the data and folds generates an evenly split dataset across the number of folds.</description>
<RFunctions>caret:createDataPartition</RFunctions>
<tags>Classification Regression, Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
from libraries.base.qtWidgets.lineEdit import lineEdit as redRlineEdit 
from libraries.base.qtWidgets.radioButtons import radioButtons as redRradioButtons 
from libraries.base.qtWidgets.comboBox import comboBox as redRcomboBox 
from libraries.base.qtWidgets.checkBox import checkBox as redRcheckBox 
from libraries.base.qtWidgets.textEdit import textEdit as redRtextEdit 
import libraries.base.signalClasses as signals
import libraries.RedRCaret.signalClasses as caret
class RedRcreateDataPartition(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.require_librarys(["caret"])
        self.setRvariableNames(["createDataPartition", 'dataOutputList'])
        self.data = {}
        self.RFunctionParam_y = ''
        self.inputs.addInput("y", "Input Caret Data", caret.CaretData.CaretData, self.processy)
        self.outputs.addOutput("createDataPartition Output","Partition/Resample/Fold List", signals.RList.RList)
        
        self.functionCombo = redRcomboBox(self.controlArea, label = 'Function:', items = ['Partition', 'Resample', 'Fold'])
        self.RFunctionParamp_spinBox = redRSpinBox(self.controlArea, label = "Percentage (Partition):", value = 50, min = 1, max = 100)
        #self.RFunctionParamlist_radioButtons = redRradioButtons(self.controlArea, label = "list:", buttons = ["TRUE"], setChecked = "")
        self.RFunctionParamgroups_spinBox = redRSpinBox(self.controlArea, label = "Number of Quantiles (Partition on Numeric Data):", value = 5, min = 1)
        self.RFunctionParamtimes_spinBox = redRSpinBox(self.controlArea, label = "Number of Partitions (Partition and Resample):", value = 1, min = 1, toolTip = 'Typically higher values are set for resampling because one wants to generate several resamples at once.')
        self.RFunctionParam_folds_spinBox = redRSpinBox(self.controlArea, label = "Number of Folds (Folds):", value = 10, min = 1)
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRtextEdit(self.controlArea, label = "R Output Window")
    def processy(self, data):
        
        if data:
            self.RFunctionParam_y=data.getData()
            self.RFunctionParam_classes = data.getClasses()
        else:
            self.RFunctionParam_y=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_classes) == '': 
            self.status.setText('No classes to work with')
            return
        injection = []
        if unicode(self.functionCombo.currentText()) == 'Partition':
            function = 'createDataPartition'
            string = ',p='+unicode(float(self.RFunctionParamp_spinBox.value())/100)+''
            injection.append(string)
            string = ',groups='+unicode(self.RFunctionParamgroups_spinBox.value())+''
            injection.append(string)
            string = ',times='+unicode(self.RFunctionParamtimes_spinBox.value())+''
            injection.append(string)
        elif unicode(self.functionCombo.currentText()) == 'Resample':
            function = 'createResample'
            string = ',times='+unicode(self.RFunctionParamtimes_spinBox.value())+''
            injection.append(string)
        elif unicode(self.functionCombo.currentText()) == 'Fold':
            function = 'createFolds'
            injection.append(', k = '+unicode(self.RFunctionParam_folds_spinBox.value()))
        inj = ''.join(injection)
        self.R(self.Rvariables['createDataPartition']+'<-'+function+'(y='+self.RFunctionParam_classes+inj+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(capture.output('+self.Rvariables['createDataPartition']+'), collapse ="\n")')
        self.RoutputWindow.insertPlainText(tmp)
        newData = signals.RList.RList(self, data = self.Rvariables["createDataPartition"])
        self.rSend("createDataPartition Output", newData)