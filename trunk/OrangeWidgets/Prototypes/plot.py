"""
<name>plot</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
class plot(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.RFunctionParam_y = ''
		self.RFunctionParam_x = ''
		self.inputs = [("y", RvarClasses.RVariable, self.processy),("x", RvarClasses.RVariable, self.processx)]
		
		box = OWGUI.widgetBox(self.controlArea, "Widget Box")
		OWGUI.button(box, self, "Commit", callback = self.commitFunction)
	def processy(self, data):
		if data:
			self.RFunctionParam_y=data["data"]
			self.commitFunction()
	def processx(self, data):
		if data:
			self.RFunctionParam_x=data["data"]
			self.commitFunction()
	def commitFunction(self):
		if self.RFunctionParam_y == '': return
		if self.RFunctionParam_x == '': return
		self.R('plot(y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+')')
