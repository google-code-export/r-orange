"""
<name>Data Explorer</name>
<description>Shows data in a spreadsheet.  The data can be subset and passed to other widgets.</description>
<tags>Data Manipulation</tags>
<RFunctions>base:data.frame,base:matrix</RFunctions>
<icon>icons/datatable.png</icon>
<priority>1010</priority>
<author>Kyle R Covington and Anup Parikh</author>
"""

from OWRpy import *
import OWGUI, redRGUI
import OWGUIEx
import math, sip

class DataExplorer(OWRpy):
    settingsList = []
    def __init__(self, parent=None, signalManager = None):
        OWRpy.__init__(self, parent, signalManager, "Data Table", wantMainArea = 0)
        
        self.data = ''
        self.orriginalData = '' # a holder for data that we get from a connection
        self.currentDataTransformation = '' # holder for data transformations ex: ((data[1:5,])[,1:3])[1:2,]
        self.dataParent = {}
        
        self.currentRow = 0
        self.currentColumn = 0
        
        self.criteriaList = []
        self.columnCriteriaList = []
        
        self.inputs = [('Data Table', RvarClasses.RDataFrame, self.processData), ('Row Subset Vector', RvarClasses.RVector, self.setRowSelectVector), ('Column Subset Vector', RvarClasses.RVector, self.setColumnSelectVector)]
        self.outputs = [('Data Subset', RvarClasses.RDataFrame)]
        
        ######## GUI ############
        
        self.tableArea = redRGUI.widgetBox(self.controlArea)
        holder = redRGUI.widgetBox(self.tableArea, orientation = 'horizontal') # need to make a holder so that all of the criteria buttons move to the left hand side.  Ideally there won't be that many criteria that they user will set, but who knows...
        
        holder.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        redRGUI.widgetLabel(holder, "Row Selection Criteria (click to remove):")
        self.criteriaArea = redRGUI.widgetBox(holder, orientation = 'horizontal')
        self.criteriaArea.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        redRGUI.widgetLabel(holder, "Column Selection Criteria (click to remove):")
        self.columnCriteriaArea = redRGUI.widgetBox(holder, orientation = 'horizontal')
        self.columnCriteriaArea.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        bufferBox = redRGUI.widgetBox(holder)
        bufferBox.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
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
        subOnSelectButton = redRGUI.button(self.rowcolDialog, "Subset on Selected", callback = self.subsetOnSelected)
        subOnSelectButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
    def showRowColumnDialog(self):
        self.rowcolDialog.show()
    def selectColumnsOnAttached(self): pass
    def selectRowsOnAttached(self): pass
    def rowListCallback(self): pass
    def colListCallback(self): pass
    def setRowSelectVector(self): pass
    def setColumnSelectVector(self): pass
    def subsetOnSelected(self):
        # collect the selected names in the list boxes and subset on those
        pass
    def processData(self, data, newData = True):
        if data:
            self.table.hide()
            self.table = redRGUI.table(self.tableArea)
            self.data = data['data']
            self.rownames = self.R('rownames('+self.data+')')
            if type(self.rownames) == str:
                self.rownames = [self.rownames]
            self.colnames = self.R('colnames('+self.data+')')
            if type(self.colnames) == str:
                self.colnames = [self.colnames]
            #print self.data
            #print self.rownames
            #print self.colnames
            if newData == True:
                self.orriginalData = data['data']
                self.orriginalRowNames = self.rownames
                self.orriginalColumnNames = self.colnames
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
                    self.rowListBox.addRItems(self.rownames)
                    self.rowListHint.setItems(self.rownames)
                    self.colListBox.addRItems(self.colnames)
                    self.colListHint.setItems(self.colnames)
                    self.rowcolDialogButton.setEnabled(True)
                elif not (int(dims[0]) < 500): # made it this far so there must be fewer columns than 500 but more than 500 rows
                    self.currentDataTransformation = self.data+'[1:500,]'
                    self.rowcolDialog.show()
                    self.rowcolDialogButton.show()
                    self.rowListBox.addRItems(self.rownames)
                    self.rowListHint.setItems(self.rownames)
                    self.rowcolDialogButton.setEnabled(True)
                elif not (int(dims[1]) < 500):
                    self.currentDataTransformation = self.data+'[,1:500]'
                    self.rowcolDialog.show()
                    self.rowcolDialogButton.show()
                    self.colListBox.addRItems(self.colnames)
                    self.colListHint.setItems(self.colnames)
                    self.rowcolDialogButton.setEnabled(True)
                ######## End Block ##########
            else:
                dims = self.R('dim('+self.data+')')
                if int(dims[0]) > 500 and int(dims[1]) > 500:
                    self.currentDataTransformation = self.data+'[1:500, 1:500]'
                elif int(dims[0]) > 500:
                    self.currentDataTransformation = self.data+'[1:500,]'
                elif int(dims[1]) > 500:
                    self.currentDataTransformation = self.data+'[,1:500]'
                else:
                    self.currentDataTransformation = self.data
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
        tableData = self.R('as.matrix('+self.currentDataTransformation+')') # collect all of the table data into an object
        tableData = numpy.array(tableData) # make the conversion to a numpy object for subsetting
        #print tableData
        
        # start to fill the table from top to bottom, left to right.
        for j in range(0, min([int(dims[1]), 500])+2):# the columns
            for i in range(0, min([int(dims[0]), 500])+2): # the rows
            
                
                # some special cases that we need to consider, is this the first row (containing the search for the row) or is this the second row (containing the rownames)
                if j == 0 and i > 1: # the data selector for the rows
                    thisClass = self.R('class('+self.currentDataTransformation+'['+str(i-1)+',])', silent = True)
                    if thisClass == 'factor':
                        cw = OWGUIEx.lineEditHint(self, None, None, callback = self.rowLevelsLineEditHintAccepted)
                        cw.setItems(self.R('levels('+self.currentDataTransformation+'['+str(i-1)+',])', silent = True))
                    elif thisClass == 'numeric':
                        cw = redRGUI.lineEdit(self, toolTip='Subsets based on the criteria that you input, ex. > 50 gives rows where this column is greater than 50, == 50 gives all rows where this column is equal to 50.\nNote, you must use two equal (=) signs, ex. ==.')
                        self.connect(cw, SIGNAL('returnPressed()'), lambda i = i, j = j: self.rowNumericCriteriaAccepted(i, j))
                    else:
                        cw = OWGUIEx.lineEditHint(self, None, None, callback = self.rowLineEditHintAccepted)
                        cw.setItems(tableData[i-2])
                    self.table.setCellWidget(i,j, cw)
                elif j == 0 and (i == 0 or i == 1):
                    upcell = QTableWidgetItem()
                    upcell.setBackgroundColor(Qt.gray)
                    upcell.setFlags(Qt.NoItemFlags) #sets the cell as being unselectable
                    self.table.setItem(i,j,upcell)
                elif j == 1 and i == 0: # the data selector for the rownames
                    cw = OWGUIEx.lineEditHint(self, None, None, callback = lambda i = i, j = j: self.rownameLineEditHintAccepted(i, j))
                    cw.setToolTip('Scroll to a specific Rowname')
                    cw.setItems(self.orriginalRowNames)
                    self.table.setCellWidget(i, j, cw)
                    
                elif j == 1 and i == 1:
                    ci = QTableWidgetItem('Rownames')
                    self.table.setItem(i, j, ci)
                    
                elif j == 1 and i > 1: # the rownames
                    # we should set the text of this cell to be the rowname of the data.frame 
                    ci = QTableWidgetItem(str(self.rownames[i-2]))
                    ci.setBackgroundColor(Qt.red)
                    self.table.setItem(i, j, ci)
                     #commented out for testing
                elif j > 1 and i == 0: # setting the line edits for looking through the columns
                    # first we need to find the colData and the class of this column
                    #colData = self.R('as.vector('+self.currentDataTransformation+'[,'+str(j-1)+'])') # we need this for setting the data that will go into the body of the table
                    # if type(colData) in [type(''), type(1), type(1.3)]:
                        # colData = [colData]
                        # print 'colData converted to list'
                    thisClass = self.R('class('+self.currentDataTransformation+'[,'+str(j-1)+'])', silent = True)
                    if thisClass in ['character']: # we want to show the element but not add it to the criteria
                        cw = OWGUIEx.lineEditHint(self, None, None, callback = lambda i = i, j = j: self.columnLineEditHintAccepted(i, j))
                        #cw.setItems(self.R('as.vector('+self.currentDataTransformation+'[,'+str(j-1)+'])'))
                        #print type(tableData[0:, j-2])
                        cw.setItems(tableData[0:, j-2])
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
                        #print self.R('levels('+self.currentDataTransformation+'[,'+str(j-1)+'])')
                        cw.setItems(self.R('levels('+self.currentDataTransformation+'[,'+str(j-1)+'])'))
                        self.table.setCellWidget(i, j, cw)
                        
                elif j > 1 and i == 1: # set the colnames
                    ci = QTableWidgetItem(self.colnames[j-2])
                    ci.setBackgroundColor(Qt.red)
                    self.table.setItem(i, j, ci)
                elif j > 1 and i> 1:
                    if dims[0] == 1: # there is only one row
                        ci = QTableWidgetItem(str(tableData[j-2]))
                    elif dims[1] == 1:
                        ci = QTableWidgetItem(str(tableData[i-2]))
                    else:
                        ci = QTableWidgetItem(str(tableData[i-2, j-2])) # need to catch the case that there might not be multiple rows or columns
                    self.table.setItem(i, j, ci)
    def columnFactorCriteriaAccepted(self, i, j):
        print str(str(i) + ' column ' + str(j) + ' row ')
        cw = self.table.cellWidget(i, j)
        text = str(cw.text())
        colName = str(self.table.item(1, j).text())
        self.criteriaList.append(self.dataParent['parent']+'$'+colName+'==\''+text+'\'')
        redRGUI.button(self.criteriaArea, colName+' == ' +text, callback = lambda k = self.criteriaArea.layout().count():self.removeCriteria(k))
        self.newProcess()
        
    def columnNumericCriteriaAccepted(self, i, j):
        cw = self.table.cellWidget(i, j)
        text = str(cw.text())
        if '==' not in text and '>' not in text and '<' not in text:
            # the person didn't put in a logical opperation even though we asked them to
            self.status.setText('Please make a logical statement beginning with either \'==\', \'>\', or \'<\'')
        colName = str(self.table.item(1, j).text())
        self.criteriaList.append('('+self.dataParent['parent']+'$'+colName+text+')')
        redRGUI.button(self.criteriaArea, colName+text, callback = lambda k = self.criteriaArea.layout().count(): self.removeCriteria(k)) 
        self.newProcess()   
        
    def columnLineEditHintAccepted(self, i, j):
        cw = self.table.cellWidget(i, j)
        text = str(cw.text())
        
        for i in range(2, self.table.rowCount()):
            ci = self.table.item(i, j)
            if str(ci.text()) == text:
                self.table.scrollToItem(ci)
                return
    def rownameLineEditHintAccepted(self, i, j):
        cw = self.table.cellWidget(i, j)
        text = str(cw.text())
        
        for i in range(2, self.table.rowCount()):
            ci = self.table.item(i, 1)
            if str(ci.text()) == text:
                self.table.scrollToItem(ci)
                return
        # if we made it this far then the rowname isn't in the visible section, we need to find that row and set that one as the current one.
    
        self.status.setText('Row is not in this data view, current data must be reset to show the data you want.')
        self.criteriaList.append('(rownames('+self.orriginalData+') == \''+text+'\')')
        redRGUI.button(self.criteriaArea, "Rowname == \'"+text+'\'', callback = lambda k = self.criteriaArea.layout().count(): self.removeCriteria(k)) 
        self.newProcess()
    def rowLineEditHintAccepted(self, i, j):
        cw = self.table.cellWidget(i, j)
        text = str(cw.text())
        
        # find the item with the matching text
        for i in range(2, self.table.columnCount()):
            ci = self.table.item(self.currentRow, i)
            if str(ci.text()) == text:
                self.table.scrollToItem(ci)
                return
                
    def rowNumericCriteriaAccepted(self, i , j):
        cw = self.table.cellWidget(i, j)
        text = str(cw.text())
        
        # set the subsetting
        self.columnCriteriaList.append('('+self.dataParent['parent']+'[\''+str(self.table.item(i, 1).text())+'\',]'+text+')')
        redRGUI.button(self.columnCriteriaArea, str(self.table.item(i, 1).text())+text, callback = lambda k = self.columnCriteriaArea.layout().count(): self.removeColumnCriteria(k))
        self.newProcess()
    def removeCriteria(self, k): # k is the widget and criteria number that we need to remove.
        print 'Removing '+str(self.criteriaList[k])
        self.criteriaList[k] = ''
        widget = self.criteriaArea.layout().itemAt(k).widget()
        #self.criteriaArea.layout().removeItem(self.criteriaArea.layout().itemAt(k))
        #sip.delete(widget)
        widget.hide()
        # widget.destroy()
        self.newProcess()
    def removeColumnCriteria(self, k):
        print 'Removing '+str(self.columnCriteriaList[k])
        self.columnCriteriaList[k] = ''
        widget = self.columnCriteriaArea.layout().itemAt(k).widget()
        #self.columnCriteriaArea.layout().removeItem(self.columnCriteriaArea.layout().itemAt(k))
        widget.hide()
        self.newProcess()
    def newProcess(self):
        cList = []
        for item in self.criteriaList:
            if item != '':
                cList.append(item)
                
        ccList = []
        for item in self.columnCriteriaList:
            if item != '':
                ccList.append(item)
        newData = {'data':self.orriginalData+'['+'&'.join(cList)+','+'&'.join(ccList)+']'} # reprocess the table
        self.processData(newData, False)
    
    def cellEntered(self, rowInt, colInt):
        self.currentRow = rowInt
        self.currentColumn = colInt
        
    def deleteWidget(self):
        self.rowcolDialog.close()