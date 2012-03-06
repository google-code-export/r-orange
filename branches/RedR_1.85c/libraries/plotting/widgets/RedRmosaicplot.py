"""
<name>Mosaic Plot</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Generates a mosaic plot given a table whose columns contain labels or factors representing the classes of the rows.  For example; subjects could be classified as male/female and blue/brown/black/green/purple eyecolor.  No continuous data should be sent to this widget and should be removed using a selection widget prior to attaching the signal.</description>
<RFunctions>:mosaicplot</RFunctions>
<tags>Plotting</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI, signals

class RedRmosaicplot(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_x = ''
        self.inputs.addInput("x", "Data Table", signals.base.RDataFrame, self.processx)
        self.plotArea = redRGUI.base.graphicsView(self.controlArea)
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if data:
                self.RFunctionParam_x=str(data.getData())
                #self.data = data
                self.commitFunction()
        else:
                self.RFunctionParam_x=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_x) == '': return
        
        self.plotArea.plot('x=table('+unicode(self.RFunctionParam_x)+')', function = 'mosaicplot')