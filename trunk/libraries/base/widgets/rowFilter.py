"""
<name>Row Filtering 2</name>
<description>Shows data in a spreadsheet.  The data can be subset and passed to other widgets.</description>
<tags>Data Visualization, Subsetting</tags>
<RFunctions>base:data.frame,base:matrix</RFunctions>
<icon>filter.png</icon>
<author>Kyle R Covington and Anup Parikh</author>
"""

from OWRpy import *
import redRGUI
import libraries.base.signalClasses.RDataFrame as rdf
import libraries.base.signalClasses.RVector as RVector


from libraries.base.qtWidgets.filterTable import filterTable
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.widgetBox import widgetBox
class rowFilter(OWRpy):
    settingsList = []
    def __init__(self, parent=None, signalManager = None):
        OWRpy.__init__(self)
        self.data = None
        self.orriginalData = '' # a holder for data that we get from a connection
        self.currentDataTransformation = '' # holder for data transformations ex: ((data[1:5,])[,1:3])[1:2,]
        self.dataParent = None
        
        self.currentRow = 0
        self.currentColumn = 0
        self.rowNameSelectionCriteria = ''
        self.criteriaList = {}
        
        self.setRvariableNames(['dataExplorer'])
        self.criteriaDialogList = []
        self.inputs = [('Data Table', rdf.RDataFrame, self.processData)] 
        self.outputs = [('Data Subset', rdf.RDataFrame)]
        
        ######## GUI ############
        
        self.tableArea = widgetBox(self.controlArea)
        
        #############################
        # self.R('data <- data.frame(a=c("a","b","c","d","e"),b=as.factor(1:5000),c=as.character(c("a","b","c","d","e")))')
       
        # self.R('data <- iris')
        
        # self.R('data$c <- as.character(data$Species)')
        # self.data = 'data'
        # self.table = filterTable(self.tableArea,sortable=True, Rdata='data')
        #############################
        self.table = filterTable(self.controlArea, sortable=True,
        filterable=True,selectionMode = QAbstractItemView.NoSelection )

        button(self.bottomAreaRight, "Commit Subsetting", callback = self.commitSubset)
        self.dimsInfoArea = widgetLabel(self.bottomAreaCenter, '')
        
    def processData(self, data):
        if not data: 
            self.table.clear()
            return
        self.dataParent = data

        self.data  = data.getData()
        self.table.setRTable(self.data)
        
    def commitSubset(self):
        filteredData = self.table.getFilteredData()
        newData = rdf.RDataFrame(data = filteredData, parent = self.dataParent.getData())

        self.rSend('Data Subset', newData)

    def saveCustomSettings(self):
        ## make a dict of settings for each of the dialogs.  These will be reloaded on reload.
        
        settings = []
        for i in self.criteriaDialogList:
            settings.append({'criteriaCollection':i['criteriaCollection'], 'colname':i['colname']})
            
        return settings
    def loadCustomSettings(self,settings=None):
        # custom function for reloading the widget
        print 'Loading Custom Settings for DataExplorer'
        # process the data again
        if self.dataParent != None:
            print 'Processing Data Parent'
            self.processData(self.dataParent) # this sets the criteriaDialogList and the widget, I'll think of a smarter way of doing this...
            print 'Done processing the parent, everything should be ready to process the criteria'
            if settings:
                for i in settings:
                    for d in self.criteriaDialogList:
                        if d['colname'] == i['colname']:
                            d['criteriaCollection'] = i['criteriaCollection']
                            d['widgetLabel'].setHtml('<pre>'+i['criteriaCollection']+'</pre>')
                            print 'Setting ', d['colname'], 'to ', i['criteriaCollection']
                self.commitCriteriaDialog()
                print 'Previously Committed data has been displayed.'
        # pass
    def customCloseEvent(self):
        pass
    def deleteWidget(self):
        pass
        
    def getReportText(self, fileDir):
        return 'Data was examined and possibly subset based on some Column Critera.  Please see the Red-R .rrs file or the included notes for more information on this subsetting.\n\n'