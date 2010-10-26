"""
<name>Dot Chart</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>graphics:dotchart</RFunctions>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RMatrix import RMatrix as redRRMatrix
from libraries.base.signalClasses.RList import RList as redRList
from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.button import button
class dotchart(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["dotchart"])
        self.data = {}
        self.RFunctionParam_x = ''
        self.labels = ''
        self.inputs.addInput('id0', 'Data', redRRMatrix, self.processx)
        self.inputs.addInput('id1', 'Labels', redRList, self.processLabels)
        
        self.standardTab = self.controlArea
        
        self.RFunctionParammain_lineEdit =  lineEdit(self.standardTab,  label = "Main Title:")
        self.RFunctionParamxlab_lineEdit =  lineEdit(self.standardTab,  label = "X Label:")
        self.RFunctionParamylab_lineEdit =  lineEdit(self.standardTab,  label = "Y Label:")
        self.labelNames = comboBox(self.standardTab, label = 'Label Data')
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if not self.require_librarys(["graphics"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def processLabels(self, data):
        if data:
            self.labels = data.getData()
            self.labelNames.update(self.R('names('+self.labels+')'))
            self.commitFunction()
        else:
            self.labels = ''
            self.labelNames.clear()
    def commitFunction(self):
        if str(self.RFunctionParam_x) == '': return
        if not self.R('is.numeric('+str(self.RFunctionParam_x)+')'):
            self.status.setText('Data is not a numberic matrix, please remove text columns and process again')
            return
        injection = []
        if str(self.RFunctionParamxlab_lineEdit.text()) != '':
            string = ',xlab=\"'+str(self.RFunctionParamxlab_lineEdit.text())+'\"'
            injection.append(string)
        if self.labels != '':
            injection.append('labels = '+self.labels + '$' + str(self.labelNames.currentText()))
        if str(self.RFunctionParamylab_lineEdit.text()) != '':
            string = ',ylab=\"'+str(self.RFunctionParamylab_lineEdit.text())+'\"'
            injection.append(string)
        if str(self.RFunctionParammain_lineEdit.text()) != '':
            string = ',main=\"'+str(self.RFunctionParammain_lineEdit.text())+'\"'
            injection.append(string)
        inj = ''.join(injection)
        self.Rplot('dotchart(x='+str(self.RFunctionParam_x)+inj+')')
        
    def getReportText(self, fileDir):
        if str(self.RFunctionParam_x) == '': return 'Nothing to plot from this widget'
        
        self.R('png(file="'+fileDir+'/plot'+str(self.widgetID)+'.png")')
            
        injection = []
        if str(self.RFunctionParamxlab_lineEdit.text()) != '':
            string = 'xlab='+str(self.RFunctionParamxlab_lineEdit.text())+''
            injection.append(string)
        if str(self.labels) != '':
            string = 'labels='+self.labels+ '$' + str(self.labelNames.currentText())
            injection.append(string)
        if str(self.RFunctionParamylab_lineEdit.text()) != '':
            string = 'ylab='+str(self.RFunctionParamylab_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParammain_lineEdit.text()) != '':
            string = 'main='+str(self.RFunctionParammain_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        self.R('dotchart(x='+str(self.RFunctionParam_x)+','+inj+')')
        self.R('dev.off()')
        text = 'The following plot was generated:\n\n'
        #text += '<img src="plot'+str(self.widgetID)+'.png" alt="Red-R R Plot" style="align:center"/></br>'
        text += '.. image:: '+fileDir+'/plot'+str(self.widgetID)+'.png\n    :scale: 50%%\n\n'
            
        return text
