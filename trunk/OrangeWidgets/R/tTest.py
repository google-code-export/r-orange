"""
<name>T Test</name>
<description>Performs Pathway Analysis on a genelist or subset (must specify gene list as either a full list or a subset on connecting)</description>
<icon>icons/readcel.png</icons>
<priority>10</priority>
"""

import os, glob
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
r.require('sigPathway')

class tTest(OWWidget):
	def __init__(self, parent=None, signalManager=None):
		OWWidget.__init__(self, parent, signalManager, "Sample Data")
		
		self.inputs = [("Numeric Vector A", orange.Variable, self.processVectorA), ("Numeric Vector B", orange.Variable, self.processVectorB)]
		self.outputs = None
		
		self.vectA = ''
		self.vectB = ''
		self.paramselected = ''
		
		pstat = OWGUI.widgetBox(self.controlArea, "p-value")
		self.infoa = OWGUI.widgetLabel(pstat, "")
		additionalParameters = OWGUI.widgetBox(self.controlArea, "Other Parameters")
		self.params = OWGUI.comboBox(additionalParameters, self, 'paramselected', label = 'Alternate Parameters', items = [], orientation = 0)
		self.infob = OWGUI.widgetLabel(additionalParameters, "")
	def processVectorA(self, data):
		if data:
			self.vectA = data['data'][0]
			self.run()
		else: return
	def processVectorB(self, data):
		if data:
			self.vectB = data['data'][0]
			self.run()
		else: return
	def run(self):
		if self.vectB != '' and self.vectA != '':
			self.results = r('t.test('+self.vectA+', '+self.vectB+')')
			#self.infoa.setText(self.results)
			self.params.clear()
			self.params.addItems(self.results.keys())
			self.params.setCurrentIndex(self.params.findText(self.paramselected))
			self.infoa.setText(str(self.results['p.value']))
			self.infob.setText(str(self.results[self.paramselected]))
		else: return
	#def paramChance(self):
		