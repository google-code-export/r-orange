"""
<name>image</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>graphics:image</RFunctions>
<tags>Prototypes</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI 
class image(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "image", wantMainArea = 0, resizingEnabled = 1)
		self.RFunctionParam_x = ''
		self.inputs = [("x", signals.RMatrix, self.processx)]
		
		box = redRGUI.tabWidget(self.controlArea)
		self.standardTab = box.createTabPage(name = "Standard")
		self.advancedTab = box.createTabPage(name = "Advanced")
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
	def processx(self, data):
		if not self.require_librarys(["graphics"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_x=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_x=''
	def commitFunction(self):
		if str(self.RFunctionParam_x) == '': return
		injection = []
		inj = ','.join(injection)
		self.Rplot('image(x='+str(self.RFunctionParam_x)+','+inj+')')
