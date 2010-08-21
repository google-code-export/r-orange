"""
<name>Rank</name>

<description>This Widget ranks elements in a vector and returns a ranked vector.</description>
<tags>Data Manipulation</tags>
<icon>readfile.png</icon>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>base:rank</RFunctions>
"""
from OWRpy import * 
import OWGUI 
import redRGUI 
import libraries.base.signalClasses.RMatrix as rmat
class rank(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["rank"])
        self.RFunctionParam_ties_method = ''
        #self.RFunctionParam_na_last = "TRUE"
         
        self.RFunctionParam_x = ''
        self.inputs = [("x", rmat.RMatrix, self.processx)]
        self.outputs = [("rank Output", rmat.RMatrix)]
        
        self.help.setHtml('<small>This Widget ranks elements in a vector and returns a ranked vector.</small>')
        box = redRGUI.tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.RFunctionParamties_method_comboBox = redRGUI.comboBox(self.standardTab, label = "ties_method:", items = ['average', 'first', 'random', 'max', 'min'])
        #self.RFunctionParamna_last_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "na_last:")
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            self.commitFunction()
        else:
            self.RFunctionParam_x = ''
    def commitFunction(self):
        if str(self.RFunctionParam_x) == '': 
            self.status.setText('No data')
            return
        injection = []
        if str(self.RFunctionParamties_method_comboBox.currentText()) != '':
            string = 'ties.method="'+str(self.RFunctionParamties_method_comboBox.currentText())+'"'
            injection.append(string)
        # if str(self.RFunctionParamna_last_lineEdit.text()) != '':
            # string = 'na.last='+str(self.RFunctionParamna_last_lineEdit.text())
            # injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['rank']+'<-rank(x='+str(self.RFunctionParam_x)+','+inj+', na.last = TRUE)')
        newData = rmat.RMatrix(data = self.Rvariables['rank'])
        self.rSend("rank Output", newData)
        
    def getReportText(self, fileDir):
        return 'Data was ranked.\n\n'

