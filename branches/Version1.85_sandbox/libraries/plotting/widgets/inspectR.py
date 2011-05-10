"""
<name>Inspect Model Fit</name>
<tags>Plotting, Stats</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 

class inspectR(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_mymodel = ''
        self.inputs.addInput('id0', 'mymodel', signals.base.RModelFit, self.processmymodel)

        
        self.RFunctionParamwhich_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "which:", text = 'all')
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
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
