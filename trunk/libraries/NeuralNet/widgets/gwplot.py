"""
<name>Generalized Weights Plot</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<Description>gwplot, a method for objects of class nn, typically produced by neuralnet. Plots the generalized
weights (Intrator and Intrator, 1993) for one specific covariate and one response variable.</Description>
<RFunctions>neuralnet:gwplot</RFunctions>
<tags>Neural Net, Prototypes</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI 
class gwplot(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "gwplot", wantMainArea = 0, resizingEnabled = 1)
		self.RFunctionParam_x = ''
		self.inputs = [("x", signals.NeuralNet.RNeuralNet, self.processx)]
		
		self.standardTab = self.controlArea
		self.RFunctionParamotherParams_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "Other Parameters:", text = '', toolTip = 'Place any parameters to be plotted from gwplot')
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
	def processx(self, data):
		if not self.require_librarys(["neuralnet"]):
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
		if str(self.RFunctionParamotherParams_lineEdit.text()) != '':
			string = str(self.RFunctionParamotherParams_lineEdit.text())
			injection.append(string)
		inj = ','.join(injection)
		self.Rplot('gwplot(x='+str(self.RFunctionParam_x)+','+inj+')')
