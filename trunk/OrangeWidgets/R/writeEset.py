"""
<name>Write eSet</name>
<description>Writes an eSet to a tab delimited file.</description>
<icon>icons/rma.png</icons>
<priority>80</priority>
"""

from rpy_options import set_options
set_options(RHOME='c:/progra~1/r/R-2.6.2/')
from rpy import *
from OWWidget import *
import OWGUI
r.require('affy')

class writeEset(OWWidget):
	def __init__(self, parent=None, signalManager=None):
		OWWidget.__init__(self, parent, signalManager, "Sample Data")
		
		self.inputs = [("Affybatch", orange.Variable, self.nothingb)]
		self.outputs = None
		
		self.data = None
		self.fileName = ""
		
		#GUI
		box = OWGUI.widgetBox(self.controlArea, "Write to file.")
		OWGUI.lineEdit(box, self, "fileName", "File Name", orientation = "horizontal") 
		writeButton = OWGUI.button(box, self, "Write to file", callback = self.write, width=200)
		self.infoa = OWGUI.widgetLabel(box, "No output yet")
		
	def nothingb(self,data):
		if data:	
			self.data = data
		else: return
			
	def write(self):
		if self.fileName == "":
			self.infoa.setText("You must input a valid file name.")
		elif self.data == None:
			self.infoa.setText("Data has not been loaded yet")
		else:
			r('write.exprs('+self.data+',file="'+self.fileName+'.txt", sep="\t")')
			self.infoa.setText("Data was writen to "+self.fileName+" successfully!")
		