"""
<name>RedRpamr.fdr</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>pamr:pamr.fdr</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals

class RedRpamr_fdr(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "pamr_fdr", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["pamr.fdr"])
		self.data = {}
		self.RFunctionParam_trained_obj = ''
		self.RFunctionParam_data = ''
		self.inputs = [("trained_obj", signals.RModelFit.RModelFit, self.processtrained_obj),("data", signals.RList.RList, self.processdata)]
		self.outputs = [("pamr.fdr Output", signals.RModelFit.RModelFit)]
		
		self.RFunctionParamnperms_lineEdit = redRGUI.lineEdit(self.controlArea, label = "nperms:", text = '100')
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
	def processtrained_obj(self, data):
		if not self.require_librarys(["pamr"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_trained_obj=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_trained_obj=''
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
		if str(self.RFunctionParam_trained_obj) == '': return
		if str(self.RFunctionParam_data) == '': return
		injection = []
		if str(self.RFunctionParamnperms_lineEdit.text()) != '':
			string = 'nperms='+str(self.RFunctionParamnperms_lineEdit.text())+''
			injection.append(string)
		inj = ','.join(injection)
		self.R(self.Rvariables['pamr.fdr']+'<-pamr.fdr(trained.obj='+str(self.RFunctionParam_trained_obj)+',data='+str(self.RFunctionParam_data)+','+inj+')')
		newData = signals.RModelFit.RModelFit(data = self.Rvariables["pamr.fdr"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
		#newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
		self.rSend("pamr.fdr Output", newData)
