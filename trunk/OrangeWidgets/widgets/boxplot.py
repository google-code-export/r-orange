"""
<name>Box Plot</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Boxplot shows a boxplot of data either in the form of a data table or a list.  This data should be only numeric, no text.  Boxplot makes a bar and wisker plot of the data with the mean represented as the bar in the center, notches representing confidence intervals, etc.  For data in the form of a table groups are taken to be the column data, if this is not correct please consider using Transpose to 'flip' the data.<description>
<RFunctions>graphics:boxplot</RFunctions>
<tags>Plotting</tags>
<icon>icons/boxplot.png</icon>
"""
from OWRpy import * 
import OWGUI, redRGUI
class boxplot(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "BoxPlot", wantMainArea = 0, resizingEnabled = 1)
        self.RFunctionParam_x = ''
        self.inputs = [("x", signals.RVariable, self.processx)]
        
        box = OWGUI.widgetBox(self.controlArea, "Widget Box")
        redRGUI.button(box, 'Save as PDF', callback = self.savePlot)
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data["data"]
            self.commitFunction()
    def savePlot(self):
        if self.x == '': return
        self.savePDF('boxplot(x=as.list('+str(self.RFunctionParam_x)+'), notch = TRUE)')
        self.status.setText('Plot Saved')
    def commitFunction(self):
        if self.x == '': return
        self.Rplot('boxplot(x=as.list('+str(self.RFunctionParam_x)+'), notch = TRUE)')
