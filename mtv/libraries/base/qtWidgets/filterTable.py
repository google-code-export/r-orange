from redRGUI import widgetState
import os.path
import redREnviron, redRReports
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

class filterTable(widgetState, QTableView):
    def __init__(self,widget,label=None, Rdata=None, editable=False, sortable=True, filterable=False,
    selectionBehavior=QAbstractItemView.SelectRows, 
    selectionMode = QAbstractItemView.NoSelection, 
    showResizeButtons = True,
    onFilterCallback = None,
    callback=None):
        #widgetBox.__init__(self,widget,orientation='vertical')
        
        if label:
            mainBox = groupBox(widget,label=label, orientation='vertical')
        else:
            mainBox = widgetBox(widget,orientation='vertical')
        self.label = label
        
        QTableView.__init__(self,widget)
        mainBox.layout().addWidget(self)
        box = widgetBox(mainBox,orientation='horizontal')
        leftBox = widgetBox(box,orientation='horizontal')
        if filterable:
            self.clearButton = button(leftBox,label='Clear All Filtering', callback=self.clearFiltering)
        self.dataInfo = widgetLabel(leftBox,label='',wordWrap=False) 
        box.layout().setAlignment(leftBox, Qt.AlignLeft)

        if showResizeButtons:
            resizeColsBox = widgetBox(box, orientation="horizontal")
            resizeColsBox.layout().setAlignment(Qt.AlignRight)
            box.layout().setAlignment(resizeColsBox, Qt.AlignRight)
            widgetLabel(resizeColsBox, label = "Resize columns: ")
            button(resizeColsBox, label = "+", callback=self.increaseColWidth, 
            toolTip = "Increase the width of the columns", width=30)
            button(resizeColsBox, label = "-", callback=self.decreaseColWidth, 
            toolTip = "Decrease the width of the columns", width=30)
            button(resizeColsBox, label = "Resize To Content", callback=self.resizeColumnsToContents, 
            toolTip = "Set width based on content size")

        
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
        self.setSelectionBehavior(selectionBehavior)

        self.setAlternatingRowColors(True)
        
        if selectionMode != -1:
            self.setSelectionMode(selectionMode)
    
        if Rdata:
            self.setRTable(Rdata)

        if editable:
            self.horizontalHeader().hide()
            self.verticalHeader().hide()
            
        # if sortable:
            # self.horizontalHeader().setSortIndicatorShown(True)
            # self.horizontalHeader().setSortIndicator(-1,0)
        if filterable or sortable:
            #self.horizontalHeader().setClickable(True)
            QObject.connect(self.horizontalHeader(), SIGNAL('sectionClicked (int)'), self.headerClicked)
            # self.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
            # self.horizontalHeader().customContextMenuRequested.connect(self.headerClicked)

        
        if callback:
            QObject.connect(self, SIGNAL('clicked (QModelIndex)'), callback)


        
    def setRTable(self,data, setRowHeaders = 1, setColHeaders = 1,filtered=False):
        # print 'in setRTable', data
        if self.R('class(%s)' %data, silent=True) != 'data.frame':
            data = 'as.data.frame(%s)' %data
        #self.Rdata = Rdata
        if not filtered:
            self.Rdata = data
            self.filteredData = data
            self.criteriaList = {}
            filteredCols = []
            
        else:
            filteredCols = self.criteriaList.keys()
        total = self.R('nrow(%s)' % self.Rdata)        
        if self.filterable:
            filtered = self.R('nrow(%s)' % data)
            self.dataInfo.setText('Showing %d of %d rows.' % (filtered,total))
        else:
            self.dataInfo.setText('Showing %d rows.' % (total))

        self.tm = MyTableModel(data,self,editable=self.editable, 
        filteredOn = filteredCols, filterable=self.filterable,sortable=self.sortable)
        self.setModel(self.tm)
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
    def addRows(self,count,headers=None):
        self.tm.insertRows(self.tm.rowCount(self),count,headers=headers)
    def addColumns(self,count,headers=None):
        self.tm.insertColumns(self.tm.columnCount(self),count,headers)
    def clear(self):
        self.setRTable('matrix("")')
        self.criteriaList = {}
    def headerClicked(self,val):
        # print '#############################', val.x()
        # ncol = self.R('ncol(%s)' % self.Rdata,silent=True)
        # start =0;
        # pos = val.x()
        # for x in range(0,ncol):
            # if pos > start and pos < start + self.horizontalHeader().sectionSize(x):
                # break
            # start += self.horizontalHeader().sectionSize(x)
        # selectedCol = x+1
        selectedCol = val + 1
        self.createMenu(selectedCol)
    
    def getData(self,row,col):
        if not self.tm: return False
        return self.tm.data(self.tm.createIndex(row,col),Qt.DisplayRole).toString()
    def createMenu(self, selectedCol):
        #print selectedCol, pos
        # print 'in createMenu', self.criteriaList

        globalPos = QCursor.pos() #self.mapToGlobal(pos)
        self.menu = QDialog(None,Qt.Popup)
        self.menu.setLayout(QVBoxLayout())
        if self.sortable:
            box = widgetBox(self.menu,orientation='horizontal')
            box.layout().setAlignment(Qt.AlignLeft)
            button(box,label='A->Z',callback= lambda: self.sort(selectedCol,Qt.AscendingOrder))
            widgetLabel(box,label='Ascending Sort')
            box = widgetBox(self.menu,orientation='horizontal')
            box.layout().setAlignment(Qt.AlignLeft)
            button(box,label='Z->A',callback= lambda: self.sort(selectedCol,Qt.DescendingOrder))
            widgetLabel(box,label='Descending Sort')
            # qmenu = QMenu(self.menu)
            # self.menu.layout().addWidget(qmenu)
            # a = QAction('A->Z',self.menu)
            # qmenu.addAction(a)
            # self.menu.addAction(a)

        if not self.filterable:
            self.menu.move(globalPos)
            self.menu.show()
            return
        
        if self.sortable:
            hr = QFrame(self.menu)
            hr.setFrameStyle( QFrame.Sunken + QFrame.HLine );
            hr.setFixedHeight( 12 );
            self.menu.layout().addWidget(hr)
    
        
        clearButton = button(self.menu,label='Clear Filter',
        callback=lambda col=selectedCol: self.createCriteriaList(col,self.menu,action='clear'))
        self.menu.layout().setAlignment(clearButton,Qt.AlignHCenter)
        clearButton.hide()
        
        self.numericLabel = widgetLabel(self.menu,label='Enter a value for one of these critera:')
        self.numericLabel.hide()
        self.stringLabel = widgetLabel(self.menu,label='Enter a value for one of these critera (case sensitive):')
        self.stringLabel.hide()

        if selectedCol in self.criteriaList.keys():
            clearButton.show()
        
        self.optionsBox = widgetBox(self.menu)
        colClass = self.R('class(%s[,%d])' % (self.Rdata,selectedCol),silent=True)
        if colClass in ['factor','logical']:
            
            if selectedCol in self.criteriaList.keys():
                checked = self.criteriaList[selectedCol]['value']
            else:
                checked = []
            if colClass =='logical':
                levels = ['TRUE','FALSE']
            else:
                levels = self.R('levels(%s[,%d])' % (self.Rdata,selectedCol),wantType='list', silent=True)
                
            if len(levels) > 1:
                levels.insert(0,'Check All')
            if len(levels) > 10:
                scroll = scrollArea(self.optionsBox,spacing=1)
                c = checkBox(scroll,buttons=levels,setChecked = checked)
                scroll.setWidget(c)
            else:
                c = checkBox(self.optionsBox,buttons=levels,setChecked = checked)
            
            QObject.connect(c.buttons, SIGNAL('buttonClicked (int)'), lambda val : self.factorCheckBox(val,self.optionsBox))
    
        elif colClass in ['integer','numeric']:
            self.numericLabel.show()
            self.options = ['Equals', 'Does Not Equal','Greater Than','Greater Than Or Equal To', 
            'Less Than', 'Less Than or Equal To', 'Between\n(2 numbers comma\nseparated, inclusive)', 
            'Not Between\n(2 numbers comma\nseparated)']
            for x in self.options:
                if selectedCol in self.criteriaList and self.criteriaList[selectedCol]['method'] == 'Numeric ' + x:
                    e = lineEdit(self.optionsBox,label=x,text=self.criteriaList[selectedCol]['value'])
                else:
                    e = lineEdit(self.optionsBox,label=x)
                self.connect(e, SIGNAL("textEdited(QString)"),
                lambda val, col=selectedCol,field=x : self.clearOthers(val,self.optionsBox,field))
    
        elif colClass in ['character']:
            self.stringLabel.show()
            self.options = ['Equals', 'Does Not Equal','Begins With','Ends With', 
            'Contains', 'Does Not Contain']
            for x in self.options:
                if selectedCol in self.criteriaList and self.criteriaList[selectedCol]['method'] == 'String ' + x:
                    e = lineEdit(self.optionsBox,label=x,text=self.criteriaList[selectedCol]['value'])
                else:
                    e = lineEdit(self.optionsBox,label=x)
                self.connect(e, SIGNAL("textEdited(QString)"),
                lambda val, col=selectedCol,field=x : self.clearOthers(val,self.optionsBox,field))
            
        buttonBox = widgetBox(self.optionsBox,orientation='horizontal')
        buttonBox.layout().setAlignment(Qt.AlignRight)
        okButton = button(buttonBox,label='OK',
        callback=lambda col=selectedCol: self.createCriteriaList(col,self.optionsBox,action='OK'))
        okButton.setDefault (True)
        button(buttonBox,label='Cancel',
        callback=lambda col=selectedCol: self.createCriteriaList(col,self.optionsBox,action='cancel'))
        
        self.menu.move(globalPos)
        self.menu.show()
    def factorCheckBox(self,val,menu):
        if val != 0: return
        checkbox = menu.findChildren(checkBox)[0]
        if checkbox.buttonAt(0) != 'Check All': return
        #print checkbox.getChecked(), 'Check All' in checkbox.getChecked()
        if 'Check All' in checkbox.getChecked():
            checkbox.checkAll()
        else: 
            checkbox.uncheckAll()
        
    def clearOthers(self,val, menu, field):
        # print '##############', val, field
        for label,value in zip(menu.findChildren(QLabel),menu.findChildren(QLineEdit)):
            if label.text() != field:
                value.setText('')

    def clearFiltering(self):
        self.criteriaList = {}
        # self.horizontalHeader().setSortIndicator(-1,order)
        self.filter()
        
    def createCriteriaList(self,col,menu,action):
        #print 'in filter@@@@@@@@@@@@@@@@@@@@@@@@@@', col,action
        #print self.criteriaList
        if action=='cancel':
            self.menu.hide()
            return
        colClass = self.R('class(%s[,%d])' % (self.Rdata,col),silent=True)
        if action =='clear':
            del self.criteriaList[col]
        elif action=='OK':
            if colClass in ['integer','numeric']:
                for label,value in zip(menu.findChildren(QLabel),menu.findChildren(QLineEdit)):
                    if value.text() != '':
                        # print label.text(),value.text()
                        self.criteriaList[col] = {'column':col, "method": 'Numeric ' + str(label.text()), "value": str(value.text())}
            elif colClass in ['character']:
                for label,value in zip(menu.findChildren(QLabel),menu.findChildren(QLineEdit)):
                    if value.text() != '':
                        # print label.text(),value.text()
                        self.criteriaList[col] = {'column':col, "method": 'String ' + str(label.text()), "value": str(value.text())}
            elif colClass in ['factor','logical']:
                checks = menu.findChildren(checkBox)[0].getChecked()
                if 'Check All' in checks:
                    checks.remove('Check All')
                if len(checks) != 0:
                    self.criteriaList[col] = {'column':col, "method": colClass, "value": checks}
                else:
                    del self.criteriaList[col]
            
        print 'criteriaList', self.criteriaList
        self.menu.hide()
        self.filter()
    
    def filter(self):
        filters  = []
        for col,criteria in self.criteriaList.items():
            print 'in loop', col,criteria['method']
            if 'Numeric Equals' == criteria['method']:
                filters.append('%s[,%s] == %s' % (self.Rdata,col,criteria['value']))
            elif 'Numeric Does Not Equal' == criteria['method']:
                filters.append('%s[,%s] != %s' % (self.Rdata,col,criteria['value']))
            elif 'Numeric Greater Than' == criteria['method']:
                filters.append('%s[,%s] > %s' % (self.Rdata,col,criteria['value']))
            elif 'Numeric Greater Than Or Equal To' == criteria['method']:
                filters.append('%s[,%s] >= %s' % (self.Rdata,col,criteria['value']))
            elif 'Numeric Less Than' == criteria['method']:
                filters.append('%s[,%s] < %s' % (self.Rdata,col,criteria['value']))
            elif 'Numeric Less Than or Equal To' == criteria['method']:
                filters.append('%s[,%s] <= %s' % (self.Rdata,col,criteria['value']))
            elif 'Numeric Between\n(2 numbers comma\nseparated, inclusive)' == criteria['method']:
                (start,comma,stop) = criteria['value'].partition(',')
                if start !='' and stop !='' or comma == ',':
                    filters.append('%s[,%s] >= %s & %s[,%s] <= %s' % (self.Rdata,col,start,self.Rdata,col,stop))
            elif 'Numeric Not Between\n(2 numbers comma\nseparated)' == criteria['method']:
                (start,comma, stop) = criteria['value'].partition(',')
                if start !='' and stop !='' or comma == ',':
                    filters.append('%s[,%s] < %s | %s[,%s] > %s' % (self.Rdata,col,start,self.Rdata,col,stop))

            elif 'String Equals' == criteria['method']:
                filters.append('%s[,%s] == "%s"' % (self.Rdata,col,criteria['value']))
            elif 'String Does Not Equal' == criteria['method']:
                filters.append('%s[,%s] != "%s"' % (self.Rdata,col,criteria['value']))
            elif 'String Begins With' == criteria['method']:
                filters.append('grepl("^%s",%s[,%s])' % (criteria['value'],self.Rdata,col))
            elif 'String Ends With' == criteria['method']:
                filters.append('grepl("%s$",%s[,%s])' % (criteria['value'],self.Rdata,col))
            elif 'String Contains' == criteria['method']:
                filters.append('grepl("%s",%s[,%s])' % (criteria['value'],self.Rdata,col))
            elif 'String Does Not Contain' == criteria['method']:
                filters.append('!grepl("%s",%s[,%s])' % (criteria['value'],self.Rdata,col))
            
            
            elif criteria['method'] in ['logical','factor']:
                f= '","'.join([str(x) for x in criteria['value']])
                filters.append(self.Rdata+'[,'+str(col)+'] %in% as.factor(c("'+f+'"))')
            #elif 'logical' == critera['method']:
            
       # print 'filters:', filters
        self.filteredData = '%s[%s,,drop = F]' % (self.Rdata,' & '.join(filters))
        #print 'string:', self.filteredData
        self.setRTable(self.filteredData,filtered=True)
        if self.onFilterCallback:
            self.onFilterCallback()
             
    def getFilteredData(self):
        return self.tm.Rdata
    def sort(self,col,order):
        #self.tm.sort(col-1,order)
        self.sortByColumn(col-1, order)
        self.horizontalHeader().setSortIndicator(col-1,order)
        self.menu.hide()
        self.sortIndex = [col-1,order]
        
        
    def getSettings(self):
        # print '############################# getSettings'
        r = {
        'Rdata': self.Rdata,
        'filteredData':self.filteredData,
        'criteriaList': self.criteriaList,
        'selection':[[i.row(),i.column()] for i in self.selectedIndexes()]
        }
        
        if self.sortIndex:
            r['sortIndex'] = self.sortIndex
        
        # print r
        return r
    def loadSettings(self,data):
        # print '############################# loadSettings'
        # print data
        if not data['Rdata']: return 

        self.Rdata = data['Rdata']
        self.criteriaList = data['criteriaList']
        self.filter()

        if 'sortIndex' in data.keys():
            self.sortByColumn(data['sortIndex'][0],data['sortIndex'][1])
        selModel = self.selectionModel()
        # print selModel
        if 'selection' in data.keys() and len(data['selection']):
            for i in data['selection']:
                selModel.select(self.tm.createIndex(i[0],i[1]),QItemSelectionModel.Select)
        
     
    def delete(self):
        sip.delete(self)
    def getReportText(self, fileDir):
        data = self.R('as.matrix(%s)'% self.getFilteredData())
        colNames = self.R('colnames(%s)' % self.getFilteredData())
        text = redRReports.createTable(data, columnNames = colNames)
        if self.label:
            label = self.label
        else:
            label='Data Table';
        
        return {'label': label, 'text': text}


class MyTableModel(QAbstractTableModel): 
    def __init__(self,Rdata,parent, filteredOn = [], editable=False,
    filterable=False,sortable=False): 

        self.range = 500
        self.parent =  parent
        self.R = Rcommand
        self.sortable = sortable
        self.editable = editable
        self.filterable = filterable
        self.filteredOn = filteredOn
        QAbstractTableModel.__init__(self,parent) 
        self.initData(Rdata)
        self.filter_delete = QIcon(os.path.join(redREnviron.directoryNames['picsDir'],'filter_delete.gif'))
        self.filter_add = QIcon(os.path.join(redREnviron.directoryNames['picsDir'],'filter_add.gif'))
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
        
        # print 'self.arraydata loaded'

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
        # print 'in data'
        if not index.isValid(): 
            return QVariant() 
        elif role != Qt.DisplayRole: 
            return QVariant() 
        
        # print self.currentRange['rstart'], index.row(), self.currentRange['rend'], self.currentRange['cstart'], index.column(), self.currentRange['cend']
        
        if (
            (self.currentRange['cstart'] + 100 > index.column() and self.currentRange['cstart'] !=1) or 
            (self.currentRange['cend'] - 100 < index.column() and self.currentRange['cend'] != self.ncol) or 
            (self.currentRange['rstart'] + 100 > index.row() and self.currentRange['rstart'] !=1) or 
            (self.currentRange['rend'] - 100 < index.row() and self.currentRange['rend'] != self.nrow)
        ):
            
            
            self.currentRange = self.getRange(index.row(), index.column())
            
            self.arraydata = self.R('as.matrix(%s[%d:%d,%d:%d])' % (self.Rdata,
            self.currentRange['rstart'],
            self.currentRange['rend'],
            self.currentRange['cstart'],
            self.currentRange['cend']
            ),
            wantType = 'listOfLists',silent=True)
        
        rowInd = index.row() - self.currentRange['rstart'] + 1
        colInd = index.column() - self.currentRange['cstart'] + 1
        
        return QVariant(self.arraydata[rowInd][colInd]) 

    def headerData(self, col, orientation, role):
        # print 'in headerData', col, orientation, role
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.colnames[col])
        elif orientation == Qt.Horizontal and role == Qt.DecorationRole and (self.filterable or self.sortable):
            # print 'DecorationRole'
            if col+1 in self.filteredOn:
                # print self.filter_delete
                return QVariant(self.filter_delete)
            else:
                # print self.filter_add
                return QVariant(self.filter_add)
                
            #return QVariant(icon)
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:     
            return QVariant(self.rownames[col])
        return QVariant()
    

    def sort(self, Ncol, order):
        if self.editable: return
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        if order == Qt.DescendingOrder:
            self.Rdata = '%s[order(%s[,%d],decreasing=TRUE),]' % (self.orgRdata,self.orgRdata,Ncol+1)
        else:
            self.Rdata = '%s[order(%s[,%d]),]' % (self.orgRdata,self.orgRdata,Ncol+1)
            
        self.colnames = self.R('colnames(as.data.frame(' +self.Rdata+ '))', wantType = 'list', silent=True)
        self.rownames = self.R('rownames(as.data.frame(' +self.Rdata+'))', wantType = 'list', silent=True)
        self.nrow = self.R('nrow(%s)' % self.Rdata, silent=True)
        self.ncol = self.R('ncol(%s)' % self.Rdata, silent=True)
        
        self.arraydata = self.R('as.matrix(%s[%d:%d,%d:%d])' % (self.Rdata,
        self.currentRange['rstart'],
        self.currentRange['rend'],
        self.currentRange['cstart'],
        self.currentRange['cend']
        ),
        wantType = 'listOfLists',silent=False)

        self.emit(SIGNAL("layoutChanged()"))


    def delete(self):
        sip.delete(self)  
  


"""
class MyTableModel(QAbstractTableModel): 
    def __init__(self, Rdata, parent,editable=False): 
        self.R = Rcommand
        self.editable = editable

        #print parent
        QAbstractTableModel.__init__(self,parent) 
        self.Rdata = Rdata
        self.orgRdata = Rdata
        
        self.colnames = self.R('colnames(as.data.frame(' +self.Rdata+ '))', wantType = 'list')
        self.rownames = self.R('rownames(as.data.frame(' +self.Rdata+'))', wantType = 'list')
        self.nrow = self.R('nrow(%s)' % self.Rdata,silent=True)
        self.ncol = self.R('ncol(%s)' % self.Rdata,silent=True)
        # nrows = self.R('nrow(%s)' % self.Rdata)
        #print 'length rownams %d' % len(self.rownames)
        
        # if self.editable:
            # self.arraydata = self.R('as.matrix(rbind(c("rownames",colnames(as.data.frame(' +Rdata+ '))), cbind(rownames(as.data.frame(' +Rdata+')),'+Rdata+')))', wantType = 'list')
            # self.colnames.insert(0,'Row Names')
            # self.rownames.insert(0,'Row Names')
        # else:
        # self.arraydata = self.R('as.matrix('+Rdata+')', wantType = 'list')
        
        # print self.arraydata
        # print 'arraydata type:' ,type(self.arraydata)
    def flags(self,index):
        if self.editable:
            return (Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
        else:
            return (Qt.ItemIsSelectable | Qt.ItemIsEnabled)
    def rowCount(self, parent): 
        return self.nrow
        #return len(self.arraydata)
    def columnCount(self, parent): 
        return self.ncol
        #return len(self.arraydata[0])
    def data(self, index, role): 
        # print 'in data'
        if not index.isValid(): 
            return QVariant() 
        elif role != Qt.DisplayRole: 
            return QVariant() 
        return self.R('%s[%d,%d]' % (self.Rdata,index.row()+1,index.column()+1))
        #return QVariant(self.arraydata[index.row()][index.column()]) 

    def setData(self,index,data, role):
        print 'in setData', data.toString(), index.row(),index.column(), role
        if not index.isValid(): 
            return False
        elif role == Qt.EditRole: 
            # print self.arraydata[index.row()][index.column()]
            # self.arraydata[index.row()][index.column()] = data.toString()
            Rcmd = '%s[%d,%d]="%s"' % (self.Rdata, index.row(), index.column(), data.toString())
            # print Rcmd
            self.R(Rcmd)
            # print self.arraydata
            # print self.arraydata[index.row()][index.column()]
            self.emit(SIGNAL("dataChanged()"))
            return True
        # elif role == Qt.BackgroundRole:
            # print 'in BackgroundRole'
            # d = self.itemDelegate(index)
            # d.paint(QBrush(Qt.red))
            # return True
        
        return False
    
    def headerData(self, col, orientation, role):
        # print 'in headerData', col
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.colnames[col])
            # return self.R('colnames(as.data.frame(%s))[%d]' % (self.Rdata,col),silent=True)
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:     
            return QVariant(self.rownames[col])
            # return self.R('rownames(as.data.frame(%s))[%d]' % (self.Rdata,col),silent=True)
        return QVariant()
    
    def setHeaderData(self,col,orientation,data,role):
        # print 'in setHeaderData'
        if orientation == Qt.Horizontal and role == Qt.EditRole:
            self.colnames[col] = data.toString()
            self.emit(SIGNAL("headerDataChanged()"))
            return True
        else:
            return False
    def clear(self):
        pass
        ## please reimplement in a later version
    def insertRows(self,beforeRow,count,headers=None):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.emit(SIGNAL("beginInsertRows()"))
        size= self.columnCount(self)
        toAppend= ['' for i in xrange(self.columnCount(self))]
        # print size
        # print toAppend
        # print count
        for i in xrange(count):
            self.arraydata.append(toAppend)

        if headers:
            self.rownames.extend(headers)
        else:
            size = len(self.rownames)+1
            # print self.rownames
            # print size
            headers = [str(i) for i in range(size,size+count)]
            # print headers
            self.rownames.extend(headers)
        self.R('t = matrix("",nrow='+str(count)+',ncol=ncol('+self.Rdata+'))')
        self.R('colnames(t) = colnames('+self.Rdata+')')
        self.R('rownames(t) = rownames("%s")' % '","'.join(headers))
        self.R(self.Rdata+'=rbind('+self.Rdata+',t)')


        self.emit(SIGNAL("endInsertRows()"))
        self.emit(SIGNAL("layoutChanged()"))
        return True
    def insertColumns(self,beforeColumn,count,headers=None):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.emit(SIGNAL("beginInsertRows()"))

        toAppend = ['' for i in xrange(count)]
        for x in self.arraydata:
            x.extend(toAppend)

        if headers:
            self.colnames.extend(headers)
        else:
            size = len(self.colnames)+1
            # print self.colnames
            # print size
            headers = ['V'  +str(i) for i in range(size,size+count)]
            # print headers
            self.colnames.extend(headers)
        
        #self.R('%s = cbind(%s,

        self.emit(SIGNAL("endInsertRows()"))
        self.emit(SIGNAL("layoutChanged()"))

    def sort(self, Ncol, order):
        if self.editable: return
        
        if order == Qt.DescendingOrder:
            self.Rdata = '%s[order(%s[,%d]),]' % (self.orgRdata,self.orgRdata,Ncol+1)
        else:
            self.Rdata = '%s[order(%s[,%d],decreasing=TRUE),]' % (self.orgRdata,self.orgRdata,Ncol+1)
            
        self.colnames = self.R('colnames(as.data.frame(' +self.Rdata+ '))', wantType = 'list')
        self.rownames = self.R('rownames(as.data.frame(' +self.Rdata+'))', wantType = 'list')
        self.nrow = self.R('nrow(%s)' % self.Rdata)
        self.ncol = self.R('ncol(%s)' % self.Rdata)

        # print 'in sort'
        # import operator
        # self.emit(SIGNAL("layoutAboutToBeChanged()"))
        
        # for r,x in zip(self.rownames, self.arraydata):
            # x.append(r)
        # self.arraydata.append(self.rownames)
        # self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        
        # if order == Qt.DescendingOrder:
            # self.arraydata.reverse()
       
        # self.rownames = [x.pop() for x in self.arraydata]
        self.emit(SIGNAL("layoutChanged()"))

    def delete(self):
        sip.delete(self)  
"""