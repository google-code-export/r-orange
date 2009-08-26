"""
<name>Subset</name>
<description>Subsets a data.frame object to pass to subsequent widgets.</description>
<icon>icons/Subset.png</icon>
<priority>3020</priority>
"""

from OWRpy import *
import OWGUI

class colSelector(OWRpy): # a simple widget that actually will become quite complex.  We want to do several things, give into about the variables that are selected (do a summary on the attributes and show them to the user) and to pass forward both a subsetted data.frame or a vector for classification for things evaluating TRUE to the subsetting
    settingsList = ['vs', 'rowcolselect']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        
        self.vs = self.variable_suffix
        self.Rvariable = {'data':'', 'result':'ssresult'+self.vs}
        self.collist = '' # a container for the names of columns that will be picked from the selector.
        self.rowcolselect = 1
        self.GorL = 0
        self.rowselectionCriteria = 0 # Counters for the criteria of selecting Rows and Cols
        self.colselectionCriteria = 0 
        self.rowactiveCriteria = [] # lists showing the active critera for subsetting the rows and cols
        self.colactiveCriteria = []
        self.RowColNamesExist = 1
        
        
        
        self.inputs = [("R DataFrame", RvarClasses.RDataFrame, self.process)]
        self.outputs = [("R DataFrame", RvarClasses.RDataFrame), ("Classified Subset Vector", RvarClasses.RVector)]
        
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
        self.rowcol = OWGUI.radioButtonsInBox(options, self, "rowcolselect", ["Rows", "Columns"], callback = self.changeRowCol)
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

    def process(self, data):
        self.require_librarys(['fields'])
        try:
            #self.columnsorrows.clear()
            self.Rvariable['data'] = data['data']
            self.olddata = data
            self.changeRowCol()
            # for v in self.rsession('colnames('+self.Rvariable['data']+')'):
                # self.columnsorrows.addItem(v)
            rows = self.rsession('length('+self.Rvariable['data']+'[,1])')
            cols = self.rsession('length('+self.Rvariable['data']+'[1,])')
            self.infoa.setText("Data Connected")
            self.tableinfoa.setText("Data Connected with:")
            self.tableinfob.setText("%s columns and %s rows." % (str(cols), str(rows)))
        except:
            self.infoa.setText("Signal not of appropriate type.")
            self.tableinfoa.setText("No Data Connected")
            self.tableinfob.setText("")
            self.tableinfoc.setText("")
            self.tableinfod.setText("")
    
    def subset(self):
        h = ''
        for j in xrange(self.subsetList.count()):
            h += '"'+str(self.subsetList.item(int(j)).text())+'",'
        self.collist = h[:len(h)-1] # need to scale back 1 element in the text to remoce the trailing ,
        self.rsession(self.Rvariable['result']+'<-'+self.Rvariable['data']+'[,c('+self.collist+')]')
        self.newdata = self.olddata.copy()
        self.newdata['data'] = self.Rvariable['result']
        self.send("R DataFrame", self.newdata)
        
    def viewdf(self): # look at the first elements of the data.frame
        self.table = MyTable(self.Rvariable['data'])
        self.table.show()

    def changeRowCol(self): # there has been a change to the RowCol selection and we need to now populate the Row or col 
        self.columnsorrows.clear() #clear the window for the new data
        if self.Rvariable['data'] != '': # this checks if data is still the default
            if self.rowcolselect == 0: # we are selecting columns based on row criteria so we need to show the row infoa
                try: # want to see if there are rownames so that we can select on them, if they don't exist 
                    self.columnsorrows.addItem("Column Names")
                    for item in self.rsession('rownames('+self.Rvariable['data']+')'):
                        self.columnsorrows.addItem(item)
                except:
                    self.infoa.setText("Rownames do not exist, showing the row numbers")
                    self.RowColNamesExist = 0
                    for l in xrange(int(self.rsession('length('+self.Rvariable['data']+'[,1])'))):
                        self.columnsorrows.addItem(str(l+1))
            if self.rowcolselect == 1: # we are selecting on rows based on columns so we need to show the columns for criteris 
                try: # want to see if there are colnames for selection 
                    self.columnsorrows.addItem("Row Names")
                    for item in self.rsession('colnames('+self.Rvariable['data']+')'):
                        self.columnsorrows.addItem(item)
                except:
                    self.infoa.setText("Column names do not exist, showing the row numbers")
                    self.RowColNamesExist = 0
                    for l in xrange(int(self.rsession('length('+self.Rvariable['data']+'[1,])'))):
                        self.columnsorrows.addItem(str(l+1))
        else:
            self.infoa.setText("Data not connected.")
            
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
                for names in self.rsession('colnames('+self.Rvariable['data']+')'):
                    self.namesList.addItem(names)
            except: # there is some problem with the colnames
                for i in xrange(self.rsession('length('+self.Rvariable['data']+'[1,])')):
                    self.namesList.addItem(str(i))
        if querytext == "Row Names":
            self.valuesStack.setCurrentWidget(self.boxIndices[3]) 
            self.namesList.clear()
            try:
                for names in self.rsession('rownames('+self.Rvariable['data']+')'):
                    self.namesList.addItem(names)
            except:
                for i in xrange(self.rsession('length('+self.Rvariable['data']+'[,1])')):
                    self.namesList.addItem(str(i))
        if self.rowcolselect == 0: # we are selecting columns based on row criteria so we need to show the row infoa
            self.rownumber = str(querytext)
            if self.RowColNamesExist:
                self.rsession('tmp<-'+self.Rvariable['data']+'["'+self.rownumber+'",]')
            else:
                self.rsession('tmp<-'+self.Rvariable['data']+'['+self.rownumber+',]')
        if self.rowcolselect == 1:
            self.colnames = str(querytext)
            if self.RowColNamesExist:
                self.rsession('tmp<-'+self.Rvariable['data']+'[,"'+self.colnames+'"]')
            else:
                self.rsession('tmp<-'+self.Rvariable['data']+'[,'+self.colnames+']')
        self.type = self.rsession('class(tmp)')
        # start logic for what type of vector tmp is
        if self.type == 'numeric':
            self.Rplot('hist(tmp)')
            self.valuesStack.setCurrentWidget(self.boxIndices[1]) #sets the correct box
            self.RstatsOutput = self.rsession('stats(tmp)') #captures the output of stats
            self.rankedVals = self.rsession('sort(tmp)')
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
            factorOutput = self.rsession('summary(tmp)')
            self.FactorTable.setColumnCount(2)
            self.FactorTable.setRowCount(len(factorOutput))
            n = 0
            for k in factorOutput.keys():
                newitem = QTableWidgetItem(str(k))
                self.FactorTable.setItem(n, 0, newitem)
                val = QTableWidgetItem(str(factorOutput[k]))
                self.FactorTable.setItem(n, 1, val)
                n += 1
            
    def SubSliderValueChanged(self, slidervalue):
        self.currentNum = str(self.rankedVals[slidervalue-1])
        self.numericInfo.setText('Sample Number: '+str(slidervalue)+'   Value'+self.currentNum) # the value of the slider reflects the rank value of the sample, can convert to an actual value if needed.
    
    def rowcolNamesSelect(self):
        self.criteriaTable.setRowCount(self.colselectionCriteria+self.rowselectionCriteria+1)
        rowcolHolder = ''
        for item in self.namesList.selectedItems(): # got the items that were selected in the names list for row col selection by names
            rowcolHolder += str(item.text())+'","'
        rowcolHolderP = rowcolHolder[:len(rowcolHolder)-3]
        if self.rowcolselect == 0:
            self.rsession('criteria'+self.vs+'rowCri'+str(self.rowselectionCriteria)+'<-colnames('+self.Rvariable['data']+') %in% c("'+rowcolHolderP+'")')
            
            self.updatecolCriteriaList(str('Column Names equal to "'+rowcolHolderP+'"')+'. Row Criteria '+str(self.rowselectionCriteria))
            self.rowselectionCriteria += 1
        if self.rowcolselect == 1:
            self.rsession('criteria'+self.vs+'colCri'+str(self.colselectionCriteria)+'<-rownames('+self.Rvariable['data']+') %in% c("'+rowcolHolderP+'")')
            
            self.updaterowCriteriaList(str('Row Names equal to "'+rowcolHolderP+'"')+'. Column Criteria '+str(self.colselectionCriteria))
            self.colselectionCriteria += 1
        
            
    def selectCriteria(self, item=None):
        self.criteriaTable.setRowCount(self.colselectionCriteria+self.rowselectionCriteria+1)
        if self.rowcolselect == 0:
            if self.type == 'numeric':
                if self.GorL == 0:
                    self.rsession('criteria'+self.vs+'rowCri'+str(self.rowselectionCriteria)+'<-tmp > '+self.currentNum)
                    self.updatecolCriteriaList(str(self.colnames)+' > '+str(self.currentNum)+'. Row Criteria '+str(self.rowselectionCriteria))
                if self.GorL == 1:
                    self.rsession('criteria'+self.vs+'rowCri'+str(self.rowselectionCriteria)+'<-tmp < '+self.currentNum)
                    self.updatecolCriteriaList(str(self.colnames+' < '+self.currentNum)+'. Row Criteria '+str(self.rowselectionCriteria))
            if self.type == 'factor':
                self.rsession('criteria'+self.vs+'rowCri'+str(self.rowselectionCriteria)+'<-tmp == "'+str(item.text())+'"')
                self.updatecolCriteriaList(str(self.colnames)+' Equal To '+item.text()+'. Row Criteria '+str(self.rowselectionCriteria))
            self.rowselectionCriteria += 1
        if self.rowcolselect == 1:
            if self.type == 'numeric':
                if self.GorL == 0:
                    self.rsession('criteria'+self.vs+'colCri'+str(self.colselectionCriteria)+'<-tmp > '+self.currentNum)
                    self.updaterowCriteriaList(str(self.colnames+' > '+self.currentNum)+'. Column Criteria '+str(self.colselectionCriteria))
                if self.GorL == 1:
                    self.rsession('criteria'+self.vs+'colCri'+str(self.colselectionCriteria)+'<-tmp < '+self.currentNum)
                    self.updaterowCriteriaList(str(self.colnames+' < '+self.currentNum)+'. Column Criteria '+str(self.colselectionCriteria))
            if self.type == 'factor':
                self.rsession('criteria'+self.vs+'colCri'+str(self.colselectionCriteria)+'<-tmp == "'+str(item.text())+'"')
                self.updaterowCriteriaList(str(self.colnames+' Equal To '+item.text())+'. Column Criteria '+str(self.colselectionCriteria))
            self.colselectionCriteria += 1
        #self.applySubsetting()
        
    def rowcriteriaActiveChange(self, checkbox, selCri):
        if selCri < len(self.rowactiveCriteria)-1 or selCri == len(self.rowactiveCriteria)-1:
            self.infob.setText('Selection Criteria '+str(selCri)+' changed to '+str(checkbox))
            self.rowactiveCriteria[selCri] = checkbox
        else:
            self.rowactiveCriteria.insert(selCri, checkbox)
        self.applySubsetting()
        
    def colcriteriaActiveChange(self, checkbox, selCri):
        if selCri < len(self.colactiveCriteria)-1 or selCri == len(self.colactiveCriteria)-1:
            self.infob.setText('Selection Criteria '+str(selCri)+' changed to '+str(checkbox))
            self.colactiveCriteria[selCri] = checkbox
        else: 
            self.colactiveCriteria.insert(selCri, checkbox)
        self.applySubsetting()
    
    def updaterowCriteriaList(self, text):
        newitem = QTableWidgetItem(text)
        self.criteriaTable.setItem(self.rowselectionCriteria + self.colselectionCriteria, 1, newitem)
        cw = QCheckBox()
        self.criteriaTable.setCellWidget(self.rowselectionCriteria + self.colselectionCriteria, 0, cw)
        self.connect(cw, SIGNAL("toggled(bool)"), lambda val, selCri=int(self.colselectionCriteria): self.rowcriteriaActiveChange(val, selCri))
        cw.setChecked(True)
        selCri=int(self.colselectionCriteria)
        self.rowcriteriaActiveChange(True, selCri)
        self.criteriaTable.resizeColumnsToContents()
        self.criteriaTable.resizeRowsToContents()
    
    def updatecolCriteriaList(self, text):
        newitem = QTableWidgetItem(text)
        self.criteriaTable.setItem(self.rowselectionCriteria + self.colselectionCriteria, 1, newitem)
        cw = QCheckBox()
        self.criteriaTable.setCellWidget(self.rowselectionCriteria + self.colselectionCriteria, 0, cw)
        self.connect(cw, SIGNAL("toggled(bool)"), lambda val, selCri=int(self.rowselectionCriteria): self.colcriteriaActiveChange(val, selCri))
        cw.setChecked(True)
        selCri=int(self.rowselectionCriteria)
        self.colcriteriaActiveChange(True, selCri)
        self.criteriaTable.resizeColumnsToContents()
        self.criteriaTable.resizeRowsToContents()
        
    def applySubsetting(self):
        # make the row subsetting criteria
        rcr = ''
        ccr = ''
        self.rsession('rows'+self.vs+'<-TRUE')
        self.rsession('cols'+self.vs+'<-TRUE')
        if sum(self.rowactiveCriteria) == 0: #there aren't any active criteria  
            pass
        else:
            rci = 0
            for rc in self.rowactiveCriteria:
                if rc: #check to see if active
                    rcr += 'criteria'+self.vs+'colCri'+str(rci)+'&'
                rci += 1
            rcrr = rcr[:len(rcr)-1]
            self.rsession('rows'+self.vs+'<-'+rcrr)
            #self.numericInfo.setText(str(self.rowactiveCriteria))
        if sum(self.colactiveCriteria) == 0:
            pass
        else:
            cci = 0
            for cc in self.colactiveCriteria:
                if cc:
                    ccr += 'criteria'+self.vs+'rowCri'+str(cci)+'&'
                cci += 1
            ccrr = ccr[:len(ccr)-1]
            self.rsession('cols'+self.vs+'<-'+ccrr)
        self.rsession(self.Rvariable['result']+'<-'+self.Rvariable['data']+'[rows'+self.vs+',cols'+self.vs+']')
        resultclass = self.rsession('class('+self.Rvariable['result']+')')
        if resultclass == 'data.frame':
            self.rSend("R DataFrame" ,{'data':self.Rvariable['result']})
            self.tableinfoc.setText("Data Frame sent with:")
            cols = self.rsession('length('+self.Rvariable['result']+'[1,])')
            rows = self.rsession('length('+self.Rvariable['result']+'[,1])')
            self.tableinfod.setText("%s columns and %s rows." % (str(cols), str(rows)))
        elif resultclass == 'numeric' or resultclass == 'factor':
            self.rSend("Classified Vector Subset", {'data':self.Rvariable['result']})
        else:
            self.infoa.setText("Send failed because of incompatable type")
                    
    # def testme(self, item=None):
        # self.infoa.setText(item.text())
        # self.rsession('criteria'+self.vs+'colCri'+str(self.colselectionCriteria)+'<-tmp == "'+str(item.text())+'"')
        # make the column subsetting criteria