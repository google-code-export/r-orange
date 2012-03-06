"""
<name>Rug Plot Attribute</name>
<tags>Plot Attributes</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
class rug(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["rug"])
        self.data = {}
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'x', signals.base.RVector, self.processx)

        self.outputs.addOutput('id0', 'rug Output', signals.plotting.RPlotAttribute)

        
        
        self.RFunctionParamside_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "side:", text = '1')
        self.RFunctionParamticksize_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "ticksize:", text = '0.03')
        self.RFunctionParamquiet_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "quiet:", text = 'getOption("warn")<0')
        self.RFunctionParamlwd_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "lwd:", text = '0.5')
        self.RFunctionParamcol_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "col:", text = 'par("fg")')
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction, 
        processOnInput=True)
        
    def processx(self, data):
        if not self.require_librarys(["graphics"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_x=''
    
    def commitFunction(self):
        if unicode(self.RFunctionParam_x) == '': return
        injection = []
        if unicode(self.RFunctionParamside_lineEdit.text()) != '':
            string = 'side='+unicode(self.RFunctionParamside_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamticksize_lineEdit.text()) != '':
            string = 'ticksize='+unicode(self.RFunctionParamticksize_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamquiet_lineEdit.text()) != '':
            string = 'quiet='+unicode(self.RFunctionParamquiet_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamlwd_lineEdit.text()) != '':
            string = 'lwd='+unicode(self.RFunctionParamlwd_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamcol_lineEdit.text()) != '':
            string = 'col='+unicode(self.RFunctionParamcol_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        
        newData = signals.plotting.RPlotAttribute(self, data = 'rug(x='+unicode(self.RFunctionParam_x)+','+inj+')') # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("id0", newData)