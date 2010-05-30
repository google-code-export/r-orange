"""
<name>cox.zph</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>survival:cox.zph</RFunctions>
<tags>Prototypes</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class cox_zph(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "cox_zph", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["cox.zph"])
		self.data = {}
		self.RFunctionParam_fit = ''
		self.inputs = [("fit", signals.RCoxphFit, self.processfit)]
		
		self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
		box = redRGUI.tabWidget(self.controlArea)
		self.standardTab = box.createTabPage(name = "Standard")
		self.advancedTab = box.createTabPage(name = "Advanced")
		self.RFunctionParamglobal_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "global:")
		self.RFunctionParamtransform_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "transform:")
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
		self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "RoutputWindow")
	def processfit(self, data):
		if not self.require_librarys(["survival"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_fit=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_fit=''
	def commitFunction(self):
		if str(self.RFunctionParam_fit) == '': return
		injection = []
		if str(self.RFunctionParamglobal_lineEdit.text()) != '':
			string = 'global='+str(self.RFunctionParamglobal_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamtransform_lineEdit.text()) != '':
			string = 'transform='+str(self.RFunctionParamtransform_lineEdit.text())+''
			injection.append(string)
		inj = ','.join(injection)
		self.R(self.Rvariables['cox.zph']+'<-cox.zph(fit='+str(self.RFunctionParam_fit)+','+inj+')')
		self.R('txt<-capture.output('+self.Rvariables['cox.zph']+')')
		self.RoutputWindow.clear()
		tmp = self.R('paste(txt, collapse ="\n")')
		self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
