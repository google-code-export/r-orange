"""Apply Data Partition

Used in conjunction with the Partition widget, this widget subsets caret data based on an established parition into two groups; in the partition and not in the partition.

.. helpdoc::

Used in conjunction with the Partition widget, this widget subsets caret data based on an established parition into two groups; in the partition and not in the partition.
"""


"""
<widgetXML>
<name>Apply Data Partition</name>
    <icon>default.png</icon>
    <tags>
        <tag priority='30'>Caret</tag>
    </tags>
    <summary>Used in conjunction with the Partition widget, this widget subsets caret data based on an established parition into two groups; in the partition and not in the partition.</summary>
    <author>
            <authorname>Red-R Core Development Team</authorname>
            <authorcontact>www.red-r.org</authorcontact>
        </author>
    </widgetXML>
"""
from OWRpy import * 
import redRGUI, signals
import libraries.RedRCaret.signalClasses as caret
class ApplyDataPartition(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.require_librarys(["caret"])
        
        """.. rrvnames::"""
        self.setRvariableNames(["includeListData", "includeListClasses", 'excludeListData', 'excludeListClasses'])
        self.data = {}
        self.RFunctionParam_y = ''
        self.RFunctionParam_classes = ''
        self.RFunctionParam_partitionList = ''
        
        """.. rrsignals::
            :description: `A Caret Data Container`
        """
        self.inputs.addInput("y", "Input Caret Data", caret.CaretData.CaretData, self.processy)
        
        """.. rrsignals::
            :description: `Partition list`
        """
        self.inputs.addInput('partition', 'Partition List', signals.base.RList, self.processList)
        
        """.. rrsignals::
            :description: `Partitioned data included in the model`
        """
        self.outputs.addOutput("createDataPartitionOutput1","Partitioned Data Included", caret.CaretData.CaretData)
        
        """.. rrsignals::
            :description: `Partitioned data excluded from the model`
        """
        self.outputs.addOutput("createDataPartitionOutput2","Partitioned Data Excluded", caret.CaretData.CaretData)

        """.. rrgui::"""
        self.ListElementCombo = redRGUI.base.comboBox(self.controlArea, label = 'List Element:')
        
        """.. rrgui::"""
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