### lmer anova, just like anova, actually runs the anova command, but comparing two lmer fits.

"""
<name>LMER Anova</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>stats:anova</RFunctions>
<tags>Stats</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class lmerAnova(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "LMER Anova", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["anova"])
        self.data = {}
        self.RFunctionParam_model = ''
        self.RFunctionParam_data = ''
        self.RFunctionParam_data2 = ''
        self.inputs = [("data", signals.RLme4ModelFit, self.processdata), ("data2", signals.RLme4ModelFit, self.processdata2)]
        
        self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')

        self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "RoutputWindow")

    def processdata(self, data):
         
        if data:
            self.RFunctionParam_data=data.getData()
            self.data = data
            #self.data = data.copy()
            self.commitFunction()
        else:
            self.RFunctionParam_data=''

    def processdata2(self, data):
         
        if data:
            self.RFunctionParam_data2=data.getData()
            self.data2 = data
            #self.data = data.copy()
            self.commitFunction()
        else:
            self.RFunctionParam_data=''
    def commitFunction(self):
        if str(self.RFunctionParam_data) == '': 
            self.status.setText('No data')
            return
        if str(self.RFunctionParam_data2) == '': 
            self.status.setText('No data')
            return
        if self.data.getItem('parent') != self.data2.getItem('parent'):
            self.status.setText('Data not of the same parent, incompatable models')
            return
        self.R(self.Rvariables['anova']+'<-anova('+str(self.RFunctionParam_data)+','+str(self.RFunctionParam_data2)+')')
        self.R('txt<-capture.output('+self.Rvariables['anova']+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertPlainText(tmp)
        
