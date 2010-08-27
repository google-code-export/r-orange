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
class prcomp(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["prcomp"])
         
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'x', redRRDataFrame, self.processx)

        self.outputs.addOutput('id0', 'prcomp Output', redRRModelFit)
        self.outputs.addOutput('id1', 'Scaled Data', redRRMatrix)


        button(self.controlArea, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            self.commitFunction()
    def commitFunction(self):
        if str(self.RFunctionParam_x) == '': return
        injection = []
        inj = ','.join(injection)
        self.R(self.Rvariables['prcomp']+'<-prcomp(x=as.matrix('+str(self.RFunctionParam_x)+'), scale = TRUE, retx=TRUE, '+inj+')')
        
        newPRComp = signals.redRRModelFit(data = self.Rvariables['prcomp'])
        self.rSend("id0", newPRComp)
        newPRCompMatrix = signals.redRRMatrix(data = self.Rvariables['prcomp']+'$x')
        self.rSend("id1", newPRCompMatrix)
    def getReportText(self, fileDir):
        text = 'This widget generates principal component fits to data and sends that fit and the resulting matrix of components to downstream widgets.  Please see the .rrs file or other output for more informaiton.\n\n'
        return text
