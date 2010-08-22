from redRGUI import widgetState
import redRGUI, os.path
from widgetBox import widgetBox
import redREnviron
from RSession import Rcommand
from RSession import require_librarys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy,sip

class filterTable(widgetBox,redRGUI.widgetState):
    def __init__(self,widget,Rdata=None, editable=False, rows=None, columns=None,
    sortable=True, selectionMode = -1, addToLayout = 1,callback=None):
        widgetBox.__init__(self,widget,orientation='vertical')

        if widget and addToLayout and widget.layout():
            widget.layout().addWidget(self)
        elif widget and addToLayout:
            try:
                widget.addWidget(self)
            except: # there seems to be no way to add this widget
                pass


        self.table = QTableView(self)
        self.layout().addWidget(self.table)
        box = redRGUI.widgetBox(self,orientation='horizontal')
        box.layout().setAlignment(Qt.AlignLeft)
        self.clearButton = redRGUI.button(box,label='Clear All Filtering', callback=self.clearFiltering)
        self.label = redRGUI.widgetLabel(box,label='') 
        
        
        self.R = Rcommand
        self.Rdata = None
        
        self.criteriaList = {}
        self.parent = widget
        self.tm=None
        self.editable=editable
        
        self.table.setAlternatingRowColors(True)
        
        if selectionMode != -1:
            self.table.setSelectionMode(selectionMode)
                
        if Rdata:
            self.setRTable(Rdata)
        if sortable:
            self.table.setSortingEnabled(True)

        if editable:
            self.table.horizontalHeader().hide()
            self.table.verticalHeader().hide()
            
        if callback:
            QObject.connect(self.table, SIGNAL('cellClicked(int, int)'), callback)
        
        #QObject.connect(self.table.horizontalHeader(), SIGNAL('sectionClicked(int)'), self.headerClicked)
        self.table.horizontalHeader().setClickable(True)
        self.table.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.horizontalHeader().customContextMenuRequested.connect(self.headerClicked)

        

    def setRTable(self,data, setRowHeaders = 1, setColHeaders = 1, filtered=False):
        #print Rdata
        if not filtered:
            self.Rdata = data
        
        filtered = self.R('nrow(%s)' % data)
        total = self.R('nrow(%s)' % self.Rdata)
        self.label.setText('Showing %d of %d rows.' % (filtered,total))
        # if self.tm:
            # self.tm.initData(Rdata)
        # else:
        self.tm = MyTableModel(data,parent=self,editable=self.editable)
        self.table.setModel(self.tm)
    
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
    def headerClicked(self,val):
        print '#############################', val.x()
        ncol = self.R('ncol(%s)' % self.Rdata,silent=True)
        start =0;
        pos = val.x()
        for x in range(0,ncol):
            if pos > start and pos < start + self.table.horizontalHeader().sectionSize(x):
                break
            start += self.table.horizontalHeader().sectionSize(x)
        selectedCol = x+1
        self.createMenu(selectedCol,val)
    
    
    def createMenu(self, selectedCol, pos):
        #print selectedCol, pos
        print 'in createMenu', self.criteriaList

        globalPos = self.mapToGlobal(pos)
        self.menu = QDialog(None,Qt.Popup)
        self.menu.setLayout(QVBoxLayout())
        clearButton = redRGUI.button(self.menu,label='Clear Filter',
        callback=lambda col=selectedCol: self.createCriteriaList(col,self.menu,action='clear'))
        clearButton.hide()
        self.optionsBox = redRGUI.widgetBox(self.menu)
        if selectedCol in self.criteriaList.keys():
            clearButton.show()
            
        
        colClass = self.R('class(%s[,%d])' % (self.Rdata,selectedCol),silent=True)
        #print colClass
        if colClass == 'factor':
            #redRGUI.widgetLabel(self.menu,label='Enter a value for one of these critera:')
            if selectedCol in self.criteriaList.keys():
                checked = self.criteriaList[selectedCol]['value']
            else:
                checked = []
            levels = self.R('levels(%s[,%d])' % (self.Rdata,selectedCol),silent=True)
            levels.insert(0,'Check All')
            if len(levels) > 1:
                scroll = redRGUI.scrollArea(self.optionsBox)
                c = redRGUI.checkBox(scroll,buttons=levels,setChecked = checked)
            else:
                c = redRGUI.checkBox(self.optionsBox,buttons=levels,setChecked = checked)
            
            QObject.connect(c.buttons, SIGNAL('buttonClicked (int)'), lambda val : self.factorCheckBox(val,self.optionsBox))
    
        elif colClass in ['integer','numeric']:
            label = redRGUI.widgetLabel(self.menu,label='Enter a value for one of these critera:')
            self.menu.layout().insertWidget(1,label)
            self.options = ['Equals', 'Does Not Equal','Greater Than','Greater Than Or Equal To', 
            'Less Than', 'Less Than or Equal To', 'Between\n(2 numbers comma\nseparated, inclusive)', 
            'Not Between\n(2 numbers comma\nseparated)']
            for x in self.options:
                if selectedCol in self.criteriaList and self.criteriaList[selectedCol]['method'] == 'Numeric ' + x:
                    e = redRGUI.lineEdit(self.optionsBox,label=x,text=self.criteriaList[selectedCol]['value'])
                else:
                    e = redRGUI.lineEdit(self.optionsBox,label=x)
                self.connect(e, SIGNAL("textEdited(QString)"),
                lambda val, col=selectedCol,field=x : self.clearOthers(val,self.optionsBox,field))
    
        elif colClass in ['character']:
            label = redRGUI.widgetLabel(self.menu,label='Enter a value for one of these critera:')
            self.menu.layout().insertWidget(1,label)
            self.options = ['Equals', 'Does Not Equal','Begins With','Ends With', 
            'Contains', 'Does Not Contain']
            for x in self.options:
                if selectedCol in self.criteriaList and self.criteriaList[selectedCol]['method'] == 'String ' + x:
                    e = redRGUI.lineEdit(self.optionsBox,label=x,text=self.criteriaList[selectedCol]['value'])
                else:
                    e = redRGUI.lineEdit(self.optionsBox,label=x)
                self.connect(e, SIGNAL("textEdited(QString)"),
                lambda val, col=selectedCol,field=x : self.clearOthers(val,self.menu,field))
    
        buttonBox = redRGUI.widgetBox(self.optionsBox,orientation='horizontal')
        buttonBox.layout().setAlignment(Qt.AlignRight)
        okButton = redRGUI.button(buttonBox,label='OK',callback=lambda col=selectedCol: self.createCriteriaList(col,self.optionsBox,action='OK'))
        okButton.setDefault (True)
        redRGUI.button(buttonBox,label='Cancel',callback=lambda col=selectedCol: self.createCriteriaList(col,self.optionsBox,action='cancel'))
        self.menu.move(globalPos)
        self.menu.show()
    def factorCheckBox(self,val,menu):
        if val != 0: return
        checkbox = menu.findChildren(redRGUI.checkBox)[0]
        print checkbox.getChecked(), 'Check All' in checkbox.getChecked()
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
        self.filter()
        
    def createCriteriaList(self,col,menu,action):
        print 'in filter@@@@@@@@@@@@@@@@@@@@@@@@@@', col,action
        print self.criteriaList
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
                        print label.text(),value.text()
                        self.criteriaList[col] = {'column':col, "method": 'Numeric ' + str(label.text()), "value": str(value.text())}
            elif colClass in ['character']:
                for label,value in zip(menu.findChildren(QLabel),menu.findChildren(QLineEdit)):
                    if value.text() != '':
                        print label.text(),value.text()
                        self.criteriaList[col] = {'column':col, "method": 'String ' + str(label.text()), "value": str(value.text())}
            elif colClass == 'factor':
                checks = menu.findChildren(redRGUI.checkBox)[0].getChecked()
                if 'Check All' in checks:
                    checks.remove('Check All')
                if len(checks) != 0:
                    self.criteriaList[col] = {'column':col, "method": 'factor', "value": checks}
                else:
                    del self.criteriaList[col]
        print 'criteriaList', self.criteriaList
        self.menu.hide()
        self.filter()
    
    def filter(self):
        filters  = []
        for col,criteria in self.criteriaList.items():
            #print 'in loop', col,criteria
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
            elif 'Numeric Less Than Or Equal To' == criteria['method']:
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
            
            
            elif 'factor' == criteria['method']:
                f= '","'.join([str(x) for x in criteria['value']])
                filters.append(self.Rdata+'[,'+str(col)+'] %in% as.factor(c("'+f+'"))')
        
        # print filters
        self.filteredData = '%s[%s,,drop = F]' % (self.Rdata,' & '.join(filters))
        # print 'string:', self.filteredData
        self.setRTable(self.filteredData,filtered=True)
             

    def getSettings(self):
        r = {'Rdata': self.Rdata,
        'selection':[[i.row(),i.column()] for i in self.selectedIndexes()]}
        if self.oldSortingIndex != None:
            r['sortIndex'] = self.oldSortingIndex
            r['order'] = self.oldSortingOrder

        return r
    def loadSettings(self,data):
        # print data
        if not data['Rdata']: return 
        
        self.setRTable(data['Rdata'])
        
        if 'sortIndex' in data.keys():
            self.sortByColumn(data['sortIndex'],data['order'])
        if 'selection' in data.keys() and len(data['selection']):
            for i in data['selection']:
                self.setItemSelected(self.item(i[0],i[1]),True)
    def delete(self):
        sip.delete(self)
    def getReportText(self, fileDir):
        # import os
        # fname = str(os.path.join(fileDir, self.Rdata+'.txt'))
        # fname = fname.replace('\\', '/')
        # print fname
        #self.R('write.table('+self.Rdata+', file = "'+fname+'", sep = "\\t")')
        # self.R('txt<-capture.output(summary('+self.Rdata+'))')
        # tmp = self.R('paste(txt, collapse ="\n      ")')
        text = 'Data was viewed in a Data Viewer.  Open the file in Red-R for more information on this data.\n\n'
        return text


class MyTableModel(QAbstractTableModel): 
    def __init__(self,Rdata,parent=None,editable=False): 
        """ datain: a list of lists
            headerdata: a list of strings
        """
        self.parent = parent 
        self.R = Rcommand
        self.editable = editable
        # self.filterable = filterable
        QAbstractTableModel.__init__(self,parent) 
        
        
        self.initData(Rdata)
    def flags(self,index):
        if self.editable:
            return (Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
        else:
            return (Qt.ItemIsSelectable | Qt.ItemIsEnabled)
    def rowCount(self,parent): 
        return len(self.arraydata)
 
    def initData(self,Rdata):
        self.Rdata = Rdata
        self.colnames = self.R('colnames(as.data.frame(' +Rdata+ '))', wantType = 'list',silent=True)
        self.rownames = self.R('rownames(as.data.frame(' +Rdata+'))', wantType = 'list',silent=True)
        self.arraydata = self.R('as.matrix('+Rdata+')', wantType = 'listOfLists',silent=True)
        
    def columnCount(self,parent): 
        return len(self.arraydata[0])
 
    def data(self, index, role): 
        # print 'in data'
        if not index.isValid(): 
            return QVariant() 
        elif role != Qt.DisplayRole: 
            return QVariant() 
        return QVariant(self.arraydata[index.row()][index.column()]) 

    def setData(self,index,data, role):
        print 'in setData', data.toString(), index.row(),index.column(), role
        if not index.isValid(): 
            return False
        elif role == Qt.EditRole: 
            print self.arraydata[index.row()][index.column()]
            self.arraydata[index.row()][index.column()] = data.toString()
            Rcmd = '%s[%d,%d]="%s"' % (self.Rdata, index.row(), index.column(), data.toString())
            # print Rcmd
            self.R(Rcmd)
            print self.arraydata
            print self.arraydata[index.row()][index.column()]
            self.emit(SIGNAL("dataChanged()"))
            return True
        # elif role == Qt.BackgroundRole:
            # print 'in BackgroundRole'
            # d = self.itemDelegate(index)
            # d.paint(QBrush(Qt.red))
            # return True
        
        return False
    
    def headerData(self, col, orientation, role):
        # print 'in headerData', col, orientation, role
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.colnames[col])
        elif orientation == Qt.Horizontal and role == Qt.DecorationRole:
            # print 'asdfasdf
            icon = QIcon(os.path.join(redREnviron.directoryNames['picsDir'],'arrow_down.png'))
            return QVariant(icon)
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:     
            return QVariant(self.rownames[col])
        return QVariant()
    
    def setHeaderData(self,col,orientation,data,role):
        print 'in setHeaderData'
        if orientation == Qt.Horizontal and role == Qt.EditRole:
            self.colnames[col] = data.toString()
            self.emit(SIGNAL("headerDataChanged()"))
            return True
        else:
            return False
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
        """Sort table by given column number.
        """
        if self.editable: return
        #print 'in sort'
        import operator
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        
        for r,x in zip(self.rownames, self.arraydata):
            x.append(r)
        # self.arraydata.append(self.rownames)
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
       
        self.rownames = [x.pop() for x in self.arraydata]
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