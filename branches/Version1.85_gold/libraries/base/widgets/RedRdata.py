"""
<name>R Datasets</name>
<tags>Data Input</tags>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
import redRi18n
_ = redRi18n.get_(package = 'base')
class RedRdata(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(['datasets',"data"])
        self.data = {}
        self.outputs.addOutput('id0', _('Example Data'), signals.base.RDataFrame)
        self.outputs.addOutput('id1', _('Example Data (Matrix)'), signals.base.RMatrix)
        self.outputs.addOutput('id2', _('Example Data (Arbitrary Example [Advanced])'), 'All')

                
        self.R('%s <- as.data.frame(data(package = .packages())$results[,c(1,3:4)])' % self.Rvariables['datasets'],silent=True, wantType = 'NoConversion')
        self.R('%s$Title <- as.character(%s$Title)' % (self.Rvariables['datasets'],self.Rvariables['datasets']),silent=True, wantType = 'NoConversion')
        
        
        self.table = redRGUI.base.filterTable(self.controlArea, label='R Datasets', includeInReports=False,
        Rdata = self.Rvariables['datasets'], sortable=True,
        filterable=True,selectionMode = QAbstractItemView.SingleSelection, callback=self.selectDataSet)


        box = redRGUI.base.groupBox(self.controlArea,orientation='horizontal', margin=16)
        self.controlArea.layout().setAlignment(box,Qt.AlignHCenter)
        # the package does not need to be loaded to get its datasets
        self.package = redRGUI.base.lineEdit(box, label = _('Package:'), text = '')#, callback = self.loadPackage)
        redRGUI.base.button(box, label = 'Load Package', callback = self.loadPackage)
        self.RFunctionParamdataName_lineEdit = redRGUI.base.lineEdit(box, label = _("Data Name:"), 
        text = '', callback = self.commitFunction)
        
        self.commit = redRGUI.base.commitButton(box, _("Commit"), callback = self.commitFunction,
        processOnChange=True, orientation='vertical')
    
    def loadPackage(self):
        if unicode(self.package.text()) != '':
            self.require_librarys([unicode(self.package.text())])
        self.R('%s <- as.data.frame(data(package = .packages())$results[,c(1,3:4)])' % self.Rvariables['datasets'],silent=True, wantType = 'NoConversion')
        self.R('%s$Title <- as.character(%s$Title)' % (self.Rvariables['datasets'],self.Rvariables['datasets']),silent=True, wantType = 'NoConversion')
        self.table.setRTable(self.Rvariables['datasets'])
        
    
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
        if self.commit.processOnChange():
            self.commitFunction()
        
    def commitFunction(self):
        package = self.package.text()
        dataset = unicode(self.RFunctionParamdataName_lineEdit.text())
        if package == '' or dataset == '':
            return
        # the package does not need to be loaded to get its datasets
        # self.loadPackage()
        self.R('data("%s", package="%s")' % (dataset,package), wantType = 'NoConversion')
        try:
            if self.R('is.data.frame(%s)' % dataset, wantType = 'convert'):
                newData = signals.base.RDataFrame(self, data = unicode(self.RFunctionParamdataName_lineEdit.text()))
                self.rSend("id0", newData)
            elif self.R('is.matrix(%s)' % dataset, wantType = 'convert'):
                newData = signals.base.RMatrix(self, data = unicode(self.RFunctionParamdataName_lineEdit.text()))
                self.rSend('id1', newData)
            else:
                newData = signals.base.RVariable(self, data = unicode(self.RFunctionParamdataName_lineEdit.text()))
                self.rSend('id2', newData)
        except Exception as inst:
            QMessageBox.information(self, _('Red-R Canvas'),_('R Error: %s') % unicode(inst),  
            QMessageBox.Ok + QMessageBox.Default)

        
        
