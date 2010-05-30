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
import redRGUI
import SurvivalClasses
class survivalPlot(OWRpy): 
    settingsList = ['RFunctionParam_cex', 'RFunctionParam_main', 'RFunctionParam_xlab', 'RFunctionParam_ylab']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Survival Plot", wantMainArea = 0, resizingEnabled = 1)
        self.RFunctionParam_x = ''
        self.inputs = [("x", signals.survival.RSurvFit, self.processx)]
        
        box = OWGUI.widgetBox(self.controlArea, "Widget Box")
        self.RFunctionParam_main = redRGUI.lineEdit(box, label = 'Main Title:', text = 'Survival Plot', toolTip = 'The title of the plot')
        self.RFunctionParam_xlab = redRGUI.lineEdit(box, label = 'X Axis Label:', text = 'Time', toolTip = 'The text representing the X axis.')
        self.RFunctionParam_ylab = redRGUI.lineEdit(box, label = 'Y Axis Label:', text = 'Percent Surviving', toolTip = 'The text representing the Y axis.')
        self.RFunctionParam_xscale = redRGUI.lineEdit(box, label = 'X Scale Adjust:', toolTip = 'Number to adjust the scale by to convert from different times ex months to years.')
        self.RFunctionParam_colors = redRGUI.lineEdit(box, label = 'Colors:', toolTip = 'Colors either as names (must be in quotes) or numbers')
        self.RFunctionParam_cex = redRGUI.lineEdit(box, label = 'Text Magnification Percent:', text = '120', toolTip = 'Magnification of the axes.')
        redRGUI.button(self.bottomAreaRight, 'Save as PDF', callback = self.saveAsPDF)
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def saveAsPDF(self):
        if self.RFunctionParam_x == '': return
        self.savePDF('boxplot(x=as.list('+str(self.RFunctionParam_x)+'), notch = TRUE)')
        self.status.setText('Plot Saved')
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            self.commitFunction()
        else:
            self.RFunctionParam_x = ''
    def commitFunction(self):
        #if self.RFunctionParam_y == '': return
        if self.RFunctionParam_x == '': return
        injection = []
        if self.RFunctionParam_main != '':
            injection.append('main = "'+str(self.RFunctionParam_main.text())+'"')
        if self.RFunctionParam_xlab != '':
            injection.append('xlab = "'+str(self.RFunctionParam_xlab.text())+'"')
        if self.RFunctionParam_ylab != '':
            injection.append('ylab = "'+str(self.RFunctionParam_ylab.text())+'"')
        if self.RFunctionParam_xscale != '':
            injection.append('xscale = '+str(self.RFunctionParam_xscale.text()))
        if self.RFunctionParam_cex != '100':
            mag = float(str(self.RFunctionParam_cex.text()))/100
            injection.append('cex.lab = '+str(mag))
            injection.append('cex.axis = '+str(mag))
        if str(self.RFunctionParam_colors.text()) != '':
            injection.append('col = c('+str(self.RFunctionParam_colors.text())+')')
        inj = ','.join(injection)
        
        self.Rplot('plot('+str(self.RFunctionParam_x)+','+inj+', yscale = 100, lty=c(1,2,3))', 5, 5)
