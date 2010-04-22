"""
<name>Data Entry</name>
<description>A table input data entry into a data.frame.</description>
<tags>Data Input</tags>
<RFunctions>base:data.frame</RFunctions>
<icon>icons/File.png</icon>
<priority>20</priority>
"""

import redRGUI
from OWRpy import *

class dataEntry(OWRpy):
    settingsList = ['savedData']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Data Entry", wantGUIDialog = 1, wantMainArea = 0, resizingEnabled = 1)

        self.rowCount = 10
        self.colCount = 10
        self.maxRow = 0 # sets the most extreme row and cols
        self.maxCol = 0
        self.classes = None
        self.savedData = {}
        self.loadSettings()
        self.setRvariableNames(['table', 'table_cm'])
        
        self.inputs = [('Data Table', RvarClasses.RDataFrame, self.processDF)]
        self.outputs = [('Data Table', RvarClasses.RDataFrame)] # trace problem with outputs
        #GUI.
        
        
        box = redRGUI.groupBox(self.GUIDialog, label = "Options")
        redRGUI.button(self.bottomAreaRight, 'Commit', self.commitTable)
        self.rowHeaders = redRGUI.checkBox(box, label=None, buttons=['Use Row Headers', 'Use Column Headers'])
        #self.colHeaders = redRGUI.checkBox(box, label=None, buttons=['Use Column Headers'])
        self.rowHeaders.setChecked(['Use Row Headers', 'Use Column Headers'])
        #self.colHeaders.setChecked(['Use Column Headers'])
        self.customClasses = redRGUI.button(box, 'Use Custom Column Classes', callback = self.setCustomClasses)
        redRGUI.button(box, 'Clear Classes', callback = self.clearClasses)

        box = redRGUI.groupBox(self.controlArea, label = "Table", 
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        #self.splitCanvas.addWidget(box)
        self.dataTable = redRGUI.Rtable(box, Rdata = None, rows = self.rowCount+1, columns = self.colCount+1)

        self.dataTable.show()
        upcell = QTableWidgetItem()
        upcell.setBackgroundColor(Qt.gray)
        upcell.setFlags(Qt.NoItemFlags) #sets the cell as being unselectable
        self.dataTable.setItem(0,0,upcell)
        # self.dataTable.item(0,0).setBackgroundColor(Qt.gray)
        self.connect(self.dataTable, SIGNAL("cellClicked(int, int)"), self.cellClicked) # works OK
        self.connect(self.dataTable, SIGNAL("cellChanged(int, int)"), self.itemChanged)
        self.window = QDialog(self)
        self.window.setLayout(QVBoxLayout())
        self.classTable = redRGUI.table(self.window, rows = self.maxCol, columns = 2)
        self.resize(700,500)
        self.move(300, 25)
    def processDF(self, data):
        if data and ('data' in data.keys()):
            self.data = data['data']
            self.savedData = data.copy()
            self.populateTable()
        else:
            return
    def populateTable(self):
        self.dataTable.setRTable('cbind(rownames = '+self.savedData.getRownames_call()+','+self.data+')')
        
        self.connect(self.dataTable, SIGNAL("cellClicked(int, int)"), self.cellClicked) # works OK
        self.connect(self.dataTable, SIGNAL("cellChanged(int, int)"), self.itemChanged)
    def cellClicked(self, row, col):
        pass

    def onCellFocus(self, currentRow, currentCol, tb):
        if len(tb) == 0: return
        print 'cell on focus'
        item = tb.item(currentRow, currentCol)
        tb.editItem(item)
    
    def itemChanged(self, row, col):
        if row > self.rowCount-3: #bump up the number of cells to keep up with the needs of the table
            self.dataTable.setRowCount(self.rowCount+3)
            self.rowCount += 3
        if col > self.colCount-3:
            self.dataTable.setColumnCount(self.colCount+3)
            self.colCount += 3
        if row > self.maxRow: self.maxRow = row #update the extremes of the row and cols
        if col > self.maxCol: self.maxCol = col
        self.dataTable.setCurrentCell(row+1, col)

    def setCustomClasses(self):
        self.classTable = redRGUI.table(self.window, rows = self.maxCol, columns = 2)
        for j in range(1, self.colCount+1):
            cb = QComboBox()
            item = self.dataTable.item(0, j)
            if item == None:
                newitem = QTableWidgetItem(str('NA'))
            else:
                newitem = QTableWidgetItem(str(item.text()))
            cb.addItems(['Default', 'Factor', 'Numeric', 'Character'])
            self.classTable.setCellWidget(j-1, 1, cb)
            newitem.setToolTip(str('Set the data type for column '+str(newitem.text())))
            self.classTable.setItem(j-1, 0, newitem)
            
        redRGUI.button(self.window, 'Set Classes', callback = self.setClasses)
        redRGUI.button(self.window, 'Clear Classes', callback = self.clearClasses)
        self.window.show()
    def clearClasses(self):
        self.classes = None
        self.window.hide()
        
    def setClasses(self):
        if self.classTable.rowCount() != self.maxCol:
            print self.classTable.rowCount()
            print self.maxCol
            self.window.hide()
            self.setCustomClasses()
            return
        else:
            self.classes = []
            for j in range(0, self.classTable.rowCount()):
                txt = self.classTable.cellWidget(j,1)
                ct = txt.currentText()
                if ct == 'Default':
                    self.classes.append(('', ''))
                elif ct == 'Factor':
                    self.classes.append(('as.factor(', ')'))
                elif ct == 'Numeric':
                    self.classes.append(('as.numeric(', ')'))
                elif ct == 'Character':
                    self.classes.append(('as.character(', ')'))
        self.window.hide()
        self.status.setText('Classes Set')
    def commitTable(self):
        #run through the table and make the output
        trange = self.dataTable.selectedRanges()[0]
        if trange.leftColumn() == trange.rightColumn() and trange.topRow() == trange.bottomRow():
            rowi = range(0, self.maxRow+1)
            coli = range(0, self.maxCol+1)
        else:

            rowi = range(trange.topRow(), trange.bottomRow()+1)
            coli = range(trange.leftColumn(), trange.rightColumn()+1)
            
        if self.dataTable.item(rowi[0], coli[0]) == None: 

            self.rowHeaders.setChecked(['Use Row Headers'])
            self.rowHeaders.setChecked(['Use Column Headers'])
        rownames = {}  
        colnames = {}        
        if 'Use Row Headers' in self.rowHeaders.getChecked():
            
            for i in rowi[1:]:
                item = self.dataTable.item(i, coli[0])
                if item != None:
                    thisText = item.text()
                else: thisText = str(i)
                if thisText == None or thisText == '':
                    thisText = str(i)
                    
                rownames[str(i)] = (str(thisText))
            coli = coli[1:] #index up the cols

        if 'Use Column Headers' in self.rowHeaders.getChecked():
            for j in coli:
                item = self.dataTable.item(rowi[0], j)
                if item != None:
                    thisText = item.text()
                else: thisText = '"'+str(j)+'"'
                if thisText == None or thisText == '':
                    thisText = '"'+str(j)+'"'
                colnames[str(j)] = (str(thisText))
            rowi = rowi[1:] #index up the row count

        rinsertion = []
        
        for j in coli:
            element = ''
            if colnames:
                element += colnames[str(j)]+'='
            if self.classes:
                element += self.classes[j-1][0]
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
                rname.append(rownames[str(i)])
            rnf = '","'.join(rname)
            rinsert += ', row.names =c("'+rnf+'")' 
        self.R(self.Rvariables['table']+'<-data.frame('+rinsert+')')
        
        # make a new data table, we copy the dictAttrs from the incoming table but nothing more, as a patch for cm managers we also remove the cm from the dictAttrs if one exists
        self.newData = RvarClasses.RDataFrame(data = self.Rvariables['table'], parent = self.Rvariables['table'])
        self.newData.dictAttrs = self.savedData.dictAttrs
        if 'cm' in self.newData.dictAttrs.keys():
            self.newData.dictAttrs.pop('cm')
        self.rSend('Data Table', self.newData)
    def loadCustomSettings(self,settings=None):
        if settings and 'newData' in settings.keys():
            self.processDF(self.newData)
            