"""
<name>survdiff</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
import RRGUI 
class survdiff(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.RFunctionParam_subset = ""
		self.RFunctionParam_formula = ""
		self.RFunctionParam_rho = "0"
		self.RFunctionParam_na_action = ""
		self.loadSettings() 
		self.RFunctionParam_data = ''
		self.inputs = [("data", RvarClasses.RVariable, self.processdata)]
		
		box = OWGUI.widgetBox(self.controlArea, "Widget Box")
		self.RFUnctionParamsubset_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParamsubset_lineEdit", self, "RFunctionParam_subset", label = "subset:")
		self.RFUnctionParamformula_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParamformula_lineEdit", self, "RFunctionParam_formula", label = "formula:")
		self.RFUnctionParamrho_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParamrho_lineEdit", self, "RFunctionParam_rho", label = "rho:")
		self.RFUnctionParamna_action_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParamna_action_lineEdit", self, "RFunctionParam_na_action", label = "na_action:")
		OWGUI.button(box, self, "Commit", callback = self.commitFunction)
		self.RoutputWindow = RRGUI.textEdit("RoutputWindow", self)
		box.layout().addWidget(self.RoutputWindow)
	def processdata(self, data):
		self.require_librarys(["survival"]) 
		if data:
			self.RFunctionParam_data=data["data"]
			self.commitFunction()
	def commitFunction(self):
		if self.RFunctionParam_data == '': return
		self.R('txt<-capture.output('+'survdiff(data='+str(self.RFunctionParam_data)+',subset='+str(self.RFunctionParam_subset)+',formula='+str(self.RFunctionParam_formula)+',rho='+str(self.RFunctionParam_rho)+',na_action='+str(self.RFunctionParam_na_action)+'))')
		self.RoutputWindow.clear()
		tmp = self.R('paste(txt, collapse ="\n")')
		self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
