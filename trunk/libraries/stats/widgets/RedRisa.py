"""
<name>isa</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>isa2:isa</RFunctions>
<tags>Prototypes</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
class RedRisa(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["isa"])
        self.data = {}
        self.RFunctionParam_data = ''
        self.inputs.addInput('id0', 'data', signals.base.RMatrix, self.processdata)

        self.outputs.addOutput('id0', 'isa Output', signals.base.RModelFit)


        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processdata(self, data):
        if not self.require_librarys(["isa2"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_data=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_data=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_data) == '': return
        
        self.R(self.Rvariables['isa']+'<-isa(data='+unicode(self.RFunctionParam_data)+')')
        newData = signals.base.RModelFit(self, data = self.Rvariables["isa"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("id0", newData)
