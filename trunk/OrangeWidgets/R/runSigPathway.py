"""
<name>Sig Pathway</name>
<description>Performs Pathway Analysis on a genelist or subset (must specify gene list as either a full list or a subset on connecting)</description>
<icon>icons/readcel.png</icons>
<priority>2030</priority>
"""

import os, glob
from rpy_options import set_options
set_options(RHOME='c:/progra~1/r/R-2.6.2/')
from rpy import *
from OWWidget import *
import OWGUI
import random
from OWRpy import *
r.require('affy')
r.require('gcrma')
r.require('limma')
r.require('panp')
r.require('sigPathway')

class runSigPathway(OWWidget, OWRpy):
	def __init__(self, parent=None, signalManager=None):
		OWWidget.__init__(self, parent, signalManager, "Sample Data")
		OWRpy.__init__(self)
	
		self.inputs = [("Expression Set", orange.Variable, self.process), ("Pathway Annotation List", orange.Variable, self.processPathAnnot), ('Phenotype Vector', orange.Variable, self.phenotypeConnected)]
		self.outputs = [("Pathway Analysis File", orange.Variable), ("Pathway Annotation List", orange.Variable), ("Pathway List", orange.Variable)]
		
		self.vs = self.variable_suffix
		self.Rpannot = None
		self.data = ''
		self.affy = ''
		self.pAnnots = ''
		self.chiptype = ''
		self.sublist = ''
		self.wd = ''
		self.rand = 'test'
		self.availablePaths = []
		self.minNPS = str(20)
		self.maxNPS = str(500)
		self.phenotype = ''
		self.weightType = 'constant'
		
		#GUI
		info = OWGUI.widgetBox(self.controlArea, "Info")
		
		self.infoa = OWGUI.widgetLabel(info, "No data connected yet.")
		self.infob = OWGUI.widgetLabel(info, '')
		self.infoc = OWGUI.widgetLabel(info, '')
		
		
		sigPathOptions = OWGUI.widgetBox(self.controlArea, "Options")
		self.pAnnotlist = OWGUI.comboBox(sigPathOptions, self, "Rpannot", label = "Pathway Annotation File:", items = []) #Gets the availiable pathway annotation files.
		self.pAnnotlist.setEnabled(False)
		self.getNewAnnotButton = OWGUI.button(sigPathOptions, self, label = "New Annotation File", callback = self.noFile, width = 200)
		OWGUI.button(sigPathOptions, self, label='Load pathway file', callback = self.loadpAnnot, width = 200)
		OWGUI.button(sigPathOptions, self, 'Run', callback = self.runPath, width = 200)

		
		
	def loadpAnnot(self):
		r('load(choose.files())')
		self.pAnnots = 'G'
	def setFileFolder(self):
		self.wd = r('choose.dir()')
	
	def process(self, data): #collect a preprocessed file for pathway analysis
		if data:
			self.olddata = data
			self.data = data['data']
			self.pAnnotlist.setEnabled(True)
			self.infoa.setText("Data connected")
			if 'eset' in data:
				self.affy = data['eset']
				self.chiptype = r('annotation('+self.affy+')')
				
			elif 'affy' in data:
				self.affy = data['affy']
				self.chiptype = r('annotation('+self.affy+')')
			if self.chiptype != '':
				self.infob.setText('Your chip type is '+self.chiptype)
			if 'classes' in self.olddata:
				self.phenotype = self.olddata['classes']
			else:
				self.rsession('data.entry(colnames('+self.data+'), cla'+self.vs+'=NULL)')
				self.phenotype = 'cla'+self.vs
		else: return
	def processPathAnnot(self, data): #connect a processed annotation file if removed, re-enable the choose file function
		if data:
			self.pAnnots = data['data']
			self.pAnnotlist.setEnabled(False)
		else: 
			self.pAnnotlist.setEnabled(True)
			self.wdline.setEnabled(True)
			self.wdfilebutton.setEnabled(True)
	def getChiptype(self):
		if self.usedbfile.checked == True:
			try:
				r('require("'+self.chiptype+'.db")')
				self.dboptions = ',annotpkg = "'+self.chiptype+'.db"'
			except:	
				self.noDbFile #try to get the db file
		else: return
	
	def noFile(self):
		r('shell.exec("http://chip.org/~ppark/Supplements/PNAS05.html")') #open website for more pathways
		self.infoa.setText("Please select the file that coresponds to your array type and save to the Pathway Folder in My Documents.") #send the user a message to download the appropriate pathway.
		self.infob.setText("Once you have saved the array please press the update button.") #prompt the user to update the pathway list
		
	def updatePaths(self):
		if self.wd == '':
			self.infob.setText("You must specify a working directory!")
		else:
			try:
				olddir = os.getcwd()
				os.chdir(self.wd)
				self.pAnnotlist.clear()
				self.pAnnotlist.addItems(glob.glob("*.RData"))
				os.chdir(olddir)
			except:
				self.infob.setText("There was a problem accessing your directory, please confirm that it is correct.")
		
	def noDbFile(self):
		try:
			r('source("http://bioconductor.org/biocLite.R")')
			r('biocLite("'+self.chiptype+'.db")')
			r('require("'+self.chiptype+'.db")')
			self.dboptions = ',annotpkg = "'+self.chiptype+'.db"'
		except: 
			self.infoa.setText("Unable to include the .db file, please check that you are connected to the internet and that your .db file is available.")
			self.infob.setText("Your chip type appears to be "+self.chiptype+".")
			self.dboptions = ''
			

		
	def runPath(self):
		r('sigpath_'+self.rand+'<-runSigPathway('+self.pAnnots+', minNPS='+self.minNPS+', maxNPS = '+self.maxNPS+', '+self.data+', phenotype = '+self.phenotype+', weightType = "'+self.weightType+'")')
		self.newdata = self.olddata.copy()
		self.newdata['data'] = 'sigpath_'+self.rand+'$df.pathways'
		self.newdata['sigPathObj'] = 'sigpath_'+self.rand
		self.send("Pathway Analysis File", self.newdata)
		
		#make the table to show the results, should be interactive and send an object containing the subset to the pathway list
		self.tstruct = self.newdata['data']
		self.createTable()
	
	def createTable(self):
		try: self.table
		except: pass
		else: self.table.hide()
		self.table = MyTable(self.tstruct)  #This section of code is really messy, clean once working properly
		
		self.table.show()
		self.table.setMinimumSize(500, 500)
		self.connect(self.table, SIGNAL("itemClicked(QTableWidgetItem*)"), self.cellClicked)
	
		
	def cellClicked(self, item):
		clickedRow = int(item.row())+1
		subtable = {'data':'sigpath_'+self.rand+'$list.gPS[['+str(clickedRow)+']]'}
		self.send("Pathway List", subtable)
		try: self.table2
		except: pass
		else: self.table2.hide()
		self.table2 = MyTable(subtable['data'])
		self.table2.setMinimumSize(400, 400)
		self.table2.show()
	def phenotypeConnected(self, data):
		if data:
			self.phenotype = data['data']
		else: return
		
		
		
class MyTable(QTableWidget):
	def __init__(self, dataframe, *args):
		QTableWidget.__init__(self, *args)
		self.dataframename = dataframe
		self.headers = r('colnames('+self.dataframename+')')
		self.dataframe = r(self.dataframename)
		self.setColumnCount(len(self.headers))
		self.setRowCount(len(self.dataframe[self.headers[0]]))
		n=0
		for key in self.headers:
			m=0
			for item in self.dataframe[key]:
				newitem = QTableWidgetItem(str(item))
				self.setItem(m,n,newitem)
				m += 1
			n += 1
		self.setHorizontalHeaderLabels(self.headers)
