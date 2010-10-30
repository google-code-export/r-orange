"""
<name>Inspect Model Fit</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>asuR:inspect</RFunctions>
<tags>Plotting, Stats</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RModelFit import RModelFit as redRRModelFit
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.tabWidget import tabWidget
from libraries.base.qtWidgets.button import button
class inspectR(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.RFunctionParam_mymodel = ''
        self.inputs.addInput('id0', 'mymodel', redRRModelFit, self.processmymodel)

        
        box = tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.RFunctionParamwhich_lineEdit =  lineEdit(self.standardTab,  label = "which:", text = 'all')
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processmymodel(self, data):
        if not self.require_librarys(["asuR"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_mymodel=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_mymodel=''
    def commitFunction(self):
        if str(self.RFunctionParam_mymodel) == '': return
        injection = []
        if str(self.RFunctionParamwhich_lineEdit.text()) != '':
            string = 'which=\''+str(self.RFunctionParamwhich_lineEdit.text())+'\''
            injection.append(string)
        inj = ','.join(injection)
        self.R('inspect(mymodel='+str(self.RFunctionParam_mymodel)+')', wantType = 'NoConversion')
        
   