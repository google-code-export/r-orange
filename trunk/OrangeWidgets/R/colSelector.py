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
        
        
        
        self.inputs = [("R DataFrame", RvarClasses.RDataFrame, self.process)]
        self.outputs = [("R DataFrame", RvarClasses.RDataFrame), ("Classified Subset Vector", RvarClasses.RVector)]
        
        # ###  GUI ###
        infobox = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(infobox, "Data not loaded")
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
        
        # a names box that shows the names of either the columns or the rows as well as the colnames or rownames
        namesBox = OWGUI.widgetBox(self.controlArea, "Factor Names")
        grid.addWidget(namesBox, 0, 1)
        self.columnsorrows = OWGUI.listBox(namesBox, self, callback = self.subListAdd) # Adds the selected item to the subset list
        
        # a summary box that shows the R summary of the selected row or columns
        self.summaryBox = OWGUI.widgetBox(self.controlArea, "Summary")
        grid.addWidget(self.summaryBox, 0, 2)
        self.criteriaOutput = QTextEdit()
        self.summaryBox.layout().addWidget(self.criteriaOutput)
        
        
        # A box that lists the criteria for the selected attributes.
        self.criteriaBox = OWGUI.widgetBox(self.controlArea, "Criteria")
        
        #self.criteriaBox.layout().addWidget(self.criteriaOutput)
        
        
        # a box that provides functionality for processing the criteria such as a run button and others
        functionBox = OWGUI.widgetBox(self.controlArea, "Functions")
        grid.addWidget(functionBox, 2, 0)
        
        
        
        # subsettingBox = OWGUI.widgetBox(self.controlArea, "Selected Columns")
        # grid.addWidget(subsettingBox, 1, 0)
        # self.subsetList = OWGUI.listBox(subsettingBox, self)
        # OWGUI.button(subsettingBox, self, "Clear", callback = self.subsetList.clear())
        
        # toolsBox = OWGUI.widgetBox(self.controlArea, "Tools") #some tools for aiding in the processing
        # grid.addWidget(toolsBox, 0, 1)
        # OWGUI.button(toolsBox, self, "Send", callback = self.subset) #starts the processing based on selected items
        # OWGUI.button(toolsBox, self, "View data.frame", callback = self.viewdf)
        
    # def subListAdd(self):
        # self.subsetList.addItem(str(self.columns.selectedItems()[0].text()))
        
    def process(self, data):
        self.require_librarys(['fields'])
        try:
            #self.columnsorrows.clear()
            self.Rvariable['data'] = data['data']
            self.olddata = data
            self.changeRowCol()
            # for v in self.rsession('colnames('+self.Rvariable['data']+')'):
                # self.columnsorrows.addItem(v)
        except:
            self.infoa.setText("Signal not of appropriate type.")
    
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
                    for item in self.rsession('rownames('+self.Rvariable['data']+')'):
                        self.columnsorrows.addItem(item)
                except:
                    self.infoa.setText("Rownames do not exist, showing the row numbers")
                    for l in xrange(int(self.rsession('length('+self.Rvariable['data']+'[,1])'))):
                        self.columnsorrows.addItem(str(l+1))
            if self.rowcolselect == 1: # we are selecting on rows based on columns so we need to show the columns for criteris 
                try: # want to see if there are colnames for selection  
                    for item in self.rsession('colnames('+self.Rvariable['data']+')'):
                        self.columnsorrows.addItem(item)
                except:
                    self.infoa.setText("Column names do not exist, showing the row numbers")
                    for l in xrange(int(self.rsession('length('+self.Rvariable['data']+'[1,])'))):
                        self.columnsorrows.addItem(str(l+1))
        else:
            self.infoa.setText("Data not connected.")
            
    def subListAdd(self): #want to show the summary of the factor that was selected, should account for the type of data that we are seeing
        # first get a tmp variable for the data that we are subsetting 
        try: #this fails if there is nothing selected in the col selector
            if self.rowcolselect == 0: # we are selecting columns based on row criteria so we need to show the row infoa
                rownumber = str(self.columnsorrows.selectedItems()[0].text())
                self.rsession('tmp<-as.vector('+self.Rvariable['data']+'["'+rownumber+'",])')
            if self.rowcolselect == 1:
                colnames = str(self.columnsorrows.selectedItems()[0].text())
                self.rsession('tmp<-as.vector('+self.Rvariable['data']+'[,"'+colnames+'"])')
            self.rsession('txt<-paste(capture.output(stats(tmp)), collapse = "\n")')
            Rsummary = self.rsession('paste("<pre>", txt, "</pre>")')
            self.criteriaOutput.setHtml(Rsummary)
        except: return
# from rpy_options import set_options
# set_options(RHOME=os.environ['RPATH'])
# from rpy import *
# from OWWidget import *
        
        
# class MyTable(QTableWidget):
    # def __init__(self, dataframe, *args):
        # QTableWidget.__init__(self, *args)
        #OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        # self.dataframename = dataframe
        # self.headers = r('colnames('+self.dataframename+')')
        # self.dataframe = r(self.dataframename)
        # self.setColumnCount(len(self.headers))
        # self.setRowCount(len(self.dataframe[self.headers[0]]))
        # n=0
        # for key in self.headers:
            # m=0
            # for item in self.dataframe[key]:
                # newitem = QTableWidgetItem(str(item))
                # self.setItem(m,n,newitem)
                # m += 1
            # n += 1
        # self.setHorizontalHeaderLabels(self.headers)