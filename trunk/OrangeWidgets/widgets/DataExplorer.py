"""
<name>Data Explorer</name>
<description>Shows data in a spreadsheet.  The data can be subset and passed to other widgets.</description>
<tags>Data Manipulation</tags>
<RFunctions>base:data.frame,base:matrix</RFunctions>
<icon>icons/datatable.png</icon>
<priority>1010</priority>
<author>Peter Juvan (peter.juvan@fri.uni-lj.si) modifications by Kyle R Covington and Anup Parikh</author>
"""

from OWRpy import *
import OWGUI, redRGUI
import OWGUIEx
import math, sip

class DataExplorer(OWRpy):
    def __init__(self, parent=None, signalManager = None):
        OWRpy.__init__(self, parent, signalManager, "Data Table", wantGUIDialog = 1, wantMainArea = 0)
        
        self.data = ''
        self.orriginalData = '' # a holder for data that we get from a connection
        self.currentDataTransformation = '' # holder for data transformations ex: ((data[1:5,])[,1:3])[1:2,]
        self.dataParent = {}
        
        self.currentRow = 0
        self.currentColumn = 0
        
        self.criteriaList = []
        
        self.inputs = [('Data Table', RvarClasses.RDataFrame, self.processData), ('Row Subset Vector', RvarClasses.RVector, self.setRowSelectVector), ('Column Subset Vector', RvarClasses.RVector, self.setColumnSelectVector)]
        self.outputs = [('Data Subset', RvarClasses.RDataFrame)]
        
        ######## GUI ############
        
        self.tableArea = redRGUI.widgetBox(self.controlArea)
        
        self.table = redRGUI.table(self.tableArea)
        #self.connect(self.table, SIGNAL('cellClicked(int, int)'), self.cellEntered) # monitors which cell is activated, this is used for setting the criteria of the lineEditHint next to the rows and the columns
        
        self.clearButton = redRGUI.button(self.bottomAreaLeft, "Clear Table", self.table.clear())
        ######## Row Column Dialog ########
        self.rowcolDialog = QDialog()
        self.rowcolDialogButton = redRGUI.button(self.bottomAreaLeft, "Show Row Column Dialog", callback = self.showRowColumnDialog)
        self.rowcolDialogButton.hide()
        self.rowcolDialogButton.setEnabled(False)
        
        self.rowcolDialog.setLayout(QVBoxLayout())
        self.rowcolDialog.setWindowTitle('Row Column Dialog')
        rowcolBoxArea = redRGUI.widgetBox(self.rowcolDialog, orientation = 'horizontal')
        rowArea = redRGUI.widgetBox(rowcolBoxArea, orientation = 'vertical')
        colArea = redRGUI.widgetBox(rowcolBoxArea, orientation = 'vertical')
        
        self.selectRowsOnAttachedButton = redRGUI.button(rowArea, "Select on Attached", callback = self.selectRowsOnAttached)
        self.selectRowsOnAttachedButton.setEnabled(False)
        self.selectColumnsOnAttachedButton = redRGUI.button(colArea, "Select on Attached", callback = self.selectColumnsOnAttached)
        self.selectColumnsOnAttachedButton.setEnabled(False)
        
        self.rowListBox = redRGUI.listBox(rowArea)
        self.colListBox = redRGUI.listBox(colArea)
        self.rowListBox.setSelectionMode(QAbstractItemView.MultiSelection) # set them to accept multiple selections
        self.colListBox.setSelectionMode(QAbstractItemView.MultiSelection)
        
        self.rowListHint = OWGUIEx.lineEditHint(rowArea, None, None, callback = self.rowListCallback) # hints that will hold the data for the row and column names, these should be searchable and allow the user to pick subsets of rows and cols to show in the data.  Ideally these will be subset from either another vector of names or will be short enough that the user can type them individually into the line hint
        
        self.colListHint = OWGUIEx.lineEditHint(colArea, None, None, callback = self.colListCallback)
    def showRowColumnDialog(self):
        self.rowcolDialog.show()
    def selectColumnsOnAttached(self): pass
    def selectRowsOnAttached(self): pass
    def rowListCallback(self): pass
    def colListCallback(self): pass
    def setRowSelectVector(self): pass
    
    def setColumnSelectVector(self): pass
        
    def processData(self, data, newData = True):
        if data:
            self.table.hide()
            self.table = redRGUI.table(self.tableArea)
            self.data = data['data']
            if newData:
                self.orriginalData = data['data']
                self.dataParent = data.copy()
            # first get some info about the table so we can put that into the current table.
            dims = self.R('dim('+self.data+')')
            
            ##### Block to set the currentDataTransformation #######
            if (int(dims[0]) != 0) and (int(dims[1]) != 0) and (int(dims[0]) < 500) and (int(dims[1]) < 500): # don't let the dims get too high or too low
                self.currentDataTransformation = self.data # there isn't any transformation to apply
            elif not (int(dims[0]) < 500) and not (int(dims[1]) < 500): # they are both over 500
                self.currentDataTransformation = self.data+'[1:500, 1:500]' # we only show the first 500 rows and cols.  This will need to be subset later and we should show the row and column names in a separate dialog
                self.rowcolDialog.show()
                self.rowcolDialogButton.show()
                self.rowcolDialogButton.setEnabled(True)
            elif not (int(dims[0]) < 500): # made it this far so there must be fewer columns than 500 but more than 500 rows
                self.currentDataTransformation = self.data+'[1:500,]'
                self.rowcolDialog.show()
                self.rowcolDialogButton.show()
                self.rowcolDialogButton.setEnabled(True)
            elif not (int(dims[1]) < 500):
                self.currentDataTransformation = self.data+'[,1:500]'
                self.rowcolDialog.show()
                self.rowcolDialogButton.show()
                self.rowcolDialogButton.setEnabled(True)
            ######## End Block ##########
            
            ######## Set the table for the data ######
            self.setDataTable()
        else: # clear all of the data and move on
            self.data = ''
            self.currentDataTransformation = ''
            self.dataParent = {}
        
    def setDataTable(self):
        ### want to set the table with the data in the currentDataTransformation object
        
        # a set of recurring cellWidgets that we will use for the column settings
        #
        # get the dims to set the data
        dims = self.R('dim('+self.currentDataTransformation+')') 
        
        # set the row and column count
        self.table.setRowCount(min([int(dims[0]), 500])+2) # set up the row and column counts of the table
        self.table.setColumnCount(min([int(dims[1]), 500])+2)
        
        rownames = self.R('rownames('+self.currentDataTransformation+')')
        colnames = self.R('colnames('+self.currentDataTransformation+')')
        # start to fill the table from top to bottom, left to right.
        for j in range(0, min([int(dims[1]), 500])+2):# the columns
            for i in range(0, min([int(dims[0]), 500])+2): # the rows
            
                
                # some special cases that we need to consider, is this the first row (containing the search for the row) or is this the second row (containing the rownames)
                if j == 0 and i > 1: # the data selector for the rows
                    cw = OWGUIEx.lineEditHint(self, None, None, callback = self.rowLineEditHintAccepted)
                    cw.setItems(self.R('as.character('+self.currentDataTransformation+'['+str(i-1)+',])'))
                    self.table.setCellWidget(i,j, cw)
                    
                elif j == 1 and i == 0: # the data selector for the rownames
                    cw = OWGUIEx.lineEditHint(self, None, None, callback = self.rownameLineEditHintAccepted)
                    cw.setItems(rownames)
                    self.table.setCellWidget(i, j, cw)
                    
                elif j == 1 and i == 1:
                    ci = QTableWidgetItem('Rownames')
                    self.table.setItem(i, j, ci)
                    
                elif j == 1 and i > 1: # the rownames
                    # we should set the text of this cell to be the rowname of the data.frame 
                    ci = QTableWidgetItem(str(rownames[i-2]))
                    self.table.setItem(i, j, ci)
                     #commented out for testing
                elif j > 1 and i == 0: # setting the line edits for looking through the columns
                    # first we need to find the colData and the class of this column
                    colData = self.R('as.vector('+self.currentDataTransformation+'[,'+str(j-1)+'])') # we need this for setting the data that will go into the body of the table
                    if type(colData) in [type(''), type(1), type(1.3)]:
                        colData = [colData]
                        print 'colData converted to list'
                    thisClass = self.R('class('+self.currentDataTransformation+'[,'+str(j-1)+'])')
                    if thisClass in ['character']: # we want to show the element but not add it to the criteria
                        cw = OWGUIEx.lineEditHint(self, None, None, callback = lambda i = i, j = j: self.columnLineEditHintAccepted(i, j))
                        cw.setItems(self.R('as.vector('+self.currentDataTransformation+'[,'+str(j-1)+'])'))
                        cw.setToolTip('Moves to the selected text, but does not subset')
                        self.table.setCellWidget(i, j, cw)
                    elif thisClass in ['numeric']:
                        cw = redRGUI.lineEdit(self, toolTip = 'Subsets based on the criteria that you input, ex. > 50 gives rows where this column is greater than 50, == 50 gives all rows where this column is equal to 50.\nNote, you must use two equal (=) signs, ex. ==.')
                        #cw.setToolTip('Subsets based on the criteria that you input, ex. > 50 gives rows where this column is greater than 50, == 50 gives all rows where this column is equal to 50.\nNote, you must use two equal (=) signs, ex. ==.')
                        self.connect(cw, SIGNAL('returnPressed()'), lambda i = i, j = j: self.columnNumericCriteriaAccepted(i, j))
                        self.table.setCellWidget(i, j, cw)
                    
                    elif thisClass in ['factor']:
                        cw = OWGUIEx.lineEditHint(self, None, None, callback = lambda i = i, j = j: self.columnFactorCriteriaAccepted(i, j))
                        cw.setToolTip('Subsets based on the elements from a factor column.  These columns contain repeating elements such as "apple", "apple", "banana", "banana".')
                        print self.R('levels('+self.currentDataTransformation+'[,'+str(j-1)+'])')
                        cw.setItems(self.R('levels('+self.currentDataTransformation+'[,'+str(j-1)+'])'))
                        self.table.setCellWidget(i, j, cw)
                        
                elif j > 1 and i == 1: # set the colnames
                    ci = QTableWidgetItem(colnames[j-2])
                    self.table.setItem(i, j, ci)
                elif j > 1 and i> 1:
                    ci = QTableWidgetItem(str(colData[i-2]))
                    self.table.setItem(i, j, ci)
    def columnFactorCriteriaAccepted(self, i, j):
        print str(str(i) + ' column ' + str(j) + ' row ')
        cw = self.table.cellWidget(i, j)
        text = str(cw.text())
        colName = str(self.table.item(1, j).text())
        self.criteriaList.append(self.dataParent['parent']+'$'+colName+'==\''+text+'\'')
        #self.criteriaList.append('['+self.dataParent['parent']+'[,"'+colName+'"] == \''+text+'\',]')
        newData = {'data':self.orriginalData+'['+'&'.join(self.criteriaList)+',]'}
        self.processData(newData, False)
        
    def columnNumericCriteriaAccepted(self, i, j):
        cw = self.table.cellWidget(i, j)
        text = str(cw.text())
        colName = str(self.table.item(1, j).text())
        self.criteriaList.append(self.dataParent['parent']+'$'+colName+text)
        #self.criteriaList.append('['+self.dataParent['parent']+'[,"'+colName+'"] == \''+text+'\',]')
        newData = {'data':self.orriginalData+'['+'&'.join(self.criteriaList)+',]'}
        self.processData(newData, False)
        
    def columnLineEditHintAccepted(self, i, j):
        cw = self.table.cellWidget(i, j)
        text = str(cw.text())
        
        for i in range(2, self.table.rowCount()):
            ci = self.table.item(i, self.currentColumn)
            if str(ci.text()) == text:
                self.table.scrollToItem(ci)
                return
    def rownameLineEditHintAccepted(self):
        cw = self.table.cellWidget(self.currentRow, self.currentColumn)
        text = str(cw.text())
        
        for i in range(2, self.table.rowCount()):
            ci = self.table.item(i, 1)
            if str(ci.text()) == text:
                self.table.scrollToItem(ci)
                return
    def rowLineEditHintAccepted(self):
        cw = self.table.cellWidget(self.currentRow, self.currentColumn)
        text = str(cw.text())
        
        # find the item with the matching text
        for i in range(2, self.table.columnCount()):
            ci = self.table.item(self.currentRow, i)
            if str(ci.text()) == text:
                self.table.scrollToItem(ci)
                return
                
    def cellEntered(self, rowInt, colInt):
        self.currentRow = rowInt
        self.currentColumn = colInt