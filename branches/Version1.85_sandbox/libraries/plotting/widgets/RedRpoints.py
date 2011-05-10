"""
<name>points</name>
<tags>Plotting</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 

import libraries.plotting.signalClasses as plotsigs


class RedRpoints(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["points"])
        self.data = {}
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.RFunctionParam_col = ''
        self.inputs.addInput('id0', 'y', signals.base.RVector, self.processy)
        self.inputs.addInput('id1', 'x', signals.base.RVector, self.processx)
        self.inputs.addInput('id2', 'col', signals.base.RVector, self.processcol)

        self.outputs.addOutput('id0', 'points Output', plotsigs.RPlotAttribute)

        
        self.RFunctionParampch_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "pch:", text = '16')
        self.RFunctionParamcex_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "cex:", text = '2')
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
        
    def processy(self, data):
        if not self.require_librarys(["graphics"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_y=data.getData()
            #self.data = data
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_y=''
    def processx(self, data):
        if not self.require_librarys(["graphics"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def processcol(self, data):
        if not self.require_librarys(["graphics"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_col=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_col=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_y) == '': return
        if unicode(self.RFunctionParam_x) == '': return
        if unicode(self.RFunctionParam_col) == '': return
        injection = []
        if unicode(self.RFunctionParampch_lineEdit.text()) != '':
            string = 'pch='+unicode(self.RFunctionParampch_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamcex_lineEdit.text()) != '':
            string = 'cex='+unicode(self.RFunctionParamcex_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        newData = plotsigs.redRRPlotAttribute(self, data = 'points(y='+unicode(self.RFunctionParam_y)+',x='+unicode(self.RFunctionParam_x)+',col='+unicode(self.RFunctionParam_col)+','+inj+')') # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("id0", newData)