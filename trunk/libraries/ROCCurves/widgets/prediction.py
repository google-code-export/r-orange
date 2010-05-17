"""
<name>prediction</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>ROCR:prediction</RFunctions>
<tags>ROC Curves</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class prediction(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "prediction", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["prediction"])
		self.data = {}
		 
		self.RFunctionParam_labels = ''
		self.RFunctionParam_predictions = ''
		self.inputs = [("labels", signals.RVector, self.processlabels),("predictions", signals.RVector, self.processpredictions)]
		self.outputs = [("prediction Output", signals.ROCCurves.RROCPredictionFit)]
		
		self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
		box = redRGUI.tabWidget(self.controlArea)
		self.standardTab = box.createTabPage(name = "Standard")
		self.advancedTab = box.createTabPage(name = "Advanced")
		self.RFunctionParamlabel_ordering_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "label_ordering:", text = 'NULL')
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
	def processlabels(self, data):
		self.require_librarys(["ROCR"]) 
		if data:
			self.RFunctionParam_labels=data.getData()
			#self.data = data.copy()
			self.commitFunction()
		else:
			self.RFunctionParam_labels=''
	def processpredictions(self, data):
		self.require_librarys(["ROCR"]) 
		if data:
			self.RFunctionParam_predictions=data.getData()
			#self.data = data.copy()
			self.commitFunction()
		else:
			self.RFunctionParam_predictions=''
	def commitFunction(self):
		if str(self.RFunctionParam_labels) == '': 
            self.status.setText('Labels do not exist')
            return
		if str(self.RFunctionParam_predictions) == '': 
            self.status.setText('Predictions do not exist')
            return
		injection = []
		if str(self.RFunctionParamlabel_ordering_lineEdit.text()) != '':
			string = 'label.ordering='+str(self.RFunctionParamlabel_ordering_lineEdit.text())+''
			injection.append(string)
		inj = ','.join(injection)
		self.R(self.Rvariables['prediction']+'<-prediction(labels='+str(self.RFunctionParam_labels)+',predictions='+str(self.RFunctionParam_predictions)+','+inj+')')
		newData = signals.ROCCurves.RROCPredictionFit(data = self.Rvariables["prediction"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
		#newData.dictAttrs = self.data.dictAttrs.copy()  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
		self.rSend("prediction Output", newData)
