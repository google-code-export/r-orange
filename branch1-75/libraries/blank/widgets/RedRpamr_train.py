"""
<name>RedRpamr.train</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Trains a model fit to expression and class data.  Generates a pamr.fit object for use in further classification analysis.</description>
<RFunctions>pamr:pamr.train</RFunctions>
<tags>Microarray</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals

class RedRpamr_train(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "pamr_train", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["pamr.train"])
		self.data = {}
		self.RFunctionParam_data = ''
		self.inputs = [("data", signals.RList.RList, self.processdata)]
		self.outputs = [("pamr.train Output", signals.RModelFit.RModelFit)]
		
		self.RFunctionParamotherOptions_lineEdit = redRGUI.lineEdit(self.controlArea, label = "otherOptions:", text = '', toolTip = 'Other options to be passed to the function.\n  These are advanced options and the help documentation should be consulted for these options.')
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
	def processdata(self, data):
		if not self.require_librarys(["pamr"]):
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
		if str(self.RFunctionParamotherOptions_lineEdit.text()) != '':
			string = str(self.RFunctionParamotherOptions_lineEdit.text())
			injection.append(string)
		inj = ','.join(injection)
		self.R(self.Rvariables['pamr.train']+'<-pamr.train(data='+str(self.RFunctionParam_data)+','+inj+')')
		newData = signals.RModelFit.RModelFit(data = self.Rvariables["pamr.train"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
		#newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
		self.rSend("pamr.train Output", newData)
