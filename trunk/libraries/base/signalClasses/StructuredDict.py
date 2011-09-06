### Python Structured Dictionary Class.  Contains python dictionary objects and can be the parent class of other classes, even R classes.
### Dict must be a dictionary of lists and the lists must be of the same length.

"""
.. convertTo:: `base:UnstructuredDict`
.. convertFrom:: ``
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libraries.base.signalClasses.UnstructuredDict import *

class StructuredDict(UnstructuredDict):
    convertToList = [BaseRedRVariable, UnstructuredDict]
    convertFromList = []
    def __init__(self, widget, data, parent = None, keys = None, checkVal = True, **kwargs):
        
        UnstructuredDict.__init__(self, widget, data = data, parent = parent, keys = keys, checkVal = False)
        
        
        if checkVal:
            self.length = len(data[data.keys()[0]]) # the length of the first element
            if type(data) not in [dict]:
                raise Exception, 'Data not of dict type'
            
            for key in data.keys():
                if type(data[key]) not in [list]:
                    raise Exception, 'Data in '+unicode(key)+' not of list type'
                if len(data[key]) != self.length:
                    print data
                    raise Exception, 'Data in '+unicode(key)+' not of same length as data in first key.'
                        
            if keys and len(keys) != len(self.data.keys()):
                print 'WARNING! Key length not same as keys.  Ignoring keys.'
                self.keys = self.data.keys()
            elif keys:
                self.keys = keys
            else:
                self.keys = self.data.keys()
        else:
            self.keys = None
            self.length = None
    def getKeys(self):
        return self.keys
    def transpose(self):
        ## transpose the structured data
        
        newDict = {}
        newKeys = []
        if 'row_names' in self.data:
            for name in self.data['row_names']:
                newDict[name] = []
                newKeys.append(name)
        else:
            for i in range(len(self.data[self.data.keys()[0]])):
                newDict[unicode(i+1)] = []
                newKeys.append(unicode(i+1))
        if not self.keys or self.keys == None:
            keys = self.data.keys()
        else:
            keys = self.keys
        for i in range(len(self.data[self.data.keys()[0]])):
            for key in keys:
                newDict[newKeys[i]].append(self.data[key][i])
                
        newData = StructuredDict(data = newDict, parent = self, keys = newKeys)
        return newData
            
    def convertToClass(self, varClass):
        if varClass == BaseRedRVariable:
            return self
        elif varClass == UnstructuredDict:
            return self
        elif varClass == StructuredDict:
            return self
        else:
            raise Exception
            
    def getDims_data(self):
        return (len(self.data.keys()), self.length)
        
    def getTableModel(self, widget, filtered = True, sortable = True):
        return StructuredDictModel(widget, self.getData(), filteredOn = [], filterable = filtered, sortable = sortable)

import os, sys, time, redREnviron
class StructuredDictModel(QAbstractTableModel): 
    def __init__(self, parent, data, filteredOn = [], editable=False,
    filterable=False,sortable=False, orgData = None, reload = False, criteriaList = {}): 
        QAbstractTableModel.__init__(self,parent) 
        if not data: raise Exception('Rdata must be present')
        self.working = False
        self.range = 500
        self.parent =  parent
        #self.R = Rcommand
        self.sortable = sortable
        self.editable = editable
        self.filterable = filterable
        self.filteredOn = filteredOn
        self.criteriaList = criteriaList
        # self.filter_delete = os.path.join(redREnviron.directoryNames['picsDir'],'filterAdd.png')
        self.columnFiltered = QIcon(os.path.join(redREnviron.directoryNames['picsDir'],'columnFilter.png'))
        
        # print self.filter_add,os.path.exists(self.filter_add),os.path.exists(self.filter_delete)
        if orgData:
            self.orgData = orgData
        else:
            self.orgRdata = data
        self.initData(data)
        
    ##########  functions accessed by filter table  #########
    def getSummary(self):
        #total = 
        #filtered = self.R('nrow(%s)' % self.Rdata, silent = True)
        return 'Displaying dict data.' # % (filtered, total) 
    def getSettings(self):
        r = {}
        r['orgData'] = self.orgData
        r['reload'] = True
        r['data'] = self.data
        r['filteredOn'] = self.filteredOn
        r['editable'] = self.editable
        r['filterable'] = self.filterable
        r['criteriaList'] = self.criteriaList
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
        
    def sort(self,col,order):
        return
        #self.tm.sort(col-1,order)
        #self.parent.sortByColumn(col-1, order)
        #self.parent.horizontalHeader().setSortIndicator(col-1,order)
        #self.menu.hide()
        #self.parent.sortIndex = [col-1,order]
    def createMenu(self, selectedCol):
        '''
        self.tm.createMenu(selectedCol, sortable = self.sortable, filterable = self.filterable
        '''
        return
        #print selectedCol, pos
        # print _('in createMenu'), self.criteriaList

        #globalPos = QCursor.pos() #self.mapToGlobal(pos)
        #self.menu = QDialog(None,Qt.Popup)
        #self.menu.setLayout(QVBoxLayout())
        #if self.sortable:
            #box = widgetBox(self.menu,orientation='horizontal')
            #box.layout().setAlignment(Qt.AlignLeft)
            #button(box,label='A->Z',callback= lambda: self.sort(selectedCol,Qt.AscendingOrder))
            #widgetLabel(box,label=_('Ascending Sort'))
            #box = widgetBox(self.menu,orientation='horizontal')
            #box.layout().setAlignment(Qt.AlignLeft)
            #button(box,label='Z->A',callback= lambda: self.sort(selectedCol,Qt.DescendingOrder))
            #widgetLabel(box,label=_('Descending Sort'))
            
        #if not self.filterable:
            #self.menu.move(globalPos)
            #self.menu.show()
            #return
        
        #if self.sortable:
            #hr = QFrame(self.menu)
            #hr.setFrameStyle( QFrame.Sunken + QFrame.HLine );
            #hr.setFixedHeight( 12 );
            #self.menu.layout().addWidget(hr)
    
        
        #clearButton = button(self.menu,label=_('Clear Filter'),
        #callback=lambda col=selectedCol: self.createCriteriaList(col,self.menu,action='clear'))
        #self.menu.layout().setAlignment(clearButton,Qt.AlignHCenter)
        #clearButton.hide()
        
        #self.numericLabel = widgetLabel(self.menu,label=_('Enter a value for one of these critera:'))
        #self.numericLabel.hide()
        
        #self.stringLabel = widgetLabel(self.menu,label=_('Enter a value for one of these critera (case sensitive):'))
        #self.stringLabel.hide()
        
        #self.factorLabel = widgetLabel(self.menu,label=_('Select Levels:'))
        #self.factorLabel.hide()
        
        
        #if selectedCol in self.criteriaList.keys():
            #clearButton.show()
        
        #self.optionsBox = widgetBox(self.menu)
        #self.optionsBox.layout().setAlignment(Qt.AlignTop)
        
        ##### Logic if R variable ###
        ##if self.varType == 0:
        #colClass = self.R('class(%s[,%d])' % (self.Rdata,selectedCol),silent=True)
        
        #if colClass in ['factor','logical']:
            #self.factorLabel.show()
            
            #if selectedCol in self.criteriaList.keys():
                #checked = self.criteriaList[selectedCol]['value']
            #else:
                #checked = []
            #if colClass =='logical':
                #levels = ['TRUE','FALSE']
            #else:
                #levels = self.R('levels(%s[,%d])' % (self.Rdata,selectedCol),wantType='list', silent=True)
                
            #if len(levels) > 1:
                #levels.insert(0,_('Check All'))
            #scroll = scrollArea(self.optionsBox,spacing=1)
            
            #c = checkBox(scroll,label=_('Levels'),displayLabel=False, buttons=levels,setChecked = checked)
            #scroll.setWidget(c.controlArea)
            
            #QObject.connect(c.buttons, SIGNAL('buttonClicked (int)'), lambda val : self.factorCheckBox(val,self.optionsBox))
    
        #elif colClass in ['integer','numeric']:
            #self.numericLabel.show()
            #self.options = [_('Equals'), _('Does Not Equal'),_('Greater Than'),_('Greater Than Or Equal To'), 
            #_('Less Than'), _('Less Than or Equal To'), 'Between\n(2 numbers comma\nseparated, inclusive)', 
            #'Not Between\n(2 numbers comma\nseparated)']
            #for x in self.options:
                #if selectedCol in self.criteriaList and self.criteriaList[selectedCol]['method'] == _('Numeric ') + x:
                    #e = lineEdit(self.optionsBox,label=x,text=self.criteriaList[selectedCol]['value'])
                #else:
                    #e = lineEdit(self.optionsBox,label=x)
                #self.connect(e, SIGNAL("textEdited(QString)"),
                #lambda val, col=selectedCol,field=x : self.clearOthers(val,self.optionsBox,field))
    
        #elif colClass in ['character']:
            #self.stringLabel.show()
            #self.options = [_('Equals'), _('Does Not Equal'),_('Begins With'),_('Ends With'), 
            #_('Contains'), _('Does Not Contain')]
            #for x in self.options:
                #if selectedCol in self.criteriaList and self.criteriaList[selectedCol]['method'] == _('String ') + x:
                    #e = lineEdit(self.optionsBox,label=x,text=self.criteriaList[selectedCol]['value'])
                #else:
                    #e = lineEdit(self.optionsBox,label=x)
                #self.connect(e, SIGNAL("textEdited(QString)"),
                #lambda val, col=selectedCol,field=x : self.clearOthers(val,self.optionsBox,field))
        
        #buttonBox = widgetBox(self.optionsBox,orientation='horizontal')
        #buttonBox.layout().setAlignment(Qt.AlignRight)
        #okButton = button(buttonBox,label=_('OK'),
        #callback=lambda col=selectedCol: self.createCriteriaList(col,self.optionsBox,action=_('OK')))
        #okButton.setDefault (True)
        #button(buttonBox,label=_('Cancel'),
        #callback=lambda col=selectedCol: self.createCriteriaList(col,self.optionsBox,action='cancel'))
        
        #self.menu.move(globalPos)
        #self.menu.show()
    def factorCheckBox(self,val,menu):
        return
        #if val != 0: return
        #checkbox = menu.findChildren(checkBox)[0]
        #if checkbox.buttonAt(0) != _('Check All'): return
        ##print checkbox.getChecked(), _('Check All') in checkbox.getChecked()
        #if _('Check All') in checkbox.getChecked():
            #checkbox.checkAll()
        #else: 
            #checkbox.uncheckAll()
        
    def clearOthers(self,val, menu, field):
        return
        # print '##############', val, field
        #for label,value in zip(menu.findChildren(QLabel),menu.findChildren(QLineEdit)):
            #if label.text() != field:
                #value.setText('')

    def clearFiltering(self):
        return
        #self.criteriaList = {}
        #self.Rdata = self.orgRdata
        ## self.horizontalHeader().setSortIndicator(-1,order)
        #self.filter()
        
    def createCriteriaList(self,col,menu,action):
        return
        #print 'in filter@@@@@@@@@@@@@@@@@@@@@@@@@@', col,action
        #print self.criteriaList
        if action=='cancel':
            self.menu.hide()
            return
        colClass = self.R('class(%s[,%d, FALSE])' % (self.Rdata,col),silent=True) # must set the subsetting to not drop in the case of only one column
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
        return
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
                f= '","'.join([unicode(x, 'UTF-8', errors='ignore') for x in criteria['value']])
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
    def getFilteredData(self):
        return self.filteredData
    def flags(self,index):
        if self.editable:
            return (Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
        else:
            return (Qt.ItemIsSelectable | Qt.ItemIsEnabled)
 
    def getRange(self,row,col):
        r = {}
        if row-self.range < 0:
            r['rstart'] = 0
        else:
            r['rstart'] = row-self.range
        
        
        if row+self.range > self.nrow:
            r['rend'] = self.nrow
        else:
            r['rend'] = row+self.range
        
        
        if col-self.range < 0:
            r['cstart'] = 0
        else:
            r['cstart'] = col-self.range   
        if col+self.range > self.ncol:
            r['cend'] = self.ncol
        else:
            r['cend'] = col+self.range
        
        return r
        
    def initData(self,data):
        self.data = data
        
        self.colnames = self.data.keys() # self.R('colnames(as.data.frame(' +Rdata+ '))', wantType = 'list',silent=True)
        self.rownames = range(1, len(self.colnames)+1)
        self.nrow = len(self.data[self.colnames[0]])#self.R('nrow(%s)' % self.Rdata,silent=True)
        #print self.nrow
        self.ncol = len(self.colnames) # self.R('ncol(%s)' % self.Rdata,silent=True)
        
        # protect if there is a null table
        if self.nrow == 0 or self.ncol == 0:
            return
        
        #print self.ncol
        self.currentRange = self.getRange(0,0)
        
        #self.arraydata = self.R('as.matrix(%s[%d:%d,%d:%d])' % (self.Rdata,
        #self.currentRange['rstart'],
        #self.currentRange['rend'],
        #self.currentRange['cstart'],
        #self.currentRange['cend']
        #),
        #wantType = 'listOfLists',silent=True)
        
        ## print _('self.arraydata loaded')

        #self.rownames = self.R('rownames(as.data.frame(' +Rdata+'))', wantType = 'list',silent=True)
        #if len(self.rownames) ==0: self.rownames = [1]
        ## print self.rownames, self.rowCount(self)
        ## print self.colnames

        #if self.arraydata == [[]]:
            #toAppend= ['' for i in xrange(self.columnCount(self))]
            #self.arraydata = [toAppend]
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
        elif not self.data or self.data == None:
            return QVariant()
        #if (
            #(self.currentRange['cstart'] + 100 > index.column() and self.currentRange['cstart'] !=1) or 
            #(self.currentRange['cend'] - 100 < index.column() and self.currentRange['cend'] != self.ncol) or 
            #(self.currentRange['rstart'] + 100 > index.row() and self.currentRange['rstart'] !=1) or 
            #(self.currentRange['rend'] - 100 < index.row() and self.currentRange['rend'] != self.nrow)
        #):

            #self.currentRange = self.getRange(index.row(), index.column())
            #if not self.working:
                #self.working = True
                #self.arraydata = self.R('as.matrix(%s[%d:%d,%d:%d])' % (self.Rdata,
            #self.currentRange['rstart'],
            #self.currentRange['rend'],
            #self.currentRange['cstart'],
            #self.currentRange['cend']
            #),
            #wantType = 'list',silent=True)
                #self.working = False
                
            #else: self.arraydata = []
        #if len(self.arraydata) == 0 or len(self.arraydata[0]) == 0:
            #return QVariant()
        
        rowInd = index.row() #- self.currentRange['rstart'] + 1
        colInd = index.column() #- self.currentRange['cstart'] + 1
        # self.working = False
        #print self.arraydata[rowInd][colInd], rowInd, colInd
        return QVariant(self.data[self.colnames[colInd]][rowInd]) 

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if not col >= len(self.colnames):
                return QVariant(self.colnames[col])
        #elif orientation == Qt.Horizontal and role == Qt.DecorationRole and (self.filterable or self.sortable):
            #if col+1 in self.filteredOn:
                #return QVariant(self.columnFiltered)
            #else:
                #return QVariant()
        elif orientation == Qt.Vertical and role == Qt.DisplayRole: 
            # print 'row number', col, len(self.rownames)
            if not col >= len(self.rownames):
                return QVariant(self.rownames[col])
        return QVariant()
    

    def sort(self, Ncol, order):
        return
        if self.editable: return
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        #print 'adfasfasdfasdfas', self.R('class(%s)' % self.orgRdata)
        if order == Qt.DescendingOrder:
            self.Rdata = '%s[order(%s[,%d],decreasing=TRUE),,FALSE]' % (self.orgRdata,self.orgRdata,Ncol)
        else:
            self.Rdata = '%s[order(%s[,%d]),,FALSE]' % (self.orgRdata,self.orgRdata,Ncol)
            
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