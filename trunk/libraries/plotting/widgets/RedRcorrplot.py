"""
<name>RedRcorrplot</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>pls:corrplot</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals

from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.button import button
class RedRcorrplot(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self)
		self.RFunctionParam_object = ''
		self.inputs = [("object", signals.RModelFit.RModelFit, self.processobject)]
		
		self.RFunctionParamtype_comboBox = comboBox(self.controlArea, label = "type:", items = ["'p'; points","'l'; lines"])
		button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
	def processobject(self, data):
		if not self.require_librarys(["pls"]):
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
		string = 'type='+str(self.RFunctionParamtype_comboBox.currentText()).split(';')[0]+''
		injection.append(string)
		inj = ','.join(injection)
		self.Rplot('corrplot(object='+str(self.RFunctionParam_object)+','+inj+')')
