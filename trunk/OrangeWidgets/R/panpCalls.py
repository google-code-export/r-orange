"""
<name>Present calls with panp</name>
<description>Calculates differential expression of genes from an eSet object</description>
<icon>icons/readcel.png</icons>
<priority>2010</priority>
"""

from rpy_options import set_options
set_options(RHOME='c:/progra~1/r/R-2.6.2/')
from rpy import *
from OWWidget import *
from OWRpy import *
import OWGUI
r.require('affy')
r.require('gcrma')
r.require('limma')
r.require('panp')

class panpCalls(OWWidget, OWRpy):
	def __init__(self, parent=None, signalManager=None):
		OWWidget.__init__(self, parent, signalManager, "Sample Data")
		OWRpy.__init__(self)
		self.inputs = [("Expression Set", orange.Variable, self.process)]
		self.outputs = [("Present Gene Signal Matrix", orange.Variable)]
		
		self.state = {}
		self.state['vs'] = self.variable_suffix
		self.looseCut = '0.02'
		self.tightCut = '0.01'
		self.percentA = '20'
		#GUI
		box = OWGUI.widgetBox(self.controlArea, "Options")
		
		OWGUI.lineEdit(box, self, "looseCut", "Loose Cut", orientation = "horizontal")
		OWGUI.lineEdit(box, self, "tightCut", "Tight Cut", orientation = "horizontal")
		OWGUI.lineEdit(box, self, "percentA", "Percent Absent", orientation = "horizontal")
		processbutton = OWGUI.button(box, self, "Process eSet", callback = self.processEset, width=200)
		self.infoa = OWGUI.widgetLabel(box, "Processing not begun")
		
		
	def process(self, dataset):
		if dataset:
			self.state['data'] = dataset
			if 'eset' in self.state['data']:
				self.eset = self.state['data']['eset'][0]
			else:
				self.infoa.setText("Processing imposible, not of eset or affybatch type")
		else:
			return
			
	def processEset(self):
		self.infoa.setText("Processing Started!!!")
		r('PA<-pa.calls('+self.eset+', looseCutoff='+self.looseCut+', tightCutoff='+self.tightCut+')')
		self.infoa.setText('PA calls have been calculated')
		r('PAcalls<-PA$Pcalls == "A"')
		r('PAcalls_sum<-apply(PAcalls, 1, sum)')
		r('Present<- PAcalls_sum/length(PAcalls[1,]) > '+self.percentA+'/100')
		r('peset_'+str(self.state['vs'])+'<-exprs('+self.eset+')[Present,]')
		self.infoa.setText('Expression matrix with expression values for present genes has been created and sent!  You may now generate a fit using the Diff Exp widget')
		emat = {'data':['peset_'+str(self.state['vs'])]}
		self.send('Present Gene Signal Matrix', emat)
		self.setState()
		
	def setState(self):
		self.state['looseCut'] = self.looseCut
		self.state['tightCut'] = self.tightCut
		self.state['percentA'] = self.percentA
		