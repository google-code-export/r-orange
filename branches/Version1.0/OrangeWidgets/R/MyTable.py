class MyTable(QTableWidget):
	def __init__(self, dataframe, *args):
		QTableWidget.__init__(self, *args)
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
		self.setVerticalHeaderLabels(r('rownames('+self.dataframename+')')  