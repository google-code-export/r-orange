"""
<name>Survival Plot</name>
<author>Based on Plot which was Generated using Widget Maker written by Kyle R. Covington</author>
<description>Plots a survival object, usually from Survival Fit</description>
<icon>icons/survival.png</icon>
<tags>Survival</tags>
<RFunctions>graphics:plot, survival:Surv</RFunctions>
"""
from OWRpy import * 
import OWGUI 
import RRGUI
class survivalPlot(OWRpy): 
    settingsList = ['RFunctionParam_cex', 'RFunctionParam_main', 'RFunctionParam_xlab', 'RFunctionParam_ylab']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.RFunctionParam_main = 'Survival Plot'
        self.RFunctionParam_xlab = 'Time'
        self.RFunctionParam_ylab = 'Percent Surviving'
        self.RFunctionParam_cex = '120'
        self.RFunctionParam_xscale = ''
        #self.RFunctionParam_y = ''
        self.loadSettings()
        self.RFunctionParam_x = ''
        self.inputs = [("x", RvarClasses.RVariable, self.processx)]
        
        box = OWGUI.widgetBox(self.controlArea, "Widget Box")
        RRGUI.lineEdit(box, None, self, 'RFunctionParam_main', label = 'Main Title:')
        RRGUI.lineEdit(box, None, self, 'RFunctionParam_xlab', label = 'X Axis Label:')
        RRGUI.lineEdit(box, None, self, 'RFunctionParam_ylab', label = 'Y Axis Label:')
        RRGUI.lineEdit(box, None, self, 'RFunctionParam_xscale', label = 'X Scale Adjust:')
        RRGUI.lineEdit(box, None, self, 'RFunctionParam_cex', label = 'Text Magnification Percent:')
        OWGUI.button(box, self, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data["data"]
            self.commitFunction()
    def commitFunction(self):
        #if self.RFunctionParam_y == '': return
        if self.RFunctionParam_x == '': return
        injection = []
        if self.RFunctionParam_main != '':
            injection.append('main = "'+self.RFunctionParam_main+'"')
        if self.RFunctionParam_xlab != '':
            injection.append('xlab = "'+self.RFunctionParam_xlab+'"')
        if self.RFunctionParam_ylab != '':
            injection.append('ylab = "'+self.RFunctionParam_ylab+'"')
        if self.RFunctionParam_xscale != '':
            injection.append('xscale = '+self.RFunctionParam_xscale)
        if self.RFunctionParam_cex != '100':
            mag = float(self.RFunctionParam_cex)/100
            injection.append('cex.lab = '+str(mag))
            injection.append('cex.axis = '+str(mag))
        inj = ','.join(injection)
        
        self.Rplot('plot('+str(self.RFunctionParam_x)+','+inj+', yscale = 100, lty=c(1,2,3))', 5, 5)
