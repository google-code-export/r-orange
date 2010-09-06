"""
<name>Row or Column Names</name>
<description>Returns a vector of rownames coresponding to the row names of a data table.</description>
<tags>Subsetting</tags>
<icon>readfile.png</icon>
<author>Anup Parikh (anup@red-r.org) and Kyle R Covington (kyle@red-r.org)</author>
<RFunctions>base:rownames, base:colnames</RFunctions>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.radioButtons import radioButtons
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.separator import separator
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.widgetBox import widgetBox
class rownames(OWRpy): 
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["rownames"])
        self.data = {}
         
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'Data Table', redRRDataFrame, self.processx)

        self.outputs.addOutput('id0', 'Set of Names', redRRVector)

        
        box = widgetBox(self.controlArea)
        self.controlArea.layout().setAlignment(box,Qt.AlignTop | Qt.AlignLeft)
        widgetLabel(box,'Get row or column names from input object.')
        separator(box,height=10)
        self.function =  radioButtons(box, 
        buttons=['Row Names','Column Names'],setChecked='Row Names', orientation='horizontal')
        separator(box,height=10)

        self.RFunctionParamprefix_lineEdit =  lineEdit(box,  label = "prefix:", 
        toolTip='prepend prefix to simple numbers when creating names.')
        separator(box,height=10)
        
        self.doNullButton =  radioButtons(box,  label = "do.NULL:",
        toolTips=['logical. Should this create names if they are NULL?']*2,
        buttons=['TRUE','FALSE'],setChecked='TRUE', orientation='horizontal')
        buttonBox = widgetBox(box,orientation='horizontal')
        button(buttonBox, "Commit", callback = self.commitFunction)
        self.autoCommit = checkBox(buttonBox,buttons=['Commit on Input'],setChecked=['Commit on Input'])
        
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            self.data = data
            self.commitFunction(userClick=False)
        else:
            self.RFunctionParam_x = ''
    def commitFunction(self,userClick=True):
        if not userClick and 'Commit on Input' not in self.autoCommit.getChecked():
            return
        if str(self.RFunctionParam_x) == '': 
            self.status.setText('No data')
            return
            
        injection = []
        if self.function.getChecked() =='Row Names':
            function = 'rownames'
        else:
            function = 'colnames'

        if str(self.RFunctionParamprefix_lineEdit.text()) != '':
            string = 'prefix="'+str(self.RFunctionParamprefix_lineEdit.text())+'"'
            injection.append(string)
        if str(self.doNullButton.getChecked()):
            string = 'do.NULL='+str(self.doNullButton.getChecked())
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['rownames']+'<-'+function+'(x='+str(self.RFunctionParam_x)+','+inj+')')
        
        newData = rvec.RVector(data = self.Rvariables["rownames"])

        self.rSend("id0", newData)
    def getReportText(self, fileDir):
        text = str(self.function.getChecked())+' were sent from this widget.\n\n'
        return text
