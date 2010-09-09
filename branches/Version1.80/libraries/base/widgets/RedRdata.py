"""
<name>R Datasets</name>
<author>Red-R Core Development Team</author>
<description>Loads data from R into Red-R.  This widget allows access to example data from within R and is useful when testing schemas or widgets to ensure that they are working as indicated in R documentation.  Novice users may also find this widget useful for exploring widget functionality when they have no data of their own to explore.</description>
<RFunctions>base:data</RFunctions>
<tags>Data Input</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.qtWidgets.filterTable import filterTable
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.button import button

class RedRdata(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(['datasets',"data"])
        self.data = {}
        self.outputs.addOutput('id0', 'data Output', redRRDataFrame)

                
        self.R('%s <- as.data.frame(data(package = .packages(all.available = TRUE))$results[,c(1,3:4)])' % self.Rvariables['datasets'],silent=True)
        self.R('%s$Title <- as.character(%s$Title)' % (self.Rvariables['datasets'],self.Rvariables['datasets']),silent=True)
        
        
        self.table = filterTable(self.controlArea,Rdata = self.Rvariables['datasets'], sortable=True,
        filterable=True,selectionMode = QAbstractItemView.SingleSelection, callback=self.selectDataSet)


        box = groupBox(self.controlArea,orientation='horizontal', margin=16)
        self.controlArea.layout().setAlignment(box,Qt.AlignHCenter)
        # the package does not need to be loaded to get its datasets
        self.package = lineEdit(box, label = 'Package:', text = '')#, callback = self.loadPackage)
        self.RFunctionParamdataName_lineEdit = lineEdit(box, label = "Data Name:", 
        text = '', callback = self.commitFunction)
        redRCommitButton(box, "Commit", callback = self.commitFunction)
    def loadPackage(self):
        if str(self.package.text()) != '':
            self.require_librarys([str(self.package.text())])
        
    
    def selectDataSet(self,ind):
        #ind.row()
        #print self.table.table.rowAt(ind.row())
        # package = self.R('%s$Package[%d]' % (self.Rvariables['datasets'],ind.row()+1),silent=True)
        # dataset = self.R('%s$Item[%d]' % (self.Rvariables['datasets'],ind.row()+1),silent=True)
        package = self.table.getData(ind.row(),0)
        dataset = self.table.getData(ind.row(),1)
        import re
        m = re.search('\((.*)\)',dataset)
        # print m
        if m: dataset = m.group(1)
        
        self.package.setText(package)
        self.RFunctionParamdataName_lineEdit.setText(dataset)
        
    def commitFunction(self):
        package = self.package.text()
        dataset = str(self.RFunctionParamdataName_lineEdit.text())
        if package == '' or dataset == '':
            return
        # the package does not need to be loaded to get its datasets
        # self.loadPackage()
        self.R('data("%s", package="%s")' % (dataset,package))
        try:
            newData = redRRDataFrame(data = 'as.data.frame(' + str(self.RFunctionParamdataName_lineEdit.text() + ')'))
            self.rSend("id0", newData)            
        except RuntimeError as inst:
            QMessageBox.information(self, 'Red-R Canvas','R Error: '+ str(inst),  
            QMessageBox.Ok + QMessageBox.Default)

        
        
