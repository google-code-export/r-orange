"""
.. helpdoc::

"""

"""
<widgetXML>    
    <name>Transpose</name>
    <icon>transpose.png</icon>
    <tags> 
        <tag>Data Manipulation</tag> 
    </tags>
    <summary></summary>
    <citation>
    <!-- [REQUIRED] -->
        <author>
            <name>Red-R Core Team</name>
            <contact>http://www.red-r.org/contact</contact>
        </author>
        <reference>http://www.red-r.org</reference>
    </citation>
</widgetXML>
"""

"""
<name>Transpose</name>
<tags>Data Manipulation</tags>
"""
from OWRpy import * 
import redRGUI, signals


import redRi18n
_ = redRi18n.get_(package = 'base')
class t(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["t"])
        self.RFunctionParam_x = ''
        self.data={}
        
        
        self.inputs.addInput('id0', _('Input Data Table or Matrix'), [signals.base.RDataFrame, signals.base.RMatrix], self.processx)

        self.outputs.addOutput('id0', _('Transposed Data Table'), signals.base.RDataFrame)

        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, _("Commit"), callback = self.commitFunction,
        processOnInput=True)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            self.data = data
            if self.commit.processOnInput():
                self.commitFunction()
    def commitFunction(self):
        if self.x == '': return
        
        self.R(self.Rvariables['t']+'<-as.data.frame(t(x='+unicode(self.RFunctionParam_x)+'))', wantType = 'NoConversion')
        
        newData = signals.base.RDataFrame(self, data = self.Rvariables['t'])
        newData.dictAttrs = self.data.dictAttrs.copy()
        self.rSend("id0", newData)
