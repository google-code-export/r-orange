"""
<name>RedRisa</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>isa2:isa</RFunctions>
<tags>Prototypes</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class RedRisa(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "isa", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["isa"])
		self.data = {}
		self.RFunctionParam_data = ''
		self.inputs = [("data", signals.RMatrix, self.processdata)]
		self.outputs = [("isa Output", signals.RModelFit)]
		
		self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
		box = redRGUI.tabWidget(self.controlArea)
		self.standardTab = box.createTabPage(name = "Standard")
		self.advancedTab = box.createTabPage(name = "Advanced")
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
	def processdata(self, data):
		if not self.require_librarys(["isa2"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_data=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_data=''
	def commitFunction(self):
		if str(self.RFunctionParam_data) == '': return
		
		self.R(self.Rvariables['isa']+'<-isa(data='+str(self.RFunctionParam_data)+')')
		newData = signals.RModelFit(data = self.Rvariables["isa"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
		#newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
		self.rSend("isa Output", newData)
