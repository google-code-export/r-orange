"""
<name>scatter.smooth</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>stats:scatter.smooth</RFunctions>
<tags>Plotting</tags>
<icon>icons/plot.png</icon>
"""
from OWRpy import * 
import redRGUI 
class scatter_smooth(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "scatter_smooth", wantMainArea = 0, resizingEnabled = 1)
		self.RFunctionParam_y = ''
		self.RFunctionParam_x = ''
		self.inputs = [("y", signals.RVector, self.processy),("x", signals.RVector, self.processx)]
		
		box = redRGUI.tabWidget(self.controlArea)
		self.standardTab = box.createTabPage(name = "Standard")
		self.advancedTab = box.createTabPage(name = "Advanced")
		self.RFunctionParamxlab_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "xlab:", text = 'NULL')
		self.RFunctionParamspan_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "span:", text = '2/3')
		self.RFunctionParamdegree_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "degree:", text = '1')
		self.RFunctionParamfamily_comboBox =  redRGUI.comboBox(self.standardTab,  label = "family:", items = ['symmetric', 'gaussian'])
		self.RFunctionParamylab_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "ylab:", text = 'NULL')
		self.RFunctionParamevaluation_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "evaluation:", text = '50')
		self.RFunctionParamylim_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "ylim:", text = '')
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
	def processy(self, data):
		if not self.require_librarys(["stats"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_y=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_y=''
	def processx(self, data):
		if not self.require_librarys(["stats"]):
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
		if str(self.RFunctionParamfamily_comboBox.currentText()) != '':
			string = 'family=\''+str(self.RFunctionParamfamily_comboBox.currentText())+'\''
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
		inj = ','.join(injection)
		self.R('scatter.smooth(y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+','+inj+')')
