"""
<name>rank</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
import redRGUI 
class rank(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["rank"])
		self.RFunctionParam_ties_method = ''
		self.RFunctionParam_na_last = "TRUE"
		self.loadSettings() 
		self.RFunctionParam_x = ''
		self.inputs = [("x", RvarClasses.RVariable, self.processx)]
		self.outputs = [("rank Output", RvarClasses.RVariable)]
		
		self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
		box = redRGUI.tabWidget(self.controlArea)
		self.standardTab = box.createTabPage(name = "Standard")
		self.advancedTab = box.createTabPage(name = "Advanced")
		self.RFunctionParamties_method_comboBox = redRGUI.comboBox(self.standardTab, label = "ties_method:", items = ['average', 'first', 'random', 'max', 'min'])
		self.RFunctionParamna_last_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "na_last:")
		redRGUI.button(self.controlArea, self, "Commit", callback = self.commitFunction)
		redRGUI.button(self.controlArea, self, "Report", callback = self.sendReport)
	def processx(self, data):
		if data:
			self.RFunctionParam_x=data["data"]
			self.commitFunction()
	def commitFunction(self):
		if str(self.RFunctionParam_x) == '': return
		injection = []
		if str(self.RFunctionParamties_method_comboBox.currentText()) != '':
			string = 'ties.method="'+str(self.RFunctionParamties_method_comboBox.currentText())+'"'
			injection.append(string)
		if str(self.RFunctionParamna_last_lineEdit.text()) != '':
			string = 'na.last='+str(self.RFunctionParamna_last_lineEdit.text())
			injection.append(string)
		inj = ','.join(injection)
		self.R(self.Rvariables['rank']+'<-rank(x='+str(self.RFunctionParam_x)+','+inj+')')
		self.rSend("rank Output", {"data":self.Rvariables["rank"]})
	def compileReport(self):
		self.reportSettings("Input Settings",[("x", self.RFunctionParam_x)])
		self.reportSettings('Function Settings', [('ties_method',str(self.RFunctionParam_ties_method))])
		self.reportSettings('Function Settings', [('na_last',str(self.RFunctionParam_na_last))])
		self.reportRaw(self.Rvariables["rank"])
	def sendReport(self):
		self.compileReport()
		self.showReport()
