"""
<name>rug</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>graphics:rug</RFunctions>
<tags>Prototypes</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class rug(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "rug", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["rug"])
		self.data = {}
		self.RFunctionParam_y = ''
		self.RFunctionParam_x = ''
		self.inputs = [("y", signals.RCoxphFit, self.processy),("x", signals.RVector, self.processx)]
		self.outputs = [("rug Output", signals.RCoxphFit)]
		
		self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
		box = redRGUI.tabWidget(self.controlArea)
		self.standardTab = box.createTabPage(name = "Standard")
		self.advancedTab = box.createTabPage(name = "Advanced")
		self.RFunctionParamxlab_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "xlab:", text = 'NULL')
		self.RFunctionParamspan_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "span:", text = '2/3')
		self.RFunctionParamdegree_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "degree:", text = '1')
		self.RFunctionParamfamily_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "family:", text = '['symmetric', 'gaussian']')
		self.RFunctionParamquiet_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "quiet:", text = 'getOption("warn")<0')
		self.RFunctionParamcol_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "col:", text = 'par("fg")')
		self.RFunctionParamticksize_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "ticksize:", text = '0.03')
		self.RFunctionParamylab_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "ylab:", text = 'NULL')
		self.RFunctionParamevaluation_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "evaluation:", text = '50')
		self.RFunctionParamylim_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "ylim:", text = '')
		self.RFunctionParamlwd_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "lwd:", text = '0.5')
		self.RFunctionParamside_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "side:", text = '1')
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
	def processy(self, data):
		if not self.require_librarys(["graphics"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_y=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_y=''
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
		if str(self.RFunctionParam_y) == '': return
		if str(self.RFunctionParam_x) == '': return
		injection = []
		if str(self.RFunctionParamxlab_lineEdit.text()) != '':
			string = 'xlab='+str(self.RFunctionParamxlab_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamspan_lineEdit.text()) != '':
			string = 'span='+str(self.RFunctionParamspan_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamdegree_lineEdit.text()) != '':
			string = 'degree='+str(self.RFunctionParamdegree_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamfamily_lineEdit.text()) != '':
			string = 'family='+str(self.RFunctionParamfamily_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamquiet_lineEdit.text()) != '':
			string = 'quiet='+str(self.RFunctionParamquiet_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamcol_lineEdit.text()) != '':
			string = 'col='+str(self.RFunctionParamcol_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamticksize_lineEdit.text()) != '':
			string = 'ticksize='+str(self.RFunctionParamticksize_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamylab_lineEdit.text()) != '':
			string = 'ylab='+str(self.RFunctionParamylab_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamevaluation_lineEdit.text()) != '':
			string = 'evaluation='+str(self.RFunctionParamevaluation_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamylim_lineEdit.text()) != '':
			string = 'ylim='+str(self.RFunctionParamylim_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamlwd_lineEdit.text()) != '':
			string = 'lwd='+str(self.RFunctionParamlwd_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamside_lineEdit.text()) != '':
			string = 'side='+str(self.RFunctionParamside_lineEdit.text())+''
			injection.append(string)
		inj = ','.join(injection)
		self.R(self.Rvariables['rug']+'<-rug(y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+','+inj+')')
		newData = signals.RCoxphFit(data = self.Rvariables["rug"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
		#newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
		self.rSend("rug Output", newData)
