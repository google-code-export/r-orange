"""
<name>R Commander</name>
<description>Accepts and sends R objects as well as performing R commands</description>
<icon>icons/readcel.png</icons>
<priority>80</priority>
"""

from rpy_options import set_options
set_options(RHOME='c:/progra~1/r/R-2.6.2/')
from rpy import *
from OWWidget import *
import OWGUI
r.require('affy')
r.require('gcrma')
r.require('limma')

class rCommand(OWWidget):
	def __init__(self, parent=None, signalManager=None):
		OWWidget.__init__(self, parent, signalManager, "Sample Data")
		
		self.inputs = [('R object', orange.Variable, self.process)]
		self.outputs = [('R object', orange.Variable)]
		self.command = ''
		self.sendthis = ''
		
		
		#GUI
		box = OWGUI.widgetBox(self.controlArea, "R Commander")
		self.infob = OWGUI.widgetLabel(box, "")
		OWGUI.lineEdit(box, self, "command", "R Command", orientation = 'horizontal')
		processbutton = OWGUI.button(box, self, "Run", callback = self.runR, width=150)
		varbutton = OWGUI.button(box, self, "Recieved", callback = self.putrecieved, width = 150)
		self.infoa = OWGUI.widgetLabel(box, "")
		
		sendbox = OWGUI.widgetBox(self.controlArea, "Send Box")
		OWGUI.lineEdit(sendbox, self, "sendthis", "Send", orientation = 'horizontal')
		sendbutton = OWGUI.button(sendbox, self, "Send", callback =self.sendThis, width=150)
		
	def putrecieved(self):
		self.command += str(self.data)
	def sendThis(self):
		sendt = {'data':[self.sendthis]}
		self.send('R object', sendt)
	def runR(self):
		self.infoa.setText(str(r(self.command)))
		
		
	def process(self, data):
		if data:
			self.data = str(data['data'][0])
			self.infob.setText(self.data)
		else: return