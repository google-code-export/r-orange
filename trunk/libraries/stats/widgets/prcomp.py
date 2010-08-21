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
import libraries.base.signalClasses.RDataFrame as rdf
import libraries.base.signalClasses.RMatrix as rmat
import libraries.base.signalClasses.RModelFit as rmf
import libraries.base.signalClasses as signals
class prcomp(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["prcomp"])
         
        self.RFunctionParam_x = ''
        self.inputs = [("x", signals.RDataFrame.RDataFrame, self.processx)]
        self.outputs = [("prcomp Output", signals.RModelFit.RModelFit), ("Scaled Data", signals.RMatrix.RMatrix)]

        redRGUI.button(self.controlArea, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            self.commitFunction()
    def commitFunction(self):
        if str(self.RFunctionParam_x) == '': return
        injection = []
        inj = ','.join(injection)
        self.R(self.Rvariables['prcomp']+'<-prcomp(x=as.matrix('+str(self.RFunctionParam_x)+'), scale = TRUE, retx=TRUE, '+inj+')')
        
        newPRComp = signals.RModelFit.RModelFit(data = self.Rvariables['prcomp'])
        self.rSend("prcomp Output", newPRComp)
        newPRCompMatrix = signals.RMatrix.RMatrix(data = self.Rvariables['prcomp']+'$x')
        self.rSend("Scaled Data", newPRCompMatrix)
    def getReportText(self, fileDir):
        text = 'This widget generates principal component fits to data and sends that fit and the resulting matrix of components to downstream widgets.  Please see the .rrs file or other output for more informaiton.\n\n'
        return text
