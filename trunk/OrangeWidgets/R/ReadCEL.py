"""
<name>Read CEL Files</name>
<description>Allows the user to pick CEL files either individually or through a .txt file and outputs the eSet as an R.object</description>
<icon>icons/readcel.png</icons>
<priority>10</priority>
"""

from rpy_options import set_options
set_options(RHOME='c:/progra~1/r/R-2.6.2/')
from rpy import *
from OWWidget import *
import OWGUI
import orngIO

r.require('affy')

class ReadCEL(OWWidget):
	def __init__(self, parent=None, signalManager=None):
		OWWidget.__init__(self, parent, signalManager, 'SampleData')
		
		self.inputs = None #There is the posibility of inputs to set the class, phenotype, abstract, etc. of the affybatch
		self.outputs = [("Affybatch Expression Matrix", orange.Variable)]
		
		self.celfilepath = None #sets the celfilepath to the current wd, not that there should be anything in there that it can read but it's better than nothing
		self.rand = 'random'
		self.FD = 'choose.dir()'
		
		#Build a GUI to select either a folder or a txt file with the names of file locations in it to pass to the ReadAffy command of bioconductor
		#This should include a button for processing the files and a window for viewing the contents of the txt file (possibly added in the future)
		
		#folderselect box
		#folderSelect = OWGUI.widgetBox(self.controlArea, "Select a Folder")
		#OWGUI.lineEdit(folderSelect, self, "folder", "Selected Folder:", labelWidth=70, orientation="horizontal")
		#button = OWGUI.button(folderSelect, self, 'Choose File', callback = self.browseFile, width = 100, disabled=0)
		
		#the process box
		processbox = OWGUI.widgetBox(self.controlArea, "Process")
		processbutton = OWGUI.button(processbox, self, 'Process', callback = self.procesS, width = 200)
		self.infoa = OWGUI.widgetLabel(processbox, 'Data not yet processed.')
	
	def browseFile(self): #should open a dialog to choose a file that will be parsed to set the wd
		FN = 'r.choose.dir()'
		#something to handle the conversion
		self.celfilepath = FN
		
	def openFolder(self, FN):#this should send the folder name to the ReadAffy folder to use for the ReadAFFy command
		self.celfilepath = FN[0]
		
	def procesS(self):
		#QCursor.setShape(QCursor.shape(3))
		if self.celfilepath == None:
			r('affybatch_'+self.rand+'<-ReadAffy(celfile.path='+self.FD+')')
			eset = {'data':['exprs(affybatch_'+self.rand+')'], 'eset':['affybatch_'+self.rand]}
			self.infoa.setText("Your data has been processed.")
		else:
			r('affybatch_'+self.rand+'<-ReadAffy(celfile.path='+self.FD+')')
			eset = {'data':['exprs(affybatch_'+self.rand+')'], 'eset':['affybatch_'+self.rand]}
		
		self.send("Affybatch Expression Matrix", eset)
		#QCursor.setShape(QCursor.shape(0))