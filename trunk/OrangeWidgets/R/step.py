"""
<name>step</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
class step(OWRpy): 
	def __init__(self, parent=None, signalManager=None):
		settingsList = []
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		#self.... = ""
		self.direction = 0
		self.scale = "0"
		self.trace = "1"
		self.k = "2"
		self.keep = "NULL"
		self.steps = "1000"
		self.scope = ""
		self.inputs = [("object", RvarClasses.RVariable, self.processobject),]
		self.outputs = [("step Output", RvarClasses.RVariable)]
		
		box = OWGUI.widgetBox(self.controlArea, "Widget Box")
		#OWGUI.lineEdit(box, self, "...", label = "...:")
		OWGUI.comboBox(box, self, "direction", label = "direction:", items = ['both', 'backward', 'forward'])
		OWGUI.lineEdit(box, self, "scale", label = "scale:")
		OWGUI.lineEdit(box, self, "trace", label = "trace:")
		OWGUI.lineEdit(box, self, "k", label = "k:")
		OWGUI.lineEdit(box, self, "keep", label = "keep:")
		OWGUI.lineEdit(box, self, "steps", label = "steps:")
		OWGUI.lineEdit(box, self, "scope", label = "scope:")
		OWGUI.button(box, self, "Commit", callback = self.commitFunction)
	def processobject(self, data):
		if data:
			self.object=data["data"]
			self.commitFunction()
	def commitFunction(self):
		self.R(self.Rvariables['step']+'<-step(object='+str(self.object)+',direction='+str(self.direction)+',scale='+str(self.scale)+',trace='+str(self.trace)+',k='+str(self.k)+',keep='+str(self.keep)+',steps='+str(self.steps)+',scope='+str(self.scope)+',)')
		self.rSend("step Output", {"data":self.Rvariables["step"]})