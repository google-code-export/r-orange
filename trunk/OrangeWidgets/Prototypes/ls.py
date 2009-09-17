"""
<name>ls</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
class ls(OWRpy): 
	def __init__(self, parent=None, signalManager=None):
		settingsList = []
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.outputs = [("ls Output", RvarClasses.RVariable)]
		
		box = OWGUI.widgetBox(self.controlArea, "Widget Box")
		OWGUI.button(box, self, "Commit", callback = self.commitFunction)
	def commitFunction(self):
		self.R(self.Rvariables['ls']+'&lt;-ls()')
		self.rSend("ls Output", {"data":self.Rvariables["ls"]})
