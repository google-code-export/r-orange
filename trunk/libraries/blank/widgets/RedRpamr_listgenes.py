"""
<name>RedRpamr.listgenes</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>pamr:pamr.listgenes</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals

class RedRpamr_listgenes(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "pamr_listgenes", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["pamr.listgenes"])
		self.data = {}
		self.RFunctionParam_data = ''
		self.RFunctionParam_fit = ''
		self.RFunctionParam_fitcv = ''
		self.inputs = [("data", signals.RList.RList, self.processdata),("fit", signals.RModelFit.RModelFit, self.processfit),("fitcv", signals.RModelFit.RModelFit, self.processfitcv)]
		self.outputs = [("pamr.listgenes Output", signals.RVector.RVector)]
		
		self.RFunctionParamthreshold_lineEdit = redRGUI.lineEdit(self.controlArea, label = "threshold:", text = '')
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
		self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "R Output Window")
	def processdata(self, data):
		if not self.require_librarys(["pamr"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_data=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_data=''
	def processfit(self, data):
		if not self.require_librarys(["pamr"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_fit=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_fit=''
	def processfitcv(self, data):
		if not self.require_librarys(["pamr"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_fitcv=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_fitcv=''
	def commitFunction(self):
		if str(self.RFunctionParam_data) == '': return
		if str(self.RFunctionParam_fit) == '': return
		if str(self.RFunctionParam_fitcv) == '': return
		injection = []
		if str(self.RFunctionParamthreshold_lineEdit.text()) != '':
			string = 'threshold='+str(self.RFunctionParamthreshold_lineEdit.text())+''
			injection.append(string)
		inj = ','.join(injection)
		self.R(self.Rvariables['pamr.listgenes']+'<-pamr.listgenes(data='+str(self.RFunctionParam_data)+',fit='+str(self.RFunctionParam_fit)+',fitcv='+str(self.RFunctionParam_fitcv)+','+inj+')')
		self.R('txt<-capture.output('+self.Rvariables['pamr.listgenes']+')')
		self.RoutputWindow.clear()
		tmp = self.R('paste(txt, collapse ="\n")')
		self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
		newData = signals.RVector.RVector(data = self.Rvariables["pamr.listgenes"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
		#newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
		self.rSend("pamr.listgenes Output", newData)
