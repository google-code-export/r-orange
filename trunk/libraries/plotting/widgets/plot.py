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
from libraries.base.signalClasses.RVariable import RVariable as redRRVariable
from libraries.plotting.signalClasses.RPlotAttribute import RPlotAttribute as redRRPlotAttribute
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.widgetLabel import widgetLabel as redRWidgetLabel
from libraries.plotting.qtWidgets.redRPlot import redRPlot
from libraries.base.qtWidgets.graphicsView import graphicsView as redRGraphicsView
from libraries.base.qtWidgets.SearchDialog import SearchDialog
class plot(OWRpy): 
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.data = None
        self.RFunctionParam_x = ''
        self.plotAttributes = {}
        self.plotLayers = []
        self.saveSettingsList = ['plotArea', 'data', 'RFunctionParam_x', 'plotAttributes']
        self.inputs.addInput('id0', 'x', redRRVariable, self.processx)
        self.inputs.addInput('id1', 'Plot Layer(s)', redRRPlotAttribute, self.processLayer, multiple = True)
        self.label = redRWidgetLabel(self.controlArea, '')
        self.plotArea = redRPlot(self.controlArea, label = 'Plot')
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)

    def processx(self, data):
        if data:
            self.data = data
            self.RFunctionParam_x=data.getData()
            self.commitFunction()
        else:
            self.clearPlots()
    def processLayer(self, data, id):
        if data:
            self.plotAttributes[id.widgetID] = data.getData()
            self.commitFunction()
        else:
            del self.plotAttributes[id.widgetID]
    def commitFunction(self):
        #if self.RFunctionParam_y == '': return
        if self.RFunctionParam_x == '': 
            self.status.setText('No Data Available')
            return
        self.status.setText('Plotting in Progress')
        self.status.setStatus(2)
        try:
            self.plotArea.plotMultiple(query = str(self.RFunctionParam_x), data = self.RFunctionParam_x, layers = self.plotAttributes.values())
        except Exception as inst:
            self.status.setText('Error occured during processing of the plot')
            self.status.setStatus(3)
            self.label.setText(unicode(inst))
            return
        self.status.setText('Plotting Complete')
        self.status.setStatus(1)
    def clearPlots(self):
        self.plotArea.clear()
