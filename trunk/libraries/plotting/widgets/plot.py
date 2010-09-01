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
import OWGUI 
import redRGUI
from libraries.base.signalClasses.RVariable import RVariable as redRRVariable
from libraries.plotting.signalClasses.RPlotAttribute import RPlotAttribute as redRRPlotAttribute
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.graphicsView import graphicsView as redRGraphicsView
class plot(OWRpy): 
    settingsList = ['RFunctionParam_cex', 'RFunctionParam_main', 'RFunctionParam_xlab', 'RFunctionParam_ylab']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.data = None
        self.RFunctionParam_x = ''
        self.plotAttributes = {}
        self.saveSettingsList = ['data', 'RFunctionParam_x', 'plotAttributes']
        self.inputs.addInput('id0', 'x', redRRVariable, self.processx)
        self.inputs.addInput('id1', 'Plot Attributes', redRRPlotAttribute, self.gotAttribute)

        
        box = OWGUI.widgetBox(self.controlArea, "Widget Box")
        self.RFunctionParam_main = lineEdit(box, label = 'Main Title:')
        # self.RFunctionParam_xlab = lineEdit(box, label = 'X Axis Label:')
        # self.RFunctionParam_ylab = lineEdit(box, label = 'Y Axis Label:')
        # self.RFunctionParam_cex = lineEdit(box, '100', label = 'Text Magnification Percent:')
        self.plotArea = redRGraphicsView(self.controlArea)
        #self.advancedOptions = lineEdit(box, label = 'Advanced Options:', toolTip = 'Advanced obtions to be added to the R command, this can be things like points, charachter labels, etc.  See R documentation for more help.')
        button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        #button(self.bottomAreaRight, "Save As PDF", callback = self.saveAsPDF)
    def gotAttribute(self, data, id):
        if data:
            self.plotAttributes[id] = data.getData()
        else:
            print 'Removing data %s' % str(id)
            self.plotAttributes[id] = None
    def processx(self, data):
        if data:
            self.data = data
            self.RFunctionParam_x=data.getData()
            self.commitFunction()
        else:
            self.clearPlots()
    # def saveAsPDF(self):
        # if self.RFunctionParam_x == '': return
        # injection = []
        # if self.R('class('+str(self.RFunctionParam_x)+')') == 'data.frame' and not 'colors' in self.data.dictAttrs:
            # injection.append('pch=rownames('+self.RFunctionParam_x+')')
        # if self.RFunctionParam_main.text() != '':
            # injection.append('main = "'+str(self.RFunctionParam_main.text())+'"')
        # if self.RFunctionParam_xlab.text() != '':
            # injection.append('xlab = "'+str(self.RFunctionParam_xlab.text())+'"')
        # if self.RFunctionParam_ylab.text() != '':
            # injection.append('ylab = "'+str(self.RFunctionParam_ylab.text())+'"')
        # if self.RFunctionParam_cex.text() != '100':
            # mag = float(self.RFunctionParam_cex.text())/100
            # injection.append('cex.lab = '+str(mag))
            # injection.append('cex.axis = '+str(mag))
        # if injection != []:
            # inj = ','+','.join(injection)
        # else: inj = ''
        ###try:
        # self.savePDF('plot('+str(self.RFunctionParam_x)+inj+')')
    def commitFunction(self):
        #if self.RFunctionParam_y == '': return
        if self.RFunctionParam_x == '': return
        injection = []
        # if self.R('class('+str(self.RFunctionParam_x)+')') == 'data.frame' and not 'colors' in self.data.dictAttrs:
            # injection.append('pch=rownames('+self.RFunctionParam_x+')')
        if str(self.RFunctionParam_main.text()) != '':
            injection.append('main = "'+str(self.RFunctionParam_main.text())+'"')
        # if str(self.RFunctionParam_xlab.text()) != '':
            # injection.append('xlab = "'+str(self.RFunctionParam_xlab.text())+'"')
        # if str(self.RFunctionParam_ylab.text()) != '':
            # injection.append('ylab = "'+str(self.RFunctionParam_ylab.text())+'"')
        # if str(self.advancedOptions.text()) != '':
            # injection.append(str(self.advancedOptions.text()))
        # if str(self.RFunctionParam_cex.text()) != '100':
            # mag = float(str(self.RFunctionParam_cex.text()))/100
            # injection.append('cex.lab = '+str(mag))
            # injection.append('cex.axis = '+str(mag))
        if injection != []:
            inj = ','+','.join(injection)
        else: inj = ''
        
        self.plotArea.plot(str(self.RFunctionParam_x)+inj)
        for name in self.plotAttributes.keys():
            if self.plotAttributes[name] != None:
                self.R(self.plotAttributes[name])
    def getReportText(self, fileDir):
        ## print the plot to the fileDir and then send a text for an image of the plot
        if self.RFunctionParam_x != '':
            self.R('png(file="'+fileDir+'/plot'+str(self.widgetID)+'.png")')
            if self.RFunctionParam_x == '': return 'Nothing to plot from this widget'
            injection = []
            # if self.R('class('+str(self.RFunctionParam_x)+')') == 'data.frame' and not 'colors' in self.data.dictAttrs:
                # injection.append('pch=rownames('+self.RFunctionParam_x+')')
            if str(self.RFunctionParam_main.text()) != '':
                injection.append('main = "'+str(self.RFunctionParam_main.text())+'"')
            # if str(self.RFunctionParam_xlab.text()) != '':
                # injection.append('xlab = "'+str(self.RFunctionParam_xlab.text())+'"')
            # if str(self.RFunctionParam_ylab.text()) != '':
                # injection.append('ylab = "'+str(self.RFunctionParam_ylab.text())+'"')
            # if str(self.RFunctionParam_cex.text()) != '100':
                # mag = float(str(self.RFunctionParam_cex.text()))/100
                # injection.append('cex.lab = '+str(mag))
                # injection.append('cex.axis = '+str(mag))
            if injection != []:
                inj = ','+','.join(injection)
            else: inj = ''

            self.R('plot('+str(self.RFunctionParam_x)+inj+')')
            for name in self.plotAttributes.keys():
                if self.plotAttributes[name] != None:
                    self.R(self.plotAttributes[name])
            self.R('dev.off()')
            text = 'The following plot was generated:\n\n'
            #text += '<img src="plot'+str(self.widgetID)+'.png" alt="Red-R R Plot" style="align:center"/></br>'
            text += '.. image:: '+fileDir+'/plot'+str(self.widgetID)+'.png\n    :scale: 50%%\n\n'
        else:
            text = 'Nothing to plot from this widget'
            
        return text
    def clearPlots(self):
        if len(self.device) > 0:
            for key, dev in self.device.items():
                dev.clear()
