"""
<name>Transpose</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Transposes a data table and sends.</description>
<priority>2040</priority>
"""
from OWRpy import * 
import OWGUI 
class t(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["t"])
		self.RFunctionParam_x = ''
		self.inputs = [("x", RvarClasses.RDataFrame, self.processx)]
		self.outputs = [("t Output", RvarClasses.RDataFrame)]
		
		box = OWGUI.widgetBox(self.controlArea, "Widget Box")
		OWGUI.button(box, self, "Commit", callback = self.commitFunction)
	def processx(self, data):
		if data:
			self.RFunctionParam_x=data["data"]
			self.commitFunction()
	def commitFunction(self):
		if self.x == '': return
		self.R(self.Rvariables['t']+'<-as.data.frame(t(x='+str(self.RFunctionParam_x)+'))')
		self.rSend("t Output", {"data":self.Rvariables["t"]})
