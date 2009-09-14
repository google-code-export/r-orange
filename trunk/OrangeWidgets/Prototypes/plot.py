"""
<name>plot</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
class plot(OWRpy): 
	def __init__(self, parent=None, signalManager=None):
		settingsList = []
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.y = ''
		self.x = ''
		self.inputs = [("y", RvarClasses.RVariable, self.processy),("x", RvarClasses.RVariable, self.processx)]
		
		box = OWGUI.widgetBox(self.controlArea, "Widget Box")
		OWGUI.button(box, self, "Commit", callback = self.commitFunction)
	def processy(self, data):
		if data:
			self.y=data["data"]
			self.commitFunction()
	def processx(self, data):
		if data:
			self.x=data["data"]
			self.commitFunction()
	def commitFunction(self):
		if self.y == '': return
		if self.x == '': return
		self.R('plot(y='+str(self.y)+',x='+str(self.x)+',)')
