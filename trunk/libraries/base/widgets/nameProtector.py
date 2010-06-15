"""
<name>Rename Rows or Columns</name>
<discription>R does not handle attachment of column names that begin with integers.  This is usually handled by R functions that read in data however some precompiled data escapes this protection.</discription>
<author>Kyle R. Covington</author>
<tags>R</tags>
<RFunctions>base:make.names</RFunctions>
<icon>RExecutor.PNG</icon>
<priority>4010</priority>
"""
from OWRpy import * 
import OWGUI 
class nameProtector(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None, forceInSignals = None, forceOutSignals = None):
        OWRpy.__init__(self, parent, signalManager, "Name Protector", wantMainArea = 0, resizingEnabled = 1)
        # the variables
        self.parentData = {}
        self.data = ''
        self.setRvariableNames(['nameProtector', 'newDataFromNameProtector', 'newDataFromNameProtector_cm'])
        self.inputs = [("Data Frame", rdf.RDataFrame, self.gotDF), ("Vector", signals.RVector, self.gotV)]
        self.outputs = [("Data Frame", rdf.RDataFrame), ("Vector", signals.RVector)]
        
        ### The data frame GUI
        self.dfbox = redRGUI.widgetBox(self.controlArea)
        self.newDataDFcheckBox = redRGUI.checkBox(self.dfbox, buttons = ['Make New Data Object'], toolTips = ['Makes a new data object instead of replacing the data in the old one'])
        self.newDataDFcheckBox.setChecked(['Make New Data Object'])
        self.nameProtectDFcheckBox = redRGUI.checkBox(self.dfbox, label = 'Protect the names in:', buttons = ['Rows', 'Columns'], toolTips = ['Use make.names to protect the names in the rows.', 'Use make.names to protect the names in the columns.'])
        self.namesProtectDFcomboBox = redRGUI.comboBox(self.dfbox, label = 'Column names to protect:')
        self.commitDFbutton = redRGUI.button(self.dfbox, "Commit", callback = self.dfCommit)
        
        
        
        ### The Vector GUI
        self.vbox = redRGUI.widgetBox(self.controlArea)
        self.vbox.hide()
        self.commitVbutton = redRGUI.button(self.vbox, "Commit", callback = self.vCommit)
        
    def gotDF(self, data):
        if data:
            self.parentData = data
            self.data = data.getData()
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
        if 'Make New Data Object' in self.newDataDFcheckBox.getChecked():
            
            
            self.R(self.Rvariables['newDataFromNameProtector']+'<-'+newData.getData())
            newData = rdf.RDataFrame(data = self.Rvariables['newDataFromNameProtector'])
            self.data = self.Rvariables['newDataFromNameProtector']

        if 'Rows' in self.nameProtectDFcheckBox.getChecked():
            self.R('rownames('+self.data+') <- make.names(rownames('+self.data+'))')
            
        if str(self.namesProtectDFcomboBox.currentText()) != '':
            self.R(self.data+'$'+self.Rvariables['nameProtector']+'<- make.names('+self.data+'[,\''+str(self.namesProtectDFcomboBox.currentText())+'\'])')
        if 'Columns' in self.nameProtectDFcheckBox.getChecked():
            self.R('colnames('+self.data+') <- make.names(colnames('+self.data+'))')
        
        self.rSend("Data Frame", newData)
        
    def vCommit(self): # make protected names for a vector
        if self.data == '': return
        
        self.R(self.Rvariables['nameProtector']+'<- make.names('+self.data+')')
        self.parentData['data'] = self.Rvariables['nameProtector']
        self.rSend("Vector", self.parentData)