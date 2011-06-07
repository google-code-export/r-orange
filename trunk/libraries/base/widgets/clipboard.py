"""
.. helpdoc::

"""

"""
<widgetXML>    
    <name>Clipboard<!-- [REQUIRED] title --></name>
    <icon>clipboard.png</icon>
    <tags>
        <tag>View Data</tag>
    </tags>
    <summary>Writes tables to the clipboard. <!-- [REQUIRED] A Brief description of the widget and what it does--></summary>
    <citation>
    <!-- [REQUIRED] -->
        <author>
            <name>Kyle R Covington</name>
            <contact>kyle@red-r.org</contact>
        </author>
        <reference></reference>
    </citation>
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
        
        
    