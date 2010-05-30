"""
<name>inspect</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>asuR:inspect</RFunctions>
<tags>Prototypes</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class inspect(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "inspect", wantMainArea = 0, resizingEnabled = 1)
		self.RFunctionParam_mymodel = ''
		self.inputs = [("mymodel", signals.RModelFit, self.processmymodel)]
		
		self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
		box = redRGUI.tabWidget(self.controlArea)
		self.standardTab = box.createTabPage(name = "Standard")
		self.advancedTab = box.createTabPage(name = "Advanced")
		self.RFunctionParamwhich_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "which:", text = 'all')
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
	def processmymodel(self, data):
		if not self.require_librarys(["asuR"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_mymodel=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_mymodel=''
	def commitFunction(self):
		if str(self.RFunctionParam_mymodel) == '': return
		injection = []
		if str(self.RFunctionParamwhich_lineEdit.text()) != '':
			string = 'which=\''+str(self.RFunctionParamwhich_lineEdit.text())+'\''
			injection.append(string)
		inj = ','.join(injection)
		self.R('inspect(mymodel='+str(self.RFunctionParam_mymodel)+')')
