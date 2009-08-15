"""
<name>Diff Exp</name>
<description>Calculates differential expression of genes from an eSet object</description>
<icon>icons/readcel.png</icons>
<priority>70</priority>
"""

from OWWidget import *
import OWGUI
from OWRpy import *



class diffExp(OWWidget, OWRpy):
	def __init__(self, parent=None, signalManager=None):
		OWWidget.__init__(self, parent, signalManager, "Sample Data")
		OWRpy.__init__(self)
		
		self.vs = self.variable_suffix
		self.Rvariables = {'results':'results_'+self.vs, 'classes':'cla'+self.vs}


		self.rsession('require("affy")')
		self.rsession('require("gcrma")')
		self.rsession('require("limma")')

		self.inputs = [("Expression Set", orange.Variable, self.process)]
		self.outputs = [("eBayes fit", orange.Variable)]

		self.samplenames = None #names of the samples (as a python object) to be used for generating the differential expression matrix
		self.classA = True #a container to maintain which list to add the arrays to
		
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
			self.data = data['data']
			self.olddata = data.copy()
			self.samplenames = self.rsession('colnames('+self.data+')') #collect the sample names to make the differential matrix
			for v in self.samplenames:
				self.arrays.addItem(v)
		else: return
	
	def processEset(self): #convert the listBox elements to R objects, perform differential expression and send the results of that to the next widget
		#first we need to construct the design
		h=''
		for j in xrange(self.selectedArrays.count()): #loop that makes r objects named holder_1,2,... that will be used to make the final vector
			h += '"'+str(self.selectedArrays.item(int(j)).text())+'",'
		
		#self.infoa.setText(h)
		self.rsession(self.Rvariables['classes']+'<-as.numeric(colnames('+self.data+') %in% c('+h[:len(h)-1]+'))') #make the cla object in R to assign the classes based on the values of h

		
		self.rsession('cvect<-data.frame(type=1, class='+self.Rvariables['classes']+')') 
		self.rsession('design<-model.matrix(~class, cvect)')
		self.rsession('fit<-lmFit('+self.data+', design)')
		self.rsession(self.Rvariables['results']+'<-eBayes(fit)')
		self.newdata = self.olddata.copy()
		self.newdata['data']=self.Rvariables['results']
		self.newdata['classes'] = self.Rvariables['classes']
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