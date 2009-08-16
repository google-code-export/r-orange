"""
<name>Merge RExampleTables</name>
<description>Merges or subsets two RExampleTables depending on options.</description>
<icon>icons/rma.png</icons>
<priority>3010</priority>
"""

from rpy_options import set_options
set_options(RHOME='c:/progra~1/r/R-2.6.2/')
from rpy import *
from OWWidget import *
import OWGUI
r.require('affy')

class mergeR(OWWidget):
	settingsList = ['vs']
	def __init__(self, parent=None, signalManager=None):
		OWWidget.__init__(self, parent, signalManager, "Sample Data")
		
		self.inputs = [("RExampleTable A", orange.Variable, self.processA), ("RExampleTable B", orange.Variable, self.processB)]
		self.outputs = [("ExampleTable", orange.Variable)]
		
		self.dataA = None
		self.dataB = None
		self.rand = str(random.random())
		self.colAsel = ''
		self.colBsel = ''
		
		#GUI
		layk = QWidget(self)
		self.controlArea.layout().addWidget(layk)
		grid = QGridLayout()
		grid.setMargin(0)
		layk.setLayout(grid)
		
		pickA = OWGUI.widgetBox(self.controlArea, "Select Columns to Merge From A")
		grid.addWidget(pickA, 0,0)
		self.colA = OWGUI.listBox(pickA, self, callback = self.setcolA)
		
		pickB = OWGUI.widgetBox(self.controlArea, "Select Columns to Merge From B")
		grid.addWidget(pickB, 0,1)
		self.colB = OWGUI.listBox(pickB, self, callback = self.setcolB)
		
		runbox = OWGUI.widgetBox(self.controlArea, "Run")
		OWGUI.button(runbox, self, "Run", callback = self.run)
		self.infoa = OWGUI.widgetLabel(runbox, "output")
		
		
	def processA(self, data):
		if data:
			self.dataA = str(data['data'])
			self.run()
			colsA = r('colnames('+self.dataA+')') #collect the sample names to make the differential matrix
			for v in colsA:
				self.colA.addItem(v)
		else: return
			#self.sendNothing

	def processB(self, data):
		if data:
			self.dataB = str(data['data'])
			self.run()
			colsB = r('colnames('+self.dataB+')') #collect the sample names to make the differential matrix
			for v in colsB:
				self.colB.addItem(v)
		else: return
			#self.sendNothing
			
	def run(self):
		if self.dataA and self.dataB:
			h = r('intersect(names('+self.dataA+'), names('+self.dataB+'))')
			if len(h) == 0: 
				if self.colAsel == '' and self.colBsel == '': 
					self.infoa.setText('columns not selected yet')
				elif self.colAsel != '' and self.colBsel != '':
					r('mergetab_'+self.rand+'<-merge('+self.dataA+', '+self.dataB+', by.x="'+self.colAsel+'", by.y="'+self.colBsel+'")')
					mtab = {'data':'mergetab_'+self.rand}
					self.send("ExampleTable", mtab)
				elif self.colAsel == '' and self.colBsel != '':
					r('mergetab_'+self.rand+'<-'+self.dataA+'['+self.dataB+'[,"'+self.colBsel+'"],]')
					mtab = {'data':'mergetab_'+self.rand}
					self.send("ExampleTable", mtab)
				else: return

			else:
				r('mergetab_'+self.rand+'<-merge('+self.dataA+', '+self.dataB+')')
				mtab = {'data':'mergetab_'+self.rand}
				self.send("ExampleTable", mtab)
		else: return 
	
	def setcolA(self):
		self.colAsel = str(self.colA.selectedItems()[0].text())
		self.infoa.setText(self.colAsel)
	def setcolB(self):
		self.colBsel = str(self.colB.selectedItems()[0].text())
		self.infoa.setText(self.colBsel)