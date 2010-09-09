"""
<name>scatter.smooth</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>stats:scatter.smooth</RFunctions>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.tabWidget import tabWidget
from libraries.base.qtWidgets.button import button
class scatter_smooth(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'y', redRRVector, self.processy)
        self.inputs.addInput('id1', 'x', redRRVector, self.processx)

        
        box = tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.RFunctionParamxlab_lineEdit =  lineEdit(self.standardTab,  label = "xlab:", text = 'NULL')
        self.RFunctionParamspan_lineEdit =  lineEdit(self.standardTab,  label = "span:", text = '2/3')
        self.RFunctionParamdegree_lineEdit =  lineEdit(self.standardTab,  label = "degree:", text = '1')
        self.RFunctionParamfamily_comboBox =  comboBox(self.standardTab,  label = "family:", items = ['symmetric', 'gaussian'])
        self.RFunctionParamylab_lineEdit =  lineEdit(self.standardTab,  label = "ylab:", text = 'NULL')
        self.RFunctionParamevaluation_lineEdit =  lineEdit(self.standardTab,  label = "evaluation:", text = '50')
        self.RFunctionParamylim_lineEdit =  lineEdit(self.standardTab,  label = "ylim:", text = '')
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processy(self, data):
        if not self.require_librarys(["stats"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_y=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_y=''
    def processx(self, data):
        if not self.require_librarys(["stats"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if str(self.RFunctionParam_y) == '': return
        if str(self.RFunctionParam_x) == '': return
        injection = []
        if str(self.RFunctionParamxlab_lineEdit.text()) != '':
            string = 'xlab='+str(self.RFunctionParamxlab_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamspan_lineEdit.text()) != '':
            string = 'span='+str(self.RFunctionParamspan_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamdegree_lineEdit.text()) != '':
            string = 'degree='+str(self.RFunctionParamdegree_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamfamily_comboBox.currentText()) != '':
            string = 'family=\''+str(self.RFunctionParamfamily_comboBox.currentText())+'\''
            injection.append(string)
        if str(self.RFunctionParamylab_lineEdit.text()) != '':
            string = 'ylab='+str(self.RFunctionParamylab_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamevaluation_lineEdit.text()) != '':
            string = 'evaluation='+str(self.RFunctionParamevaluation_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamylim_lineEdit.text()) != '':
            string = 'ylim='+str(self.RFunctionParamylim_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        self.Rplot('scatter.smooth(y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+','+inj+')')
    def getReportText(self, fileDir):
        if str(self.RFunctionParam_y) == '': return 'Nothing to plot from this widget'
        if str(self.RFunctionParam_x) == '': return 'Nothing to plot from this widget'
        
        self.R('png(file="'+fileDir+'/plot'+str(self.widgetID)+'.png")')
            
        injection = []
        if str(self.RFunctionParamxlab_lineEdit.text()) != '':
            string = 'xlab='+str(self.RFunctionParamxlab_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamspan_lineEdit.text()) != '':
            string = 'span='+str(self.RFunctionParamspan_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamdegree_lineEdit.text()) != '':
            string = 'degree='+str(self.RFunctionParamdegree_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamfamily_comboBox.currentText()) != '':
            string = 'family=\''+str(self.RFunctionParamfamily_comboBox.currentText())+'\''
            injection.append(string)
        if str(self.RFunctionParamylab_lineEdit.text()) != '':
            string = 'ylab='+str(self.RFunctionParamylab_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamevaluation_lineEdit.text()) != '':
            string = 'evaluation='+str(self.RFunctionParamevaluation_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamylim_lineEdit.text()) != '':
            string = 'ylim='+str(self.RFunctionParamylim_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        self.R('scatter.smooth(y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+','+inj+')')
        self.R('dev.off()')
        text = 'The following plot was generated:\n\n'
        #text += '<img src="plot'+str(self.widgetID)+'.png" alt="Red-R R Plot" style="align:center"/></br>'
        text += '.. image:: '+fileDir+'/plot'+str(self.widgetID)+'.png\n    :scale: 50%%\n\n'
            
        return text
