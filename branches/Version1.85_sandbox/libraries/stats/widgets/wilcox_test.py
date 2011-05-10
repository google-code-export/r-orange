"""
<name>Wilcoxon Test</name>
<tags>Non Parametric</tags>
<icon>stats.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI


class wilcox_test(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["wilcox.test"])
         
        self.RFunctionParam_x = ''
        self.RFunctionParam_y = ''
        self.inputs.addInput('id0', 'x', signals.base.RVector, self.processx)
        self.inputs.addInput('id1', 'y', signals.base.RVector, self.processy)

        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
        self.RoutputWindow = redRGUI.base.textEdit(self.controlArea,label='R Output', displayLabel=False)
        
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            self.status.setText('X data set to %s' % self.RFunctionParam_x)
            if self.commit.processOnInput():
                self.commitFunction()
    def processy(self, data):
        if data:
            self.RFunctionParam_y=data.getData()
            if self.commit.processOnInput():
                self.commitFunction()
    def commitFunction(self):
        if self.RFunctionParam_x == '': 
            self.status.setText('No X data available')
            return
        injection = []
        if self.RFunctionParam_y != '':
            injection.append(unicode('y='+unicode(self.RFunctionParam_y)))
        inj = ','.join(injection)
        self.R('txt<-capture.output('+self.Rvariables['wilcox.test']+'<-wilcox.test(x='+unicode(self.RFunctionParam_x)+','+inj+'))')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')