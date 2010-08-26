"""
<name>Box Plot</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Boxplot shows a boxplot of data either in the form of a data table or a list.  This data should be only numeric, no text.  Boxplot makes a bar and wisker plot of the data with the mean represented as the bar in the center, notches representing confidence intervals, etc.  For data in the form of a table groups are taken to be the column data, if this is not correct please consider using Transpose to 'flip' the data.<description>
<RFunctions>graphics:boxplot</RFunctions>
<tags>Plotting</tags>
<icon>boxplot.png</icon>
"""
from OWRpy import * 
import OWGUI, redRGUI
from libraries.base.signalClasses.RList import RList as redRRList
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.lineEdit import lineEdit
class boxplot(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'x', redRRList, self.processx)

        
        box = OWGUI.widgetBox(self.controlArea, "Widget Box")
        button(box, 'Save as PDF', callback = self.savePlot)
        self.commandLine = lineEdit(box, label = 'Command Line')
        button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            self.commitFunction()
    def savePlot(self):
        if self.x == '': return
        self.savePDF('boxplot(x=as.list('+str(self.RFunctionParam_x)+'), notch = TRUE'+str(self.commandLine.text())+')')
        self.status.setText('Plot Saved')
    def commitFunction(self):
        if self.x == '': 
            self.status.setText('Do data. Can not plot')
            return
        try:
            self.Rplot('boxplot(x=as.list('+str(self.RFunctionParam_x)+'), notch = TRUE'+str(self.commandLine.text())+')')
        except:
            QMessageBox.information(self,'R Error', "Plotting failed.  Try to format the data in a way that is acceptable for this widget.\nSee the documentation for help.", 
            QMessageBox.Ok + QMessageBox.Default)
            return
    def getReportText(self, fileDir):
        if self.x == '': return 'Nothing to plot from this widget.\n\n'
        
        self.R('png(file="'+fileDir+'/plot'+str(self.widgetID)+'.png")')
            
        self.R('boxplot(x=as.list('+str(self.RFunctionParam_x)+'), notch = TRUE'+str(self.commandLine.text())+')')
        self.R('dev.off()')
        text = 'The following plot was generated:\n\n'
        #text += '<img src="plot'+str(self.widgetID)+'.png" alt="Red-R R Plot" style="align:center"/></br>'
        text += '.. image:: '+fileDir+'/plot'+str(self.widgetID)+'.png\n    :scale: 50%%\n\n'
            
        return text