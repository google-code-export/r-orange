"""
<name>RedRplot</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>graphics:plot</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals
import libraries.plotting.signalClasses as plotSignals

class RedRplot(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "plot", wantMainArea = 0, resizingEnabled = 1)
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.plotAttributes = {}
        self.RFunctionParam_plotatt = ''
        self.inputs = [("y", signals.RVector.RVector, self.processy),("x", signals.RVector.RVector, self.processx),("plotatt", plotSignals.RPlotAttribute.RPlotAttribute, self.processplotatt, 'Multiple')]
        
        self.RFunctionParamxlab_lineEdit = redRGUI.lineEdit(self.controlArea, label = "X Label:", text = 'X Label')
        self.RFunctionParamylab_lineEdit = redRGUI.lineEdit(self.controlArea, label = "Y Label:", text = 'Y Label')
        self.RFunctionParammain_lineEdit = redRGUI.lineEdit(self.controlArea, label = "Main Title:", text = 'Main Title')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processy(self, data):
        if not self.require_librarys(["graphics"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_y=data.getData()
            #self.data = data
            self.commitFunction()
        else:
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
            self.plotAttributes[id[0].widgetID] = data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_plotatt=''
    def commitFunction(self):
        if str(self.RFunctionParam_y) == '': return
        if str(self.RFunctionParam_x) == '': return
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
        self.Rplot('plot(y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+','+inj+')')
        for name in self.plotAttributes.keys():
            if self.plotAttributes[name] != None:
                self.R(self.plotAttributes[name])
