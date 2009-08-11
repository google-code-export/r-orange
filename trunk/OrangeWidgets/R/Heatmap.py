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
		self.infoa = OWGUI.widgetLabel(infobox, "Nothing to report")
		
		
	def processMatrix(self, data):
		if data:
			self.plotdata = data['data'][0]
			if 'classes' in data:
				self.classes = data['classes'][0]
			else:
				self.classes = 'rep(0, length('+self.plotdata+'[1,]))'
			# if r('class('+self.data+')') == "data.frame":
				# self.data = 'as.matrix('+self.data+')'
			self.rowvChoiceprocess()
			self.makePlot()
		else: return
	
	def makePlot(self):
		self.infoa.setText("You are plotting "+self.plotdata)
		r('heatmap('+self.plotdata+', Rowv='+self.rowvChoice+', ColSideColors=rgb(t(col2rgb('+self.classes+'+2)), maxColorValue=255))')
		
	def rowvChoiceprocess(self):
		if self.plotdata:
			rowlen = r('length(rownames('+self.plotdata+'))')
			if rowlen > 1000:
				self.rowvChoice = 'NA'
			else:
				self.rowvChoice = 'NULL'
	