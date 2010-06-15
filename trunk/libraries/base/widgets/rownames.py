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
class rownames(OWRpy): 
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Rownames", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["rownames"])
        self.data = {}
         
        self.RFunctionParam_x = ''
        self.inputs = [("x", rdf.RDataFrame, self.processx)]
        self.outputs = [("Names Output", signals.RVector)]
        
        box = redRGUI.widgetBox(self.controlArea)
        self.controlArea.layout().setAlignment(box,Qt.AlignTop | Qt.AlignLeft)
        redRGUI.widgetLabel(box,'Get row or column names from input object.')
        redRGUI.separator(box,height=10)
        self.function =  redRGUI.radioButtons(box, 
        buttons=['Row Names','Column Names'],setChecked='Row Names', orientation='horizontal')
        redRGUI.separator(box,height=10)

        self.RFunctionParamprefix_lineEdit =  redRGUI.lineEdit(box,  label = "prefix:", 
        toolTip='prepend prefix to simple numbers when creating names.')
        redRGUI.separator(box,height=10)
        
        self.doNullButton =  redRGUI.radioButtons(box,  label = "do.NULL:",
        toolTips=['logical. Should this create names if they are NULL?']*2,
        buttons=['TRUE','FALSE'],setChecked='TRUE', orientation='horizontal')
        buttonBox = redRGUI.widgetBox(box,orientation='horizontal')
        redRGUI.button(buttonBox, "Commit", callback = self.commitFunction)
        self.autoCommit = redRGUI.checkBox(buttonBox,buttons=['Commit on Input'],setChecked=['Commit on Input'])
        
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
        
        newData = signals.RVector(data = self.Rvariables["rownames"])

        self.rSend("Names Output", newData)

