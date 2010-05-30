"""
<name>Arrow</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>graphics:arrows</RFunctions>
<tags>Prototypes</tags>
<icon>icons/plot.png</icon>
"""
from OWRpy import * 
import redRGUI 
class arrows(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "arrows", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["arrows"])
        self.data = {}
        self.outputs = [("arrows Output", signals.RPlotAttribute)]
        self.standardTab = self.controlArea
        self.RFunctionParamx0_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "x0:", text = '')
        self.RFunctionParamy0_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "y0:", text = '')
        
        self.RFunctionParamx1_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "x1:", text = '')
        self.RFunctionParamy1_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "y1:", text = '')
        self.RFunctionParamcode_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "code:", text = '1')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def commitFunction(self):
        if str(self.RFunctionParamx0_lineEdit.text()) == '':
            self.status.setText('No x0 specified')
            return
        if str(self.RFunctionParamx1_lineEdit.text()) == '':
            self.status.setText('No x1 specified')
            return
        if str(self.RFunctionParamy0_lineEdit.text()) == '':
            self.status.setText('No y0 specified')
            return
        if str(self.RFunctionParamy1_lineEdit.text()) == '':
            self.status.setText('No y1 specified')
            return
        injection = []
        if str(self.RFunctionParamy1_lineEdit.text()) != '':
            string = 'y1='+str(self.RFunctionParamy1_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamy0_lineEdit.text()) != '':
            string = 'y0='+str(self.RFunctionParamy0_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamx0_lineEdit.text()) != '':
            string = 'x0='+str(self.RFunctionParamx0_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamcode_lineEdit.text()) != '':
            string = 'code='+str(self.RFunctionParamcode_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamx1_lineEdit.text()) != '':
            string = 'x1='+str(self.RFunctionParamx1_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        
        newData = signals.RPlotAttribute(data = 'arrows('+inj+')')# moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("arrows Output", newData)
