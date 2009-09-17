"""
<name>t.test</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
class t.test(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["t.test"])
		self.RFunctionParam_x = ''
		self.inputs = [("x", RvarClasses.RVariable, self.processx)]
		self.outputs = [("t.test Output", RvarClasses.RVariable)]
		
		box = OWGUI.widgetBox(self.controlArea, "Widget Box")
		OWGUI.button(box, self, "Commit", callback = self.commitFunction)
	def processx(self, data):
		if data:
			self.RFunctionParam_x=data["data"]
			self.commitFunction()
	def commitFunction(self):
		if self.x == '': return
		self.R(+self.Rvariables['t.test']+'<-t.test(x='+str(self.RFunctionParam_x)+')')
		self.rSend("t.test Output", {"data":self.Rvariables["t.test"]})
