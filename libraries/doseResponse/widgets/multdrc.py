"""
<name>Multi Dose Response</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>drc:drm,stats:anova</RFunctions>
<tags>Dose Response</tags>
<icon>icons/drc.PNG</icon>
"""
from OWRpy import * 
import redRGUI 
class multdrc(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "MultDRC", wantMainArea = 0, resizingEnabled = 1, wantGUIDialog = 1)
        self.autoShowDialog = 0
        self.setRvariableNames(["drm"])
        self.data = {}
        self.colNames = []
        self.RFunctionParam_data = ''
        self.RFunctionParam_formula = ''
        self.inputs = [("data", signals.RDataFrame, self.processdata)]
        self.outputs = [("drm Output", signals.RModelFit)]
        
        self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
        box = redRGUI.tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.responseComboBox = redRGUI.comboBox(self.standardTab, label = "Response Data:", toolTip = 'The column of the data that specifies the outcome data of the experiment.')
        self.doseComboBox = redRGUI.comboBox(self.standardTab, label = "Dose Data:", toolTip = 'The column of the data that specifies the dosing of the experiment.')
        self.RFunctionParamcurve_comboBox =  redRGUI.comboBox(self.standardTab,  label = "Curve:", toolTip = 'The column of data that specifies the grouping of data to make the curves')
        self.RFunctionParamhetvar_lineEdit =  redRGUI.lineEdit(self.GUIDialog, label = "hetvar:")
        self.RFunctionParamna_action_lineEdit =  redRGUI.lineEdit(self.GUIDialog, label = "na_action:")
        self.RFunctionParamfct_comboBox =  redRGUI.comboBox(self.advancedTab,  label = "Starter Function:", items = ['LL.2()', 'LL.3()', 'LL.3u()', 'LL.4()', 'LL.5()', 'W1.2()', 'W1.3()', 'W1.4()', 'W2.2()', 'W2.3()', 'W2.4()', 'BC.4()', 'BC.5()', 'LL2.2()', 'LL2.3()', 'LL2.3u()', 'LL2.4()', 'LL2.5()', 'AR.2()', 'AR.3()', 'MM.2()', 'MM.3()'])
        self.RFunctionParamcollapse_lineEdit =  redRGUI.lineEdit(self.GUIDialog, label = "collapse:")
        self.RFunctionParamcm_lineEdit =  redRGUI.lineEdit(self.GUIDialog, label = "cm:")
        self.RFunctionParamfctList_lineEdit =  redRGUI.lineEdit(self.GUIDialog, label = "fctList:")
        self.RFunctionParambcAdd_lineEdit =  redRGUI.lineEdit(self.GUIDialog, label = "bcAdd:")
        
        self.RFunctionParamboxcox_lineEdit =  redRGUI.lineEdit(self.GUIDialog, label = "boxcox:")
        self.RFunctionParamvarPower_lineEdit =  redRGUI.lineEdit(self.GUIDialog, label = "varPower:")
        #self.RFunctionParamformula_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "formula:")
        self.RFunctionParamcontrol_lineEdit =  redRGUI.lineEdit(self.GUIDialog, label = "control:")
        self.RFunctionParamweights_lineEdit =  redRGUI.lineEdit(self.GUIDialog, label = "weights:", toolTip = 'A vector of wieghts to add to the model, should be in the form c(weight1, weight2, ...) for R compatability.')
        self.RFunctionParamstartVal_lineEdit =  redRGUI.lineEdit(self.GUIDialog, label = "startVal:")
        self.RFunctionParamrobust_lineEdit =  redRGUI.lineEdit(self.GUIDialog, label = "robust:")
        self.RFunctionParamtype_lineEdit =  redRGUI.lineEdit(self.GUIDialog, label = "type:")
        self.RFunctionParamlogDose_lineEdit =  redRGUI.lineEdit(self.advancedTab,  label = "logDose:")
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.anovaTextArea = redRGUI.textEdit(self.controlArea)
    def processdata(self, data):
        if not self.require_librarys(["drc"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_data=data.getData()
            self.data = data
            
            if self.colNames == self.R('colnames('+data.getData()+')'):
                self.commitFunction()
                return
            else:
                self.colNames = self.R('colnames('+data.getData()+')')
            self.responseComboBox.update(self.colNames)
            self.doseComboBox.update(self.colNames)
            #self.RFunctionParamcurve_comboBox.('None')
            curves = self.colNames
            curves.insert(0, 'None')
            self.RFunctionParamcurve_comboBox.update(curves)
            
            self.commitFunction()
            #self.anovaTextArea.clear()
    def commitFunction(self):
        if str(self.RFunctionParam_data) == '': 
            self.status.setText('No Data')
            return
        if str(self.RFunctionParamfct_comboBox.currentText()) == '':
            self.status.setText('No Starter Function')
            return
        if self.RFunctionParamcurve_comboBox.currentText() == self.doseComboBox.currentText() or self.RFunctionParamcurve_comboBox.currentText() == self.responseComboBox.currentText():
            print "Comparison not possible"
            return
        if self.doseComboBox.currentText() == self.responseComboBox.currentText():
            print "Comparison not possible"
            return
        self.RFunctionParam_formula = self.responseComboBox.currentText() + '~' + self.doseComboBox.currentText()
        injection = []
        if str(self.RFunctionParamhetvar_lineEdit.text()) != '':
            string = 'hetvar='+str(self.RFunctionParamhetvar_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamna_action_lineEdit.text()) != '':
            string = 'na_action='+str(self.RFunctionParamna_action_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamfct_comboBox.currentText()) != '':
            string = 'fct='+str(self.RFunctionParamfct_comboBox.currentText())
            injection.append(string)
        if str(self.RFunctionParamcollapse_lineEdit.text()) != '':
            string = 'collapse='+str(self.RFunctionParamcollapse_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamcm_lineEdit.text()) != '':
            string = 'cm='+str(self.RFunctionParamcm_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamfctList_lineEdit.text()) != '':
            string = 'fctList='+str(self.RFunctionParamfctList_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParambcAdd_lineEdit.text()) != '':
            string = 'bcAdd='+str(self.RFunctionParambcAdd_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamcurve_comboBox.currentText()) != 'None':
            string = 'curveid='+str(self.RFunctionParamcurve_comboBox.currentText())
            injection.append(string)
        if str(self.RFunctionParamboxcox_lineEdit.text()) != '':
            string = 'boxcox='+str(self.RFunctionParamboxcox_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamvarPower_lineEdit.text()) != '':
            string = 'varPower='+str(self.RFunctionParamvarPower_lineEdit.text())
            injection.append(string)
        if self.RFunctionParam_formula != '':
            string = 'formula='+str(self.RFunctionParam_formula)
            injection.append(string)
        if str(self.RFunctionParamcontrol_lineEdit.text()) != '':
            string = 'control='+str(self.RFunctionParamcontrol_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamweights_lineEdit.text()) != '':
            string = 'weights='+str(self.RFunctionParamweights_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamstartVal_lineEdit.text()) != '':
            string = 'startVal='+str(self.RFunctionParamstartVal_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamrobust_lineEdit.text()) != '':
            string = 'robust='+str(self.RFunctionParamrobust_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamtype_lineEdit.text()) != '':
            string = 'type='+str(self.RFunctionParamtype_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamlogDose_lineEdit.text()) != '':
            string = 'logDose='+str(self.RFunctionParamlogDose_lineEdit.text())
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['drm']+'<-drm(data='+str(self.RFunctionParam_data)+','+inj+')')
        
        newData = signals.RModelFit(data = self.Rvariables["drm"])
        
        self.rSend("drm Output", newData)
        self.anovaTextArea.clear()
        self.R('txt<-capture.output(modelFit('+self.Rvariables["drm"]+'))')
        tmp = self.R('paste(txt, collapse ="\n")')
        self.anovaTextArea.insertHtml('Check that the p-value of this output is greater that 0.05.  The p-value indicates goodness of fit of the data to the specified model.  Significantly different fits violate the assumptions of the model and make comparisons unreliable.  If you have a significant p-value please change the model in the model box above.  <br><pre>'+tmp+'</pre>')
   