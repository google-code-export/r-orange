"""
<name>Row Filtering</name>
<tags>Subsetting</tags>
<icon>filter.png</icon>
"""

from OWRpy import *
import redRGUI
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.signalClasses.RVector import RVector as redRRVector


from libraries.base.qtWidgets.filterTable import filterTable
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.checkBox import checkBox as redRCheckBox

class rowFilter(OWRpy):
    globalSettingsList = ['commitOnInput']
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
        self.inputs.addInput('id0', 'Data Table', redRRDataFrame, self.processData)
 
        self.outputs.addOutput('id0', 'Data Table', redRRDataFrame)

        
        ######## GUI ############
        
        self.tableArea = widgetBox(self.controlArea)
        self.table = filterTable(self.controlArea, sortable=True,
        filterable=True,selectionMode = QAbstractItemView.NoSelection,onFilterCallback=self.onFilter)
        
        self.commitOnInput = redRCheckBox(self.bottomAreaRight, buttons = ['Commit on Filter'],
        toolTips = ['On filter send data forward.'])
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitSubset)
        
    def processData(self, data):
        if not data: 
            self.table.clear()
            return
        self.dataParent = data

        self.data  = data.getData()
        self.table.setRTable(self.data)
        
    def onFilter(self):
        # print '############################ onFilter'
        if 'Commit on Filter' in self.commitOnInput.getChecked():
            self.commitSubset()

    def commitSubset(self):
        filteredData = self.table.getFilteredData()
        newData = redRRDataFrame(data = filteredData, parent = self.dataParent.getData())

        self.rSend('id0', newData)
   
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