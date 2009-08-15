"""
<name>Read CEL Files</name>
<description>Allows the user to pick CEL files either individually or through a .txt file and outputs the eSet as an R.object</description>
<icon>icons/readcel.png</icons>
<priority>10</priority>
"""

from OWWidget import *
import OWGUI
import orngIO
from OWRpy import *


class ReadCEL(OWWidget, OWRpy):
	settingsList = ['vs', 'FD', 'eset', 'folder']
	def __init__(self, parent=None, signalManager=None):
		OWWidget.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		OWRpy.__init__(self)
		
		self.eset = {}
		self.vs = self.variable_suffix
		self.FD = 'choose.dir()'
		self.loadSettings()
		self.rsession('require("affy")')
		self.inputs = None #There is the posibility of inputs to set the class, phenotype, abstract, etc. of the affybatch
		self.outputs = [("Affybatch Expression Matrix", orange.Variable)]
		
		if 'eset' in self.eset: #check if data was loaded from a previous session and resend the data if so.
			self.send("Affybatch Expression Matrix", self.eset)
		
		self.Rab = 'affybatch_'+self.vs	
		self.FN = 'fnt'+self.vs
		self.folder = ''
		#Build a GUI to select either a folder or a txt file with the names of file locations in it to pass to the ReadAffy command of bioconductor
		#This should include a button for processing the files and a window for viewing the contents of the txt file (possibly added in the future)
		
		#folderselect box
		folderSelect = OWGUI.widgetBox(self.controlArea, "Select a Folder")
		OWGUI.lineEdit(folderSelect, self, "folder", "Selected Folder:", labelWidth=70, orientation="horizontal")
		button = OWGUI.button(folderSelect, self, 'Choose File', callback = self.browseFile, width = 100, disabled=0)
		
		#the process box
		processbox = OWGUI.widgetBox(self.controlArea, "Process")
		processbutton = OWGUI.button(processbox, self, 'Process', callback = self.procesS, width = 200)
		self.infoa = OWGUI.widgetLabel(processbox, 'Data not yet processed.')
		self.infob = OWGUI.widgetLabel(processbox, 'file_suffix: ' + self.variable_suffix)
	
	def browseFile(self): #should open a dialog to choose a file that will be parsed to set the wd
		self.rsession(self.FN+'<-choose.dir()')
		self.folder = str(self.rsession(self.FN))
		
	def procesS(self):
		
		# block to set the celfile FN
		try:
			self.rsession(self.FN) #should throw and error if self.FN DNE
		except:
			self.browseFiles()
			self.procesS()
		
		self.infoa.setText("Your data is processing")
		
		self.rsession(self.Rab+'<-ReadAffy(celfile.path='+self.FN+')')
		self.eset = {'data':'exprs('+self.Rab+')', 'eset':self.Rab}
		self.infoa.setText("Your data has been processed.")
	
		self.send("Affybatch Expression Matrix", self.eset)
