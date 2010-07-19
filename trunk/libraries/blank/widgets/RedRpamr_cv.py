"""
<name>RedRpamr.cv</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>pamr:pamr.cv</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals

class RedRpamr_cv(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "pamr_cv", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["pamr.cv"])
		self.data = {}
		self.RFunctionParam_data = ''
		self.RFunctionParam_fit = ''
		self.inputs = [("data", signals.RList.RList, self.processdata),("fit", signals.RModelFit.RModelFit, self.processfit)]
		self.outputs = [("pamr.cv Output", signals.RModelFit.RModelFit)]
		
		self.RFunctionParamnfold_lineEdit = redRGUI.lineEdit(self.controlArea, label = "nfold:", text = 'NULL')
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
	def processfit(self, data):
		if not self.require_librarys(["pamr"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_fit=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_fit=''
	def commitFunction(self):
		if str(self.RFunctionParam_data) == '': return
		if str(self.RFunctionParam_fit) == '': return
		injection = []
		if str(self.RFunctionParamnfold_lineEdit.text()) != '':
			string = 'nfold='+str(self.RFunctionParamnfold_lineEdit.text())+''
			injection.append(string)
		inj = ','.join(injection)
		self.R(self.Rvariables['pamr.cv']+'<-pamr.cv(data='+str(self.RFunctionParam_data)+',fit='+str(self.RFunctionParam_fit)+','+inj+')')
		newData = signals.RModelFit.RModelFit(data = self.Rvariables["pamr.cv"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
		#newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
		self.rSend("pamr.cv Output", newData)
