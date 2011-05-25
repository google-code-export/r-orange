from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libraries.base.signalClasses.RList import *
from libraries.base.signalClasses.StructuredDict import *
from libraries.base.signalClasses.UnstructuredDict import *
from libraries.base.signalClasses.TableView import *

import time, sys, os, redREnviron
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.scrollArea import scrollArea
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.checkBox import checkBox
import redRi18n
_ = redRi18n.get_(package = 'base')
class RDataFrame(RList, StructuredDict, TableView):
    
    convertFromList = [StructuredDict]
    convertToList = [RList, RVariable, StructuredDict, UnstructuredDict, TableView]
    def __init__(self, widget, data, parent = None, checkVal = True):
        StructuredDict.__init__(self, widget = widget, data = data, parent = parent, checkVal = False)
        RList.__init__(self, widget, data = data, parent = parent, checkVal = False)
        TableView.__init__(self)
        if checkVal and not self.R('is.data.frame(%s)' % self.data, silent = True, wantType = 'convert'):
            raise Exception('not a dataframe') # there this isn't the right kind of data for me to get !!!!!
        self.newDataID = unicode(time.time()).replace('.', '_')
        self.RListSignal = None
        self.structuredDict = None
        self.matrix = None
    def convertFromClass(self, signal):
        if isinstance(signal, StructuredDict):
            return self._convertFromStructuredDict(signal)
    def _convertFromStructuredDict(self, signal):
        self.assignR('DataFrameConversion_'+self.newDataID, signal.getData())
        self.R('DataFrameConversion_'+self.newDataID+'<-as.data.frame('+'DataFrameConversion_'+self.newDataID+')', wantType = 'NoConversion')
        if 'row_names' in signal.getData().keys():
            self.R('rownames('+'DataFrameConversion_'+self.newDataID+')<-'+'DataFrameConversion_'+self.newDataID+'$row_names', wantType = 'NoConversion')
            self.R('DataFrameConversion_'+self.newDataID+'$row_names<-NULL', wantType = 'NoConversion')
        return RDataFrame(data = 'DataFrameConversion_'+self.newDataID)  
    def convertToClass(self, varClass):
        if varClass == RList:
            return self._convertToList()
        elif varClass == RVariable:
            return self._convertToVariable()
        elif varClass == RDataFrame:
            return self
        elif varClass == StructuredDict or varClass == UnstructuredDict:
            return self._convertToStructuredDict()
        elif varClass == TableView:
            return self
        else:
            raise Exception

    def _convertToStructuredDict(self):
        if not self.structuredDict:
            dictData = self.R('as.data.frame(%s)' % self.data, wantType = 'dict', silent = False)
            
            dictData['row_names'] = self.R('rownames('+self.data+')', wantType = 'list')
            keys = ['row_names']
            keys += self.R('colnames('+self.data+')')
            self.structuredDict = StructuredDict(self.widget, data = dictData, parent = self, keys = keys)
            return self.structuredDict
        else:
            return self.structuredDict
    def _convertToList(self):
        if not self.RListSignal:
            #self.R('list_of_'+self.data+'<-as.list('+self.data+')')
            self.RListSignal = RList(self.widget, data = 'as.list('+self.data+')', parent = self.parent)
            self.RListSignal.dictAttrs = self.dictAttrs.copy()
            return self.RListSignal
        else:
            return self.RListSignal
    def getSimpleOutput(self, subsetting = '[1:5, 1:5]'):
        # return the text for a simple output of this variable
        text = 'Simple Output\n\n'
        text += 'Class: '+self.getClass_data()+'\n\n'
        text += self._simpleOutput(subsetting)
        return text
    def _fullOutput(self, subsetting = ''):
        text = self._simpleOutput()+'\n\n'
        text += 'R Data Variable Value: '+self.getAttrOutput_data('data', subsetting)+'\n\n'
        dims = self.getDims_data()
        text += 'R Data Variable Size: '+unicode(dims[0])+' Rows and '+unicode(dims[1])+' Columns\n\n'
        text += 'R Parent Variable Name: '+self.parent+'\n\n'
        text += 'R Parent Variable Value: '+self.getAttrOutput_data('parent', subsetting)+'\n\n'
        text += 'Class Dictionary: '+unicode(self.dictAttrs)+'\n\n'
        return text
    def getRownames_call(self):
        return 'rownames('+self.data+')'
    def getRownames_data(self):
        return self.R(self.getRownames_call(), wantType = 'list', silent = True)
    def getItem_call(self, item):
        if type(item) in [int, float, long]:
            item = int(item)
            return self.data+'[,'+unicode(item)+']'
        elif type(item) in [str]:
            return self.data+'[,\''+unicode(item)+'\']'
        elif type(item) in [list]:
            newItemList = []
            for i in item:
                if type(i) in [int, float, long]:
                    newItemList.append(unicode(int(i)))
                elif type(i) in [str]:
                    newItemList.append('\"'+unicode(i)+'\"')
            return self.data+'[,c('+unicode(newItemList)[1:-1]+')]'
        else:
            return self.data #just return all of the data and hope the widget picks up from there
    def getItem_data(self, item, wantType = 'dict'): # native functionality is to return a dict (this is what lists do)
        call = self.getItem_call(item)
        if call != None:
            if type(item) in [int, str, long, float]:
                return self.R(call, wantType = wantType, silent = True) # returns a single column
            elif type(item) in [list] and wantType not in ['array', 'list']: # returns a dict
                return self.R(call, wantType = wantType, silent = True)
                
            elif type(item) in [list] and wantType in  ['array', 'list']: # returns a list of lists
                return self.R('as.matrix('+call+')', wantType = wantType, silent = True)
        else:
            print 'No data to return'
            return {}
    def getColumnnames_call(self):
        return self.getNames_call()
    def getColumnnames_data(self):
        return self.getNames_data()
    def getRange_call(self, rowRange = None, colRange = None):
        if rowRange == None and colRange == None:
            return self.data
        if rowRange:
            rr = unicode(rowRange)
        else:
            rr = ''
        if colRange:
            cr = unicode(colRange)
        else:
            cr = ''
        return self.data+'['+rr+','+cr+']'
    def getRowData_call(self, item):
        if type(item) in [int, float, long]:
            item = int(item)
            return self.data+'['+unicode(item)+',]'
        elif type(item) in [str]:
            return self.data+'[\''+unicode(item)+'\',]'
        elif type(item) in [list]:
            newItemList = []
            for i in item:
                if type(i) in [int, float, long]:
                    newItemList.append(unicode(int(i)))
                elif type(i) in [str]:
                    newItemList.append('\"'+unicode(i)+'\"')
            return self.data+'[c('+unicode(newItemList)[1:-1]+'),]'
        else:
            return self.data #just return all of the data and hope the widget picks up from there
    def getRowData_data(self, item):
        output = self.R(self.getRowData_call(item), wantType = 'list', silent = True)
        return output
    
    def getTableModel(self, widget, filtered = True, sortable = True):
        return RDataFrameModel(self.getData(), widget, filteredOn = [], filterable = filtered, sortable = sortable)
        
class RDataFrameModel(QAbstractTableModel): 
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
        self.criteriaList = {}
        # self.filter_delete = os.path.join(redREnviron.directoryNames['picsDir'],'filterAdd.png')
        self.columnFiltered = QIcon(os.path.join(redREnviron.directoryNames['picsDir'],'columnFilter.png'))
        
        # print self.filter_add,os.path.exists(self.filter_add),os.path.exists(self.filter_delete)
        self.orgRdata = Rdata
        self.initData(Rdata)
        
    ##########  functions accessed by filter table  #########
    def getSummary(self):
        total = self.R('nrow(%s)' % self.orgRdata,silent=True)
        filtered = self.R('nrow(%s)' % self.Rdata, silent = True)
        return 'Displaying %d of %s rows' % (filtered, total) 
        
    def startProgressBar(self, title,text,max):
        progressBar = QProgressDialog()
        progressBar.setCancelButtonText(QString())
        progressBar.setWindowTitle(title)
        progressBar.setLabelText(text)
        progressBar.setMaximum(max)
        progressBar.setValue(0)
        progressBar.show()
        return progressBar
        
    def sort(self,col,order):
        #self.tm.sort(col-1,order)
        self.parent.sortByColumn(col-1, order)
        self.parent.horizontalHeader().setSortIndicator(col-1,order)
        self.menu.hide()
        self.parent.sortIndex = [col-1,order]
    def createMenu(self, selectedCol):
        '''
        self.tm.createMenu(selectedCol, sortable = self.sortable, filterable = self.filterable
        '''
        #print selectedCol, pos
        # print _('in createMenu'), self.criteriaList

        globalPos = QCursor.pos() #self.mapToGlobal(pos)
        self.menu = QDialog(None,Qt.Popup)
        self.menu.setLayout(QVBoxLayout())
        if self.sortable:
            box = widgetBox(self.menu,orientation='horizontal')
            box.layout().setAlignment(Qt.AlignLeft)
            button(box,label='A->Z',callback= lambda: self.sort(selectedCol,Qt.AscendingOrder))
            widgetLabel(box,label=_('Ascending Sort'))
            box = widgetBox(self.menu,orientation='horizontal')
            box.layout().setAlignment(Qt.AlignLeft)
            button(box,label='Z->A',callback= lambda: self.sort(selectedCol,Qt.DescendingOrder))
            widgetLabel(box,label=_('Descending Sort'))
            
        if not self.filterable:
            self.menu.move(globalPos)
            self.menu.show()
            return
        
        if self.sortable:
            hr = QFrame(self.menu)
            hr.setFrameStyle( QFrame.Sunken + QFrame.HLine );
            hr.setFixedHeight( 12 );
            self.menu.layout().addWidget(hr)
    
        
        clearButton = button(self.menu,label=_('Clear Filter'),
        callback=lambda col=selectedCol: self.createCriteriaList(col,self.menu,action='clear'))
        self.menu.layout().setAlignment(clearButton,Qt.AlignHCenter)
        clearButton.hide()
        
        self.numericLabel = widgetLabel(self.menu,label=_('Enter a value for one of these critera:'))
        self.numericLabel.hide()
        
        self.stringLabel = widgetLabel(self.menu,label=_('Enter a value for one of these critera (case sensitive):'))
        self.stringLabel.hide()
        
        self.factorLabel = widgetLabel(self.menu,label=_('Select Levels:'))
        self.factorLabel.hide()
        
        
        if selectedCol in self.criteriaList.keys():
            clearButton.show()
        
        self.optionsBox = widgetBox(self.menu)
        self.optionsBox.layout().setAlignment(Qt.AlignTop)
        
        #### Logic if R variable ###
        #if self.varType == 0:
        colClass = self.R('class(%s[,%d])' % (self.Rdata,selectedCol),silent=True)
        
        if colClass in ['factor','logical']:
            self.factorLabel.show()
            
            if selectedCol in self.criteriaList.keys():
                checked = self.criteriaList[selectedCol]['value']
            else:
                checked = []
            if colClass =='logical':
                levels = ['TRUE','FALSE']
            else:
                levels = self.R('levels(%s[,%d])' % (self.Rdata,selectedCol),wantType='list', silent=True)
                
            if len(levels) > 1:
                levels.insert(0,_('Check All'))
            scroll = scrollArea(self.optionsBox,spacing=1)
            
            c = checkBox(scroll,label=_('Levels'),displayLabel=False, buttons=levels,setChecked = checked)
            scroll.setWidget(c.controlArea)
            
            QObject.connect(c.buttons, SIGNAL('buttonClicked (int)'), lambda val : self.factorCheckBox(val,self.optionsBox))
    
        elif colClass in ['integer','numeric']:
            self.numericLabel.show()
            self.options = [_('Equals'), _('Does Not Equal'),_('Greater Than'),_('Greater Than Or Equal To'), 
            _('Less Than'), _('Less Than or Equal To'), 'Between\n(2 numbers comma\nseparated, inclusive)', 
            'Not Between\n(2 numbers comma\nseparated)']
            for x in self.options:
                if selectedCol in self.criteriaList and self.criteriaList[selectedCol]['method'] == _('Numeric ') + x:
                    e = lineEdit(self.optionsBox,label=x,text=self.criteriaList[selectedCol]['value'])
                else:
                    e = lineEdit(self.optionsBox,label=x)
                self.connect(e, SIGNAL("textEdited(QString)"),
                lambda val, col=selectedCol,field=x : self.clearOthers(val,self.optionsBox,field))
    
        elif colClass in ['character']:
            self.stringLabel.show()
            self.options = [_('Equals'), _('Does Not Equal'),_('Begins With'),_('Ends With'), 
            _('Contains'), _('Does Not Contain')]
            for x in self.options:
                if selectedCol in self.criteriaList and self.criteriaList[selectedCol]['method'] == _('String ') + x:
                    e = lineEdit(self.optionsBox,label=x,text=self.criteriaList[selectedCol]['value'])
                else:
                    e = lineEdit(self.optionsBox,label=x)
                self.connect(e, SIGNAL("textEdited(QString)"),
                lambda val, col=selectedCol,field=x : self.clearOthers(val,self.optionsBox,field))
        
        buttonBox = widgetBox(self.optionsBox,orientation='horizontal')
        buttonBox.layout().setAlignment(Qt.AlignRight)
        okButton = button(buttonBox,label=_('OK'),
        callback=lambda col=selectedCol: self.createCriteriaList(col,self.optionsBox,action=_('OK')))
        okButton.setDefault (True)
        button(buttonBox,label=_('Cancel'),
        callback=lambda col=selectedCol: self.createCriteriaList(col,self.optionsBox,action='cancel'))
        
        self.menu.move(globalPos)
        self.menu.show()
    def factorCheckBox(self,val,menu):
        if val != 0: return
        checkbox = menu.findChildren(checkBox)[0]
        if checkbox.buttonAt(0) != _('Check All'): return
        #print checkbox.getChecked(), _('Check All') in checkbox.getChecked()
        if _('Check All') in checkbox.getChecked():
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
        self.Rdata = self.orgRdata
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
                        self.criteriaList[col] = {'column':col, "method": _('Numeric ') + unicode(label.text()), "value": unicode(value.text())}
            elif colClass in ['character']:
                for label,value in zip(menu.findChildren(QLabel),menu.findChildren(QLineEdit)):
                    if value.text() != '':
                        # print label.text(),value.text()
                        self.criteriaList[col] = {'column':col, "method": _('String ') + unicode(label.text()), "value": unicode(value.text())}
            elif colClass in ['factor','logical']:
                checks = menu.findChildren(checkBox)[0].getChecked()
                if _('Check All') in checks:
                    checks.remove(_('Check All'))
                if len(checks) != 0:
                    self.criteriaList[col] = {'column':col, "method": colClass, "value": checks}
                else:
                    del self.criteriaList[col]
            
        #print _('criteriaList'), self.criteriaList
        self.menu.hide()
        self.filter()
    
    def filter(self):
        filters  = []
        for col,criteria in self.criteriaList.items():
            #print _('in loop'), col,criteria['method']
            if _('Numeric Equals') == criteria['method']:
                filters.append('%s[,%s] == %s' % (self.Rdata,col,criteria['value']))
            elif _('Numeric Does Not Equal') == criteria['method']:
                filters.append('%s[,%s] != %s' % (self.Rdata,col,criteria['value']))
            elif _('Numeric Greater Than') == criteria['method']:
                filters.append('%s[,%s] > %s' % (self.Rdata,col,criteria['value']))
            elif _('Numeric Greater Than Or Equal To') == criteria['method']:
                filters.append('%s[,%s] >= %s' % (self.Rdata,col,criteria['value']))
            elif _('Numeric Less Than') == criteria['method']:
                filters.append('%s[,%s] < %s' % (self.Rdata,col,criteria['value']))
            elif _('Numeric Less Than or Equal To') == criteria['method']:
                filters.append('%s[,%s] <= %s' % (self.Rdata,col,criteria['value']))
            elif 'Numeric Between\n(2 numbers comma\nseparated, inclusive)' == criteria['method']:
                (start,comma,stop) = criteria['value'].partition(',')
                if start !='' and stop !='' or comma == ',':
                    filters.append('%s[,%s] >= %s & %s[,%s] <= %s' % (self.Rdata,col,start,self.Rdata,col,stop))
            elif 'Numeric Not Between\n(2 numbers comma\nseparated)' == criteria['method']:
                (start,comma, stop) = criteria['value'].partition(',')
                if start !='' and stop !='' or comma == ',':
                    filters.append('%s[,%s] < %s | %s[,%s] > %s' % (self.Rdata,col,start,self.Rdata,col,stop))

            elif _('String Equals') == criteria['method']:
                filters.append('%s[,%s] == "%s"' % (self.Rdata,col,criteria['value']))
            elif _('String Does Not Equal') == criteria['method']:
                filters.append('%s[,%s] != "%s"' % (self.Rdata,col,criteria['value']))
            elif _('String Begins With') == criteria['method']:
                filters.append('grepl("^%s",%s[,%s])' % (criteria['value'],self.Rdata,col))
            elif _('String Ends With') == criteria['method']:
                filters.append('grepl("%s$",%s[,%s])' % (criteria['value'],self.Rdata,col))
            elif _('String Contains') == criteria['method']:
                filters.append('grepl("%s",%s[,%s])' % (criteria['value'],self.Rdata,col))
            elif _('String Does Not Contain') == criteria['method']:
                filters.append('!grepl("%s",%s[,%s])' % (criteria['value'],self.Rdata,col))
            
            
            elif criteria['method'] in ['logical','factor']:
                f= '","'.join([unicode(x) for x in criteria['value']])
                filters.append(self.Rdata+'[,'+unicode(col)+'] %in% as.factor(c("'+f+'"))')
            #elif 'logical' == critera['method']:
            
       # print 'filters:', filters
        self.filteredData = '%s[%s,,drop = F]' % (self.Rdata,' & '.join(filters))
        #print 'string:', self.filteredData
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.initData(self.filteredData)
        self.emit(SIGNAL("layoutChanged()"))
        if self.parent.onFilterCallback:
            self.parent.onFilterCallback()
    
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
        self.nrow = self.R('nrow(%s)' % self.Rdata,silent=True)
        #print self.nrow
        self.ncol = self.R('ncol(%s)' % self.Rdata,silent=True)
        #print self.ncol
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
        self.parent.setModel(self)
        #self.parent.setModel(self)
        
    def rowCount(self, parent): 
        return self.nrow
        #return len(self.arraydata)
    def columnCount(self, parent): 
        return self.ncol
        #return len(self.arraydata[0])
 
    def data(self, index, role): 
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
        #print self.arraydata[rowInd][colInd], rowInd, colInd
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
    

    def sort(self, Ncol, order):
        if self.editable: return
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        #print 'adfasfasdfasdfas', self.R('class(%s)' % self.orgRdata)
        if order == Qt.DescendingOrder:
            self.Rdata = '%s[order(%s[,%d],decreasing=TRUE),]' % (self.orgRdata,self.orgRdata,Ncol)
        else:
            self.Rdata = '%s[order(%s[,%d]),]' % (self.orgRdata,self.orgRdata,Ncol)
            
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