"""
<name>Box Plot</name>
<tags>Plotting</tags>
<icon>boxplot.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import OWGUI, redRGUI
class boxplot(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'x', signals.base.RList, self.processx)
        self.guiparam_plottype = redRGUI.base.comboBox(self.controlArea, label = 'Chart Type', items = [('boxplot', "Boxplot"), ('stripchart', "Jitter Plot")], callback = self.commitFunction)
        self.plotArea = redRGUI.plotting.redRPlot(self.controlArea, label = 'Boxplot')
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,processOnInput=True)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=str(data.getData())
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_x = ''
    def commitFunction(self):
        
        if self.RFunctionParam_x == '': 
            self.status.setText('Do data. Can not plot')
            return
        if self.guiparam_plottype.currentId() == 'boxplot':
            self.plotArea.plot('x=as.list(%(data)s), notch = TRUE' % {'data':self.RFunctionParam_x}, function = self.guiparam_plottype.currentId())
        elif self.guiparam_plottype.currentId() == 'stripchart':
            self.plotArea.plot('x=as.list(%(data)s)' % {'data':self.RFunctionParam_x}, function = self.guiparam_plottype.currentId())
        