"""
<name>GDS2eSet</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
import RRGUI 
class GDS2eSet(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["GDS2eSet"])
		self.RFunctionParam_GPL = "NULL"
		self.RFunctionParam_do_log2 = "FALSE"
		self.loadSettings() 
		self.RFunctionParam_GDS = ''
		self.inputs = [("GDS", RvarClasses.RVariable, self.processGDS)]
		self.outputs = [("GDS2eSet Output", RvarClasses.RVariable)]
		
		box = RRGUI.tabWidget(self.controlArea, None, self)
		self.standardTab = RRGUI.createTabPage(box, "standardTab", self, "Standard")
		self.advancedTab = RRGUI.createTabPage(box, "advancedTab", self, "Advanced")
		self.RFUnctionParamGPL_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamGPL_lineEdit", self, "RFunctionParam_GPL", label = "GPL:")
		self.RFUnctionParamdo_log2_lineEdit =  RRGUI.lineEdit(self.standardTab, "RFUnctionParamdo_log2_lineEdit", self, "RFunctionParam_do_log2", label = "do_log2:")
		OWGUI.button(self.controlArea, self, "Commit", callback = self.commitFunction)
	def processGDS(self, data):
		self.require_librarys(["GEOquery"]) 
		if data:
			self.RFunctionParam_GDS=data["data"]
			self.commitFunction()
	def commitFunction(self):
		if self.RFunctionParam_GDS == '': return
		if self.RFunctionParam_do_log2 == '': return
		injection = []
		if self.RFunctionParam_GPL != '':
			string = 'GPL='+str(self.RFunctionParam_GPL)
			injection.append(string)
		if self.RFunctionParam_do_log2 != '':
			string = 'do_log2='+str(self.RFunctionParam_do_log2)
			injection.append(string)
		inj = ','.join(injection)
		self.R(self.Rvariables['GDS2eSet']+'<-GDS2eSet(GDS='+str(self.RFunctionParam_GDS)+','+inj+')')
		self.rSend("GDS2eSet Output", {"data":self.Rvariables["GDS2eSet"]})
