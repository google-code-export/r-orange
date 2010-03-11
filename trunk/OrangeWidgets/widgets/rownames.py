"""
<name>rownames</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import redRGUI 
class rownames(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["rownames"])
		self.data = {}
		self.loadSettings() 
		self.RFunctionParam_x = ''
		self.inputs = [("x", RvarClasses.RDataFrame, self.processx)]
		self.outputs = [("rownames Output", RvarClasses.RVector)]
		
		self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
		box = redRGUI.tabWidget(self.controlArea)
		self.standardTab = box.createTabPage(name = "Standard")
		self.advancedTab = box.createTabPage(name = "Advanced")
		self.RFunctionParamprefix_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "prefix:")
		self.RFunctionParamdo_NULL_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "do_NULL:")
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
		redRGUI.button(self.controlArea, "Report", callback = self.sendReport)
	def processx(self, data):
		if data:
			self.RFunctionParam_x=data["data"]
			self.data = data.copy()
			self.commitFunction()
	def commitFunction(self):
		if str(self.RFunctionParam_x) == '': return
		injection = []
		if str(self.RFunctionParamprefix_lineEdit.text()) != '':
			string = 'prefix='+str(self.RFunctionParamprefix_lineEdit.text())
			injection.append(string)
		if str(self.RFunctionParamdo_NULL_lineEdit.text()) != '':
			string = 'do_NULL='+str(self.RFunctionParamdo_NULL_lineEdit.text())
			injection.append(string)
		inj = ','.join(injection)
		self.R(self.Rvariables['rownames']+'<-rownames(x='+str(self.RFunctionParam_x)+','+inj+')')
		self.data["data"] = self.Rvariables["rownames"]
		self.rSend("rownames Output", self.data)
	def compileReport(self):
		self.reportSettings("Input Settings",[("x", self.RFunctionParam_x)])
		self.reportSettings('Function Settings', [('prefix',str(self.RFunctionParamprefix_lineEdit.text()))])
		self.reportSettings('Function Settings', [('do_NULL',str(self.RFunctionParamdo_NULL_lineEdit.text()))])
		self.reportRaw(self.Rvariables["rownames"])
	def sendReport(self):
		self.compileReport()
		self.showReport()
