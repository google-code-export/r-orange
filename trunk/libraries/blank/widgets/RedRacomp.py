"""
<name>acomp</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>compositions:acomp</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
from libraries.base.qtWidgets.lineEdit import lineEdit as redRlineEdit 
from libraries.base.qtWidgets.radioButtons import radioButtons as redRradioButtons 
from libraries.base.qtWidgets.comboBox import comboBox as redRcomboBox 
from libraries.base.qtWidgets.checkBox import checkBox as redRcheckBox 
from libraries.base.qtWidgets.textEdit import textEdit as redRtextEdit 
import libraries.base.signalClasses as signals

class RedRacomp(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["acomp"])
        self.data = {}
        self.require_librarys(["compositions"])
        self.RFunctionParam_X = ''
        self.inputs.addInput("X", "X", signals.RDataFrame.RDataFrame, self.processX)
        self.outputs.addOutput("acomp Output","acomp Output", signals.RMatrix.RMatrix)
        
        self.RFunctionParamSZ_lineEdit = redRlineEdit(self.controlArea, label = "SZ:", text = 'NULL')
        self.RFunctionParamMAR_lineEdit = redRlineEdit(self.controlArea, label = "MAR:", text = 'NULL')
        self.RFunctionParamBDL_lineEdit = redRlineEdit(self.controlArea, label = "BDL:", text = 'NULL')
        self.RFunctionParamparts_lineEdit = redRlineEdit(self.controlArea, label = "parts:", text = '')
        self.RFunctionParamwarn_na_lineEdit = redRlineEdit(self.controlArea, label = "warn_na:", text = 'FALSE')
        self.RFunctionParamMNAR_lineEdit = redRlineEdit(self.controlArea, label = "MNAR:", text = 'NULL')
        self.RFunctionParamtotal_lineEdit = redRlineEdit(self.controlArea, label = "total:", text = '1')
        self.RFunctionParamdetectionlimit_lineEdit = redRlineEdit(self.controlArea, label = "detectionlimit:", text = 'NULL')
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processX(self, data):
        
        if data:
            self.RFunctionParam_X=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_X=''
    def commitFunction(self):
        if str(self.RFunctionParam_X) == '': return
        injection = []
        if str(self.RFunctionParamSZ_lineEdit.text()) != '':
            string = 'SZ='+str(self.RFunctionParamSZ_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamMAR_lineEdit.text()) != '':
            string = 'MAR='+str(self.RFunctionParamMAR_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamBDL_lineEdit.text()) != '':
            string = 'BDL='+str(self.RFunctionParamBDL_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamparts_lineEdit.text()) != '':
            string = 'parts='+str(self.RFunctionParamparts_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamwarn_na_lineEdit.text()) != '':
            string = 'warn.na='+str(self.RFunctionParamwarn_na_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamMNAR_lineEdit.text()) != '':
            string = 'MNAR='+str(self.RFunctionParamMNAR_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamtotal_lineEdit.text()) != '':
            string = 'total='+str(self.RFunctionParamtotal_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamdetectionlimit_lineEdit.text()) != '':
            string = 'detectionlimit='+str(self.RFunctionParamdetectionlimit_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['acomp']+'<-acomp(X='+str(self.RFunctionParam_X)+','+inj+')')
        newData = signals.RMatrix.RMatrix(data = self.Rvariables["acomp"], checkVal = False) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("acomp Output", newData)