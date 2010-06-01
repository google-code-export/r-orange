"""
<name>neuralnet</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>neuralnet:neuralnet</RFunctions>
<tags>Prototypes</tags>
<icon>RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class neuralnet(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "neuralnet", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["neuralnet"])
		self.data = {}
		self.RFunctionParam_data = ''
		self.inputs = [("data", signals.RDataFrame, self.processdata)]
		self.outputs = [("neuralnet Output", signals.NeuralNet.RNeuralNet)]
		
		box = redRGUI.tabWidget(self.controlArea)
		self.standardTab = box.createTabPage(name = "Standard")
		self.advancedTab = box.createTabPage(name = "Advanced")
		self.RFunctionParamlearningrate_factor_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "learningrate_factor:")
		self.RFunctionParamconstant_weights_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "constant_weights:", text = 'NULL')
		self.RFunctionParamalgorithm_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "algorithm:", text = '"rprop+"')
		self.RFunctionParamlikelihood_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "likelihood:", text = 'FALSE')
		self.RFunctionParamrep_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "rep:", text = '1')
		self.RFunctionParamlifesign_step_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "lifesign_step:", text = '1000')
		self.RFunctionParamlifesign_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "lifesign:", text = '"none"')
		self.RFunctionParamlearningrate_limit_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "learningrate_limit:", text = 'NULL')
		self.RFunctionParamerr_fct_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "err_fct:")
		self.RFunctionParamstartweights_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "startweights:")
		self.RFunctionParamformula_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "formula:", text = '')
		self.RFunctionParamact_fct_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "act_fct:")
		self.RFunctionParamthreshold_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "threshold:", text = '0.01')
		self.RFunctionParamexclude_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "exclude:")
		self.RFunctionParamhidden_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "hidden:", text = '1')
		self.RFunctionParamstepmax_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "stepmax:", text = '1e+05')
		self.RFunctionParamlinear_output_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "linear_output:", text = 'TRUE')
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
		self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "RoutputWindow")
	def processdata(self, data):
		if not self.require_librarys(["neuralnet"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_data=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_data=''
	def commitFunction(self):
		if str(self.RFunctionParam_data) == '': return
		injection = []
		if str(self.RFunctionParamlearningrate_factor_lineEdit.text()) != '':
			string = 'learningrate.factor='+str(self.RFunctionParamlearningrate_factor_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamconstant_weights_lineEdit.text()) != '':
			string = 'constant.weights='+str(self.RFunctionParamconstant_weights_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamalgorithm_lineEdit.text()) != '':
			string = 'algorithm='+str(self.RFunctionParamalgorithm_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamlikelihood_lineEdit.text()) != '':
			string = 'likelihood='+str(self.RFunctionParamlikelihood_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamrep_lineEdit.text()) != '':
			string = 'rep='+str(self.RFunctionParamrep_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamlifesign_step_lineEdit.text()) != '':
			string = 'lifesign.step='+str(self.RFunctionParamlifesign_step_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamlifesign_lineEdit.text()) != '':
			string = 'lifesign='+str(self.RFunctionParamlifesign_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamlearningrate_limit_lineEdit.text()) != '':
			string = 'learningrate.limit='+str(self.RFunctionParamlearningrate_limit_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamerr_fct_lineEdit.text()) != '':
			string = 'err.fct='+str(self.RFunctionParamerr_fct_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamstartweights_lineEdit.text()) != '':
			string = 'startweights='+str(self.RFunctionParamstartweights_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamformula_lineEdit.text()) != '':
			string = 'formula='+str(self.RFunctionParamformula_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamact_fct_lineEdit.text()) != '':
			string = 'act.fct='+str(self.RFunctionParamact_fct_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamthreshold_lineEdit.text()) != '':
			string = 'threshold='+str(self.RFunctionParamthreshold_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamexclude_lineEdit.text()) != '':
			string = 'exclude='+str(self.RFunctionParamexclude_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamhidden_lineEdit.text()) != '':
			string = 'hidden='+str(self.RFunctionParamhidden_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamstepmax_lineEdit.text()) != '':
			string = 'stepmax='+str(self.RFunctionParamstepmax_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamlinear_output_lineEdit.text()) != '':
			string = 'linear.output='+str(self.RFunctionParamlinear_output_lineEdit.text())+''
			injection.append(string)
		inj = ','.join(injection)
		self.R(self.Rvariables['neuralnet']+'<-neuralnet(data='+str(self.RFunctionParam_data)+','+inj+')')
		self.R('txt<-capture.output('+self.Rvariables['neuralnet']+')')
		self.RoutputWindow.clear()
		tmp = self.R('paste(txt, collapse ="\n")')
		self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
		newData = signals.NeuralNet.RNeuralNet(data = self.Rvariables["neuralnet"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
		#newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
		self.rSend("neuralnet Output", newData)
