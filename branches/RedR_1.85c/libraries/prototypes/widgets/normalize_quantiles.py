"""
<name>Quantile Normalization</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
import redRGUI, signals
from libraries.base.qtWidgets.commitButton import commitButton as redRCommitButton

class normalize_quantiles(OWRpy):
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        
        self.require_librarys(["preprocessCore"])
        
        self.setRvariableNames(["normalize.quantiles"])
        self.RFunctionParam_x = ""
        self.RFunctionParam_copy = "TRUE"
         
        self.RFunctionParam_x = ''
        self.inputs.addInput("x", 'Data Table', signals.base.RDataFrame, self.processx)
        self.outputs.addOutput("normalize.quantiles Output", 'Normalized Quantiles', signals.base.RDataFrame)
        
        redRCommitButton(self.controlArea,label = "Commit", callback = self.commitFunction)
    def processx(self, data):
        
        if data:
            self.RFunctionParam_x=data.getData()
            self.commitFunction()
    def commitFunction(self):
        if unicode(self.RFunctionParam_x) == '': return
        self.R(self.Rvariables['normalize.quantiles']+'<-normalize.quantiles(x=data.matrix('+unicode(self.RFunctionParam_x)+'), copy=T)')
        self.R('rownames('+self.Rvariables['normalize.quantiles']+') <- rownames('+ self.RFunctionParam_x +')')
        self.R('colnames('+self.Rvariables['normalize.quantiles']+') <- colnames('+ self.RFunctionParam_x +')')
        newData = signals.base.RDataFrame(self, data = 'as.data.frame('+self.Rvariables["normalize.quantiles"]+')')
        self.rSend("normalize.quantiles Output", newData)
