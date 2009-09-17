"""
<name>Plot Test</name>
<description>Calculates differential expression of genes from an eSet object</description>
<icon>icons/readcel.png</icons>
<priority>4090</priority>
"""

import numpy
from rpy_options import set_options
set_options(RHOME='c:/progra~1/r/R-2.6.2/')
from rpy import *
from OWWidget import *
import OWGUI, OWToolbars, OWColorPalette
from OWRpy import *
from OWGraph import *
from OWWidget import *
from OWScatterPlotGraph import *
from OWkNNOptimization import *
import orngVizRank
import OWGUI, OWToolbars, OWColorPalette
from orngScaleData import *
from OWGraph import OWGraph
r.require('affy')
r.require('gcrma')
r.require('limma')

class Rplot(OWWidget, OWRpy):
	def __init__(self, parent=None, signalManager=None, name="Rplot"):
		OWWidget.__init__(self, parent, signalManager, "Sample Data")
		OWRpy.__init__(self)
		#OWGraph.__init__(self, parent, name)
		
		############# Start the self.data's for optiong  #############3
		self.inputs = [("Data Table", orange.Variable, self.process)]
		self.outputs = [("Selected Points", orange.Variable), ("Not Selected Points", orange.Variable)]
		SELECT_RECTANGLE = 2
		self.State = {}
		self.state = SELECT_RECTANGLE
		
		self.graphShowGrid = 1  # show gridlines in the graph
		self.graphDrawLines = 1
		self.graphPointSize = 5
		self.State['vs'] = self.variable_suffix
		
		########### End the self.data's for options ##################

		################ Start the GUI boxes  #####################
		plotarea = OWGUI.widgetBox(self.controlArea, "Graph")
		self.graph = OWScatterPlotGraph(plotarea)
		self.graph.setAxisAutoScale(QwtPlot.xBottom)
		self.graph.setAxisAutoScale(QwtPlot.yLeft)
		plotarea.layout().addWidget(self.graph)
		self.setGraphGrid()  #Not clear why this is here, comes from example code, this initializes the graph
		
		runarea = OWGUI.widgetBox(self.controlArea, "Run")
		OWGUI.button(runarea, self, "Plot", callback=self.plot)
		
		box = OWGUI.widgetBox(self.controlArea, "Arrays")
		self.arraysA = OWGUI.listBox(box, self, callback=self.setState)
		#setAbutton = OWGUI.button(box, self, "Switch Class", callback = self.switchClass, width = 200)
		#self.infoa = OWGUI.widgetLabel(box, "No arrays selected")
		
		self.arraysB = OWGUI.listBox(box, self, callback = self.setState)
		#setAbutton = OWGUI.button(box, self, "Switch Class", callback = self.switchClass, width = 200)
		#self.infoa = OWGUI.widgetLabel(box, "No arrays selected")
		
		optionsarea = OWGUI.widgetBox(self.controlArea, "Options")
		self.graphDrawLinesRadio = OWGUI.radioButtonsInBox(optionsarea, self, 'graphDrawLines', ["No", "Yes"])
		self.memmo = OWGUI.widgetLabel(optionsarea, "")
		self.zoomSelectToolbar = OWToolbars.ZoomSelectToolbar(optionsarea, self, self.graph, self.sendSelections)
        #self.connect(self.zoomSelectToolbar.buttonSendSelections, SIGNAL("clicked()"), self.sendSelections)
		OWGUI.button(optionsarea, self, "Run", callback=self.sendSelections)
		
		################# End the GUI Boxes ##################
	def process(self, data):
		if data:
			self.State['data'] = 'as.data.frame('+data['data'][0]+')'#coerce to data.frame, for some reason this is required
			self.samplenames = r('colnames('+self.State['data']+')') #collect the sample names to make the differential matrix
			self.arraysA.clear()
			self.arraysB.clear()
			### logic block to reset old params if they still exist ####
			
			#### end set params logic block  #########
			for v in self.samplenames:
				self.arraysA.addItem(v) #set up the variables when data is connected
				self.arraysB.addItem(v)
			if r('length('+self.State["data"]+'[,1])') > 10:
				self.graphDrawLines = 0
				#self.setGraphDrawLines()
			self.plot()
		else: return
	
	def setGraphDrawLines(self): #logic to set weather or not to draw lines.
		self.graphDrawLinesRadio.setButton(self.graphDrawLines)
	####### Set parameters from logic, could also be addapted to set from the self.state var on-load  ############
	def setState(self):
		if self.arraysA.selectedItems() and self.arraysB.selectedItems():
			self.A = str(self.arraysA.selectedItems()[0].text()) #Allows to run on connect as long as something connected before.
			self.B = str(self.arraysB.selectedItems()[0].text())
		
		
		########## The graphing section, contains info for making the graph  ###############3
	def setGraphGrid(self):
		self.graph.enableGridYL(self.graphShowGrid) #part of the OWGraph structure
		self.graph.enableGridXB(self.graphShowGrid)
	
	def plot(self):
		#if self.arraysA.selectedItems() and self.arraysB.selectedItems():
		try: #try to generate the vectors and if they don't exist or there is some other problem indicate the same
			self.graph.clear()
			self.vecA = r(self.State['data']+'[,"'+self.A+'"]') #set the data to be plotted.   This is a scatterplot so there are only pairs of points.
			self.vecB = r(self.State['data']+'[,"'+self.B+'"]')
			#self.vecA = r(self.state['data']+'[,"a"]')
			#self.vecB = r(self.state['data']+'[,"b"]')
			if not self.vecA and self.vecB: return
			curve = self.graph.addCurve('MyData', xData=self.vecA, yData=self.vecB, autoScale=True)
			self.setGraphStyle(curve)
			self.graph.replot()
		except: 
			self.memmo.setText("There was a problem with plotting your data")
		#else: return
		
	def setGraphStyle(self, curve):
		colors = ColorPaletteHSV(2)
		if self.graphDrawLines == 1:
			curve.setStyle(QwtPlotCurve.Lines)
		else:
			curve.setStyle(QwtPlotCurve.NoCurve)
		curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, 
			QBrush(QColor(0,0,0)), QPen(QColor(0,0,0)),
			QSize(self.graphPointSize, self.graphPointSize)))
		#curve.setPen(QPen(learner.color, 5))
		curve.setPen(QPen(colors[1], 3))

	###########  Some of the plotting functions from other packages, may recreate these for other uses and put into a repository
		
	def sendSelections(self):
		self.getRSelectedPoints(self.vecA, self.vecB) #first get the selections
		#now make the data.frames to send on 
		tmp_sel = str(self.selected.tolist())[1:len(str(self.selected.tolist()))-1]
		tmp_unsel = str(self.unselected.tolist())[1:len(str(self.unselected.tolist()))-1]
		r('selected'+self.State['vs']+'<-'+self.State['data']+'[c('+tmp_sel+'),]')
		r('unselected'+self.State['vs']+'<-'+self.State['data']+'[c('+tmp_unsel+'),]')
		self.rows_selected = 'selected'+self.State['vs']
		self.rows_unselected = 'unselected'+self.State['vs']
		self.send("Selected Points", self.rows_selected)
		self.send("Unselected Points", self.rows_unselected)
		
	def getRSelectedPoints(self, xData, yData, validData = None):
		if validData == None:	
			validData = r('as.numeric(!is.na('+self.State['data']+'[,"'+self.B+'"]'') & !is.na('+self.State['data']+'[,"'+self.A+'"]''))')
		total = numpy.zeros(len(xData)) #make a holder vector to put index returns into 
		#self.memmo.setText(str(xData))
		for curve in self.graph.selectionCurveList:
			total += curve.getSelectedPoints(xData, yData, validData) #get data from the OWScatterPlotGraph class and tell if a point is inside of the curve or not
		self.unselected = numpy.equal(total, 0) #makes an array of selected indicies that should be sent to R for subsetting
		self.selected = 1 - self.unselected
		# self.memmo.setText(str(self.selected.tolist())) ### used to test that a vector was returned
		return
if __name__=="__main__":
	appl = QApplication(sys.argv)
	# ow = rCommand()
	# ow.show()

	# l1 = orange.BayesLearner()
	# l1.name = 'Naive Bayes'
	# ow.learner(l1, 1)

	# data = orange.ExampleTable('../datasets/iris.tab')
	# ow.dataset(data)

	# l2 = orange.BayesLearner()
	# l2.name = 'Naive Bayes (m=10)'
	# l2.estimatorConstructor = orange.ProbabilityEstimatorConstructor_m(m=10)
	# l2.conditionalEstimatorConstructor = orange.ConditionalProbabilityEstimatorConstructor_ByRows(estimatorConstructor = orange.ProbabilityEstimatorConstructor_m(m=10))

	# l3 = orange.kNNLearner(name="k-NN")
	# ow.learner(l3, 3)

	# import orngTree
	# l4 = orngTree.TreeLearner(minSubset=2)
	# l4.name = "Decision Tree"
	# ow.learner(l4, 4)

	#    ow.learner(None, 1)
	#    ow.learner(None, 2)
	#    ow.learner(None, 4)



	appl.exec_()
