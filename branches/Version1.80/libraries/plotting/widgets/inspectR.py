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
        self.R('inspect(mymodel='+str(self.RFunctionParam_mymodel)+')')
        
    def getReportText(self, fileDir):
        ## print the plot to the fileDir and then send a text for an image of the plot
        if str(self.RFunctionParam_mymodel) == '': return 'Nothing to plot from this widget.\n\n'
        self.R('png(file="'+fileDir+'/plot'+str(self.widgetID)+'.png")')
        injection = []
        if str(self.RFunctionParamwhich_lineEdit.text()) != '':
            string = 'which=\''+str(self.RFunctionParamwhich_lineEdit.text())+'\''
            injection.append(string)
        inj = ','.join(injection)
        self.R('inspect(mymodel='+str(self.RFunctionParam_mymodel)+')')
        self.R('dev.off()')
        text = 'The following plot was generated:\n\n'
        #text += '<img src="plot'+str(self.widgetID)+'.png" alt="Red-R R Plot" style="align:center"/></br>'
        text += '.. image:: '+fileDir+'/plot'+str(self.widgetID)+'.png\n    :scale: 50%%\n\n'
        
        return text
