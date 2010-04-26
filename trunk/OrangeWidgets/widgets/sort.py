"""
<name>sort</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>base:sort</RFunctions>
<tags>Prototypes</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class sort(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["sort"])
		self.data = {}
		self.loadSettings() 
		self.RFunctionParam_x = ''
		self.inputs = [("x", RvarClasses.RDataFrame, self.processx)]
		self.outputs = [("sort Output", RvarClasses.RDataFrame)]
		
		self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
		box = redRGUI.tabWidget(self.controlArea)
		self.standardTab = box.createTabPage(name = "Standard")
		self.advancedTab = box.createTabPage(name = "Advanced")
		self.RFunctionParamdecreasing_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "decreasing:", text = 'FALSE')
		redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
	def processx(self, data):
		self.require_librarys(["base"]) 
		if data:
			self.RFunctionParam_x=data.data
			#self.data = data.copy()
			self.commitFunction()
		else:
			self.RFunctionParam_x=''
	def commitFunction(self):
		if str(self.RFunctionParam_x) == '': return
		injection = []
		if str(self.RFunctionParamdecreasing_lineEdit.text()) != '':
			string = 'decreasing='+str(self.RFunctionParamdecreasing_lineEdit.text())+''
			injection.append(string)
		inj = ','.join(injection)
        self.R('s<-sort(x='+str(self.RFunctionParam_x)+','+inj+')')
		self.R(self.Rvariables['sort']+'<-'+self.RFunctionParam_x+'[s,]')
		newData = RvarClasses.RDataFrame(data = self.Rvariables["sort"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
		#newData.dictAttrs = self.data.dictAttrs.copy()  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
		self.rSend("sort Output", newData)
