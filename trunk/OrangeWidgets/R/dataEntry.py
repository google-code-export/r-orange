"""
<name>Data Entry</name>
<description>A table input data entry into a data.frame.</description>
<icon>icons/readcel.png</icons>
<priority>20</priority>
"""

import OWGUI
from OWRpy import *


class dataEntry(OWRpy):
    settingsList = ['modelProcessed', 'olddata', 'newdata', 'dmethod', 'adjmethods', 'foldchange', 'pval', 'data', 'sending', 'ebdata', 'eset']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Data Entry", wantMainArea = 0, resizingEnabled = 1)
        
        self.rowCount = 2 #Counters for the number of rows and cols so that new ones can be added as the last rows and cols are entered
        self.colCount = 1
        self.setRvariableNames(['table'])
        
        self.outputs = [('Data Table', RvarClasses.RDataFrame)]
        #GUI.
        
        box = OWGUI.widgetBox(self.controlArea, "Options")
        OWGUI.button(box, self, 'Commit', self.commitTable)
        OWGUI.button(box, self, 'Add Column', self.addColumn)
        
        
        box = OWGUI.widgetBox(self.controlArea, "Table")
        self.dataClassTable = QTableWidget()
        box.layout().addWidget(self.dataClassTable)
        self.dataClassTable.setColumnCount(self.colCount+1)
        self.dataClassTable.setRowCount(3)
        # rowatt = QTableWidgetItem()
        # rowatt.setText('Data Type')
        # self.dataClassTable.setVerticalHeaderItem(0, rowatt)
        classatt = QTableWidgetItem()
        classatt.setText('Label')
        self.dataClassTable.setVerticalHeaderItem(1, classatt)
        for i in xrange(self.colCount+1):
            cw = QComboBox()
            tb = QTableWidget()
            tb.setColumnCount(1)
            tb.setRowCount(1)
            # vh = tb.verticalHeader()
            # vh.setSectionHidden(0, True)
            # hh = tb.horizontalHeader()
            # hh.setSectionHidden(0, True)
            cw.addItems(['Numeric', 'Text'])
            self.dataClassTable.setCellWidget(0,i,cw)
            self.dataClassTable.setCellWidget(2, i, tb)
        self.dataClassTable.show()
        #self.dataClassTable.resize()
        self.dataTable = QTableWidget()
        box.layout().addWidget(self.dataTable)
        self.dataTable.setColumnCount(self.colCount+1)
        self.dataTable.setRowCount(self.rowCount+1)
        self.dataTable.show()
        self.connect(self.dataTable, SIGNAL("cellClicked(int, int)"), self.cellClicked) # works OK
        self.connect(self.dataTable, SIGNAL("cellChanged(int, int)"), self.itemChanged)
        #self.connect(self.dataTable, SIGNAL("cellEntered(int, int)"), self.itemEntered)
        
        
    def addColumn(self):
        self.dataTable.insertColumn(self.colCount+1)
        self.dataClassTable.insertColumn(self.colCount+1)
        self.colCount += 1
        cw = QComboBox()
        cw.addItems(['Numeric', 'Text'])
        self.dataClassTable.setCellWidget(0,self.colCount,cw)
    def cellClicked(self, row, col):
        # currentRow = item.row()
        # currentCol = item.column()
        self.onCellFocus(row, col)
    
    # def itemEntered(self, row, col):
        # currentRow = item.row()
        # currentCol = item.column()
        # print col
        # print row
        # self.onCellFocus(row, col)
    def onCellFocus(self, currentRow, currentCol):
        item = self.dataTable.item(currentRow, currentCol)
        self.dataTable.editItem(item)
    def itemChanged(self, row, col):
        print row
        print self.rowCount
        if row == self.rowCount:
            self.dataTable.insertRow(self.rowCount+1)
            self.rowCount += 1
            
        self.dataTable.setCurrentCell(row+1, col)
        item = self.dataTable.item(row+1, col)
        self.onCellFocus(row+1, col)
        self.dataTable.editItem(item)


        
    def commitTable(self):
        #run through the table and make the output
        rinsertion = ''
        print self.colCount
        
        for i in range(0, self.colCount+1): # move across the columns
            combo = self.dataClassTable.cellWidget(0, i)
            
            rinsertion += str(self.dataClassTable.item(1, i).text())
            rinsertion += '=c('
            print self.rowCount
            for j in range(0, self.rowCount):
                print 'j'+str(j)
                tableItem = self.dataTable.item(j,i)
                if tableItem == None:
                    text = 'NA'
                else:
                    text = tableItem.text()
                if combo.currentText() == 'Text':
                    rinsertion += '"'+str(text)+'"'
                elif combo.currentText() == 'Numeric':  
                    rinsertion += str(text)
                rinsertion += ','
            rinsertion = rinsertion[:-1]
            rinsertion += '),'
        rinsertion = rinsertion[:-1]
        print rinsertion
        self.R(self.Rvariables['table']+'<-data.frame('+rinsertion+')')
        self.rSend('Data Table', {'data':self.Rvariables['table']})
        
    def reloadTable(self):
        # reload the table from the table input data likely in R
        pass