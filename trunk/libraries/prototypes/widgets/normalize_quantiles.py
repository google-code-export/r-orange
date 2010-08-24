"""
<name>Quantile Normalization</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
import redRGUI 
import libraries.base.signalClasses as signals
class normalize_quantiles(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["normalize.quantiles"])
        self.RFunctionParam_x = ""
        self.RFunctionParam_copy = "TRUE"
         
        self.RFunctionParam_x = ''
        self.inputs = [("x", signals.RDataFrame.RDataFrame, self.processx)]
        self.outputs = [("normalize.quantiles Output", signals.RDataFrame.RDataFrame)]
        
        #self.help.setHtml('<small>Performs <a href="http://en.wikipedia.org/wiki/Normalization_(statistics)">quantile normailzation</a> on a data table containing numeric data.  This is generally used for expression array data but will work to standardize any numeric data.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
        OWGUI.button(self.controlArea, self, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if not self.require_librarys(["preprocessCore"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_x=data.getData()
            self.commitFunction()
    def commitFunction(self):
        if str(self.RFunctionParam_x) == '': return
        self.R(self.Rvariables['normalize.quantiles']+'<-normalize.quantiles(x=as.matrix('+str(self.RFunctionParam_x)+'), copy=T)')
        self.R('rownames('+self.Rvariables['normalize.quantiles']+') <- rownames('+ self.RFunctionParam_x +')')
        self.R('colnames('+self.Rvariables['normalize.quantiles']+') <- colnames('+ self.RFunctionParam_x +')')
        newData = signals.RDataFrame.RDataFrame(data = 'as.data.frame('+self.Rvariables["normalize.quantiles"]+')')
        self.rSend("normalize.quantiles Output", newData)
