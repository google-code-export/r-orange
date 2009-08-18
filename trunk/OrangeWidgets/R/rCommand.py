"""
<name>R Commander</name>
<description>Accepts and sends R objects as well as performing R commands</description>
<icon>icons/readcel.png</icons>
<priority>80</priority>
"""

from OWRpy import *
import OWGUI
from rpy_options import set_options
set_options(RHOME=os.environ['RPATH'])
from rpy import *


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
		
		self.inputs = [('R.object', RvarClasses.RVariable, self.process)]
		self.outputs = [('R.object', RvarClasses.RVariable)]
		
		
		
		#GUI
		self.box = OWGUI.widgetBox(self.controlArea, "R Commander")
		self.infob = OWGUI.widgetLabel(self.box, "")
		OWGUI.lineEdit(self.box, self, "command", "R Command", orientation = 'horizontal')
		processbutton = OWGUI.button(self.box, self, "Run", callback = self.runR, width=150)
		varbutton = OWGUI.button(self.box, self, "Recieved", callback = self.putrecieved, width = 150)
		self.infoa = OWGUI.widgetLabel(self.box, "")
		self.thistext = QTextEdit(self)
		self.box.layout().addWidget(self.thistext)
		
		sendbox = OWGUI.widgetBox(self.controlArea, "Send Box")
		OWGUI.lineEdit(sendbox, self, "sendthis", "Send", orientation = 'horizontal')
		sendbutton = OWGUI.button(sendbox, self, "Send", callback =self.sendThis, width=150)
		self.resize(800,600)
		
	def putrecieved(self):
		self.command = str(self.data)
	def sendThis(self):
		self.sendt = {'data':self.sendthis}
		self.send('R object', self.sendt)
	def runR(self):
		self.rsession('txt<-capture.output('+self.command+')')
		
		pasted = self.rsession('paste(txt, collapse = " \n")')
		
		self.thistext.setHtml('<pre>'+pasted+'<\pre>')
		
	def process(self, data):
		if data:
			self.data = str(data['data'])
			self.infob.setText(self.data)
		else: return
	
	def sendMe(self):
		self.send('R Object', self.sendt)