"""
<name>Reshape Data</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<tags>Data Manipulation</tags>
<RFunctions>reshape:melf</RFunctions>
<icon>icons/rexecutor.png</icon>
<priority>2060</priority>
"""
from OWRpy import * 
import redRGUI 
class Melt_DF(OWRpy): 
    settingsList = ['RFunctionParam_data']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["melt.data.frame", "melt.data.frame.cm"])
        self.RFunctionParam_data = ''
        self.data = {}
        self.require_librarys(['reshape'])
        self.loadSettings()
        self.inputs = [("data", RvarClasses.RDataFrame, self.processdata)]
        self.outputs = [("melt.data.frame Output", RvarClasses.RDataFrame)]
        
        box = redRGUI.widgetBox(self.controlArea, "Widget Box")
        self.RFunctionParam_na_rm = redRGUI.comboBox(box, label = "Remove NA:", items = ['Yes', 'No'])
        self.RFunctionParam_measure_var = redRGUI.listBox(box, label = "Result Variable:", toolTip = 'The column that contains the result or the measurement that the data should be melted around.')
        self.RFunctionParam_measure_var.setSelectionMode(QAbstractItemView.MultiSelection)
        self.RFunctionParam_id_var = redRGUI.listBox(box, label = "Groupings:", toolTip = 'The columns indicating the groupings of the data.')
        self.RFunctionParam_id_var.setSelectionMode(QAbstractItemView.MultiSelection)
        self.RFunctionParam_variable_name = redRGUI.lineEdit(box, label = "New Group Name:", toolTip = 'The name of the new column that the groupings will be put into.')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def RWidgetReload(self):
        self.commitFunction()
    def processdata(self, data):
        if data:
            
            self.RFunctionParam_data=data["data"]
            self.data = data.copy()
            colnames = self.R('colnames('+self.RFunctionParam_data+')')
            self.RFunctionParam_measure_var.update(colnames)
            self.RFunctionParam_id_var.update(colnames)

            self.commitFunction()
    def commitFunction(self):
        if self.RFunctionParam_na_rm == 0: pna = 'TRUE'
        else: pna = 'FALSE'
        if self.RFunctionParam_data == '': return
        mvItem = self.RFunctionParam_measure_var.selectedItems()
        try:
            mvStr = []
            for item in mvItem:
                mvStr.append(str(item.text()))
            mvStr = ', measure.var = c(\''+'\',\''.join(mvStr)+'\')'
            if mvStr == ', measure.var = c(\'\')':
                mvStr = ''
        except:
            mvStr = ''
        ivItem = self.RFunctionParam_id_var.selectedItems()
        try:
            ivStr = []
            for item in ivItem:
                ivStr.append(str(ivItem.text()))
            ivStr = ', id.var = c(\''+'\',\''.join(ivStr)+'\')'
            if ivStr == ', id.var = c(\'\')': ivStr = ''
        except:
            ivStr = ''
            
        self.R(self.Rvariables['melt.data.frame']+'<-melt.data.frame(data='+str(self.RFunctionParam_data)+',na.rm='+str(pna)+mvStr+',variable.name="'+str(self.RFunctionParam_variable_name.text())+'"'+ivStr+')')
        # copy the RvarClasses class and send the newData
        newData = self.data.copy()
        newData.data = self.Rvariables["melt.data.frame"]
        self.makeCM(self.Rvariables['melt.data.frame.cm'], self.Rvariables['melt.data.frame'])
        newData.cm = self.Rvariables['melt.data.frame.cm']
        newData.parent = self.Rvariables['melt.data.frame']
        self.rSend("melt.data.frame Output", newData)
