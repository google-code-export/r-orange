"""
<name>Diff Exp</name>
<description>Calculates differential expression of genes from an eSet object</description>
<icon>icons/readcel.png</icons>
<priority>70</priority>
"""

from rpy_options import set_options
set_options(RHOME='c:/progra~1/r/R-2.6.2/')
from rpy import *
from OWWidget import *
import OWGUI
r.require('affy')
r.require('gcrma')
r.require('limma')

class diffExp(OWWidget):
	def __init__(self, parent=None, signalManager=None):
		OWWidget.__init__(self, parent, signalManager, "Sample Data")
		
		self.inputs = [("Expression Set", orange.Variable, self.process)]
		self.outputs = [("eBayes fit", orange.Variable)]
		
		self.data = None
		self.samplenames = None #names of the samples (as a python object) to be used for generating the differential expression matrix
		self.classA = True #a container to maintain which list to add the arrays to
		self.rand = random.random()
		
		#GUI
		
		layk = QWidget(self)
		self.controlArea.layout().addWidget(layk)
		grid = QGridLayout()
		grid.setMargin(0)
		layk.setLayout(grid)
		
		box = OWGUI.widgetBox(self.controlArea, "Process")
		grid.addWidget(box, 0,0)
		processButton = OWGUI.button(box, self, "Process eSet", callback = self.processEset, width=200)
		self.arrays = OWGUI.listBox(box, self, callback = self.printSelected)
		setAbutton = OWGUI.button(box, self, "Switch Class", callback = self.switchClass, width = 200)
		self.infoa = OWGUI.widgetLabel(box, "No arrays selected")
		
		selecteda = OWGUI.widgetBox(self.controlArea, "Selected Arrays")
		grid.addWidget(selecteda, 0,1)
		self.selectedArrays = OWGUI.listBox(selecteda, self)
		clearaButton = OWGUI.button(selecteda, self, "Clear",callback = self.clearA, width = 200)
		
		# selectedb = OWGUI.widgetBox(self.controlArea, "Selected Arrays")
		# grid.addWidget(selectedb, 0,2)
		# self.selectedArraysB = OWGUI.listBox(selectedb, self)
		# clearbButton = OWGUI.button(selectedb, self, "Clear", callback = self.clearB, width = 200)
	
	def clearA(self):
		self.infoa.setText(str(self.selectedArrays.count()))
		self.infoa.setText(str(self.selectedArrays.item(0).text()))
		self.selectedArrays.clear()
		
		
	def clearB(self):
		self.selectedArraysB.clear()
		
	def switchClass(self):
		if self.classA == True:
			self.classA = False
		elif self.classA == False:
			self.classA = True
		else: self.classA = True
		
	def process(self, data):
		if data:
			self.data = data['data'][0]
			self.olddata = data
			self.samplenames = r('colnames('+self.data+')') #collect the sample names to make the differential matrix
			for v in self.samplenames:
				self.arrays.addItem(v)
		else: return
	
	def processEset(self): #convert the listBox elements to R objects, perform differential expression and send the results of that to the next widget
		#first we need to construct the design
		h=''
		for j in xrange(self.selectedArrays.count()): #loop that makes r objects named holder_1,2,... that will be used to make the final vector
			h += '"'+str(self.selectedArrays.item(int(j)).text())+'",'
		
		self.infoa.setText(h)
		r('cla<-colnames('+self.data+') %in% c('+h[:len(h)-1]+')') #make the cla object in R to assign the classes based on the values of h
		# for a in range(i): #loop that makes a string that will be sent to r to make the vector that we want for class designation
			# h = h+'holder_'+str(a)+'+'
		
		r('cvect<-data.frame(type=1, class=cla)')
		r('design<-model.matrix(~class, cvect)')
		
		#now use the class vector to continue the flow by making
		r('fit<-lmFit('+self.data+', design)')
		r('results_'+str(self.rand)+'<-eBayes(fit)')
		self.newdata = self.olddata.copy()
		self.newdata['data']=['results_'+str(self.rand)]
		self.newdata['classes'] = ['cla']
		self.send('eBayes fit', self.newdata)
		self.infoa.setText('Your data fit has been sent.  Use the diffSelector widget to select significant cutoffs')
		
		
	
	def printSelected(self):
		if self.classA == True:
			if self.arrays:
				self.selectedArrays.addItem(str(self.arrays.selectedItems()[0].text()))
				self.infoa.setText("An array was selected, and it's name is "+str(self.arrays.selectedItems()[0].text()))
				#self.arrays.selectedItems.clear()
			else: 
				self.infoa.setText("No arrays selected")
		elif self.classA == False:
			if self.arrays:
				self.selectedArraysB.addItem(str(self.arrays.selectedItems()[0].text()))
				self.infoa.setText("An array was selected, and it's name is "+str(self.arrays.selectedItems()[0].text()))
				#self.arrays.selectedItems.clear()
			else: 
				self.infoa.setText("No arrays selected")