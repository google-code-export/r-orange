"""
<name>RedRpoints</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Adds points to an existing plot.  Data should be in the form of two RVector signals representing the X and Y coordinates of the points.</description>
<RFunctions>graphics:points</RFunctions>
<tags>Plotting</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals
import libraries.plotting.signalClasses as plotsigs

from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.button import button
class RedRpoints(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["points"])
        self.data = {}
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.RFunctionParam_col = ''
        self.inputs = [("y", signals.RVector.RVector, self.processy),("x", signals.RVector.RVector, self.processx),("col", signals.RVector.RVector, self.processcol)]
        self.outputs = [("points Output", plotsigs.RPlotAttribute.RPlotAttribute)]
        
        self.RFunctionParampch_lineEdit = lineEdit(self.controlArea, label = "pch:", text = '16')
        self.RFunctionParamcex_lineEdit = lineEdit(self.controlArea, label = "cex:", text = '2')
        button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
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
    def processcol(self, data):
        if not self.require_librarys(["graphics"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_col=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_col=''
    def commitFunction(self):
        if str(self.RFunctionParam_y) == '': return
        if str(self.RFunctionParam_x) == '': return
        if str(self.RFunctionParam_col) == '': return
        injection = []
        if str(self.RFunctionParampch_lineEdit.text()) != '':
            string = 'pch='+str(self.RFunctionParampch_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamcex_lineEdit.text()) != '':
            string = 'cex='+str(self.RFunctionParamcex_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        newData = plotsigs.RPlotAttribute.RPlotAttribute(data = 'points(y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+',col='+str(self.RFunctionParam_col)+','+inj+')') # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("points Output", newData)
    def getReportText(self, fileDir):
        return 'Generated a points plot attribute based on the incomming data.  This attribute will plot the specified points on any connected plot.  Please see those plots for more information on the points that were added.\n\n'
