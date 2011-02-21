"""
<name>Inspect Model Fit</name>
<tags>Plotting, Stats</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RModelFit import RModelFit as redRRModelFit
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.tabWidget import tabWidget
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.commitButton import commitButton as redRCommitButton

class inspectR(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.RFunctionParam_mymodel = ''
        self.inputs.addInput('id0', 'mymodel', redRRModelFit, self.processmymodel)

        
        self.RFunctionParamwhich_lineEdit =  lineEdit(self.controlArea,  label = "which:", text = 'all')
        self.commit = redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
    def processmymodel(self, data):
        if not self.require_librarys(["asuR"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_mymodel=data.getData()
            #self.data = data
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_mymodel=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_mymodel) == '': return
        injection = []
        if unicode(self.RFunctionParamwhich_lineEdit.text()) != '':
            string = 'which=\''+unicode(self.RFunctionParamwhich_lineEdit.text())+'\''
            injection.append(string)
        inj = ','.join(injection)
        self.R('inspect(mymodel='+unicode(self.RFunctionParam_mymodel)+')')
