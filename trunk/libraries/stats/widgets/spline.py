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
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.signalClasses.RModelFit import RModelFit as redRRModelFit
from libraries.plotting.signalClasses.RPlotAttribute import RPlotAttribute as redRRPlotAttribute


from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.textEdit import textEdit
class spline(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["spline"])
        self.data = {}
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'y', redRRVector, self.processy)
        self.inputs.addInput('id1', 'x', redRRVector, self.processx)

        self.outputs.addOutput('id0', 'spline Output', redRRModelFit)
        self.outputs.addOutput('id1', 'spline plot attribute', redRRPlotAttribute)

        
        self.standardTab = groupBox(self.controlArea, label = 'Parameters')
        self.RFunctionParamxmin_lineEdit =  lineEdit(self.standardTab,  label = "xmin:", text = 'min(x)')
        self.RFunctionParamties_lineEdit =  lineEdit(self.standardTab,  label = "ties:", text = 'mean')
        self.RFunctionParammethod_lineEdit =  lineEdit(self.standardTab,  label = "method:", text = '"fmm"')
        self.RFunctionParamxmax_lineEdit =  lineEdit(self.standardTab,  label = "xmax:", text = 'max(x)')
        self.RFunctionParamn_lineEdit =  lineEdit(self.standardTab,  label = "n:", text = '3*length(x)')
        
        self.xcolumnComboBox = comboBox(self.standardTab, label = 'X data')
        self.ycolumnComboBox = comboBox(self.standardTab, label = 'Y data')
        button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = textEdit(self.controlArea, label = "RoutputWindow")
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
        newData = redRRModelFit(data = self.Rvariables["spline"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("id0", newData)
        
        newLine = redRRPlotAttribute(data = 'lines('+self.Rvariables['spline']+')')
        self.rSend("id1", newLine)
        
    def getReportText(self, fileDir):
        text = 'A spline fit was made to the incoming data.  This fit can be used in downstream statistical analysis.  A plot attribute was also generated for this fit and can be appended to any plot from Generic Plot or some other plotting widgets.  Please see the .rrs file or the specific plotting or analysis widgets for more details.\n\n'
        return text
