"""
<name>data.frame</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
class data.frame(OWRpy): 
	def __init__(self, parent=None, signalManager=None):
		settingsList = []
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.outputs = [("data.frame Output", RvarClasses.RVariable)]
		
		box = OWGUI.widgetBox(self.controlArea, "Widget Box")
		OWGUI.button(box, self, "Commit", callback = self.commitFunction)
	def commitFunction(self):
		self.R(self.Rvariables['data.frame']+'&lt;-data.frame()')
		self.rSend("data.frame Output", {"data":self.Rvariables["data.frame"]})
