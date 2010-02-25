"""
<name>Multi Dose Response</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>drc:,stats:anova</RFunctions>
<tags>Dose Response</tags>
<icon>icons/drc.PNG</icon>
"""
from OWRpy import * 
import redRGUI
class multdrc(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["multdrc"])
        self.RFunctionParam_hetvar = "NULL"
        self.RFunctionParam_na_action = "na.omit"
        self.RFunctionParam_fct = "l4()"
        self.RFunctionParam_collapse = ""
        self.RFunctionParam_cm = "NULL"
        self.RFunctionParam_fctList = "NULL"
        self.RFunctionParam_bcAdd = "0"
        self.curve = 0
        self.RFunctionParam_boxcox = "FALSE"
        self.RFunctionParam_varPower = "FALSE"
        self.RFunctionParam_formula = ""
        self.RFunctionParam_control = "mdControl()"
        self.RFunctionParam_weights = ""
        self.RFunctionParam_startVal = ""
        self.RFunctionParam_robust = "mean"
        self.RFunctionParam_type = "continuous"
        self.RFunctionParam_logDose = "NULL"
        self.response = 0
        self.data = {}
        self.dose = 0
        self.colNames = []
        self.RFunctionParam_data = ''
        self.loadSettings() 

        self.inputs = [("data", RvarClasses.RVariable, self.processdata)]
        self.outputs = [("multdrc Output", RvarClasses.RVariable)]
        
        box = redRGUI.tabWidget(self.controlArea, None, self)
        self.standardTab = redRGUI.createTabPage(box, "standardTab", self, "Standard")
        self.advancedTab = redRGUI.createTabPage(box, "advancedTab", self, "Advanced")
        self.RFUnctionParamhetvar_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamhetvar_lineEdit", self, "RFunctionParam_hetvar", label = "hetvar:")
        self.RFUnctionParamna_action_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamna_action_lineEdit", self, "RFunctionParam_na_action", label = "na_action:")
        self.RFUnctionParamfct_lineEdit =  redRGUI.lineEdit(self.standardTab, "RFUnctionParamfct_lineEdit", self, "RFunctionParam_fct", label = "Model:")
        self.RFUnctionParamcollapse_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamcollapse_lineEdit", self, "RFunctionParam_collapse", label = "collapse:")
        self.RFUnctionParamcm_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamcm_lineEdit", self, "RFunctionParam_cm", label = "cm:")
        self.RFUnctionParamfctList_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamfctList_lineEdit", self, "RFunctionParam_fctList", label = "fctList:")
        self.RFUnctionParambcAdd_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParambcAdd_lineEdit", self, "RFunctionParam_bcAdd", label = "bcAdd:")
        self.curveComboBox =  redRGUI.comboBox(self.standardTab, "curveComboBox", self, "curve", label = "Curves:")
        self.RFUnctionParamboxcox_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamboxcox_lineEdit", self, "RFunctionParam_boxcox", label = "boxcox:")
        self.RFUnctionParamvarPower_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamvarPower_lineEdit", self, "RFunctionParam_varPower", label = "varPower:")
        #self.RFUnctionParamformula_lineEdit =  redRGUI.lineEdit(self.standardTab, "RFUnctionParamformula_lineEdit", self, "RFunctionParam_formula", label = "formula:")
        self.responseComboBox = redRGUI.comboBox(self.standardTab, "responseComboBox", self, "response", label = "Response Data:")
        self.doseComboBox = redRGUI.comboBox(self.standardTab, "doseComboBox", self, "dose", label = "Dose Data:")
        self.RFUnctionParamcontrol_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamcontrol_lineEdit", self, "RFunctionParam_control", label = "control:")
        self.RFUnctionParamweights_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamweights_lineEdit", self, "RFunctionParam_weights", label = "weights:")
        self.RFUnctionParamstartVal_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamstartVal_lineEdit", self, "RFunctionParam_startVal", label = "startVal:")
        self.RFUnctionParamrobust_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamrobust_lineEdit", self, "RFunctionParam_robust", label = "robust:")
        self.RFUnctionParamtype_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamtype_lineEdit", self, "RFunctionParam_type", label = "type:")
        self.RFUnctionParamlogDose_lineEdit =  redRGUI.lineEdit(self.advancedTab, "RFUnctionParamlogDose_lineEdit", self, "RFunctionParam_logDose", label = "logDose:")
        redRGUI.button(self.controlArea, self, "Commit", callback = self.commitFunction)
        self.anovaTextArea = redRGUI.textEdit('anovaTextArea', self)
        self.standardTab.layout().addWidget(self.anovaTextArea)
    def processdata(self, data):
        self.require_librarys(["drc"]) 
        if data:
            self.RFunctionParam_data=data["data"]
            self.data = data.copy()

            if self.colNames == self.R('colnames('+data['data']+')'):
                self.commitFunction()
                return
            else:
                self.colNames = self.R('colnames('+data['data']+')')
                self.responseComboBox.clear()
                self.doseComboBox.clear()
                self.curveComboBox.clear()
            self.responseComboBox.addItems(self.colNames)
            self.doseComboBox.addItems(self.colNames)
            self.curveComboBox.addItems(self.colNames)
            self.curveComboBox.addItem('None')
            #self.commitFunction()
            self.anovaTextArea.clear()
    def commitFunction(self):
        if self.RFunctionParam_data == '': return
        #if self.curve == '': return
        if self.curveComboBox.currentText() == self.doseComboBox.currentText() or self.curveComboBox.currentText() == self.responseComboBox.currentText():
            print "Comparison not possible"
            return
        if self.doseComboBox.currentText() == self.responseComboBox.currentText():
            print "Comparison not possible"
            return
        self.RFunctionParam_formula = self.responseComboBox.currentText() + '~' + self.doseComboBox.currentText()
        
        #if self.RFunctionParam_formula == '': return
        injection = []
        if self.RFunctionParam_hetvar != '':
            string = 'hetvar='+str(self.RFunctionParam_hetvar)
            injection.append(string)
        if self.RFunctionParam_na_action != '':
            string = 'na.action='+str(self.RFunctionParam_na_action)
            injection.append(string)
        if self.RFunctionParam_fct != '':
            string = 'fct='+str(self.RFunctionParam_fct)
            injection.append(string)
        if self.RFunctionParam_collapse != '':
            string = 'collapse='+str(self.RFunctionParam_collapse)
            injection.append(string)
        if self.RFunctionParam_cm != '':
            string = 'cm='+str(self.RFunctionParam_cm)
            injection.append(string)
        if self.RFunctionParam_fctList != '':
            string = 'fctList='+str(self.RFunctionParam_fctList)
            injection.append(string)
        if self.RFunctionParam_bcAdd != '':
            string = 'bcAdd='+str(self.RFunctionParam_bcAdd)
            injection.append(string)
        if self.curveComboBox.currentText() != '' and self.curveComboBox.currentText() != 'None':
            string = 'curve='+str(self.curveComboBox.currentText())
            injection.append(string)
        if self.RFunctionParam_boxcox != '':
            string = 'boxcox='+str(self.RFunctionParam_boxcox)
            injection.append(string)
        if self.RFunctionParam_varPower != '':
            string = 'varPower='+str(self.RFunctionParam_varPower)
            injection.append(string)
        if self.RFunctionParam_formula != '':
            string = 'formula='+str(self.RFunctionParam_formula)
            injection.append(string)
        if self.RFunctionParam_control != '':
            string = 'control='+str(self.RFunctionParam_control)
            injection.append(string)
        if self.RFunctionParam_weights != '':
            string = 'weights='+str(self.RFunctionParam_weights)
            injection.append(string)
        if self.RFunctionParam_startVal != '':
            string = 'startVal='+str(self.RFunctionParam_startVal)
            injection.append(string)
        if self.RFunctionParam_robust != '':
            string = 'robust="'+str(self.RFunctionParam_robust)+'"'
            injection.append(string)
        if self.RFunctionParam_type != '':
            string = 'type="'+str(self.RFunctionParam_type)+'"'
            injection.append(string)
        if self.RFunctionParam_logDose != '':
            string = 'logDose='+str(self.RFunctionParam_logDose)
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['multdrc']+'<-multdrc(data='+str(self.RFunctionParam_data)+','+inj+') # I made a dose response object')
        self.data['data'] = self.Rvariables["multdrc"]
        self.rSend("multdrc Output", self.data)
        self.anovaTextArea.clear()
        self.R('txt<-capture.output(anova('+self.Rvariables["multdrc"]+'))')
        tmp = self.R('paste(txt, collapse ="\n")')
        self.anovaTextArea.insertHtml('Check that the p-value of this output is greater that 0.05.  The p-value indicates goodness of fit of the data to the specified model.  Significantly different fits violate the assumptions of the model and make comparisons unreliable.  If you have a significant p-value please change the model in the model box above.  <br><pre>'+tmp+'</pre>')
