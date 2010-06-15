"""
<name>Test For Correlation (Single)</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>stats:cor.test</RFunctions>
<tags>Parametric</tags>
<icon>stats.png</icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses.RVector as rvec
class cor_test(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "cor_test", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["cor.test"])
		self.data = {}
		self.RFunctionParam_y = ''
		self.RFunctionParam_x = ''
		self.inputs = [("y", rvec.RVector, self.processy),("x", rvec.RVector, self.processx)]
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
		self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "RoutputWindow")
	def processy(self, data):
		if not self.require_librarys(["stats"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_y=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_y=''
	def processx(self, data):
		if not self.require_librarys(["stats"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_x=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_x=''
	def commitFunction(self):
		if str(self.RFunctionParam_y) == '': return
		if str(self.RFunctionParam_x) == '': return
		injection = []
		inj = ','.join(injection)
		self.R(self.Rvariables['cor.test']+'<-cor.test(y=as.numeric(as.character('+str(self.RFunctionParam_y)+')),x=as.numeric(as.character('+str(self.RFunctionParam_x)+')),'+','+inj+')')
		self.R('txt<-capture.output('+self.Rvariables['cor.test']+')')
		self.RoutputWindow.clear()
		tmp = self.R('paste(txt, collapse ="\n")')
		self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
