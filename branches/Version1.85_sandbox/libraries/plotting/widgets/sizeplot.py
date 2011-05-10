"""
<name>Size Plot</name>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 

class sizeplot(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'y', signals.base.RVector, self.processy)
        self.inputs.addInput('id1', 'x', signals.base.RVector, self.processx)

        
        self.standardTab = self.controlArea
        self.RFunctionParamy_lineEdit =  redRGUI.base.lineEdit(self.standardTab,  label = "y:", text = '')
        self.RFunctionParamx_lineEdit =  redRGUI.base.lineEdit(self.standardTab,  label = "x:", text = '')
        self.RFunctionParamscale_lineEdit =  redRGUI.base.lineEdit(self.standardTab,  label = "scale:", text = '1')
        self.RFunctionParamsize_lineEdit =  redRGUI.base.lineEdit(self.standardTab,  label = "size:", text = 'c(1,4)')
        self.RFunctionParampow_lineEdit =  redRGUI.base.lineEdit(self.standardTab,  label = "pow:", text = '0.5')
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
    def processy(self, data):
        if not self.require_librarys(["plotrix"]):
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
        if not self.require_librarys(["plotrix"]):
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
        if unicode(self.RFunctionParamy_lineEdit.text()) != '':
            string = 'y='+unicode(self.RFunctionParamy_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamx_lineEdit.text()) != '':
            string = 'x='+unicode(self.RFunctionParamx_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamscale_lineEdit.text()) != '':
            string = 'scale='+unicode(self.RFunctionParamscale_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamsize_lineEdit.text()) != '':
            string = 'size='+unicode(self.RFunctionParamsize_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParampow_lineEdit.text()) != '':
            string = 'pow='+unicode(self.RFunctionParampow_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        self.Rplot('sizeplot(y='+unicode(self.RFunctionParam_y)+',x='+unicode(self.RFunctionParam_x)+','+inj+')')
        