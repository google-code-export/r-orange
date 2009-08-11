"""
<name>Plot Affy Image</name>
<description>Obtains an affybatch and plots the images of the files</description>
<icon>icons/readcel.png</icons>
<priority>70</priority>
"""

from rpy_options import set_options
set_options(RHOME='c:/progra~1/r/R-2.6.2/')
from rpy import *
from OWWidget import *
import OWGUI
r.require('affy')

class plotAffy(OWWidget):
	def __init__(self, parent=None, signalManager=None):
		OWWidget.__init__(self, parent, signalManager, "Sample Data")
		
		self.inputs = [("Affybatch", orange.Variable, self.nothing)]
		self.outputs = None
		self.testLineEdit = ""
		self.irows = 1 #this sets the global variable for the rows
		self.icols = 1 #this sets the global variable for the cols
		
		#the GUI
		info = OWGUI.widgetBox(self.controlArea, "Info")
		self.infoa = OWGUI.widgetLabel(info, 'No data loaded.')
		plotbutton = OWGUI.button(info, self, "Show Image", callback = self.process, width = 200)
		boxplotbutton = OWGUI.button(info, self, "Show Boxplot", callback = self.myboxplot, width = 200)
		
		optionsa = OWGUI.widgetBox(self.controlArea, "Options")
		self.infob = OWGUI.widgetLabel(optionsa, 'Button not pressed')
		OWGUI.lineEdit(optionsa, self, "testLineEdit", "Test Line Edit", orientation = "horizontal")
		OWGUI.lineEdit(optionsa, self, "irows", "Number of rows:", orientation="horizontal") #make line edits that will set the values of the irows and icols variables, this seems to happen automatically.  Only need to include variable name where the "irows" is in this example
		OWGUI.lineEdit(optionsa, self, "icols", "Number of columns:", orientation="horizontal")
		testlineButton = OWGUI.button(optionsa, self, "test line edit", callback = self.test, width = 200)
		
		
	def test(self):
		self.infob.setText('You put' + self.testLineEdit + 'into the line edit')
		
	
	def nothing(self, dataset):
		if dataset:
			self.data = dataset
		else:
			return
	
	def process(self):
		if self.data:
			r('par(mfrow=c('+self.irows+','+self.icols+'))') #get the values that are in the irows and icols and put them into the par(mfrow...) function in r
			r('image('+self.data+')')
		else: return
	
	def myboxplot(self):
		if self.data:
			r('boxplot('+self.data+')')
		else: return