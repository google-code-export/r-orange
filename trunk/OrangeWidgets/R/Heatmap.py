"""
<name>Heatmap</name>
<description>Calculates differential expression of genes from an eSet object</description>
<icon>icons/readcel.png</icons>
<priority>2040</priority>
"""

from OWRpy import *
import OWGUI
import random

class Heatmap(OWRpy):
	#This widget has no settings list
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		
		self.inputs = [("Expression Matrix", orange.Variable, self.processMatrix)]
		self.outputs = None
		
		self.rowvChoice = None
		
		#GUI
		infobox = OWGUI.widgetBox(self.controlArea, "Options")
		OWGUI.button(infobox, self, "Replot", callback=self.makePlot, width=200)
		self.infoa = OWGUI.widgetLabel(infobox, "Nothing to report")
		
		
	def processMatrix(self, data):
		if data:
			self.plotdata = data['data']
			if 'classes' in data:
				self.classes = data['classes']
			else:
				self.classes = 'rep(0, length('+self.plotdata+'[1,]))'
			if self.rsession('class('+self.plotdata+')') == "data.frame":
				self.plotdata = 'as.matrix('+self.plotdata+')'
			self.rowvChoiceprocess()
			self.makePlot()
		else: return
	
	def makePlot(self):
		self.infoa.setText("You are plotting "+self.plotdata)
		self.rsession('heatmap('+self.plotdata+', Rowv='+self.rowvChoice+', ColSideColors=rgb(t(col2rgb('+self.classes+'+2)), maxColorValue=255))')
		
	def rowvChoiceprocess(self):
		if self.plotdata:
			rowlen = self.rsession('length(rownames('+self.plotdata+'))')
			if rowlen > 1000:
				self.rowvChoice = 'NA'
			else:
				self.rowvChoice = 'NULL'
	