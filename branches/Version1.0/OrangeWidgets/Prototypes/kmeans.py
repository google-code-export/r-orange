"""
<name>kmeans</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
class kmeans(OWRpy): 
	def __init__(self, parent=None, signalManager=None):
		settingsList = []
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.nstart = "1"
		self.iter.max = "10"
		self.centers = ""
		self.algorithm = 0
		self.inputs = [("x", RvarClasses.RVariable, self.processx)]
		self.outputs = [("kmeans Output", RvarClasses.RVariable)]
		
		box = OWGUI.widgetBox(self.controlArea, "Widget Box")
		OWGUI.lineEdit(box, self, "nstart", label = "nstart:")
		OWGUI.lineEdit(box, self, "iter.max", label = "iter.max:")
		OWGUI.lineEdit(box, self, "centers", label = "centers:")
		OWGUI.comboBox(box, self, "algorithm", label = "algorithm:", items = ['Hartigan-Wong', 'Lloyd', 'Forgy', 'MacQueen'])
		OWGUI.button(box, self, "Commit", callback = self.commitFunction)
	def processx(self, data):
		if data:
			self.x=data["data"]
			self.commitFunction()
	def commitFunction(self):
		self.R(self.Rvariables['kmeans']+'&lt;-kmeans(x='+str(self.x)+',nstart='+str(self.nstart)+',iter.max='+str(self.iter.max)+',centers='+str(self.centers)+',algorithm='+str(self.algorithm)+',)')
		self.rSend("kmeans Output", {"data":self.Rvariables["kmeans"]})
