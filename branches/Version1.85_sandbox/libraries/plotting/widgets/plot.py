"""
<name>Generic Plot</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Generic plot is the basis of most RedR plotting.  This accepts fits, data tables, or other RedR outputs and attempts to plot them.  However, there is no guarantee that your data will plot correctly.</description>
<tags>Plotting</tags>
<icon>plot.png</icon>
<inputWidgets></inputWidgets>
<outputWidgets></outputWidgets>

"""
from OWRpy import * 
import redRGUI, signals
class plot(OWRpy): 
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.data = None
        self.RFunctionParam_x = ''
        self.plotAttributes = {}
        self.plotLayers = []
        self.saveSettingsList = ['plotArea', 'data', 'RFunctionParam_x', 'plotAttributes']
        self.inputs.addInput('id0', 'x', signals.base.RVariable, self.processx)
        self.inputs.addInput('id1', 'Plot Layer(s)', signals.plotting.RPlotAttribute, self.processLayer, multiple = True)
        self.label = redRGUI.base.widgetLabel(self.bottomAreaLeft, '')
        self.plotArea = redRGUI.plotting.redRPlot(self.controlArea, label = 'Plot')
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)

    def processx(self, data):
        if data:
            self.data = data
            self.RFunctionParam_x=data.getData()
            if data.optionalDataExists('plotTheme'):
                self.plotArea.setTheme(data.getOptionalData('plotTheme')['data'])
            self.commitFunction()
        else:
            self.clearPlots()
    def processLayer(self, data, id):
        if data:
            self.plotAttributes[id] = data.getData()
            self.commitFunction()
        else:
            del self.plotAttributes[id.widgetID]
    def commitFunction(self):
        #if self.RFunctionParam_y == '': return
        if self.RFunctionParam_x == '': 
            self.status.setText('No Data Available')
            return
        self.status.setText('Plotting in Progress')
        self.status.setStatus(1)
        self.label.setText('')
        try:
            self.plotArea.plotMultiple(query = str(self.RFunctionParam_x), data = self.RFunctionParam_x, layers = self.plotAttributes.values())
        except Exception as inst:
            self.status.setText('Error occured during processing of the plot')
            self.status.setStatus(3)
            self.label.setText(unicode(inst))
            return
        self.status.setText('Plotting Complete')
        self.status.setStatus(2)
    def clearPlots(self):
        self.plotArea.clear()
