"""
<name>Principal Component</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>This widget performs principal component analysis on a data table containing numeric data.  The entire data fit is returned in the prcomp Output channel and the fit to the principal components is returned from the Scaled Data channel.  To view the prinicpal components graphically you may want to select the desired principal components and pass that on to a plotting widget.</description>
<icon>stats.png</icon>
<tags>Parametric</tags>
<RFunctions>stats:prcomp</RFunctions>
"""
from OWRpy import * 
import OWGUI 
import redRGUI 
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.signalClasses.RMatrix import RMatrix as redRRMatrix
from libraries.base.signalClasses.RModelFit import RModelFit as redRRModelFit
import libraries.base.signalClasses as signals
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.checkBox import checkBox
class prcomp(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["prcomp"])
         
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'x', redRRDataFrame, self.processx)

        self.outputs.addOutput('id0', 'prcomp Output', redRRModelFit)
        self.outputs.addOutput('id1', 'Scaled Data', redRRMatrix)
        self.options = checkBox(self.controlArea, label = 'Options:', buttons = ['Center', 'Scale'])
        self.options.setChecked(['Center', 'Scale'])
        self.commitOnConnect = checkBox(self.controlArea, buttons = ['Commit On Connection'], setChecked = 'Commit On Connection')
        redRCommitButton(self.controlArea, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            if 'Commit On Connection' in self.commitOnConnect.getChecked():
                self.commitFunction()
        else:
            self.RFunctionParam_x = ''
    def commitFunction(self):
        if str(self.RFunctionParam_x) == '': return
        injection = []
        if 'Center' in self.options.getChecked():
            injection.append('center = TRUE')
        else:
            injection.append('center = FALSE')
        if 'Scale' in self.options.getChecked():
            injection.append('scale = TRUE')
        else:
            injection.append('scale = FALSE')
        inj = ','.join(injection)
        self.R(self.Rvariables['prcomp']+'<-prcomp(x=as.matrix('+str(self.RFunctionParam_x)+'), '+inj+')')
        
        newPRComp = redRRModelFit(data = self.Rvariables['prcomp'])
        self.rSend("id0", newPRComp)
        newPRCompMatrix = redRRMatrix(data = self.Rvariables['prcomp']+'$x')
        self.rSend("id1", newPRCompMatrix)
    def getReportText(self, fileDir):
        text = 'This widget generates principal component fits to data and sends that fit and the resulting matrix of components to downstream widgets.  Please see the .rrs file or other output for more informaiton.\n\n'
        return text
