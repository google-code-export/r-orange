"""
<name>image</name>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 

class image(OWRpy): 
    globalSettingsList = ['commitButton']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'x', signals.base.RMatrix, self.processx)

        self.gview1 = redRGUI.base.graphicsView(self.controlArea,label='Heatmap', displayLabel=False)
        self.commitButton = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            if not self.R('is.numeric('+self.RFunctionParam_x+')', silent=True):
                self.status.setText('Data not numeric')
                self.commitButton.setDisabled(True)
                return
            else:
                self.status.setText('')
                self.commitButton.setEnabled(True)
                
            if self.commitButton.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_x) == '': return
        self.gview1.plot('x='+unicode(self.RFunctionParam_x), function = 'image')