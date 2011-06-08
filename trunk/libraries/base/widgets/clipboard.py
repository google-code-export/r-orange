"""Clipboard
.. helpdoc::
This widget copies data to the clipboard, it is relatively generic but should only take data of the RDataFrame signal type.
"""

"""
<widgetXML>    
    <name>Clipboard<!-- [REQUIRED] title --></name>
    <icon>clipboard.png</icon>
    <tags>
        <tag>View Data</tag>
    </tags>
    <summary>Writes tables to the clipboard. <!-- [REQUIRED] A Brief description of the widget and what it does--></summary>
    <author>
        <authorname>Red-R Core Development Team</authorname>
        <authorcontact>www.red-r.org</authorcontact>
    </author>
</widgetXML>
"""

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
        
        """.. rrsignals::"""
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
        
        
    