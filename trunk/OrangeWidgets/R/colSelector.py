"""
<name>Column Selection</name>
<description>Subsets a data.frame object to pass to subsequent widgets.</description>
<icon>icons/Subset.png</icon>
<priority>2020</priority>
"""

from OWRpy import *
import OWGUI

class colSelector(OWRpy): # a simple widget that actually will become quite complex.  We want to do several things, give into about the variables that are selected (do a summary on the attributes and show them to the user) and to pass forward both a subsetted data.frame or a vector for classification for things evaluating TRUE to the subsetting
    settingsList = ['vs', 'saveData', 'rowcolselect', 'newdata', 'olddata', 'rowselectionCriteria', 'colselectionCriteria', 'cTableTexts', 'rowactiveCriteria', 'colactiveCriteria']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        
        self.vs = self.variable_suffix
        self.saveData = None
        self.setRvariableNames(['data', 'result'])
        self.collist = '' # a container for the names of columns that will be picked from the selector.
        self.rowcolselect = 1
        self.GorL = 0
        self.rowselectionCriteria = 0 # Counters for the criteria of selecting Rows and Cols
        self.colselectionCriteria = 0 
        self.rowactiveCriteria = [] # lists showing the active critera for subsetting the rows and cols
        self.colactiveCriteria = []
        self.RowColNamesExist = 1
        self.searchLineEdit = ''
        self.newdata = {}
        self.olddata = {}
        self.sentalready = 0
        self.cTableTexts = []
        self.loadSettings()
        

        self.inputs = [("R DataFrame", RvarClasses.RDataFrame, self.process), ("Subsetting Vector", RvarClasses.RVector, self.ssvAttached)]
        self.outputs = [("R DataFrame", RvarClasses.RDataFrame), ("Classified Vector Subset", RvarClasses.RVector)]
        
        # ###  GUI ###
        infobox = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(infobox, "Data not loaded")
        self.infob = OWGUI.widgetLabel(infobox, "")
        # The GUI should have a few attributes such as a selector for using either the rows or columns (columns should be the default) when an attribute is selected a summary of that should be printed on the GUI.  It would be nice if we could implement multipe selection criteria for a single widget.
        layk = QWidget(self)
        self.controlArea.layout().addWidget(layk)
        grid = QGridLayout()
        grid.setMargin(0)
        layk.setLayout(grid)
        
        # first implement a widget that allows for selection of options
        options = OWGUI.widgetBox(self.controlArea, "Options")
        grid.addWidget(options, 0,0)
        #self.rowcol = OWGUI.radioButtonsInBox(options, self, "rowcolselect", ["Rows", "Columns"], callback = self.changeRowCol)
        self.subOnAttachedButton = OWGUI.button(options, self, "Subset on Attached List", callback = self.subOnAttached)
        self.subOnAttachedButton.setEnabled(False)
        self.cycleUpButton = OWGUI.button(options, self, "Cycle Up", callback = self.cycleUp)
        self.cycleDownButton = OWGUI.button(options, self, "Cycle Down", callback = self.cycleDown)
        self.cycleDownButton.setEnabled(False)
        self.cycleUpButton.setEnabled(False)
        self.tableinfoa = OWGUI.widgetLabel(options, "No Data Connected")
        self.tableinfob = OWGUI.widgetLabel(options, "")
        self.tableinfoc = OWGUI.widgetLabel(options, "")
        self.tableinfod = OWGUI.widgetLabel(options, "")
        
        # a names box that shows the names of either the columns or the rows as well as the colnames or rownames
        namesBox = OWGUI.widgetBox(self.controlArea, "Factor Names")
        grid.addWidget(namesBox, 0, 1)
        self.columnsorrows = OWGUI.listBox(namesBox, self, callback = self.subListAdd) # Adds the selected item to the subset list
        
        # a summary box that shows the R summary of the selected row or columns
        
        self.boxIndices = {}
        self.valuesStack = QStackedWidget(self)
        grid.addWidget(self.valuesStack, 0, 2)
        
        # valuesStack 0: No data selected
        boxVal = OWGUI.widgetBox(self, "Values", addToLayout = 0)
        self.boxIndices[0] = boxVal
        self.valuesStack.addWidget(boxVal)
        
        # valuesStack 1: continuous data
        boxVal = OWGUI.widgetBox(self, "Values", addToLayout = 0)
        self.boxIndices[1] = boxVal
        self.StatTable = QTableWidget()
        boxVal.layout().addWidget(self.StatTable)
        self.SubSlider = QSlider()
        self.SubSlider.setOrientation(Qt.Horizontal)
        self.connect(self.SubSlider, SIGNAL('valueChanged(int)'), self.SubSliderValueChanged)
        boxVal.layout().addWidget(self.SubSlider)
        self.numericInfo = OWGUI.widgetLabel(boxVal, "")
        greaterLessRadio = OWGUI.radioButtonsInBox(boxVal, self, 'GorL', ['Greater Than', 'Less Than'])
        OWGUI.button(boxVal, self, "Select Criteria", callback = self.selectCriteria)
        self.valuesStack.addWidget(boxVal)
        
        # valuesStack 2: factor data
        boxVal = OWGUI.widgetBox(self, "Values", addToLayout = 0)
        self.boxIndices[2] = boxVal
        self.FactorTable = QTableWidget()
        boxVal.layout().addWidget(self.FactorTable)
        #insert a searchbox
        self.FactorList = OWGUI.listBox(boxVal, self)
        self.FactorList.setSelectionMode(QAbstractItemView.MultiSelection)
        sle = OWGUI.lineEdit(boxVal, self, 'searchLineEdit', 'Search:')
        self.connect(sle, SIGNAL("textChanged(QString)"), self.highlightItems) 
        OWGUI.button(boxVal, self, "Select Criteria", callback = self.selectCriteria)
        self.valuesStack.addWidget(boxVal)
        self.connect(self.FactorTable, SIGNAL("itemClicked(QTableWidgetItem*)"), self.selectCriteria)
        
        # values Stack 3: row/col names
        boxVal = OWGUI.widgetBox(self, "Values", addToLayout = 0)
        self.boxIndices[3] = boxVal
        self.namesList = OWGUI.listBox(boxVal, self)
        self.namesList.setSelectionMode(QAbstractItemView.MultiSelection)
        OWGUI.button(boxVal, self, "Select Criteria", callback = self.rowcolNamesSelect)
        self.valuesStack.addWidget(boxVal)
        
        # self.summaryBox = OWGUI.widgetBox(self.controlArea, "Summary")
        # grid.addWidget(self.summaryBox, 0, 2)
        # self.criteriaOutput = QTextEdit()
        # self.summaryBox.layout().addWidget(self.criteriaOutput)
        
        
        # A box that lists the criteria for the selected attributes.
        #criteriaBox = OWGUI.widgetBox(self.controlArea, "Criteria")
        self.criteriaTable = QTableWidget()
        self.controlArea.layout().addWidget(self.criteriaTable)
        self.criteriaTable.setColumnCount(2)
        self.criteriaTable.setHorizontalHeaderLabels(['Active', 'Criteria'])
        #criteriaBox.layout().addWidget(self.criteriaTable)
        
        # tableInfoBox = OWGUI.widgetBox(self, "Table Info")
        # grid.addWidget(tableInfoBox, 1,1)
        
        
        # a box that provides functionality for processing the criteria such as a run button and others
        # functionBox = OWGUI.widgetBox(self.controlArea, "Functions")
        # grid.addWidget(functionBox, 2, 0)
        
        # try:
            # varexists1 = self.R('exists("'+self.Rvariables['result']+'")') #should trigger an exception if it doesn't exist
           
            # if varexists1:
                # self.normalize(reload = True)
            # else:
                # return
        # except:
            # pass

    def onLoadSavedSession(self):
        if self.Rvariables['result'] in self.R('ls()'):
            self.applySubsetting(reload = True)
        i = 0
        for text in self.cTableTexts:
            newitem = QTableWidgetItem(text)
            self.criteriaTable
            cw = QCheckBox()
            self.criteriaTable.setCellWidget(i, 0, cw)
            self.connect(cw, SIGNAL("toggled(bool)"), lambda val, selCri=int(self.rowselectionCriteria): self.colcriteriaActiveChange(val, selCri))
            cw.setChecked(self.rowactiveCriteria[i])
            i += 1
        self.criteriaTable.resizeColumnsToContents()
        self.criteriaTable.resizeRowsToContents()
        
        self.process(data = self.saveData)
        self.ssvAttached(data = self.ssvdata)
        
    def process(self, data):
        self.require_librarys(['fields'])
        
        if data == None:
            self.columnsorrows.clear() #clear the window for the new data
            self.selectCriteria.clear()
            self.olddata = {} #clear the old data
            self.newdata = {} #clear just in case processing fails
            self.infoa.setText('None Type Recieved')
        try:
            #self.columnsorrows.clear()
            self.Rvariables['data'] = data['data']
            self.olddata = data
            self.saveData = data
            #self.changeRowCol()
            # for v in self.rsession('colnames('+self.Rvariables['data']+')'):
                # self.columnsorrows.addItem(v)
            #(rows,cols) = self.R('dim('+self.Rvariables['data']+')')
            self.rows = self.rsession('length('+self.Rvariables['data']+'[,1])') #one day replace with a more susinct data query
            cols = self.rsession('length('+self.Rvariables['data']+'[1,])')
            self.infoa.setText("Data Connected")
            self.tableinfoa.setText("Data Connected with:")
            self.tableinfob.setText("%s columns and %s rows." % (str(cols), str(self.rows)))
        except:
            self.olddata = {}
            self.newdata = {}
            self.infoa.setText("Signal not of appropriate type.")
            self.tableinfoa.setText("No Data Connected")
            self.tableinfob.setText("")
            self.tableinfoc.setText("")
            self.tableinfod.setText("")
            return
            
        self.columnsorrows.clear() #clear the window for the new data
        if self.rows > 500:
            self.tableinfoc.setText("More than 500 rows, showing only first 500")
        if self.Rvariables['data'] != '': # this checks if data is still the default
            try: # want to see if there are rownames so that we can select on them, if they don't exist 
                self.columnsorrows.addItem("Column Names")
                if self.rows > 500:
                    rownames = self.rsession('rownames('+self.Rvariables['data']+'[1:500,])')
                    self.cycleUpButton.setEnabled(True)
                    #self.cycleDownButton.setEnabled(True)
                else:
                    rownames = self.rsession('rownames('+self.Rvariables['data']+')')
                if type(rownames) is str:
                    self.columnsorrows.addItem(rownames)
                else:
                    for item in rownames:
                        self.columnsorrows.addItem(item)
            except:
                self.infoa.setText("Rownames do not exist, showing the row numbers")
                self.RowColNamesExist = 0
                for l in xrange(int(self.rsession('length('+self.Rvariables['data']+'[,1])'))):
                    self.columnsorrows.addItem(str(l+1))
        else:
            self.infoa.setText("Data not connected.")
    
    def cycleUp(self):
        self.cycle += 1
        self.columnsorrows.clear()
        if 500*(self.cycle+1) > self.rows:
            self.cycleUpButton.setEnabled(False)
            rownames = self.rsession('rownames('+self.Rvariables['data']+'['+str((500*self.cycle)+1)+':'+str(self.rows)+',])')
        else:
            rownames = self.rsession('rownames('+self.Rvariables['data']+'['+str((500*self.cycle)+1)+':'+str(500*(self.cycle+1))+',])')
        
        
        if type(rownames) is str:
            self.columnsorrows.addItem(rownames)
        else:
            for item in rownames:
                self.columnsorrows.addItem(item)
    
    def cycleDown(self):
        self.cycle -= 1
        if self.cycle == 0:
            self.cycleDownButton.setEnabled(False) #prevents going below 0
        self.cycleUpButton.setEnabled(True) #restore cycle up if deactivated
        
        rownames = self.rsession('rownames('+self.Rvariables['data']+'['+str((500*self.cycle)+1)+':'+str(500*(self.cycle+1))+',])')
    
        if type(rownames) is str:
            self.columnsorrows.addItem(rownames)
        else:
            for item in rownames:
                self.columnsorrows.addItem(item)
    def ssvAttached(self, data):
        if 'data' in data:
            self.subOnAttachedButton.setEnabled(True)
            self.ssv = data['data']
        else:
            return
            
    def subset(self):
        h = ''
        for j in xrange(self.subsetList.count()):
            h += '"'+str(self.subsetList.item(int(j)).text())+'",'
        self.collist = h[:len(h)-1] # need to scale back 1 element in the text to remoce the trailing ,
        self.rsession(self.Rvariables['result']+'<-'+self.Rvariables['data']+'[,c('+self.collist+')]')
        self.newdata = self.olddata.copy()
        self.newdata['data'] = self.Rvariables['result']
        self.send("R DataFrame", self.newdata)
        
    def viewdf(self): # look at the first elements of the data.frame
        self.table = MyTable(self.Rvariables['data'])
        self.table.show()

 
    
    def highlightItems(self, text=''):
        if text == '':
            for item in self.FactorList.selectedItems():
                self.FactorList.setItemSelected(item, False)
        else:
            for item in self.FactorList.selectedItems():
                self.FactorList.setItemSelected(item, False)
            trueItems = self.FactorList.findItems(text, Qt.MatchContains) # a tableWidgetItem list
            for item in trueItems:
                self.FactorList.setItemSelected(item, True) 
            if len(self.FactorList.selectedItems()) > 0:
                self.FactorList.scrollToItem(self.FactorList.selectedItems()[0])
            else:
                self.infoa.setText("Item does not exist")
    
    def subListAdd(self): #want to show the summary of the factor that was selected, should account for the type of data that we are seeing
        # first get a tmp variable for the data that we are subsetting 
        try: 
            querytext = self.columnsorrows.selectedItems()[0].text()
        except: 
            return # nothing selected
        #try: #this fails if there is nothing selected in the col selector
        
        # Did we pick the names of Column Names or Row Names?
        if querytext == "Column Names": # pick the column names and populate the list
            self.valuesStack.setCurrentWidget(self.boxIndices[3])  
            self.namesList.clear()
            try:
                for names in self.rsession('colnames('+self.Rvariables['data']+')'):
                    self.namesList.addItem(names)
            except: # there is some problem with the colnames
                for i in xrange(self.rsession('length('+self.Rvariables['data']+'[1,])')):
                    self.namesList.addItem(str(i))
            self.type = 'Col Names'
            return
            
            
        # ## if we've gotten this far then the selection wasn't one of the special types
        self.setRvariableNames(['tmp'])
        # we are selecting columns based on row criteria so we need to show the row infoa
        self.rownumber = str(querytext)
        if self.RowColNamesExist:
            self.rsession(self.Rvariables['tmp']+'<-as.vector(t('+self.Rvariables['data']+'["'+self.rownumber+'",]))')
        else:
            self.rsession(self.Rvariables['tmp']+'<-as.vector(t('+self.Rvariables['data']+'['+self.rownumber+',]))')
        
        self.type = self.rsession('class('+self.Rvariables['tmp']+')')
        # start logic for what type of vector tmp is
        if self.type == 'numeric':
            self.Rplot('hist('+self.Rvariables['tmp']+')',3,3)
            self.valuesStack.setCurrentWidget(self.boxIndices[1]) #sets the correct box
            self.RstatsOutput = self.rsession('stats('+self.Rvariables['tmp']+')') #captures the output of stats
            self.rankedVals = self.rsession('sort('+self.Rvariables['tmp']+')')
            #   Use the ranks of the values to set the slider, works better than continuous data as the slider 
            self.SubSlider.setMinimum(1) 
            self.SubSlider.setMaximum(self.RstatsOutput[0][0]) # the lagging [0] is nessisary because of the subsetting of RstatsOutput
            #self.SubSlider.setTickPosition(2)
            self.StatTable.setColumnCount(2)
            self.StatTable.setRowCount(9)
            n = 0
            for item in ['Number', 'Mean', 'Stdev', 'Min', '1st Quartile', 'Median', '3rd Quartile', 'Max', 'Missing']:
                newitem = QTableWidgetItem(str(item))
                self.StatTable.setItem(n, 0, newitem)
                n += 1
            n = 0
            for k in self.RstatsOutput:
                newitem = QTableWidgetItem(str(k[0]))
                self.StatTable.setItem(n, 1, newitem)
                n += 1

        if self.type == 'factor':
            self.FactorTable.setHorizontalHeaderLabels(['Factor', 'Count'])
            self.valuesStack.setCurrentWidget(self.boxIndices[2])
            self.factorOutput = self.rsession('summary('+self.Rvariables['tmp']+')')
            self.FactorTable.setColumnCount(2)
            self.FactorTable.setRowCount(len(self.factorOutput))
            self.FactorList.clear()
            n = 0
            for k in self.factorOutput.keys():
                newitem = QTableWidgetItem(str(k))
                self.FactorTable.setItem(n, 0, newitem)
                val = QTableWidgetItem(str(self.factorOutput[k]))
                self.FactorTable.setItem(n, 1, val)
                self.FactorList.addItem(k)
                n += 1
            
    def SubSliderValueChanged(self, slidervalue):
        self.currentNum = str(self.rankedVals[slidervalue-1])
        self.numericInfo.setText('Sample Number: '+str(slidervalue)+'   Value'+self.currentNum) # the value of the slider reflects the rank value of the sample, can convert to an actual value if needed.
    
    def subOnAttached(self):
        tmpitem = self.rsession(self.ssv) #get the items to subset with
        if type(tmpitem) is str: #it's a string!!!!!!!
            items = []
            items.append(tmpitem)
        elif type(tmpitem) is list: #it's a list
            items = tmpitem
        elif type(tmpitem) is dict: #it's a dict
            items = []
            for key in tmpitem.keys():
                items.append(tmpitem['key'])
        #self.infob.setText("Subsetting on "+str(items))
            
        choices = []
        if self.type == 'factor':
            for k in self.factorOutput.keys():
                choices.append(k)
        elif self.type == 'Col Names':
            choices = self.rsession('colnames('+self.Rvariables['data']+')')
        elif self.type == 'Row Names':# row or col name selected
            choices = self.rsession('rownames('+self.Rvariables['data']+')')
                
        #self.infob.setText(str(choices))
        trues = []
        for item in items:
            if item in choices:
                trues.append(item)
            
        if len(trues) == 0:
            self.infoa.setText("No items from your list match your input.")
            return
        else:
            if self.type == 'factor':
                for selected in trues:
                    listItems = self.FactorList.findItems(selected, Qt.MatchExactly)
                    for litems in listItems:
                        self.FactorList.setItemSelected(litems, True)
                self.FactorList.scrollToItem(self.FactorList.selectedItems()[0])
                self.infoa.setText("%i of your items from a list of %i were selected." % (len(self.FactorList.selectedItems()) , len(items) ))
                return
                
            else:
                for selected in trues:
                    listItems = self.namesList.findItems(selected, Qt.MatchExactly)
                    for litems in listItems:
                        self.namesList.setItemSelected(litems, True)
                self.namesList.scrollToItem(self.namesList.selectedItems()[0])
                self.infoa.setText("%i of your items from a list of %i were selected." % (len(self.namesList.selectedItems()) , len(items) ))
        

    def rowcolNamesSelect(self):
        self.criteriaTable.setRowCount(self.colselectionCriteria+self.rowselectionCriteria+1)
        rowcolHolder = ''
        for item in self.namesList.selectedItems(): # got the items that were selected in the names list for row col selection by names
            rowcolHolder += str(item.text())+'","'
        rowcolHolderP = rowcolHolder[:len(rowcolHolder)-3]

        self.rsession('criteria'+self.vs+'rowCri'+str(self.rowselectionCriteria)+'<-colnames('+self.Rvariables['data']+') %in% c("'+rowcolHolderP+'")')
        
        self.updatecolCriteriaList(str('Column Names equal to "'+rowcolHolderP+'"')+'. Row Criteria '+str(self.rowselectionCriteria))
        self.rowselectionCriteria += 1
        
            
    def selectCriteria(self, item=None):
        self.criteriaTable.setRowCount(self.rowselectionCriteria+1)
        if self.type == 'numeric':
            if self.GorL == 0:
                self.rsession('criteria'+self.vs+'rowCri'+str(self.rowselectionCriteria)+'<-'+self.Rvariables['tmp']+' > '+self.currentNum)
                self.updatecolCriteriaList(str(self.rownumber)+' > '+str(self.currentNum)+'. Row Criteria '+str(self.rowselectionCriteria))
            if self.GorL == 1:
                self.rsession('criteria'+self.vs+'rowCri'+str(self.rowselectionCriteria)+'<-'+self.Rvariables['tmp']+' < '+self.currentNum)
                self.updatecolCriteriaList(str(self.rownumber+' < '+self.currentNum)+'. Row Criteria '+str(self.rowselectionCriteria))
        if self.type == 'factor':
            if item != None:
                self.rsession('criteria'+self.vs+'rowCri'+str(self.rowselectionCriteria)+'<-'+self.Rvariables['tmp']+' == "'+str(item.text())+'"')
                self.updatecolCriteriaList(str(self.rownumber)+' Equal To '+item.text()+'. Row Criteria '+str(self.rowselectionCriteria))
            elif item == None and len(self.FactorList.selectedItems()) != 0:
                tmpitems = ''
                for item in self.FactorList.selectedItems():
                    tmpitems += str(item.text())+'","'
                tmpitems2 = tmpitems[:len(tmpitems)-3]
                self.rsession('criteria'+self.vs+'rowCri'+str(self.rowselectionCriteria)+'<-'+self.Rvariables['tmp']+' %in% c("'+tmpitems2+'")')
                self.updatecolCriteriaList(str(self.rownumber)+' Equal To "'+tmpitems2+'". Row Criteria '+str(self.rowselectionCriteria))    
        self.rowselectionCriteria += 1
        
        #self.applySubsetting()
        

    def colcriteriaActiveChange(self, checkbox, selCri):
        if selCri < len(self.colactiveCriteria)-1 or selCri == len(self.colactiveCriteria)-1:
            self.infob.setText('Selection Criteria '+str(selCri)+' changed to '+str(checkbox))
            self.colactiveCriteria[selCri] = checkbox
        else: 
            self.colactiveCriteria.insert(selCri, checkbox)
        self.applySubsetting()
            
    def updatecolCriteriaList(self, text):
        newitem = QTableWidgetItem(text)
        self.criteriaTable.setItem(self.rowselectionCriteria, 1, newitem)
        cw = QCheckBox()
        self.criteriaTable.setCellWidget(self.rowselectionCriteria, 0, cw)
        self.connect(cw, SIGNAL("toggled(bool)"), lambda val, selCri=int(self.rowselectionCriteria): self.colcriteriaActiveChange(val, selCri))
        cw.setChecked(True)
        selCri=int(self.rowselectionCriteria)
        self.colcriteriaActiveChange(True, selCri)
        self.criteriaTable.resizeColumnsToContents()
        self.criteriaTable.resizeRowsToContents()
        self.sentalready = 0
        self.cTableTexts.append(text)
        

    
        
    def applySubsetting(self, reload = False):
        if not reload and not self.sentalready: # make the row subsetting criteria
            rcr = ''
            ccr = ''
            self.rsession('cols'+self.vs+'<-TRUE')
            if sum(self.colactiveCriteria) == 0:
                pass
            else:
                cci = 0
                for cc in self.colactiveCriteria:
                    if cc:
                        self.Rvariables['criteria'+self.vs+'rowCri'+str(cci)] = 'criteria'+self.vs+'rowCri'+str(cci)
                        ccr += 'criteria'+self.vs+'rowCri'+str(cci)+'&'
                    cci += 1
                ccrr = ccr[:len(ccr)-1]
                self.rsession('cols'+self.vs+'<-'+ccrr)
            self.rsession(self.Rvariables['result']+'<-'+self.Rvariables['data']+'[,cols'+self.vs+']')
            self.newdata = self.olddata.copy()
        self.newdata['data'] = self.Rvariables['result']
        resultclass = self.rsession('class('+self.Rvariables['result']+')')
        if resultclass == 'data.frame':
            self.rSend("R DataFrame" , self.newdata)
            self.tableinfoc.setText("Data Frame sent with:")
            cols = self.rsession('length('+self.Rvariables['result']+'[1,])')
            rows = self.rsession('length('+self.Rvariables['result']+'[,1])')
            self.tableinfod.setText("%s columns and %s rows." % (str(cols), str(rows)))
        elif resultclass == 'numeric' or resultclass == 'factor':
            
            self.rSend("Classified Vector Subset", self.newdata)
        else:
            self.infoa.setText("Send failed because of incompatable type")
            
        self.sentalready = 1
