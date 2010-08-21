"""
<name>RedRattributes</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>base:attributes</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals

class RedRattributes(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "attributes", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["attributes"])
		self.data = {}
		self.RFunctionParam_obj = ''
		self.inputs = [("obj", signals.RVariable.RVariable, self.processobj)]
		
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
		self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "R Output Window")
	def processobj(self, data):
		if not self.require_librarys(["base"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_obj=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_obj=''
	def commitFunction(self):
		if str(self.RFunctionParam_obj) == '': return
		injection = []
		inj = ','.join(injection)
		self.R(self.Rvariables['attributes']+'<-attributes(obj='+str(self.RFunctionParam_obj)+','+inj+')')
		self.R('txt<-capture.output('+self.Rvariables['attributes']+')')
		self.RoutputWindow.clear()
		tmp = self.R('paste(txt, collapse ="\n")')
		self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
