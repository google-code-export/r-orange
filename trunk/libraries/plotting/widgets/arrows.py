"""
<name>Arrow</name>
<tags>Plot Attributes</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
class arrows(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["arrows"])
        self.data = {}
        self.outputs.addOutput('id0', 'arrows Output', signals.plotting.RPlotAttribute)

        self.standardTab = self.controlArea
        self.RFunctionParamx0_lineEdit =  redRGUI.base.lineEdit(self.standardTab,  label = "x0:", text = '')
        self.RFunctionParamy0_lineEdit =  redRGUI.base.lineEdit(self.standardTab,  label = "y0:", text = '')
        
        self.RFunctionParamx1_lineEdit =  redRGUI.base.lineEdit(self.standardTab,  label = "x1:", text = '')
        self.RFunctionParamy1_lineEdit =  redRGUI.base.lineEdit(self.standardTab,  label = "y1:", text = '')
        self.RFunctionParamcode_lineEdit =  redRGUI.base.lineEdit(self.standardTab,  label = "code:", text = '1')
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def commitFunction(self):
        if unicode(self.RFunctionParamx0_lineEdit.text()) == '':
            self.status.setText('No x0 specified')
            return
        if unicode(self.RFunctionParamx1_lineEdit.text()) == '':
            self.status.setText('No x1 specified')
            return
        if unicode(self.RFunctionParamy0_lineEdit.text()) == '':
            self.status.setText('No y0 specified')
            return
        if unicode(self.RFunctionParamy1_lineEdit.text()) == '':
            self.status.setText('No y1 specified')
            return
        injection = []
        if unicode(self.RFunctionParamy1_lineEdit.text()) != '':
            string = 'y1='+unicode(self.RFunctionParamy1_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamy0_lineEdit.text()) != '':
            string = 'y0='+unicode(self.RFunctionParamy0_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamx0_lineEdit.text()) != '':
            string = 'x0='+unicode(self.RFunctionParamx0_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamcode_lineEdit.text()) != '':
            string = 'code='+unicode(self.RFunctionParamcode_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamx1_lineEdit.text()) != '':
            string = 'x1='+unicode(self.RFunctionParamx1_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        
        newData = signals.plotting.RPlotAttribute(self, data = 'arrows('+inj+')')# moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("id0", newData)
