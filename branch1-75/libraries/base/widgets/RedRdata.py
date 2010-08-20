"""
<name>R Example Data</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Loads data from R into Red-R.  This widget allows access to example data from within R and is useful when testing schemas or widgets to ensure that they are working as indicated in R documentation.  Novice users may also find this widget useful for exploring widget functionality when they have no data of their own to explore.</description>
<RFunctions>base:data</RFunctions>
<tags>Data Input</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals

class RedRdata(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["data"])
        self.data = {}
        self.outputs = [("data Output", signals.RDataFrame.RDataFrame)]
        
        self.package = redRGUI.lineEdit(self.controlArea, label = 'Package:', text = '', callback = self.loadPackage)
        self.RFunctionParamdataName_lineEdit = redRGUI.lineEdit(self.controlArea, label = "Data Name:", text = '', callback = self.commitFunction)
        
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def loadPackage(self):
        self.require_libraries([str(self.package.text())])
    
    def commitFunction(self):
        injection = []
        if str(self.RFunctionParamdataName_lineEdit.text()) != '':
            string = str(self.RFunctionParamdataName_lineEdit.text())
            injection.append(string)
        inj = ','.join(injection)
        self.R('data('+inj+')')
        newData = signals.RDataFrame.RDataFrame(data = str(self.RFunctionParamdataName_lineEdit.text())) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("data Output", newData)
