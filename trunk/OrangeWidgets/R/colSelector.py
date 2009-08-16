"""
<name>Column Selector</name>
<description>Subsets columns in a data.frame object to pass to subsequent widgets.</description>
<icon>icons/rma.png</icons>
<priority>3020</priority>
"""

from OWRpy import *
import OWGUI

class colSelector(OWRpy):
	settingsList = ['vs']
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		
		self.vs = self.variable_suffix
		self.Rvariable = {'data':'', 'result':'ssresult'+self.vs}
		self.collist = '' # a container for the names of columns that will be picked from the selector.
		self.inputs = [("R DataFrame", orange.Variable, self.process)]
		self.outputs = [("R DataFrame", orange.Variable)]
		
		# ###  GUI ###
		layk = QWidget(self)
		self.controlArea.layout().addWidget(layk)
		grid = QGridLayout()
		grid.setMargin(0)
		layk.setLayout(grid)
		
		colnamesBox = OWGUI.widgetBox(self.controlArea, "Column Names")
		grid.addWidget(colnamesBox, 0, 0)
		self.columns = OWGUI.listBox(colnamesBox, self, callback = self.subListAdd) # Adds the selected item to the subset list
		
		subsettingBox = OWGUI.widgetBox(self.controlArea, "Selected Columns")
		grid.addWidget(subsettingBox, 1, 0)
		self.subsetList = OWGUI.listBox(subsettingBox, self)
		OWGUI.button(subsettingBox, self, "Clear", callback = self.subsetList.clear())
		
		toolsBox = OWGUI.widgetBox(self.controlArea, "Tools") #some tools for aiding in the processing
		grid.addWidget(toolsBox, 0, 1)
		OWGUI.button(toolsBox, self, "Send", callback = self.subset) #starts the processing based on selected items
		OWGUI.button(toolsBox, self, "View data.frame", callback = self.viewdf)
		
	def subListAdd(self):
		self.subsetList.addItem(str(self.columns.selectedItems()[0].text()))
		
	def process(self, data):
		if 'data' in data:
			self.columns.clear()
			self.Rvariable['data'] = data['data']
			self.olddata = data
			for v in self.rsession('colnames('+self.Rvariable['data']+')'):
				self.columns.addItem(v)
		else:
			self.infoa.setText("Signal not of appropriate type.")
	
	def subset(self):
		h = ''
		for j in xrange(self.subsetList.count()):
			h += '"'+str(self.subsetList.item(int(j)).text())+'",'
		self.collist = h[:len(h)-1] # need to scale back 1 element in the text to remoce the trailing ,
		self.rsession(self.Rvariable['result']+'<-'+self.Rvariable['data']+'[,c('+self.collist+')]')
		self.newdata = self.olddata.copy()
		self.newdata['data'] = self.Rvariable['result']
		self.send("R DataFrame", self.newdata)
		
	def viewdf(self): # look at the first elements of the data.frame
		self.table = MyTable(self.Rvariable['data'])
		self.table.show()

from rpy_options import set_options
set_options(RHOME=os.environ['RPATH'])
from rpy import *
from OWWidget import *
		
		
class MyTable(QTableWidget):
	def __init__(self, dataframe, *args):
		QTableWidget.__init__(self, *args)
		#OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.dataframename = dataframe
		self.headers = r('colnames('+self.dataframename+')')
		self.dataframe = r(self.dataframename)
		self.setColumnCount(len(self.headers))
		self.setRowCount(len(self.dataframe[self.headers[0]]))
		n=0
		for key in self.headers:
			m=0
			for item in self.dataframe[key]:
				newitem = QTableWidgetItem(str(item))
				self.setItem(m,n,newitem)
				m += 1
			n += 1
		self.setHorizontalHeaderLabels(self.headers)