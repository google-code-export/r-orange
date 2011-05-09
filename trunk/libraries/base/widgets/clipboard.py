"""
<name>Clipboard</name>
"""
from OWRpy import * 
import redRGUI, signals
import redR

class clipboard(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_data = ''
        self.inputs.addInput("data", "Data Table", signals.base.RDataFrame, self.processdata)
        
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processdata(self, data):
        if data:
            self.RFunctionParam_data=data.getData()
            self.commitFunction()
        else:
            self.RFunctionParam_data=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_data) == '': 
            self.status.setText('No data to work with')
            return
        self.R('write.table(%s, "clipboard", sep = \'\\t\', col.names = NA)' % self.RFunctionParam_data, wantType = redR.NOCONVERSION)
        
        
    