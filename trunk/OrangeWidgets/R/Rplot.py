"""
<name>Plot Test</name>
<description>Calculates differential expression of genes from an eSet object</description>
<icon>icons/readcel.png</icons>
<priority>4090</priority>
"""

from rpy_options import set_options
set_options(RHOME='c:/progra~1/r/R-2.6.2/')
from rpy import *
from OWWidget import *
import OWGUI
from OWRpy import *
from OWGraph import *

r.require('affy')
r.require('gcrma')
r.require('limma')

class Rplot(OWWidget, OWRpy):
	def __init__(self, parent=None, signalManager=None, name="Rplot"):
		OWWidget.__init__(self, parent, signalManager, "Sample Data")
		OWRpy.__init__(self)
		#OWGraph.__init__(self, parent, name)
		
		self.inputs = [("Data Table", orange.Variable, self.process)]
		self.outputs = [("Selected Points", orange.Variable), ("Not Selected Points", orange.Variable)]
		r('df1<-data.frame(a=c(1,2,3), b=c(7,4,5))')
		self.state = {}
		self.state['data'] = 'df1'
		self.graphShowGrid = 1  # show gridlines in the graph
		self.graphDrawLines = 1
		self.graphPointSize = 5

		plotarea = OWGUI.widgetBox(self.controlArea, "Graph")
		self.graph = OWGraph(plotarea)
		self.graph.setAxisAutoScale(QwtPlot.xBottom)
		self.graph.setAxisAutoScale(QwtPlot.yLeft)
		plotarea.layout().addWidget(self.graph)
		self.setGraphGrid()
		
		runarea = OWGUI.widgetBox(self.controlArea, "Run")
		OWGUI.button(runarea, self, "Plot", callback=self.plot)
		
		box = OWGUI.widgetBox(self.controlArea, "Arrays")
		self.arraysA = OWGUI.listBox(box, self)
		#setAbutton = OWGUI.button(box, self, "Switch Class", callback = self.switchClass, width = 200)
		#self.infoa = OWGUI.widgetLabel(box, "No arrays selected")
		
		self.arraysB = OWGUI.listBox(box, self)
		#setAbutton = OWGUI.button(box, self, "Switch Class", callback = self.switchClass, width = 200)
		#self.infoa = OWGUI.widgetLabel(box, "No arrays selected")
	def setGraphGrid(self):
		self.graph.enableGridYL(self.graphShowGrid)
		self.graph.enableGridXB(self.graphShowGrid)
		
	def process(self, data):
		self.state['data'] = data['data'][0]
		self.samplenames = r('colnames('+self.state['data']+')') #collect the sample names to make the differential matrix
		for v in self.samplenames:
			self.arraysA.addItem(v)
			self.arraysB.addItem(v)
		
	
	def plot(self):
		#self.vecA = r(self.state['data']+'[,"'+self.arraysA.selectedItems()[0].text()+'"]')
		#self.vecB = r(self.state['data']+'[,"'+self.arraysB.selectedItems()[0].text()+'"]')
		self.vecA = r(self.state['data']+'[,"a"]')
		self.vecB = r(self.state['data']+'[,"b"]')
		if not self.vecA and self.vecB: return
		curve = self.graph.addCurve('MyData', xData=self.vecA, yData=self.vecB, autoScale=True)
		self.setGraphStyle(curve)
		self.graph.replot()
		
	def setGraphStyle(self, curve):
		colors = ColorPaletteHSV(2)
		if self.graphDrawLines:
			curve.setStyle(QwtPlotCurve.Lines)
		else:
			curve.setStyle(QwtPlotCurve.NoCurve)
		curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, 
			QBrush(QColor(0,0,0)), QPen(QColor(0,0,0)),
			QSize(self.graphPointSize, self.graphPointSize)))
		#curve.setPen(QPen(learner.color, 5))
		curve.setPen(QPen(colors[1], 5))
		
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
