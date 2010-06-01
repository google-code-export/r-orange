"""
<name>dotchart</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>graphics:dotchart</RFunctions>
<tags>Prototypes</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI 
class dotchart(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "dotchart", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["dotchart"])
		self.data = {}
		self.RFunctionParam_x = ''
		self.inputs = [("x", signals.RMatrix, self.processx)]
		
		self.standardTab = self.controlArea
		self.RFunctionParamxlab_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "xlab:", text = 'NULL')
		self.RFunctionParambg_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "bg:", text = 'par("bg")')
		#self.RFunctionParamxlim_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "xlim:", text = 'range(x[is.finite(x)])')
		self.RFunctionParamcolor_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "color:", text = 'par("fg")')
		self.RFunctionParamlabels_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "labels:", text = 'NULL')
		self.RFunctionParamlcolor_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "lcolor:", text = '"gray"')
		self.RFunctionParampch_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "pch:", text = '21')
		self.RFunctionParamylab_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "ylab:", text = 'NULL')
		self.RFunctionParammain_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "main:", text = 'NULL')
		self.RFunctionParamcex_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "cex:", text = 'par("cex")')
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
		if str(self.RFunctionParamxlab_lineEdit.text()) != '':
			string = 'xlab='+str(self.RFunctionParamxlab_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParambg_lineEdit.text()) != '':
			string = 'bg='+str(self.RFunctionParambg_lineEdit.text())+''
			injection.append(string)
		# if str(self.RFunctionParamxlim_lineEdit.text()) != '':
			# string = 'xlim='+str(self.RFunctionParamxlim_lineEdit.text())+''
			# injection.append(string)
		if str(self.RFunctionParamcolor_lineEdit.text()) != '':
			string = 'color='+str(self.RFunctionParamcolor_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamlabels_lineEdit.text()) != '':
			string = 'labels='+str(self.RFunctionParamlabels_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamlcolor_lineEdit.text()) != '':
			string = 'lcolor='+str(self.RFunctionParamlcolor_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParampch_lineEdit.text()) != '':
			string = 'pch='+str(self.RFunctionParampch_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamylab_lineEdit.text()) != '':
			string = 'ylab='+str(self.RFunctionParamylab_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParammain_lineEdit.text()) != '':
			string = 'main='+str(self.RFunctionParammain_lineEdit.text())+''
			injection.append(string)
		if str(self.RFunctionParamcex_lineEdit.text()) != '':
			string = 'cex='+str(self.RFunctionParamcex_lineEdit.text())+''
			injection.append(string)
		inj = ','.join(injection)
		self.Rplot('dotchart(x='+str(self.RFunctionParam_x)+','+inj+')')
		
