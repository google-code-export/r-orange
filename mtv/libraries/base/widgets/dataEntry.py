"""
<name>Data Entry</name>
<tags>Data Input</tags>
<icon>readfile.png</icon>
"""

import redRGUI
from OWRpy import *
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.qtWidgets.table import table
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.lineEdit import lineEdit
class dataEntry(OWRpy):
    
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)

        self.rowCount = 1
        self.colCount = 1
        self.maxRow = 0 # sets the most extreme row and cols
        self.maxCol = 0
        self.classes = None
        self.savedData = None
        self.setRvariableNames(['table', 'table_cm'])
        
        self.inputs.addInput('id0', 'Data Table', redRRDataFrame, self.processDF)

        self.outputs.addOutput('id0', 'Data Table', redRRDataFrame)
 # trace problem with outputs
        #GUI.
        
        
        # box = groupBox(self.GUIDialog, label = "Options")
        redRCommitButton(self.bottomAreaRight, 'Commit', self.commitTable)
        # self.rowHeaders = checkBox(box, label=None, buttons=['Use Row Headers', 'Use Column Headers'])
        #self.colHeaders = checkBox(box, label=None, buttons=['Use Column Headers'])
        #self.rowHeaders.setChecked(['Use Row Headers', 'Use Column Headers'])
        #self.colHeaders.setChecked(['Use Column Headers'])
        # self.customClasses = button(box, 'Use Custom Column Classes', callback = self.setCustomClasses)
        # button(box, 'Clear Classes', callback = self.clearClasses)
        
        self.columnDialog = QDialog(self)
        self.columnDialog.setLayout(QVBoxLayout())
        self.columnDialog.hide()
        self.columnNameLineEdit = lineEdit(self.columnDialog, label = 'Column Name:')
        button(self.columnDialog, 'Commit', callback = self.commitNewColumn)
        button(self.bottomAreaRight, "Add Column", callback = self.columnDialog.show)
        
        
        box = groupBox(self.controlArea, label = "Table", 
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        #self.splitCanvas.addWidget(box)
        

        self.dataTable = table(box, data = None, rows = self.rowCount+1, columns = self.colCount)
        if self.dataTable.columnCount() < 1:
            self.dataTable.setColumnCount(1)
            self.dataTable.setHorizontalHeaderLabels(['Rownames'])
        if self.dataTable.rowCount() < 1:
            self.dataTable.setRowCount(1)
        self.dataTable.setHorizontalHeaderLabels(['Rownames'])
        
        self.connect(self.dataTable, SIGNAL("cellClicked(int, int)"), self.cellClicked) # works OK
        self.connect(self.dataTable, SIGNAL("cellChanged(int, int)"), self.itemChanged)
        # self.window = QDialog(self)
        # self.window.setLayout(QVBoxLayout())
        # self.classTable = table(self.window, rows = self.maxCol, columns = 2)
        self.resize(700,500)
        self.move(300, 25)
    def commitNewColumn(self):
        labels = []
        for i in range(self.dataTable.columnCount()):
            item = self.dataTable.horizontalHeaderItem(i)
            
            if item:
                labels.append(item.text())
        labels.append(str(self.columnNameLineEdit.text()))
        self.dataTable.setColumnCount(self.dataTable.columnCount()+1)
        self.dataTable.setHorizontalHeaderLabels(labels)
        self.colCount = self.dataTable.columnCount()
        self.columnNameLineEdit.clear()
        self.columnDialog.hide()
    def processDF(self, data):
        if data:
            self.data = data.getData()
            self.savedData = data
            self.populateTable()
        else:
            return
    def populateTable(self):
        #pythonData = self.R('cbind(rownames = '+self.savedData.getRownames_call()+','+self.data+')')
        pythonData = self.savedData._convertToStructuredDict()
        self.dataTable.setTable(pythonData.getData())
        self.connect(self.dataTable, SIGNAL("cellClicked(int, int)"), self.cellClicked) # works OK
        self.connect(self.dataTable, SIGNAL("cellChanged(int, int)"), self.itemChanged)
    def cellClicked(self, row, col):
        print str(row), str(col)
        pass

    def onCellFocus(self, currentRow, currentCol, tb):
        if len(tb) == 0: return
        print 'cell on focus'
        item = tb.item(currentRow, currentCol)
        tb.editItem(item)
    
    def itemChanged(self, row, col):
        if row == self.rowCount-1: #bump up the number of cells to keep up with the needs of the table
            self.dataTable.setRowCount(self.rowCount+1)
            self.rowCount += 1
        if row > self.maxRow: self.maxRow = row #update the extremes of the row and cols
        if col > self.maxCol: self.maxCol = col
        self.dataTable.setCurrentCell(row+1, col)

    def commitTable(self):
        #run through the table and make the output
        try:
            trange = self.dataTable.selectedRanges()[0]
        except:
            trange = None
        if trange and trange.leftColumn() == trange.rightColumn() and trange.topRow() == trange.bottomRow():
            rowi = range(0, self.maxRow+1)
            coli = range(0, self.maxCol+1)
        else:
            rowi = range(trange.topRow(), trange.bottomRow())
            coli = range(trange.leftColumn(), trange.rightColumn()+1)
            
       
        rownames = {}  
        colnames = {}        
        #if 'Use Row Headers' in self.rowHeaders.getChecked():
            
        for i in rowi:
            item = self.dataTable.item(i, coli[0])
            if item != None:
                thisText = item.text()
            else: thisText = str(i)
            if thisText == None or thisText == '':
                thisText = str(i)
                
            rownames[str(i)] = (str(thisText))
        coli = coli[1:] #index up the cols

       # if 'Use Column Headers' in self.rowHeaders.getChecked():
        for j in coli:
            item = self.dataTable.horizontalHeaderItem(j)
            if item != None:
                thisText = item.text()
            else: thisText = '"'+str(j)+'"'
            if thisText == None or thisText == '':
                thisText = '"'+str(j)+'"'
            thisText = thisText.split(' ')[0]
            colnames[str(j)] = (str(thisText))

        rinsertion = []
        
        for j in coli:
            element = ''
            if colnames:
                element += colnames[str(j)]+'='
            # if self.classes:
                # element += self.classes[j-1][0]
            element += 'c('
            inserts = []
            for i in rowi:

                tableItem = self.dataTable.item(i,j)
                if tableItem == None:
                    inserts.append('NA')
                else:
                    try: #catch if the element can be coerced to numeric in the table
                        float(tableItem.text()) #will fail if can't be coerced to int 
                        inserts.append(str(tableItem.text()))
                    except:
                        if tableItem.text() == 'NA': 
                            inserts.append(str(tableItem.text()))
                            print 'set NA'
                        elif tableItem.text() == '1.#QNAN': 
                            inserts.append('NA') #if we read in some data
                            print 'set QNAN to NA'
                        else: 
                            inserts.append('"'+str(tableItem.text())+'"')
                            print str(tableItem.text())+' set as text'

            insert = ','.join(inserts)
            element += insert+')'
            if self.classes:
                element += self.classes[j-1][1]
            rinsertion.append(element)
            
        rinsert = ','.join(rinsertion)

        if len(rownames) > 0:
            rname = []
            for i in rowi:
                if rownames[str(i)] in rname:
                    rname.append(rownames[str(i)]+'_at_'+str(i))
                else:
                    rname.append(rownames[str(i)])
            rnf = '","'.join(rname)
            rinsert += ', row.names =c("'+rnf+'")' 
        self.R(self.Rvariables['table']+'<-data.frame('+rinsert+')', wantType = 'NoConversion')
        
        # make a new data table, we copy the dictAttrs from the incoming table but nothing more, as a patch for cm managers we also remove the cm from the dictAttrs if one exists
        
        self.newData = redRRDataFrame(data = self.Rvariables['table'], parent = self.Rvariables['table'])
        
        self.rSend("id0", self.newData)
        self.processDF(self.newData)  ## a good way to ensure loading and saving.
        
    def getReportText(self, fileDir):
        return 'Data was entered into the R session manually through this widget.  For more informaiton please see the Red-R .rrs file or some output from the Red-R file.\n\n'

            