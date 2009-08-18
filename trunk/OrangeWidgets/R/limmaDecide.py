"""
<name>Limma Decide</name>
<description>Calculates differential expression of genes from an eSet object</description>
<icon>icons/readcel.png</icons>
<priority>2030</priority>
"""

import OWGUI
from OWRpy import *


class limmaDecide(OWRpy):
	settingsList = ['vs', 'dmethod', 'adjmethods', 'foldchange', 'pval', 'Rvariables', 'data', 'sending', 'ebdata']
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		
		self.vs = self.variable_suffix
		self.rsession("require('affy')")
		self.rsession("require('gcrma')")
		self.rsession("require('limma')")
		self.rsession("require('panp')")
		self.dmethod = "separate"
		self.adjmethods = "BH"
		self.foldchange = "0"
		self.pval = "0.05"
		self.data = ''
		self.ebdata = ''
		self.Rvariables = {'gcm':'siggenes_'+self.vs, 'eset_sub':'esetsubset_'+self.vs}
		self.sending = None
		self.loadSettings()
		
		#self.sendMe()
		
		self.inputs = [("eBayes fit", orange.Variable, self.process), ('NormalizedAffybatch', RvarClasses.RDataFrame, self.processeset)]
		self.outputs = [("Gene Change Matrix", RvarClasses.RDataFrame), ("Expression Subset", RvarClasses.RDataFrame)]
		
		#GUI
		#want to have an options part, a data viewing part and a run part
		
		layk = QWidget(self)
		self.controlArea.layout().addWidget(layk)
		grid = QGridLayout()
		grid.setMargin(0)
		layk.setLayout(grid)
		
		optionsbox = OWGUI.widgetBox(self.controlArea, "Options")
		grid.addWidget(optionsbox, 0,0)
		OWGUI.comboBox(optionsbox, self, "dmethod", label = "Combine Method"+"  ", items = ["separate", "global", "hierarchical", "nestedF"], orientation=0)
		OWGUI.comboBox(optionsbox, self, "adjmethods", label = "P-value Adjust Methods", items = ["BH", "none", "fdr", "BY", "holm"], orientation=0)
		OWGUI.lineEdit(optionsbox, self, "pval", label = "Minimum p-value change:", orientation = 0)
		OWGUI.lineEdit(optionsbox, self, "foldchange", label = "Minimum fold change:", orientation = 0)
		
		computebox = OWGUI.widgetBox(self.controlArea, "Compute")
		grid.addWidget(computebox, 1,0)
		self.infoa = OWGUI.widgetLabel(computebox, "Data not yet connected")
		runbutton = OWGUI.button(computebox, self, "Run Analysis", callback = self.runAnalysis, width=200)
		
		#self.table = OWGUI.table(self.controlArea, 0,0)
		
	def process(self, dataset):
		if dataset:
			self.data = dataset['data']
			self.ebdata = dataset
			self.infoa.setText("Data connected")
		else: return
		
	def runAnalysis(self):
		#run the analysis using the parameters selected or input
		self.rsession(self.Rvariables['gcm']+'<-decideTests('+str(self.data)+', method="'+str(self.dmethod)+'", adjust.method="'+str(self.adjmethods)+'", p.value='+str(self.pval)+', lfc='+str(self.foldchange)+')')
		self.infoa.setText("Gene Matrix Processed and sent!  You may use this list to subset in the future.")
		self.sending = {'data':self.Rvariables['gcm']}
		self.send("Gene Change Matrix", self.sending)
		# show table of the significant gene changes
		self.rsession(self.Rvariables['gcm']+'[,2]!=0 -> geneissig')
		self.rsession(self.Rvariables['gcm']+'[geneissig,] -> dfsg')
		
		if self.eset != None:
			self.sendesetsubset()			
		
		#now make the table to do the subsetting
		#first get the data as a python obj

		#self.probesets = r('rownames(dfsg)')
		#self.dirchange = r('dfsg[,1]')
		self.siggenemat = self.rsession('data.frame(Names=rownames(dfsg), Change=dfsg[,1])') #makes a dict object in orange with keys Names and Change
		
		#now put the data into a table in orange
		#self.table = self.createTable()
		mystructKeys = self.siggenemat.keys()
		self.table = MyTable(self.siggenemat, len(self.siggenemat[mystructKeys[0]]), len(self.siggenemat)+1)
		self.table.show()
		
	def createTable(self):
		mystructKeys = self.siggenemat.keys()
		self.table = MyTable(self.siggenemat, len(self.siggenemat[mystructKeys[0]]), len(self.siggenemat))
		
	def processeset(self, data):
		if data:
			self.eset = data['data'] #this is data from an expression matrix or data.frame
			self.olddata = data.copy()
			if self.sending != None and self.ebdata != '':
				self.sendesetsubset()
		else: return
	
	def sendesetsubset(self):
		self.rsession(self.Rvariables['eset_sub']+'<-'+self.eset+'[rownames(dfsg),]')
		self.newdata = self.ebdata.copy()
		self.newdata['data']=self.Rvariables['eset_sub']
		if 'classes' in self.ebdata:
			self.newdata['classes'] = self.ebdata['classes']
		self.send("Expression Subset", self.newdata)
		

		
				
class MyTable(QTableWidget):
	def __init__(self, thestruct, *args):
		QTableWidget.__init__(self, *args)
		self.tdata = thestruct
		self.setmydata()
		
	def setmydata(self):
		n=0
		for key in self.tdata:
			m=0
			for item in self.tdata[key]:
				newitem = QTableWidgetItem(str(item))
				self.setItem(m,n,newitem)
				m += 1
			n += 1