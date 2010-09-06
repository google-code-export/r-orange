"""
<name>RedRcbind</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>base:cbind</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame

from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.button import button
class RedRcbind(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self)
		self.setRvariableNames(["cbind"])
		self.data = {}
		self.RFunctionParam_a = ''
		self.RFunctionParam_b = ''
		self.inputs.addInput('id0', 'a', redRRDataFrame, self.processa)
		self.inputs.addInput('id1', 'b', redRRDataFrame, self.processb)

		self.outputs.addOutput('id0', 'cbind Output', redRRDataFrame)

		
		self.RFunctionParamdeparse_level_lineEdit = lineEdit(self.controlArea, label = "deparse_level:", text = '1')
		button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
	def processa(self, data):
		if not self.require_librarys(["base"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_a=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_a=''
	def processb(self, data):
		if not self.require_librarys(["base"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_b=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_b=''
	def commitFunction(self):
		if str(self.RFunctionParam_a) == '': return
		if str(self.RFunctionParam_b) == '': return
		injection = []
		if str(self.RFunctionParamdeparse_level_lineEdit.text()) != '':
			string = 'deparse.level='+str(self.RFunctionParamdeparse_level_lineEdit.text())+''
			injection.append(string)
		inj = ','.join(injection)
		self.R(self.Rvariables['cbind']+'<-cbind('+str(self.RFunctionParam_a)+','+str(self.RFunctionParam_b)+','+inj+')')
		newData = signals.redRRDataFrame(data = self.Rvariables["cbind"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
		#newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
		self.rSend("id0", newData)
