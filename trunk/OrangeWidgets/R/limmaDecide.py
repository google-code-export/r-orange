"""
<name>Limma Decide</name>
<description>Calculates differential expression of genes from an eSet object</description>
<icon>icons/readcel.png</icons>
<priority>2030</priority>
"""

from rpy_options import set_options
set_options(RHOME='c:/progra~1/r/R-2.6.2/')
from rpy import *
from OWWidget import *
import OWGUI
import random
r.require('affy')
r.require('gcrma')
r.require('limma')
r.require('panp')

class limmaDecide(OWWidget):
	def __init__(self, parent=None, signalManager=None):
		OWWidget.__init__(self, parent, signalManager, "Sample Data")
		self.inputs = [("eBayes fit", orange.Variable, self.process), ('NormalizedAffybatch',orange.Variable, self.processeset)]
		self.outputs = [("Gene Change Matrix", orange.Variable), ("Expression Subset", orange.Variable)]
		
		self.rand = random.random()
		self.data = None
		self.dmethod = "separate"
		self.adjmethods = "BH"
		self.foldchange = "0"
		self.pval = "0.05"
		self.sending = None
		self.eset = None
		
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
		
		self.table = OWGUI.table(self.controlArea, 0,0)
		
	def process(self, dataset):
		if dataset:
			self.data = dataset['data'][0]
			self.olddata = dataset
			self.infoa.setText("Data connected")
		else: return
		
	def runAnalysis(self):
		#run the analysis using the parameters selected or input
		r('siggenes_'+str(self.rand)+'<-decideTests('+str(self.data)+', method="'+str(self.dmethod)+'", adjust.method="'+str(self.adjmethods)+'", p.value='+str(self.pval)+', lfc='+str(self.foldchange)+')')
		self.infoa.setText("Gene Matrix Processed and sent!  You may use this list to subset in the future.")
		self.sending = {'data':['siggenes_'+str(self.rand)]}
		r('siggenes_'+str(self.rand)+'[,2]!=0 -> geneissig')
		r('siggenes_'+str(self.rand)+'[geneissig,] -> dfsg')
		if self.eset != None:
			self.sendesetsubset()
		else:
			self.send("Gene Change Matrix", self.sending)
		
		#now make the table to do the subsetting
		#first get the data as a python obj

		#self.probesets = r('rownames(dfsg)')
		#self.dirchange = r('dfsg[,1]')
		self.siggenemat = r('data.frame(Names=rownames(dfsg), Change=dfsg[,1])') #makes a dict object in orange with keys Names and Change
		
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
			self.eset = data['data'][0]
			if self.sending != None:
				self.sendesetsubset()
		else: return
	
	def sendesetsubset(self):
		r('esetsubset_'+str(self.rand)+'<-'+self.eset+'[rownames(dfsg),]')
		self.newdata = self.olddata.copy()
		self.newdata['data']=['esetsubset_'+str(self.rand)]
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