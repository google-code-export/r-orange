"""
<name>Melt Data</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Generates a molten set of data.  The function Cast can be used to recast the data into a new shape.</description>
<RFunctions>reshape:melt</RFunctions>
<tags>Reshape</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI, signals

class RedRmelt(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["melt"])
        self.require_librarys(["reshape"])
        self.data = {}
        self.RFunctionParam_data = ''
        self.inputs.addInput("data", "Data Table", [signals.base.RDataFrame, signals.base.RDataFrame], self.processdata)
        self.outputs.addOutput("melt Output","Molten Data", signals.base.RDataFrame)
        box = redRGUI.base.gridBox(self.controlArea)
        self.RFunctionParamna_rm_radioButtons = redRGUI.base.radioButtons(self.controlArea, label = "Remove NA's:", buttons = ["TRUE","FALSE"], setChecked = "TRUE", orientation = 'horizontal')
        self.RFunctionParammeasure_vars_listBox = redRGUI.base.listBox(box.cell(0,0), label = "Measure Variables (Values):")
        self.RFunctionParammeasure_vars_listBox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #self.RFunctionParamvariable_name_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "New Variable Column Name:", text = 'variable')
        self.RFunctionParamid_vars_listBox = redRGUI.base.listBox(box.cell(0,1), label = "Static Variables:")
        self.RFunctionParamid_vars_listBox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRGUI.base.textEdit(self.controlArea, label = "R Output Window")
    def processdata(self, data):
        if data:
            self.RFunctionParam_data=data.getData()
            #self.data = data
            if data.getClass_data() == 'matrix':
                self.RFunctionParammeasure_vars_listBox.setEnabled(False)
                self.RFunctionParamid_vars_listBox.setEnabled(False)
                self.RFunctionParammeasure_vars_listBox.hide()
                self.RFunctionParamid_vars_listBox.hide()
            else:
                self.RFunctionParammeasure_vars_listBox.show()
                self.RFunctionParamid_vars_listBox.show()
                self.RFunctionParammeasure_vars_listBox.setEnabled(True)
                self.RFunctionParamid_vars_listBox.setEnabled(True)
                self.RFunctionParammeasure_vars_listBox.update(['None'] + self.R('names('+self.RFunctionParam_data+')', wantType = 'list'))
                self.RFunctionParamid_vars_listBox.update(self.R('names('+self.RFunctionParam_data+')'))
            
            self.commitFunction()
        else:
            self.RFunctionParam_data=''
    def commitFunction(self):
        if str(self.RFunctionParam_data) == '': return
        injection = []
        ## make commit function for self.RFunctionParamna_rm_radioButtons
        injection.append(',na.rm = '+str(self.RFunctionParamna_rm_radioButtons.getChecked()))
        if self.RFunctionParammeasure_vars_listBox.isEnabled() and len(self.RFunctionParammeasure_vars_listBox.selectedItems()) > 0:
            string = ',measure.vars= c("'+'","'.join([unicode(i) for i in self.RFunctionParammeasure_vars_listBox.selectedItems()])+'")'
            injection.append(string)
        #if str(self.RFunctionParamvariable_name_lineEdit.text()) != '':
            #string = ',variable_name="'+str(self.RFunctionParamvariable_name_lineEdit.text())+'"'
            #injection.append(string)
        if self.RFunctionParamid_vars_listBox.isEnabled() and len(self.RFunctionParamid_vars_listBox.selectedItems()) > 0:
            string = ',id.vars= c("'+'","'.join([unicode(i) for i in self.RFunctionParamid_vars_listBox.selectedItems()])+'")'   #unicode(self.RFunctionParamid_vars_comboBox.currentText())+''
            injection.append(string)
        inj = ''.join(injection)
        self.R(self.Rvariables['melt']+'<-melt(data='+str(self.RFunctionParam_data)+inj+')', wantType = 'NoConversion')
        self.R('txt<-capture.output(head(%s))' % self.Rvariables['melt'], wantType = 'NoConversion')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertPlainText('This is your data:\n\n'+tmp)
        newData = signals.base.RDataFrame(self, data = self.Rvariables['melt'], parent = self.Rvariables['melt'])
        self.rSend('melt Output', newData)