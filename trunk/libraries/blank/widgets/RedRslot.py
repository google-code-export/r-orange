"""
<name>RedRslot</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>base:slot</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals

class RedRslot(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "slot", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["slot"])
		self.data = {}
		self.RFunctionParam_object = ''
		self.inputs = [("object", signals.RVariable.RVariable, self.processobject)]
		self.outputs = [("slot Output", signals.RDataFrame.RDataFrame)]
		
		self.RFunctionParamname_comboBox = redRGUI.comboBox(self.controlArea, label = "name:", items = [""])
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
	def processobject(self, data):
		if not self.require_librarys(["base"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_object=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_object=''
	def commitFunction(self):
		if str(self.RFunctionParam_object) == '': return
		injection = []
		string = 'name='+str(self.RFunctionParamname_comboBox.currentText())+''
		injection.append(string)
		inj = ','.join(injection)
		self.R(self.Rvariables['slot']+'<-slot(object='+str(self.RFunctionParam_object)+','+inj+')')
		newData = signals.RDataFrame.RDataFrame(data = self.Rvariables["slot"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
		#newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
		self.rSend("slot Output", newData)
