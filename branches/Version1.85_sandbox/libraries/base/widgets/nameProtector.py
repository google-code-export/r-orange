"""
<name>Create Valid Rows\Columns</name>
<tags>R</tags>
"""
from OWRpy import * 
import redRGUI, signals
import OWGUI 
import redRi18n
_ = redRi18n.get_(package = 'base')
class nameProtector(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        # the variables
        self.parentData = {}
        self.data = ''
        self.setRvariableNames(['nameProtector', 'newDataFromNameProtector'])
        self.inputs.addInput('id0', _('Data Frame'), signals.base.RDataFrame, self.gotDF)
        self.inputs.addInput('id1', _('Vector'), signals.base.RVector, self.gotV)

        self.outputs.addOutput('id0', _('Data Frame'), signals.base.RDataFrame)
        self.outputs.addOutput('id1', _('Vector'), signals.base.RVector)

        
        ### The data frame GUI
        self.dfbox = redRGUI.base.widgetBox(self.controlArea)
        self.nameProtectDFcheckBox = redRGUI.base.checkBox(self.dfbox, label = _('Protect the names in:'), 
        buttons = [_('Rows'), _('Columns')], toolTips = [_('Use make.names to protect the names in the rows.'), 
        _('Use make.names to protect the names in the columns.')])
        self.namesProtectDFcomboBox = redRGUI.base.comboBox(self.dfbox, label = _('Column names to protect:'))
        self.commit =redRGUI.base.commitButton(self.dfbox, _("Commit"), callback = self.dfCommit,processOnInput=True)
        
        
        self.newRowNames = redRGUI.base.lineEdit(self.dfbox, label = _('Custom Row Names'), toolTip = _('Set new custom names for the rows.'))
        self.newColumnNames = redRGUI.base.lineEdit(self.dfbox, label = _('Custom Column Names'), toolTip = _('Set new custom names for the columns'))
        self.commitNewNames = redRGUI.base.commitButton(self.dfbox, label = _('Commit Custom'), callback = self.commitNewNames)
        
        
        
        ### The Vector GUI
        self.vbox = redRGUI.base.widgetBox(self.controlArea)
        self.vbox.hide()
        self.commitVbutton = redRGUI.base.button(self.vbox, _("Commit"), callback = self.vCommit,alignment=Qt.AlignRight)
        
    def gotDF(self, data):
        if data:
            self.parentData = data
            self.R(self.Rvariables['newDataFromNameProtector']+'<-'+data.getData(), wantType = 'NoConversion')
            #newData = signals.base.RDataFrame(data = self.Rvariables['newDataFromNameProtector'])
            self.data = self.Rvariables['newDataFromNameProtector']
            #self.data = data.getData()
            self.dfbox.show()
            self.vbox.hide()
            cols = self.R('colnames('+self.data+')', wantType = 'list')
            cols.insert(0, '') # in case you don't want to protect a column name
            self.namesProtectDFcomboBox.update(cols)
            rowNames = self.R('rownames(%s)' % self.data, wantType = 'list')
            colNames = self.R('colnames(%s)' % self.data, wantType = 'list')
            self.newRowNames.setText(','.join(rowNames))
            self.newColumnNames.setText(','.join(colNames))
            if self.commit.processOnInput():
                self.dfCommit()
        else:
            self.parentData = {}
            self.data = ''
            self.namesProtectDFcomboBox.clear()
            
    def gotV(self, data):
        if data:
            self.parentData = data
            self.data = self.Rvariables['newDataFromNameProtector']
            self.dfbox.hide()
            self.vbox.show()
            if self.commit.processOnInput():
                self.vCommit()

        else:
            self.parentData = {}
            self.data = ''
            
    def dfCommit(self):
        if self.data == '': return

        if len(self.nameProtectDFcheckBox.getChecked()) == 0 and unicode(self.namesProtectDFcomboBox.currentText()) == '': return # there is nothing to protect
        if 'Rows' in self.nameProtectDFcheckBox.getChecked():
            self.R('rownames('+self.data+') <- make.names(rownames('+self.data+'))', wantType = 'NoConversion')
            
        if unicode(self.namesProtectDFcomboBox.currentText()) != '':
            self.R(self.data+'$'+self.Rvariables['nameProtector']+'<- make.names('+self.data+'[,\''+unicode(self.namesProtectDFcomboBox.currentText())+'\'])', wantType = 'NoConversion')
        if 'Columns' in self.nameProtectDFcheckBox.getChecked():
            self.R('colnames('+self.data+') <- make.names(colnames('+self.data+'))', wantType = 'NoConversion')
        newData = signals.base.RDataFrame(self, data = self.Rvariables['newDataFromNameProtector'])
        self.rSend("id0", newData)
    def commitNewNames(self):
        ## reset the names to those listed in the line Edits
        self.R('rownames(%s)<-c(\"%s\")' % (self.data, '\",\"'.join([i.strip() for i in unicode(self.newRowNames.text()).split(',')])), wantType = 'NoConversion')
        self.R('colnames(%s)<-c(\"%s\")' % (self.data, '\",\"'.join([i.strip() for i in unicode(self.newColumnNames.text()).split(',')])), wantType = 'NoConversion')
        newData = signals.base.RDataFrame(self, data = self.Rvariables['newDataFromNameProtector'])
        self.rSend("id0", newData)
    def vCommit(self): # make protected names for a vector
        if self.data == '': return
        
        self.R(self.Rvariables['nameProtector']+'<- make.names('+self.data+')', wantType = 'NoConversion')
        newData = signals.base.RVector(self, data = self.Rvariables['nameProtector'])
        self.rSend("id1", newData)