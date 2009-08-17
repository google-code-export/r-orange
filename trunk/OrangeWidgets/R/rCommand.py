"""
<name>R Commander</name>
<description>Accepts and sends R objects as well as performing R commands</description>
<icon>icons/readcel.png</icons>
<priority>80</priority>
"""

from OWRpy import *
import OWGUI

class rCommand(OWRpy):
	settingsList = ['command', 'sendthis', 'sendt']
	def __init__(self, parent=None, signalManager=None):
		#OWWidget.__init__(self, parent, signalManager, "Sample Data")
		OWRpy.__init__(self)
		
		self.command = ''
		self.sendthis = ''
		self.sendt = {}
		self.loadSettings()
		self.sendMe()
		
		self.inputs = [('R object', orange.Variable, self.process)]
		self.outputs = [('R object', orange.Variable)]
		
		
		
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
		self.command = str(self.data)
	def sendThis(self):
		self.sendt = {'data':self.sendthis}
		self.send('R object', self.sendt)
	def runR(self):
		self.rsession('txt<-capture.output('+self.command+')')
		self.rsession('require(tcltk)')
		self.rsession('tt<-tktoplevel()')
		self.rsession('txtWidget <- tktext(tt)')
		self.rsession('tkpack(txtWidget)')
		self.rsession('tkinsert(txtWidget, "end", paste(txt, collapse="\n"))')
		#self.infoa.setText(str(r(self.command)))
		
		
	def process(self, data):
		if data:
			self.data = str(data['data'])
			self.infob.setText(self.data)
		else: return
	
	def sendMe(self):
		self.send('R Object', self.sendt)