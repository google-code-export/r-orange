"""
.. helpdoc::
<p></p>
"""

"""
<widgetXML>    
    <name>Intersect</name>
    <icon>datatable.png</icon>
    <tags> 
        <tag>Deprecated</tag> 
    </tags>
    <summary>This widget takes two vectors and performs a set intersect. Returns the set of element common to both.</summary>
    <citation>
        <author>
            <name>Red-R Core Team</name>
            <contact>http://www.red-r.org/contact</contact>
        </author>
        <reference>http://www.red-r.org</reference>
    </citation>
</widgetXML>
"""

"""
<name>Intersect</name>
<tags>Deprecated</tags>
<icon>datatable.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
import redRi18n
_ = redRi18n.get_(package = 'base')
class intersect(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["intersect"])
        self.data = {}
         
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', _('y'), signals.base.RVector, self.processy)
        self.inputs.addInput('id1', _('x'), signals.base.RVector, self.processx)

        self.outputs.addOutput('id0', _('intersect Output'), signals.base.RVector)

        
        redRGUI.base.commitButton(self.bottomAreaRight, _("Commit"), callback = self.commitFunction)
        self.RoutputWindow = redRGUI.base.textEdit(self.controlArea, label = _("Intersect Output"))
        self.resize(500, 200)
    def processy(self, data):
        if data:
            self.RFunctionParam_y=data.getData()
            self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_y = ''
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data.copy()
            self.commitFunction()
        else:
            self.RFunctionParam_x = ''
    def commitFunction(self):
        if unicode(self.RFunctionParam_y) == '': 
            self.status.setText(_('No Y data exists'))
            return
        if unicode(self.RFunctionParam_x) == '': 
            self.status.setText(_('No X data exists'))
            return
        self.R(self.Rvariables['intersect']+'<-intersect(y='+unicode(self.RFunctionParam_y)+',x='+unicode(self.RFunctionParam_x)+')', wantType = 'NoConversion')
        self.R('txt<-capture.output('+self.Rvariables['intersect']+')', wantType = 'NoConversion')
        
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse =" \n")')
        self.RoutputWindow.insertHtml(_('<br><br><pre>Shared elements between your inputs:\n')+unicode(tmp)+'</pre>')        
        newData = signals.base.RVector(self, data = self.Rvariables["intersect"])
        
        self.rSend("id0", newData)

