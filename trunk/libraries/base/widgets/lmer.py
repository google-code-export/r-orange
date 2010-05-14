"""
<name>lmer</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>lme4:lmer</RFunctions>
<tags>Prototypes</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class lmer(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["lmer"])
		self.data = {}
		self.RFunctionParam_model = ''
		self.RFunctionParam_data = ''
		self.inputs = [("model", signals.RModelFit, self.processmodel),("data", signals.RDataFrame, self.processdata)]
		self.outputs = [("lmer Output", signals.RModelFit)]
		
		self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
		box = redRGUI.tabWidget(self.controlArea)
		self.standardTab = box.createTabPage(name = "Standard")
		self.advancedTab = box.createTabPage(name = "Advanced")
		self.RFunctionParamcontrol_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "control:")
		self.RFunctionParamsubset_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "subset:")
		self.RFunctionParamverbose_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "verbose:")
		self.RFunctionParamfamily_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "family:")
		self.RFunctionParamna_action_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "na_action:")
		self.RFunctionParamformula_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "formula:", text = '')
		self.RFunctionParamoffset_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "offset:")
		self.RFunctionParamstart_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "start:")
		self.RFunctionParamweights_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "weights:")
		self.RFunctionParamx_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "x:")
		self.RFunctionParamcontrasts_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "contrasts:")
		self.RFunctionParamREML_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "REML:", text = 'TRUE')
		self.RFunctionParamdoFit_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "doFit:")
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
		self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "RoutputWindow")
	def processmodel(self, data):
		self.require_librarys(["lme4"]) 
		if data:
			self.RFunctionParam_model=data.data
			#self.data = data.copy()
			self.commitFunction()
		else:
			self.RFunctionParam_model=''
	def processdata(self, data):
		self.require_librarys(["lme4"]) 
		if data:
			self.RFunctionParam_data=data.data
			#self.data = data.copy()
			self.commitFunction()
		else:
			self.RFunctionParam_data=''
	def commitFunction(self):
		if str(self.RFunctionParam_data) == '': return
		if str(self.RFunctionParamformula_lineEdit.text()) == '': return
		injection = []
		if str(self.RFunctionParamcontrol_lineEdit.text()) != '':
			string = 'control='+str(self.RFunctionParamcontrol_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamsubset_lineEdit.text()) != '':
			string = 'subset='+str(self.RFunctionParamsubset_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamverbose_lineEdit.text()) != '':
			string = 'verbose='+str(self.RFunctionParamverbose_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamfamily_lineEdit.text()) != '':
			string = 'family='+str(self.RFunctionParamfamily_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamna_action_lineEdit.text()) != '':
			string = 'na.action='+str(self.RFunctionParamna_action_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamformula_lineEdit.text()) != '':
			string = 'formula='+str(self.RFunctionParamformula_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamoffset_lineEdit.text()) != '':
			string = 'offset='+str(self.RFunctionParamoffset_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamstart_lineEdit.text()) != '':
			string = 'start='+str(self.RFunctionParamstart_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamweights_lineEdit.text()) != '':
			string = 'weights='+str(self.RFunctionParamweights_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamx_lineEdit.text()) != '':
			string = 'x='+str(self.RFunctionParamx_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamcontrasts_lineEdit.text()) != '':
			string = 'contrasts='+str(self.RFunctionParamcontrasts_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamREML_lineEdit.text()) != '':
			string = 'REML='+str(self.RFunctionParamREML_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamdoFit_lineEdit.text()) != '':
			string = 'doFit='+str(self.RFunctionParamdoFit_lineEdit.text())+''
			injection.append(string)
		inj = ','.join(injection)
		self.R(self.Rvariables['lmer']+'<-lmer(data='+str(self.RFunctionParam_data)+','+inj+')')
		self.R('txt<-capture.output('+self.Rvariables['lmer']+')')
		self.RoutputWindow.clear()
		tmp = self.R('paste(txt, collapse ="\n")')
		self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
		newData = signals.RModelFit(data = self.Rvariables["lmer"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
		#newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
		self.rSend("lmer Output", newData)
