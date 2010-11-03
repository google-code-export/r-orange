"""
<name>Generic Plot</name>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI
from libraries.base.signalClasses.RVariable import RVariable as redRRVariable
from libraries.plotting.signalClasses.RPlotAttribute import RPlotAttribute as redRRPlotAttribute
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.commitButton import commitButton as redRCommitButton
from libraries.base.qtWidgets.graphicsView import graphicsView as redRGraphicsView
from libraries.base.qtWidgets.SearchDialog import SearchDialog

class plot(OWRpy): 
    globalSettingsList= ['commit']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.data = None
        self.RFunctionParam_x = ''
        self.plotAttributes = {}
        self.saveSettingsList = ['plotArea', 'data', 'RFunctionParam_x', 'plotAttributes']
        self.inputs.addInput('id0', 'x', redRRVariable, self.processx)

        self.RFunctionParam_main = lineEdit(self.controlArea, label = 'Main Title:')
        self.plotArea = redRGraphicsView(self.controlArea,label='Plot', displayLabel=False)
        self.commit = redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
        # button(self.bottomAreaRight, 'Inspect Plot', callback = self.InspectPlot)
    # def InspectPlot(self):
        # fn = QFileDialog.getOpenFileName(self, "Open File", '~',
        # "Text file (*.png);; All Files (*.*)")
        # print str(fn)
        # if fn.isEmpty(): return
        # self.plotArea.addImage(str(fn))
    def processx(self, data):
        if data:
            self.data = data
            self.RFunctionParam_x=data.getData()
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.clearPlots()
    def commitFunction(self):
        #if self.RFunctionParam_y == '': return
        if self.RFunctionParam_x == '': return
        injection = []
        if str(self.RFunctionParam_main.text()) != '':
            injection.append('main = "'+str(self.RFunctionParam_main.text())+'"')
        if injection != []:
            inj = ','+','.join(injection)
        else: inj = ''
        
        self.plotArea.plot(query = str(self.RFunctionParam_x)+inj, data = self.RFunctionParam_x)
    def getReportText(self, fileDir):
        ## print the plot to the fileDir and then send a text for an image of the plot
        if self.RFunctionParam_x != '':
            self.R('png(file="'+fileDir+'/plot'+str(self.widgetID)+'.png")')
            if self.RFunctionParam_x == '': return 'Nothing to plot from this widget'
            injection = []
            if str(self.RFunctionParam_main.text()) != '':
                injection.append('main = "'+str(self.RFunctionParam_main.text())+'"')
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
        self.plotArea.clear()
