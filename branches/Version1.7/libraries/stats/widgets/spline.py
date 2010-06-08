"""
<name>Spline Fit</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<Description>Generates a spline fit to X, Y data.  This can be used for plotting or for interogating the splines.</Description>
<RFunctions>stats:spline</RFunctions>
<tags>Parametric</tags>
<icon>stats.png</icon>
"""
from OWRpy import * 
import redRGUI 
class spline(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "spline", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["spline"])
        self.data = {}
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.inputs = [("y", signals.RVector, self.processy),("x", signals.RDataFrame, self.processx)]
        self.outputs = [("spline Output", signals.RModelFit), ('spline plot attribute', signals.plotting.RPlotAttribute)]
        
        self.standardTab = redRGUI.groupBox(self.controlArea, label = 'Parameters')
        self.RFunctionParamxmin_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "xmin:", text = 'min(x)')
        self.RFunctionParamties_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "ties:", text = 'mean')
        self.RFunctionParammethod_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "method:", text = '"fmm"')
        self.RFunctionParamxmax_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "xmax:", text = 'max(x)')
        self.RFunctionParamn_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "n:", text = '3*length(x)')
        
        self.xcolumnComboBox = redRGUI.comboBox(self.standardTab, label = 'X data')
        self.ycolumnComboBox = redRGUI.comboBox(self.standardTab, label = 'Y data')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "RoutputWindow")
    def processy(self, data):
        if not self.require_librarys(["stats"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_y=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_y=''
    def processx(self, data):
        if not self.require_librarys(["stats"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_x=data.getData()
            self.data = data
            colnames = self.R('colnames('+self.RFunctionParam_x+')', wantType = 'list')
            if len(colnames) > 1:
                self.xcolumnComboBox.update(colnames)
                self.ycolumnComboBox.update(colnames)
            else:
                self.xcolumnComboBox.clear()
                self.ycolumnComboBox.clear()
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if str(self.ycolumnComboBox.currentText()) == '':
            if str(self.RFunctionParam_y) == '': return
            if str(self.RFunctionParam_x) == '': return
        else:
            data = self.data.getData()
            self.RFunctionParam_x = data+'$'+str(self.xcolumnComboBox.currentText())
            self.RFunctionParam_y = data+'$'+str(self.ycolumnComboBox.currentText())
        injection = []
        if str(self.RFunctionParamxmin_lineEdit.text()) != '':
            string = 'xmin='+str(self.RFunctionParamxmin_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamties_lineEdit.text()) != '':
            string = 'ties='+str(self.RFunctionParamties_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParammethod_lineEdit.text()) != '':
            string = 'method='+str(self.RFunctionParammethod_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamxmax_lineEdit.text()) != '':
            string = 'xmax='+str(self.RFunctionParamxmax_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamn_lineEdit.text()) != '':
            string = 'n='+str(self.RFunctionParamn_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        self.R('x <- as.vector('+str(self.RFunctionParam_x)+')')
        self.R(self.Rvariables['spline']+'<-spline(x = as.vector('+str(self.RFunctionParam_x)+'),y=as.vector('+str(self.RFunctionParam_y)+'),'+','+inj+')')
        self.R('rm(x)')
        self.R('txt<-capture.output('+self.Rvariables['spline']+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
        newData = signals.RModelFit(data = self.Rvariables["spline"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("spline Output", newData)
        
        newLine = signals.plotting.RPlotAttribute(data = 'lines('+self.Rvariables['spline']+')')
        self.rSend('spline plot attribute', newLine)
