"""
<name>Hexbin Plot</name>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals
import libraries.plotting.signalClasses as plotSignals
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.signalClasses.RList import RList as redRList
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRDataFrame

from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.graphicsView import graphicsView
from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.commitButton import commitButton as redRCommitButton

class krcggplothexbin(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        
        self.require_librarys(["ggplot2"])
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.setRvariableNames(["hexbin"])
        #self.dataFrame = ''
        #self.plotAttributes = {}
        #self.RFunctionParam_plotatt = ''
        self.inputs.addInput('id0', 'Data Table', redRDataFrame, self.processy)
        #self.inputs.addInput('id1', 'x', redRRVector, self.processx)
        #self.inputs.addInput('id2', 'plotatt', redRRPlotAttribute, self.processplotatt, multiple = True)

        
        self.RFunctionParamxlab_lineEdit = lineEdit(self.controlArea, label = "X Label:", text = 'X Label')
        self.RFunctionParamylab_lineEdit = lineEdit(self.controlArea, label = "Y Label:", text = 'Y Label')
        self.RFunctionParammain_lineEdit = lineEdit(self.controlArea, label = "Main Title:", text = 'Main Title')
        self.namesListX = comboBox(self.controlArea, label = 'X Axis Data:')
        #self.namesListX.setEnabled(False)
        self.namesListY = comboBox(self.controlArea, label = 'Y Axis Data:')
        #self.namesListY.setEnabled(False)
        self.graphicsView = graphicsView(self.controlArea,label='Hexbin Plot',displayLabel=False,
        name = self.captionTitle)
        self.commit = redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
        
    def processy(self, data):
        
        if data:
            self.RFunctionParam_y = data.getData()
            self.namesListX.setEnabled(True)
            self.namesListX.update(self.R('names('+data.getData()+')'))
            self.namesListY.setEnabled(True)
            self.namesListY.update(self.R('names('+data.getData()+')'))
            self.dataFrame = data.getData()
            self.dataFrameAttached = True

            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.graphicsView.clear()
            self.RFunctionParam_y=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_y) == '': return
        if self.namesListY.currentText() == self.namesListX.currentText(): 
            self.status.setText(_("X and Y data can't be the same"))
            return
        injection = []
        if unicode(self.RFunctionParamxlab_lineEdit.text()) != '':
            string = 'xlab=\''+unicode(self.RFunctionParamxlab_lineEdit.text())+'\''
            injection.append(string)
        if unicode(self.RFunctionParamylab_lineEdit.text()) != '':
            string = 'ylab=\''+unicode(self.RFunctionParamylab_lineEdit.text())+'\''
            injection.append(string)
        if unicode(self.RFunctionParammain_lineEdit.text()) != '':
            string = 'main=\''+unicode(self.RFunctionParammain_lineEdit.text())+'\''
            injection.append(string)
        inj = ','.join(injection)
        self.R('%(VAR)s<-ggplot(%(DATA)s, aes(x = %(XDATA)s, y = %(YDATA)s))' % {'DATA':self.RFunctionParam_y, 'VAR':self.Rvariables['hexbin'], 'XDATA':self.namesListX.currentText(), 'YDATA':self.namesListY.currentText()}, wantType = 'NoConversion')
        self.graphicsView.plot(self.Rvariables['hexbin']+','+inj)
    
    