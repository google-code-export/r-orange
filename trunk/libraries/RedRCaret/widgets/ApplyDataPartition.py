"""
<name>Apply Data Partition (Caret)</name>
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
class ApplyDataPartition(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.require_librarys(["caret"])
        self.setRvariableNames(["includeListData", "includeListClasses", 'excludeListData', 'excludeListClasses'])
        self.data = {}
        self.RFunctionParam_y = ''
        self.RFunctionParam_classes = ''
        self.RFunctionParam_partitionList = ''
        self.inputs.addInput("y", "Input Caret Data", caret.CaretData.CaretData, self.processy)
        self.inputs.addInput('partition', 'Partition List', signals.RList.RList, self.processList)
        self.outputs.addOutput("createDataPartitionOutput1","Partitioned Data Included", caret.CaretData.CaretData)
        self.outputs.addOutput("createDataPartitionOutput2","Partitioned Data Excluded", caret.CaretData.CaretData)

        self.ListElementCombo = redRcomboBox(self.controlArea, label = 'List Element:')
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
            self.RFunctionParam_partitionList = data.getData()
            self.ListElementCombo.update(self.R('names('+self.RFunctionParam_partitionList+')', wantType = 'list'))
            self.commitFunction()
        else:
            self.RFunctionParam_partitionList = ''
    def commitFunction(self):
        if self.RFunctionParam_y == '':
            self.status.setText('No data to work with')
            return
        if self.RFunctionParam_partitionList == '':
            self.status.setText('No list to work with')
            return
            
        ## fairly simple, we just send two classes, one with the in samples and one with the out samples.
        self.R('%s<-%s[%s,]' % (self.Rvariables['includeListData'], self.RFunctionParam_y, self.RFunctionParam_partitionList+'$'+self.ListElementCombo.currentText()))
        self.R('%s<-%s[%s]' % (self.Rvariables['includeListClasses'], self.RFunctionParam_classes, self.RFunctionParam_partitionList+'$'+self.ListElementCombo.currentText()))
        self.R('%s<-%s[-%s,]' % (self.Rvariables['excludeListData'], self.RFunctionParam_y, self.RFunctionParam_partitionList+'$'+self.ListElementCombo.currentText()))
        self.R('%s<-%s[-%s]' % (self.Rvariables['excludeListClasses'], self.RFunctionParam_classes, self.RFunctionParam_partitionList+'$'+self.ListElementCombo.currentText()))
        newDataIncluded = caret.CaretData.CaretData(self, data = self.Rvariables['includeListData'], classes = self.Rvariables['includeListClasses'])
        newDataExcluded = caret.CaretData.CaretData(self, data = self.Rvariables['excludeListData'], classes = self.Rvariables['excludeListClasses'])
        self.rSend('createDataPartitionOutput1', newDataIncluded)
        self.rSend('createDataPartitionOutput2', newDataExcluded)