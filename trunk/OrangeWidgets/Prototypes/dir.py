<pre>"""
&lt;name&gt;dir&lt;/name&gt;
&lt;author&gt;Generated using Widget Maker written by Kyle R. Covington&lt;/author&gt;
"""
from OWRpy import * 
import OWGUI 
class dir(OWRpy): 
	def __init__(self, parent=None, signalManager=None):
		settingsList = []
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["dir"])
		self.outputs = [("dir Output", RvarClasses.RVariable)]
		
		box = OWGUI.widgetBox(self.controlArea, "Widget Box")
		OWGUI.button(box, self, "Commit", callback = self.commitFunction)
	def commitFunction(self):
		self.R(self.Rvariables['dir']+'&lt;-dir()')
		self.rSend("dir Output", {"data":self.Rvariables["dir"]})
</pre>