"""
<name>lines</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
import RRGUI 
class lines(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.loadSettings() 
		self.RFunctionParam_x = ''
		self.inputs = [("x", RvarClasses.RVariable, self.processx)]
		
		box = RRGUI.tabWidget(self.controlArea, None, self)
		self.standardTab = RRGUI.createTabPage(box, "standardTab", self, "Standard")
		self.advancedTab = RRGUI.createTabPage(box, "advancedTab", self, "Advanced")
		OWGUI.button(self.controlArea, self, "Commit", callback = self.commitFunction)
	def processx(self, data):
		if data:
			self.RFunctionParam_x=data["data"]
			self.commitFunction()
	def commitFunction(self):
		if self.RFunctionParam_x == '': return
		injection = []
		inj = ','.join(injection)
		self.R('lines(x='+str(self.RFunctionParam_x)+','+inj+')')
