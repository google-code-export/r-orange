"""
<name>Heatmap</name>
<description>Calculates differential expression of genes from an eSet object</description>
<icon>icons/readcel.png</icons>
<priority>2040</priority>
"""

from rpy_options import set_options
set_options(RHOME='c:/progra~1/r/R-2.6.2/')
from rpy import *
from OWWidget import *
import OWGUI
import random
r.require('affy')
r.require('gcrma')
r.require('limma')
r.require('panp')

class Heatmap(OWWidget):
	def __init__(self, parent=None, signalManager=None):
		OWWidget.__init__(self, parent, signalManager, "Sample Data")
		
		self.inputs = [("Expression Matrix", orange.Variable, self.processMatrix)]
		self.outputs = None
		
		self.rowvChoice = None
		
		#GUI
		infobox = OWGUI.widgetBox(self.controlArea, "Options")
		OWGUI.button(infobox, self, "Replot", callback=self.makePlot, width=200)
		
		
	def processMatrix(self, data):
		if data:
			self.data = data['data'][0]
			if r('class('+self.data+')') == "data.frame":
				self.data = 'as.matrix('+self.data+')'
			self.rowvChoiceprocess()
			self.makePlot()
		else: return
	
	def makePlot(self):
		r('heatmap('+self.data+', Rowv='+self.rowvChoice+', col=rainbow(60))')
		
	def rowvChoiceprocess(self):
		if self.data:
			rowlen = r('length(rownames('+self.data+'))')
			if rowlen > 1000:
				self.rowvChoice = 'NA'
			else:
				self.rowvChoice = 'NULL'
	