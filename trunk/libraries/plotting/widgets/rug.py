"""
<name>Rug Plot Attribute</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>graphics:rug</RFunctions>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.signalClasses.RPlotAttribute import RPlotAttribute as redRRPlotAttribute
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.tabWidget import tabWidget
from libraries.base.qtWidgets.button import button
class rug(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["rug"])
        self.data = {}
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'x', redRRVector, self.processx)

        self.outputs.addOutput('id0', 'rug Output', redRRPlotAttribute)

        
        
        box = tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.RFunctionParamside_lineEdit =  lineEdit(self.standardTab,  label = "side:", text = '1')
        self.RFunctionParamticksize_lineEdit =  lineEdit(self.standardTab,  label = "ticksize:", text = '0.03')
        self.RFunctionParamquiet_lineEdit =  lineEdit(self.standardTab,  label = "quiet:", text = 'getOption("warn")<0')
        self.RFunctionParamlwd_lineEdit =  lineEdit(self.standardTab,  label = "lwd:", text = '0.5')
        self.RFunctionParamcol_lineEdit =  lineEdit(self.standardTab,  label = "col:", text = 'par("fg")')
        button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
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
    def commitFunction(self):
        if str(self.RFunctionParam_x) == '': return
        injection = []
        if str(self.RFunctionParamside_lineEdit.text()) != '':
            string = 'side='+str(self.RFunctionParamside_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamticksize_lineEdit.text()) != '':
            string = 'ticksize='+str(self.RFunctionParamticksize_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamquiet_lineEdit.text()) != '':
            string = 'quiet='+str(self.RFunctionParamquiet_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamlwd_lineEdit.text()) != '':
            string = 'lwd='+str(self.RFunctionParamlwd_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamcol_lineEdit.text()) != '':
            string = 'col='+str(self.RFunctionParamcol_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        
        newData = redRRPlotAttribute(data = 'rug(x='+str(self.RFunctionParam_x)+','+inj+')') # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("rug Output", newData)
    def getReportText(self, fileDir):
        return 'A rug plot attribute was generated for use in plotting a rug plot on any connected widget.  Please see those widgets plots for the rug plot output.\n\n'
