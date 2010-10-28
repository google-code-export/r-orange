"""
<name>Create Valid Rows\Columns</name>
<tags>R</tags>
"""
from OWRpy import * 
import OWGUI 
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.widgetBox import widgetBox
class nameProtector(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None, forceInSignals = None, forceOutSignals = None):
        OWRpy.__init__(self)
        # the variables
        self.parentData = {}
        self.data = ''
        self.setRvariableNames(['nameProtector', 'newDataFromNameProtector'])
        self.inputs.addInput('id0', 'Data Frame', redRRDataFrame, self.gotDF)
        self.inputs.addInput('id1', 'Vector', redRRVector, self.gotV)

        self.outputs.addOutput('id0', 'Data Frame', redRRDataFrame)
        self.outputs.addOutput('id1', 'Vector', redRRVector)

        
        ### The data frame GUI
        self.dfbox = widgetBox(self.controlArea)
        self.nameProtectDFcheckBox = checkBox(self.dfbox, label = 'Protect the names in:', buttons = ['Rows', 'Columns'], toolTips = ['Use make.names to protect the names in the rows.', 'Use make.names to protect the names in the columns.'])
        self.namesProtectDFcomboBox = comboBox(self.dfbox, label = 'Column names to protect:')
        self.commitDFbutton = button(self.dfbox, "Commit", callback = self.dfCommit)
        
        
        
        ### The Vector GUI
        self.vbox = widgetBox(self.controlArea)
        self.vbox.hide()
        self.commitVbutton = button(self.vbox, "Commit", callback = self.vCommit)
        
    def gotDF(self, data):
        if data:
            self.parentData = data
            self.R(self.Rvariables['newDataFromNameProtector']+'<-'+data.getData())
            #newData = redRRDataFrame(data = self.Rvariables['newDataFromNameProtector'])
            self.data = self.Rvariables['newDataFromNameProtector']
            #self.data = data.getData()
            self.dfbox.show()
            self.vbox.hide()
            cols = self.R('colnames('+self.data+')', wantType = 'list')
            cols.insert(0, '') # in case you don't want to protect a column name
            self.namesProtectDFcomboBox.update(cols)
        else:
            self.parentData = {}
            self.data = ''
            self.namesProtectDFcomboBox.clear()
            
    def gotV(self, data):
        if data:
            self.parentData = data
            self.data = data.getData()
            self.dfbox.hide()
            self.vbox.show()
        else:
            self.parentData = {}
            self.data = ''
            
    def dfCommit(self):
        if self.data == '': return

        if len(self.nameProtectDFcheckBox.getChecked()) == 0 and str(self.namesProtectDFcomboBox.currentText()) == '': return # there is nothing to protect
        newData = self.parentData.copy()
        newData.data = self.Rvariables['newDataFromNameProtector']
        if 'Rows' in self.nameProtectDFcheckBox.getChecked():
            self.R('rownames('+self.data+') <- make.names(rownames('+self.data+'))')
            
        if str(self.namesProtectDFcomboBox.currentText()) != '':
            self.R(self.data+'$'+self.Rvariables['nameProtector']+'<- make.names('+self.data+'[,\''+str(self.namesProtectDFcomboBox.currentText())+'\'])')
        if 'Columns' in self.nameProtectDFcheckBox.getChecked():
            self.R('colnames('+self.data+') <- make.names(colnames('+self.data+'))')
        
        self.rSend("id0", newData)
        
    def vCommit(self): # make protected names for a vector
        if self.data == '': return
        
        self.R(self.Rvariables['nameProtector']+'<- make.names('+self.data+')')
        self.parentData['data'] = self.Rvariables['nameProtector']
        self.rSend("id1", self.parentData)
    def getReportText(self, fileDir):
        return 'Names of the incomming data were changed to fit valid names in R.\n\n'