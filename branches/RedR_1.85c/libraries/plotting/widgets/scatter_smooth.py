"""
<name>scatter.smooth</name>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 

class scatter_smooth(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'y', signals.base.RVector, self.processy)
        self.inputs.addInput('id1', 'x', signals.base.RVector, self.processx)

        
        self.RFunctionParamxlab_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "xlab:", text = 'NULL')
        self.RFunctionParamspan_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "span:", text = '2/3')
        self.RFunctionParamdegree_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "degree:", text = '1')
        self.RFunctionParamfamily_comboBox =  redRGUI.base.comboBox(self.controlArea,  label = "family:", 
        items = ['symmetric', 'gaussian'])
        self.RFunctionParamylab_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "ylab:", text = 'NULL')
        self.RFunctionParamevaluation_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "evaluation:", text = '50')
        self.RFunctionParamylim_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "ylim:", text = '')
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
    
    def processy(self, data):
        if not self.require_librarys(["stats"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_y=data.getData()
            #self.data = data
            if self.commit.processOnInput():
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
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_y) == '': return
        if unicode(self.RFunctionParam_x) == '': return
        injection = []
        if unicode(self.RFunctionParamxlab_lineEdit.text()) != '':
            string = 'xlab='+unicode(self.RFunctionParamxlab_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamspan_lineEdit.text()) != '':
            string = 'span='+unicode(self.RFunctionParamspan_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamdegree_lineEdit.text()) != '':
            string = 'degree='+unicode(self.RFunctionParamdegree_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamfamily_comboBox.currentText()) != '':
            string = 'family=\''+unicode(self.RFunctionParamfamily_comboBox.currentText())+'\''
            injection.append(string)
        if unicode(self.RFunctionParamylab_lineEdit.text()) != '':
            string = 'ylab='+unicode(self.RFunctionParamylab_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamevaluation_lineEdit.text()) != '':
            string = 'evaluation='+unicode(self.RFunctionParamevaluation_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamylim_lineEdit.text()) != '':
            string = 'ylim='+unicode(self.RFunctionParamylim_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        self.Rplot('scatter.smooth(y='+unicode(self.RFunctionParam_y)+',x='+unicode(self.RFunctionParam_x)+','+inj+')')
    