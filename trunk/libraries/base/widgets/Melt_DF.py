"""
<name>Reshape Data</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<tags>Data Manipulation</tags>
<RFunctions>reshape:melf</RFunctions>
<icon>rexecutor.png</icon>
<priority>2060</priority>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses.RDataFrame as rdf
class Melt_DF(OWRpy): 
    settingsList = ['RFunctionParam_data']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["melt.data.frame", "melt.data.frame.cm"])
        self.RFunctionParam_data = ''
        self.data = {}
        self.inputs = [("data", rdf.RDataFrame, self.processdata)]
        self.outputs = [("melt.data.frame Output", rdf.RDataFrame)]
        
        box = redRGUI.widgetBox(self.controlArea, "Widget Box")
        self.RFunctionParam_na_rm = redRGUI.comboBox(box, label = "Remove NA:", items = ['Yes', 'No'])
        self.RFunctionParam_measure_var = redRGUI.listBox(box, label = "Result Variable:", toolTip = 'The column that contains the result or the measurement that the data should be melted around.')
        self.RFunctionParam_measure_var.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.RFunctionParam_id_var = redRGUI.listBox(box, label = "Groupings:", toolTip = 'The columns indicating the groupings of the data.')
        self.RFunctionParam_id_var.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.RFunctionParam_variable_name = redRGUI.lineEdit(box, label = "New Group Name:", toolTip = 'The name of the new column that the groupings will be put into.')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def RWidgetReload(self):
        self.commitFunction()
    def processdata(self, data):
        if data:
            if not self.require_librarys(['reshape']):
                self.status.setText('R Libraries Not Loaded.')
                return
            self.RFunctionParam_data=data.getData()
            self.data = data
            colnames = self.R('colnames('+self.RFunctionParam_data+')')
            self.RFunctionParam_measure_var.update(colnames)
            self.RFunctionParam_id_var.update(colnames)

            self.commitFunction()
    def commitFunction(self):
        if not self.require_librarys(['reshape']):
            self.status.setText('R Libraries Not Loaded.')
            return
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
        self.R('OldRownames<-rownames('+str(self.RFunctionParam_data)+')')
        self.R(self.Rvariables['melt.data.frame']+'<-melt.data.frame(data=cbind('+str(self.RFunctionParam_data)+', OldRownames),na.rm='+str(pna)+mvStr+',variable.name="'+str(self.RFunctionParam_variable_name.text())+'"'+ivStr+')')
        self.R('rm(OldRownames)')
        # copy the signals class and send the newData
        newData = rdf.RDataFrame(data = self.Rvariables['melt.data.frame'])
        newData.dictAttrs = self.data.dictAttrs.copy()
        self.rSend("melt.data.frame Output", newData)
        
    def getReportText(self, fileDir):
        text = 'Reshaped (melted) the data using the following parameters:\n\n'
        text += 'Remove NA: '
        if self.RFunctionParam_na_rm == 0: text += 'TRUE'
        else: text += 'FALSE'
        text += '\n\nVariable Name For Reshaping: %s\n\n' % str(self.RFunctionParam_variable_name.text())
        text += 'ID Variables: '
        for item in ivItem:
            text += str(ivItem.text())+', '
        text += '\n\n'
        return text
        