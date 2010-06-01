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
class prcomp(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Principal Components", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["prcomp"])
         
        self.RFunctionParam_x = ''
        self.inputs = [("x", signals.RDataFrame, self.processx)]
        self.outputs = [("prcomp Output", signals.RModelFit), ("Scaled Data", signals.RMatrix)]
        self.help.setHtml('<small>This widget performs principal component analysis on a data table containing numeric data.  The entire data fit is returned in the prcomp Output channel and the fit to the principal components is returned from the Scaled Data channel.  To view the prinicpal components graphically you may want to select the desired principal components and pass that on to a plotting widget.  More infromation on this function can be seen <a href="http://sekhon.berkeley.edu/stats/html/prcomp.html">here</a>.</small>')
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
        
        newPRComp = signals.RModelFit(data = self.Rvariables['prcomp'])
        self.rSend("prcomp Output", newPRComp)
        newPRCompMatrix = signals.RMatrix(data = self.Rvariables['prcomp']+'$x')
        self.rSend("Scaled Data", newPRCompMatrix)
