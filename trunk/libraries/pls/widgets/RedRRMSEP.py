"""
<name>RedRRMSEP</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>pls:RMSEP</RFunctions>
<tags>PLS</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals

class RedRRMSEP(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "RMSEP", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["RMSEP"])
		self.data = {}
		self.RFunctionParam_object = ''
		self.inputs = [("object", signals.RModelFit.RModelFit, self.processobject)]
		self.outputs = [("RMSEP Output", signals.RModelFit.RModelFit)]
		
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
		self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "R Output Window")
	def processobject(self, data):
		if not self.require_librarys(["pls"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_object=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_object=''
	def commitFunction(self):
		if str(self.RFunctionParam_object) == '': return
		
		self.R(self.Rvariables['RMSEP']+'<-RMSEP(object='+str(self.RFunctionParam_object)+')')
		self.R('txt<-capture.output('+self.Rvariables['RMSEP']+')')
		self.RoutputWindow.clear()
		tmp = self.R('paste(txt, collapse ="\n")')
		self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
		newData = signals.RModelFit.RModelFit(data = self.Rvariables["RMSEP"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
		#newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
		self.rSend("RMSEP Output", newData)
