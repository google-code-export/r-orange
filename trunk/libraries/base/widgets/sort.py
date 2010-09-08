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
from libraries.base.qtWidgets.tabWidget import tabWidget
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

        self.standardTab = self.controlArea
        self.RFunctionParamdecreasing_lineEdit =  checkBox(self.standardTab,  buttons = ["Decreasing", 'NA Last'])
        
        self.sortingColumn = comboBox(self.standardTab, label = 'Column to Sort:')
        commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if not self.require_librarys(["base"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data.copy()
            self.sortingColumn.update(self.R('names('+self.RFunctionParam_x+')'))
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if str(self.RFunctionParam_x) == '': return
        injection = []
        if 'Decreasing' in self.RFunctionParamdecreasing_lineEdit.getChecked():
            string = 'decreasing='+str(self.RFunctionParamdecreasing_lineEdit.text())+''
            injection.append(string)
        else:
            injection.append('decreasing = FALSE')
        if 'NA Last' in self.RFunctionParamdecreasing_lineEdit.getChecked():
            injection.append('na.last = TRUE')
        inj = ','.join(injection)
        self.R('s<-order(x='+str(self.RFunctionParam_x)+'$'+str(self.sortingColumn.currentText())+','+inj+')')
        self.R(self.Rvariables['sort']+'<-'+self.RFunctionParam_x+'[s,]')
        newData = redRRDataFrame(data = self.Rvariables["sort"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.dictAttrs = self.data.dictAttrs.copy()  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("id0", newData)
    def getReportText(self, fileDir):
        text = 'Sorted the incomming data in '
        if str(self.RFunctionParamdecreasing_lineEdit.text()) != 'FALSE':
            text += 'increasing'
        else:
            text += 'decreasing'
        text += 'order.\n\n'
        return text
