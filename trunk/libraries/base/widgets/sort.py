"""
<name>Sort</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>base:sort</RFunctions>
<tags>Data Manipulation</tags>
<icon>RExecutor.png</icon>
"""
from OWRpy import *
import redRGUI 
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame

from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.radioButtons import radioButtons
from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.commitButton import commitButton
class sort(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["sort"])
        self.data = {}
         
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'Data Tabel', redRRDataFrame, self.processx)

        self.outputs.addOutput('id0', 'Sorted Data Table', redRRDataFrame)

        self.standardTab = widgetBox(self.controlArea)
        self.options =  checkBox(self.standardTab,label='Options',
        buttons = ["Decreasing", 'NA Last'], orientation='horizontal')
        # self.standardTab.layout().setAlignment(self.options,Qt.AlignLeft)
        
        self.sortingColumn1 = comboBox(self.standardTab, label = 'First Column to Sort:')
        self.sortingColumn2 = comboBox(self.standardTab, label = 'Second Column to Sort:')
        self.sortingColumn3 = comboBox(self.standardTab, label = 'Third Column to Sort:')
        
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            colNames = self.R('colnames('+self.RFunctionParam_x+')',wantType='list')
            colNames.insert(0,'')
            self.sortingColumn1.update(colNames)
            self.sortingColumn2.update(colNames)
            self.sortingColumn3.update(colNames)
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if str(self.RFunctionParam_x) == '': return
        if self.sortingColumn1.currentText() =='':
            return
        injection = []

        injection.append('%s$%s' % (self.RFunctionParam_x, self.sortingColumn1.currentText()))
        if self.sortingColumn2.currentText() !='':
            injection.append('%s$%s' % (self.RFunctionParam_x, self.sortingColumn2.currentText()))
        if self.sortingColumn3.currentText() !='':
            injection.append('%s$%s' % (self.RFunctionParam_x, self.sortingColumn3.currentText()))
            
            
        if 'Decreasing' in self.options.getChecked():
            string = 'decreasing=TRUE'
            injection.append(string)
        else:
            injection.append('decreasing = FALSE')
        if 'NA Last' in self.options.getChecked():
            injection.append('na.last = TRUE')
        inj = ','.join(injection)

        self.R(self.Rvariables['sort']+'<-%s[order(%s),]' % (self.RFunctionParam_x, inj))
        newData = redRRDataFrame(data = self.Rvariables["sort"]) 
        
        self.rSend("id0", newData)
    def getReportText(self, fileDir):
        text = 'Sorted the incomming data in '
        if str(self.options.text()) != 'FALSE':
            text += 'increasing'
        else:
            text += 'decreasing'
        text += 'order.\n\n'
        return text
