"""
<name>XY Plot</name>
<author>Generated using Widget Maker written by Kyle R. Covington, modifications by Kyle R. Covington (kyle@red-r.org)</author>
<description>Generates a plot along an X and Y axis, when numeric data is supplied the plot will result in a scatterplot of X and Y data.  When one of the elements is a factor the plot will result in a boxplot of the data.  Finally, if only factor data is supplied the plot results in a two dimentional plot of the factor levels.</description>
<RFunctions>graphics:plot</RFunctions>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals
import libraries.plotting.signalClasses as plotSignals
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.signalClasses.RList import RList as redRList
from libraries.plotting.signalClasses.RPlotAttribute import RPlotAttribute as redRRPlotAttribute
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.graphicsView import graphicsView
from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.comboBox import comboBox
class RedRplot(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.dataFrame = ''
        self.plotAttributes = {}
        self.RFunctionParam_plotatt = ''
        self.inputs.addInput('id0', 'y', [redRRVector, redRList], self.processy)
        self.inputs.addInput('id1', 'x', redRRVector, self.processx)
        self.inputs.addInput('id2', 'plotatt', redRRPlotAttribute, self.processplotatt, multiple = True)

        
        self.RFunctionParamxlab_lineEdit = lineEdit(self.controlArea, label = "X Label:", text = 'X Label')
        self.RFunctionParamylab_lineEdit = lineEdit(self.controlArea, label = "Y Label:", text = 'Y Label')
        self.RFunctionParammain_lineEdit = lineEdit(self.controlArea, label = "Main Title:", text = 'Main Title')
        self.namesListX = comboBox(self.controlArea, label = 'X Axis Data:')
        self.namesListX.setEnabled(False)
        self.namesListY = comboBox(self.controlArea, label = 'Y Axis Data:')
        self.namesListY.setEnabled(False)
        self.graphicsView = graphicsView(self.controlArea, name = self.captionTitle)
        button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processy(self, data):
        
        if not self.require_librarys(["graphics"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            if self.R('class('+data.getData()+')') in ['data.frame', 'list']:
                self.namesListX.setEnabled(True)
                self.namesListX.update(self.R('names('+data.getData()+')'))
                self.namesListY.setEnabled(True)
                self.namesListY.update(self.R('names('+data.getData()+')'))
                
                self.dataFrame = data.getData()
                
                self.dataFrameAttached = True
            else:
                self.RFunctionParam_y=data.getData()
                #self.data = data
                self.dataFrame = ''
                self.namesListX.setEnabled(False)
                self.namesListY.setEnabled(False)
                self.dataFrameAttached = False
                self.commitFunction()
        else:
            self.namesListX.setEnabled(False)
            self.namesListY.setEnabled(False)
            self.dataFrameAttached = False
            self.graphicsView.clear()
            self.RFunctionParam_y=''
    def processx(self, data):
        if not self.require_librarys(["graphics"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def processplotatt(self, data, id):
        if not self.require_librarys(["graphics"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.plotAttributes[id] = data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_plotatt=''
    def commitFunction(self):
        if not self.dataFrameAttached:
            if str(self.RFunctionParam_y) == '': return
            if str(self.RFunctionParam_x) == '': return
        else:
            if self.dataFrame == '': return
            self.RFunctionParam_x = self.dataFrame + '$' + str(self.namesListX.currentText())
            self.RFunctionParam_y = self.dataFrame + '$' + str(self.namesListY.currentText())
        injection = []
        if str(self.RFunctionParamxlab_lineEdit.text()) != '':
            string = 'xlab=\''+str(self.RFunctionParamxlab_lineEdit.text())+'\''
            injection.append(string)
        if str(self.RFunctionParamylab_lineEdit.text()) != '':
            string = 'ylab=\''+str(self.RFunctionParamylab_lineEdit.text())+'\''
            injection.append(string)
        if str(self.RFunctionParammain_lineEdit.text()) != '':
            string = 'main=\''+str(self.RFunctionParammain_lineEdit.text())+'\''
            injection.append(string)
        inj = ','.join(injection)
        self.graphicsView.plotMultiple('y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+','+inj, layers = [a for (k, a) in self.plotAttributes.items()])
    
    def getReportText(self, fileDir):
        if not self.dataFrameAttached:
            if str(self.RFunctionParam_y) == '': return 'Nothing to plot from this widget'
            if str(self.RFunctionParam_x) == '': return 'Nothing to plot from this widget'
        else:
            if self.dataFrame == '': return 'Nothing to plot from this widget'
            self.RFunctionParam_x = self.dataFrame + '$' + str(self.namesListX.currentText())
            self.RFunctionParam_y = self.dataFrame + '$' + str(self.namesListY.currentText())
        self.R('png(file="'+fileDir+'/plot'+str(self.widgetID)+'.png")')
            
        injection = []
        if str(self.RFunctionParamxlab_lineEdit.text()) != '':
            string = 'xlab=\''+str(self.RFunctionParamxlab_lineEdit.text())+'\''
            injection.append(string)
        if str(self.RFunctionParamylab_lineEdit.text()) != '':
            string = 'ylab=\''+str(self.RFunctionParamylab_lineEdit.text())+'\''
            injection.append(string)
        if str(self.RFunctionParammain_lineEdit.text()) != '':
            string = 'main=\''+str(self.RFunctionParammain_lineEdit.text())+'\''
            injection.append(string)
        inj = ','.join(injection)
        self.R('plot(y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+','+inj+')')
        self.R('dev.off()')
        text = 'The following plot was generated:\n\n'
        #text += '<img src="plot'+str(self.widgetID)+'.png" alt="Red-R R Plot" style="align:center"/></br>'
        text += '.. image:: '+fileDir+'/plot'+str(self.widgetID)+'.png\n    :scale: 50%%\n\n'
            
        return text
