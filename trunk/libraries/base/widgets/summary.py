"""
.. helpdoc::
<p><!-- [REQUIRED] A detailed description of the widget and what it does--></p>
"""

"""
<widgetXML>    
    <name>Summary</name>
    <icon>default.png</icon>
    <tags> 
        <tag>R</tag> 
    </tags>
    <summary>Output a summary of the data</summary>
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
<name>Summary</name>
<tags>R</tags>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
import redRi18n
_ = redRi18n.get_(package = 'base')
class summary(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["summary"])
        self.data = {}
         
        self.RFunctionParam_object = ''
        self.inputs.addInput('id0', _('R Variable Object'), signals.base.RVariable, self.processobject)
        self.outputs.addOutput('id0', _('R Summary'), signals.base.RArbitraryList)
        
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, _('Commit'), callback = self.commitFunction,
        processOnInput=True)
        
        self.RoutputWindow = redRGUI.base.textEdit(self.controlArea, label = _("RoutputWindow"))
    def processobject(self, data):
        if data:
            self.RFunctionParam_object=data.getData()
            self.data = data
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_object=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_object) == '': 
            self.status.setText('No data to work with')
            return
        self.R('txt<-capture.output(summary(object='+unicode(self.RFunctionParam_object)+'))', wantType = 'NoConversion')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
        newData = signals.base.RArbitraryList(self, data = 'as.list(summary(%s))' % self.RFunctionParam_object)
        self.rSend('id0', newData)

