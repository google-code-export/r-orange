"""Filter Table

Likely the main table class of Red-R this table allows data to be displayed in a table view with tabs for filtering the data.

This widget accepts an entire signal class, not simply the data argument.  The signal class should pass a table model using the function getTableModel(self). 

The table model must expose the following functions to filter table.
    def __init__(self, parent, filtered):
        ## takes the parent filter table and filtered to indicate if the data can be filtered.  Note that some data structures may not provide filtering.  The constructor may also take other arguments passed by the signal class.
    def flags(self,index):
        ## return a set of Qt flags for the data, this will generally be static.
        if self.editable:
            return (Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
        else:
            return (Qt.ItemIsSelectable | Qt.ItemIsEnabled)
    def getSummary(self):
        ## return a summary of the data as a string.
        return ''
    def getRange(self,row,col):
        ## return a dict of integers specifying row and column start and end locations, this is to read in chunks of data at a time.
        r = {}
        if row-self.range < 0:
            r['rstart'] = 1
        else:
            r['rstart'] = row-self.range
        
        
        if row+self.range > self.nrow:
            r['rend'] = self.nrow
        else:
            r['rend'] = row+self.range
        
        
        if col-self.range < 0:
            r['cstart'] = 1
        else:
            r['cstart'] = col-self.range
        
        #print 'cend: ', row+self.range,  self.nrow        
        if col+self.range > self.ncol:
            r['cend'] = self.ncol
        else:
            r['cend'] = col+self.range
        
        return r
        
    def initData(self,Rdata):
        ## this function initiates the data, should set the nrow, ncol, currentRange, and arraydata
        ## arraydata should be a list of lists specifying the data.  colnames and rownames should also be set for the selected range.

    def rowCount(self, parent): 
        ## return the row count
        return self.nrow
        #return len(self.arraydata)
    def columnCount(self, parent):
        return the column count
        return self.ncol
        #return len(self.arraydata[0])
 
    def data(self, index, role):
        ### return a QVariant() for the data at index.row and index.column
        if not index.isValid(): 
            return QVariant() 
        elif role != Qt.DisplayRole: 
            return QVariant() 
        elif not self.Rdata or self.Rdata == None:
            return QVariant()
        if (
            (self.currentRange['cstart'] + 100 > index.column() and self.currentRange['cstart'] !=1) or 
            (self.currentRange['cend'] - 100 < index.column() and self.currentRange['cend'] != self.ncol) or 
            (self.currentRange['rstart'] + 100 > index.row() and self.currentRange['rstart'] !=1) or 
            (self.currentRange['rend'] - 100 < index.row() and self.currentRange['rend'] != self.nrow)
        ):

            self.currentRange = self.getRange(index.row(), index.column())
            if not self.working:
                self.working = True
                self.arraydata = self.R('as.matrix(%s[%d:%d,%d:%d])' % (self.Rdata,
            self.currentRange['rstart'],
            self.currentRange['rend'],
            self.currentRange['cstart'],
            self.currentRange['cend']
            ),
            wantType = 'list',silent=True)
                self.working = False
                
            else: self.arraydata = []
        if len(self.arraydata) == 0 or len(self.arraydata[0]) == 0:
            return QVariant()
        
        rowInd = index.row() - self.currentRange['rstart'] + 1
        colInd = index.column() - self.currentRange['cstart'] + 1
        # self.working = False
        return QVariant(self.arraydata[rowInd][colInd]) 


    def headerData(self, col, orientation, role):
        ## return a QVariant() for the header data.
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if not col >= len(self.colnames):
                return QVariant(self.colnames[col])
        elif orientation == Qt.Horizontal and role == Qt.DecorationRole and (self.filterable or self.sortable):
            if col+1 in self.filteredOn:
                return QVariant(self.columnFiltered)
            else:
                return QVariant()
        elif orientation == Qt.Vertical and role == Qt.DisplayRole: 
            # print 'row number', col, len(self.rownames)
            if not col >= len(self.rownames):
                return QVariant(self.rownames[col])
        return QVariant()
    

    def sort(self, Ncol, order):
        ## takes a column number (Ncol) and an order.  should generate a new arraydata, rownames and colnames and emit the signal layoutChanged.
        if self.editable: return
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        #print 'adfasfasdfasdfas', self.R('class(%s)' % self.orgRdata)
        if order == Qt.DescendingOrder:
            self.Rdata = '%s[order(%s[,%d],decreasing=TRUE),]' % (self.orgRdata,self.orgRdata,Ncol+1)
        else:
            self.Rdata = '%s[order(%s[,%d]),]' % (self.orgRdata,self.orgRdata,Ncol+1)
            
        self.colnames = self.R('colnames(as.data.frame(' +self.Rdata+ '))', wantType = 'list', silent=True)
        self.rownames = self.R('rownames(as.data.frame(' +self.Rdata+'))', wantType = 'list', silent=True)
        self.nrow = self.R('nrow(as.matrix(%s))' % self.Rdata, silent=True)
        self.ncol = self.R('ncol(as.matrix(%s))' % self.Rdata, silent=True)
        
        self.arraydata = self.R('as.matrix(as.matrix(%s)[%d:%d,%d:%d])' % (self.Rdata,
        self.currentRange['rstart'],
        self.currentRange['rend'],
        self.currentRange['cstart'],
        self.currentRange['cend']
        ),
        wantType = 'listOfLists',silent=True)

        self.emit(SIGNAL("layoutChanged()"))

    def filteredData(self):
        ## returns the filtered data
        return self.Rdata
        
    def delete(self):
        sip.delete(self)  
"""


from redRGUI import widgetState
import os.path, redRLog
import redREnviron, redRReports
import signals
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.scrollArea import scrollArea
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.checkBox import checkBox


from RSession import Rcommand
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sip
import redRi18n
_ = redRi18n.get_(package = 'base')

class filterTable(widgetState, QTableView):
    def __init__(self,widget,label=None, displayLabel=True, includeInReports=True, Rdata=None, 
    editable=False, sortable=True, filterable=False,
    selectionBehavior=QAbstractItemView.SelectRows, 
    selectionMode = QAbstractItemView.ExtendedSelection, 
    showResizeButtons = True,
    onFilterCallback = None,
    callback=None,
    selectionCallback=None):
        
        widgetState.__init__(self,widget,label,includeInReports)
        
        if displayLabel:
            mainBox = groupBox(self.controlArea,label=label, orientation='vertical')
        else:
            mainBox = widgetBox(self.controlArea,orientation='vertical')
        self.label = label
        
        QTableView.__init__(self,self.controlArea)
        mainBox.layout().addWidget(self)
        box = widgetBox(mainBox,orientation='horizontal')
        leftBox = widgetBox(box,orientation='horizontal')
        if filterable:
            self.clearButton = button(leftBox,label=_('Clear All Filtering'), callback=self.clearFiltering)
        self.dataInfo = widgetLabel(leftBox,label='',wordWrap=False) 
        box.layout().setAlignment(leftBox, Qt.AlignLeft)

        
        if showResizeButtons:
            resizeColsBox = widgetBox(box, orientation="horizontal")
            resizeColsBox.layout().setAlignment(Qt.AlignRight)
            box.layout().setAlignment(resizeColsBox, Qt.AlignRight)
            widgetLabel(resizeColsBox, label = _("Resize columns: "))
            button(resizeColsBox, label = "+", callback=self.increaseColWidth, 
            toolTip = _("Increase the width of the columns"), width=30)
            button(resizeColsBox, label = "-", callback=self.decreaseColWidth, 
            toolTip = _("Decrease the width of the columns"), width=30)
            button(resizeColsBox, label = _("Resize To Content"), callback=self.resizeColumnsToContents, 
            toolTip = _("Set width based on content size"))

        
        self.R = Rcommand
        self.Rdata = None
        self.filteredData = None
        self.sortIndex = None
        self.criteriaList = {}
        self.parent = widget
        self.tm=None
        self.sortable=sortable
        self.editable=editable
        self.filterable=filterable
        self.onFilterCallback = onFilterCallback
        self.selectionCallback = selectionCallback
        # self.selections = QItemSelection()
        self.working = False

        self.setHorizontalHeader(myHeaderView(self))
        self.setSelectionBehavior(selectionBehavior)
        self.setAlternatingRowColors(True)
        
        # self.horizontalHeader().setMovable(True)
        
        if selectionMode != -1:
            self.setSelectionMode(selectionMode)
    
        if Rdata:
            self.setRTable(Rdata)

        if editable:
            self.horizontalHeader().hide()
            self.verticalHeader().hide()
            
        if sortable:
            self.horizontalHeader().setSortIndicatorShown(True)
            self.horizontalHeader().setSortIndicator(-1,0)
        if filterable or sortable:
            self.horizontalHeader().setClickable(True)
            self.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
            self.horizontalHeader().customContextMenuRequested.connect(self.headerClicked)

            
        if callback:
            QObject.connect(self, SIGNAL('clicked (QModelIndex)'), callback)
    def selectColumn(self,val):
        print 'selectColumn#############################', val

    def cellSelection(self,newSelected,oldSelected):
        
        selections = self.selectionModel().selection()
        if self.working:
            return 
        self.working = True
        self.selectionCallback(selections)
        self.working = False
    def setDataModel(self, data, filtered = False):
        self.tm = data.getTableModel(self, filtered)
        self.setModel(self.tm)
        self.dataInfo.setText(self.tm.getSummary())
        
    def setTable(self, data, filterable = False, sortable = False):
        """Sets the table to a table model returned from a signal.  data represents a Red-R signal that contains a table model function getTableModel()."""
        self.tm = data.getTableModel(self, filterable, sortable)
        self.setModel(self.tm)
        
    def setStructuredDictTable(self, data):
        self.tm = StructuredDictTableModel(data, self, [], False, False, True)
        self.setModel(self.tm)
        self.dataInfo.setText(self.tm.getSummary())
    
    def setRTable(self,data, setRowHeaders = 1, setColHeaders = 1,filtered=False):
        """Conveinience function for setting an R table."""
        redRLog.log(redRLog.REDRCORE, redRLog.WARNING, 'setRTable method depricated, use setTable instead.')
        self.tm = signals.base.RDataFrame(self.parent, data = data).getTableModel(self)
        self.setModel(self.tm)
    
    def setModel(self, model):
        QTableView.setModel(self, model)
        if self.selectionCallback:
            self.connect(self.selectionModel(),  
                         SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),  
                         self.cellSelection) 

    def resizeColumnsToContents(self):
        QTableView.resizeColumnsToContents(self)
        for i in range(self.tm.columnCount(self)):
            if self.columnWidth(i) > 600:
                self.setColumnWidth(i,600)

    def increaseColWidth(self):        
        for col in range(self.tm.columnCount(self)):
            w = self.columnWidth(col)
            self.setColumnWidth(col, w + 10)

    def decreaseColWidth(self):
        for col in range(self.tm.columnCount(self)):
            w = self.columnWidth(col)
            minW = self.sizeHintForColumn(col)
            self.setColumnWidth(col, max(w - 10, minW))

    def columnCount(self):
        if self.tm:
            return self.tm.columnCount(self)
        else:
            return 0
    
    def rowCount(self):
        if self.tm:
            return self.tm.rowCount(self)
        else:
            return 0
    
    def copy(self):
        """Copies data to the clipboard"""
        selection = self.selectionModel() #self.table = QAbstractItemView
        indexes = selection.selectedIndexes()

        columns = indexes[-1].column() - indexes[0].column() + 1
        rows = len(indexes) / columns
        textTable = [[""] * columns for i in xrange(rows)]

        for i, index in enumerate(indexes):
         textTable[i % rows][i / rows] = unicode(self.tm.data(index,Qt.DisplayRole).toString()) #self.model = QAbstractItemModel 

         qApp.clipboard().setText("\n".join(("\t".join(i) for i in textTable)))
    
    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            self.copy()
        else:
            QTableView.keyPressEvent(self,event)

    def addRows(self,count,headers=None):
        self.tm.insertRows(self.tm.rowCount(self),count,headers=headers)
    def addColumns(self,count,headers=None):
        self.tm.insertColumns(self.tm.columnCount(self),count,headers)
    def clear(self):
        self.setTable(BlankTable())
        #self.setRTable('matrix("")')
        self.criteriaList = {}
    def headerClicked(self,val):
        
        selectedCol = self.horizontalHeader().logicalIndexAt(val) + 1
        #self.tm.createMenu(selectedCol)
        self.createMenu(selectedCol)
    def getData(self,row,col):
        if not self.tm: return False
        return self.tm.data(self.tm.createIndex(row,col),Qt.DisplayRole).toString()
    def createMenu(self, selectedCol):
        self.tm.createMenu(selectedCol)
        
    def clearFiltering(self):
        if self.tm:
            self.tm.clearFiltering()
        
    def getFilteredData(self):
        try:
            return self.tm.filteredData()
        except:
            return None
    # def sort(self,col,order):
        ##self.tm.sort(col-1,order)
        # self.sortByColumn(col-1, order)
        # self.horizontalHeader().setSortIndicator(col-1,order)
        # self.menu.hide()
        # self.sortIndex = [col-1,order]
        
        
    def getSettings(self):
        # print '############################# getSettings'
        if self.selectionModel():
    
          selections = [(x.top(),x.left(),x.bottom(),x.right()) for x in self.selectionModel().selection()]
        else:
            selections = None
        r = {
        'Rdata': self.Rdata,
        'filteredData':self.filteredData,
        'criteriaList': self.criteriaList
        ,'selection2':selections
        }
        
        if self.sortIndex:
            r['sortIndex'] = self.sortIndex
        
        # print r
        return r
    def startProgressBar(self, title,text,max):
        progressBar = QProgressDialog()
        progressBar.setCancelButtonText(QString())
        progressBar.setWindowTitle(title)
        progressBar.setLabelText(text)
        progressBar.setMaximum(max)
        progressBar.setValue(0)
        progressBar.show()
        return progressBar
    def loadSettings(self,data):
        # print _('loadSettings for a filter table')
        # print data
        if not data['Rdata']: return 
        self.Rdata = data['Rdata']
        self.criteriaList = data['criteriaList']
        # print 'filtering data on the following criteria %s' % unicode(self.criteriaList)
        self.filter()

        if 'sortIndex' in data.keys():
            self.sortByColumn(data['sortIndex'][0],data['sortIndex'][1])
        selModel = self.selectionModel()
        # print selModel
        
        if 'selection2' in data.keys() and len(data['selection2']):
            for x in data['selection2']:
                selModel.select( QItemSelection(self.tm.createIndex(x[0],x[1]),self.tm.createIndex(x[2],x[3])),QItemSelectionModel.Select)
        
        
        if 'selection' in data.keys() and selection and len(data['selection']):
            progressBar = self.startProgressBar(_('Filter Table Loading'), _('Loading Fiter Table'), 50)

            if len(data['selection']) > 1000:
                mb = QMessageBox.question(None, _('Setting Selection'), _('There are more than 1000 selections to set for %s,\ndo you want to discard them?\nSetting may take a very long time.') % self.label, QMessageBox.Yes, QMessageBox.No)
                if mb.exec_() == QMessageBox.No:
                
                    progressBar.setLabelText(_('Loading Selections'))
                    progressBar.setMaximum(len(data['selection']))
                    progressBar.setValue(0)
                    val = 0
                    for i in data['selection']:
                        selModel.select(self.tm.createIndex(i[0],i[1]),QItemSelectionModel.Select)
                        val += 1
                        progressBar.setValue(val)
            progressBar.hide()
            progressBar.close()
     
    def delete(self):
        sip.delete(self)
    def getReportText(self, fileDir):
        if self.getFilteredData():
            limit = min(self.tm.rowCount(self),50)
            # import time
            # start = time.time()
            # print 'start'
            data = self.R('as.matrix(%s[1:%d,])'% (self.getFilteredData(),limit))
            # print 'stop', time
            colNames = self.R('colnames(%s)' % self.getFilteredData())
            # text = redRReports.createTable(data, columnNames = colNames)
            return {self.widgetName:{'includeInReports': self.includeInReports, 'type':'table', 
            'data':data,'colNames': colNames,
            'numRowLimit': limit}}

        else:
            return {self.widgetName:{'includeInReports': self.includeInReports, 'text':''}}
        

class StructuredDictTableModel(QAbstractTableModel):
    def __init__(self, data, parent, filteredOn = [], editable = False, filterable=False, sortable=False):
        QAbstractTableModel.__init__(self, parent)
        
        self.Pdata = parent
        self.working = False
        self.working = False
        self.range = 500
        self.parent =  parent
        self.R = Rcommand
        self.sortable = sortable
        self.editable = editable
        self.filterable = filterable
        self.filteredOn = filteredOn
        self.columnFiltered = QIcon(os.path.join(redREnviron.directoryNames['picsDir'],'columnFilter.png'))
        self.initData(data)
    def flags(self,index):
        if self.editable:
            return (Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
        else:
            return (Qt.ItemIsSelectable | Qt.ItemIsEnabled)
 
    def getRange(self, row, col):
        r = {}
        if row - self.range < 0:
            r['rstart'] = 0
        else:
            r['rstart'] = row-self.range
        
        if row + self.range > self.nrow:
            r['rend'] = self.nrow
        else:
            r['rend'] = row + self.range
            
        if col-self.range < 0:
            r['cstart'] = 0
        else:
            r['cstart'] = col-self.range
        
        #print 'cend: ', row+self.range,  self.nrow        
        if col+self.range > self.ncol:
            r['cend'] = self.ncol
        else:
            r['cend'] = col+self.range
        
        return r
        
    def initData(self, data):
        self.Pdata = data
        self.orgData = data
        self.colnames = data.keys()
        self.nrow = len(data[self.colnames[0]])
        self.rownames = range(1, self.nrow+1)
        self.ncol = len(self.colnames)
        
        self.currentRange = self.getRange(0, 0)
        
        self.arraydata = self.dictToArray(self.Pdata, self.currentRange['rstart'], self.currentRange['rend'], self.currentRange['cstart'], self.currentRange['cend'])  ## we now get a list of lists
        
    def rowCount(self, parent): 
        return self.nrow
        #return len(self.arraydata)
    def columnCount(self, parent): 
        return self.ncol
        #return len(self.arraydata[0])
        
    def data(self, index, role): 
        # print _('in data')
        # if self.working == True:
            # return QVariant()
        # self.working = True
        if not index.isValid(): 
            return QVariant() 
        elif role != Qt.DisplayRole: 
            return QVariant() 
        elif not self.Pdata or self.Pdata == None:
            return QVariant()
            
        if (
            (self.currentRange['cstart'] + 100 > index.column() and self.currentRange['cstart'] !=1) or 
            (self.currentRange['cend'] - 100 < index.column() and self.currentRange['cend'] != self.ncol) or 
            (self.currentRange['rstart'] + 100 > index.row() and self.currentRange['rstart'] !=1) or 
            (self.currentRange['rend'] - 100 < index.row() and self.currentRange['rend'] != self.nrow)
        ):

            self.currentRange = self.getRange(index.row(), index.column())
            self.arraydata = self.dictToArray(self.Pdata, self.currentRange['rstart'], self.currentRange['rend'], self.currentRange['cstart'], self.currentRange['cend'])  ## we now get a list of lists
            
        if len(self.arraydata) == 0 or len(self.arraydata[0]) == 0:
            return QVariant()
        rowInd = index.row() - self.currentRange['rstart']
        colInd = index.column() - self.currentRange['cstart']
        # self.working = False
        return QVariant(self.arraydata[rowInd][colInd]) 
        
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if not col >= len(self.colnames):
                return QVariant(self.colnames[col])
        elif orientation == Qt.Horizontal and role == Qt.DecorationRole and (self.filterable or self.sortable):
            if col+1 in self.filteredOn:
                return QVariant(self.columnFiltered)
            else:
                return QVariant()
        elif orientation == Qt.Vertical and role == Qt.DisplayRole: 
            # print 'row number', col, len(self.rownames)
            if not col >= len(self.rownames):
                return QVariant(self.rownames[col])
        return QVariant()
    
    def get_sorted(self, vector):
        return sorted(range(len(vector)), key = vector.__getitem__)
    def sort(self, Ncol, order):
        if self.editable: return
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        #print 'adfasfasdfasdfas', self.R('class(%s)' % self.orgRdata)
        self.Pdata = self.sortDict(self.orgData, Ncol, decreasing = (order == Qt.DescendingOrder))  ## returns a list of lists sorted 
        self.arraydata = self.dictToArray(self.Pdata, self.currentRange['rstart'], self.currentRange['rend'], self.currentRange['cstart'], self.currentRange['cend'])  ## we now get a list of lists
        self.emit(SIGNAL("layoutChanged()"))
    def delete(self):
        sip.delete(self)  
    def dictToArray(self, data, rstart, rend, cstart, cend):
        ## we have a dict and we need to make a list of lists
        returnData = []
        for r in range(rstart, rend):
            row = []
            for c in range(cstart, cend):
                row.append(data[self.colnames[c]][r])
            returnData.append(row)
        return returnData
    def sortDict(self, data, col, decreasing):
        indecies = self.get_sorted(data[self.colnames[col]])
        if not decreasing:
            indecies.reverse()
        newDict = {}
        for k, v in data.items():
            newDict[k] = [v[i] for i in indecies]
        return newDict

class MyTableModel(QAbstractTableModel): 
    def __init__(self,Rdata,parent, filteredOn = [], editable=False,
    filterable=False,sortable=False): 
        QAbstractTableModel.__init__(self,parent) 

        self.working = False
        self.range = 500
        self.parent =  parent
        self.R = Rcommand
        self.sortable = sortable
        self.editable = editable
        self.filterable = filterable
        self.filteredOn = filteredOn
        # self.filter_delete = os.path.join(redREnviron.directoryNames['picsDir'],'filterAdd.png')
        self.columnFiltered = QIcon(os.path.join(redREnviron.directoryNames['picsDir'],'columnFilter.png'))
        
        # print self.filter_add,os.path.exists(self.filter_add),os.path.exists(self.filter_delete)
        self.initData(Rdata)
        
    def flags(self,index):
        if self.editable:
            return (Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
        else:
            return (Qt.ItemIsSelectable | Qt.ItemIsEnabled)
 
    def getRange(self,row,col):
        r = {}
        if row-self.range < 0:
            r['rstart'] = 1
        else:
            r['rstart'] = row-self.range
        
        
        if row+self.range > self.nrow:
            r['rend'] = self.nrow
        else:
            r['rend'] = row+self.range
        
        
        if col-self.range < 0:
            r['cstart'] = 1
        else:
            r['cstart'] = col-self.range
        
        #print 'cend: ', row+self.range,  self.nrow        
        if col+self.range > self.ncol:
            r['cend'] = self.ncol
        else:
            r['cend'] = col+self.range
        
        return r
        
    def initData(self,Rdata):
        self.Rdata = Rdata
        self.orgRdata = Rdata
        self.nrow = self.R('nrow(%s)' % self.Rdata,silent=True)
        self.ncol = self.R('ncol(%s)' % self.Rdata,silent=True)
        
        self.currentRange = self.getRange(0,0)
        
        self.arraydata = self.R('as.matrix(%s[%d:%d,%d:%d])' % (self.Rdata,
        self.currentRange['rstart'],
        self.currentRange['rend'],
        self.currentRange['cstart'],
        self.currentRange['cend']
        ),
        wantType = 'listOfLists',silent=True)
        
        # print _('self.arraydata loaded')

        self.colnames = self.R('colnames(as.data.frame(' +Rdata+ '))', wantType = 'list',silent=True)
        self.rownames = self.R('rownames(as.data.frame(' +Rdata+'))', wantType = 'list',silent=True)
        if len(self.rownames) ==0: self.rownames = [1]
        # print self.rownames, self.rowCount(self)
        # print self.colnames

        if self.arraydata == [[]]:
            toAppend= ['' for i in xrange(self.columnCount(self))]
            self.arraydata = [toAppend]
        # print 'self.arraydata' , self.arraydata
        
    def rowCount(self, parent): 
        return self.nrow
        #return len(self.arraydata)
    def columnCount(self, parent): 
        return self.ncol
        #return len(self.arraydata[0])
 
    def data(self, index, role): 
        # print _('in data')
        # if self.working == True:
            # return QVariant()
        # self.working = True
        if not index.isValid(): 
            return QVariant() 
        elif role != Qt.DisplayRole: 
            return QVariant() 
        elif not self.Rdata or self.Rdata == None:
            return QVariant()
        # print self.currentRange['rstart'], index.row(), self.currentRange['rend'], self.currentRange['cstart'], index.column(), self.currentRange['cend']
        # return QVariant(QIcon(self.filter_add))

        if (
            (self.currentRange['cstart'] + 100 > index.column() and self.currentRange['cstart'] !=1) or 
            (self.currentRange['cend'] - 100 < index.column() and self.currentRange['cend'] != self.ncol) or 
            (self.currentRange['rstart'] + 100 > index.row() and self.currentRange['rstart'] !=1) or 
            (self.currentRange['rend'] - 100 < index.row() and self.currentRange['rend'] != self.nrow)
        ):

            self.currentRange = self.getRange(index.row(), index.column())
            if not self.working:
                self.working = True
                self.arraydata = self.R('as.matrix(%s[%d:%d,%d:%d])' % (self.Rdata,
            self.currentRange['rstart'],
            self.currentRange['rend'],
            self.currentRange['cstart'],
            self.currentRange['cend']
            ),
            wantType = 'list',silent=True)
                self.working = False
                
            else: self.arraydata = []
        if len(self.arraydata) == 0 or len(self.arraydata[0]) == 0:
            return QVariant()
        
        rowInd = index.row() - self.currentRange['rstart'] + 1
        colInd = index.column() - self.currentRange['cstart'] + 1
        # self.working = False
        return QVariant(self.arraydata[rowInd][colInd]) 


    def headerData(self, col, orientation, role):
        # print col,orientation,role
        # return QVariant(QIcon(self.filter_add))
        # print _('in headerData'), col, orientation, role

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if not col >= len(self.colnames):
                return QVariant(self.colnames[col])
        elif orientation == Qt.Horizontal and role == Qt.DecorationRole and (self.filterable or self.sortable):
            if col+1 in self.filteredOn:
                return QVariant(self.columnFiltered)
            else:
                return QVariant()
        elif orientation == Qt.Vertical and role == Qt.DisplayRole: 
            # print 'row number', col, len(self.rownames)
            if not col >= len(self.rownames):
                return QVariant(self.rownames[col])
        return QVariant()
    

    def sort(self, Ncol, order):
        if self.editable: return
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        #print 'adfasfasdfasdfas', self.R('class(%s)' % self.orgRdata)
        if order == Qt.DescendingOrder:
            self.Rdata = '%s[order(%s[,%d],decreasing=TRUE),]' % (self.orgRdata,self.orgRdata,Ncol+1)
        else:
            self.Rdata = '%s[order(%s[,%d]),]' % (self.orgRdata,self.orgRdata,Ncol+1)
            
        self.colnames = self.R('colnames(as.data.frame(' +self.Rdata+ '))', wantType = 'list', silent=True)
        self.rownames = self.R('rownames(as.data.frame(' +self.Rdata+'))', wantType = 'list', silent=True)
        self.nrow = self.R('nrow(as.matrix(%s))' % self.Rdata, silent=True)
        self.ncol = self.R('ncol(as.matrix(%s))' % self.Rdata, silent=True)
        
        self.arraydata = self.R('as.matrix(as.matrix(%s)[%d:%d,%d:%d])' % (self.Rdata,
        self.currentRange['rstart'],
        self.currentRange['rend'],
        self.currentRange['cstart'],
        self.currentRange['cend']
        ),
        wantType = 'listOfLists',silent=True)

        self.emit(SIGNAL("layoutChanged()"))


    def delete(self):
        sip.delete(self)  
  

class myHeaderView(QHeaderView):
    def __init__(self,parent):
        QHeaderView.__init__(self,Qt.Horizontal,parent)
    
