"""
<name>XY Plot</name>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
import libraries.plotting.signalClasses as plotSignals

class RedRplot(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.dataFrame = ''
        self.dataFrameAttached = False
        self.plotAttributes = {}
        self.RFunctionParam_plotatt = ''
        self.inputs.addInput('id0', 'y', [signals.base.RVector, signals.base.RList], self.processy)
        self.inputs.addInput('id1', 'x', signals.base.RVector, self.processx)
        self.inputs.addInput('id2', 'plotatt', signals.plotting.RPlotAttribute, self.processplotatt, multiple = True)

        
        self.RFunctionParamxlab_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "X Label:", text = 'X Label')
        self.RFunctionParamylab_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "Y Label:", text = 'Y Label')
        self.RFunctionParammain_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "Main Title:", text = 'Main Title')
        self.namesListX = redRGUI.base.comboBox(self.controlArea, label = 'X Axis Data:')
        self.namesListX.setEnabled(False)
        self.namesListY = redRGUI.base.comboBox(self.controlArea, label = 'Y Axis Data:')
        self.namesListY.setEnabled(False)
        self.graphicsView = redRGUI.plotting.redRPlot(self.controlArea,label='XY Plot',displayLabel=False,
        name = self.captionTitle)
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
    def processy(self, data):
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

            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.namesListX.setEnabled(False)
            self.namesListY.setEnabled(False)
            self.dataFrameAttached = False
            self.graphicsView.clear()
            self.RFunctionParam_y=''
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def processplotatt(self, data, id):
        if data:
            self.plotAttributes[id] = data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_plotatt=''
    def commitFunction(self):
        if not self.dataFrameAttached:
            if unicode(self.RFunctionParam_y) == '': return
            if unicode(self.RFunctionParam_x) == '': return
        else:
            if self.dataFrame == '': return
            self.RFunctionParam_x = self.dataFrame + '$' + unicode(self.namesListX.currentText())
            self.RFunctionParam_y = self.dataFrame + '$' + unicode(self.namesListY.currentText())
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
        self.graphicsView.plotMultiple('y='+unicode(self.RFunctionParam_y)+',x='+unicode(self.RFunctionParam_x)+','+inj, layers = self.plotAttributes.values())
    
