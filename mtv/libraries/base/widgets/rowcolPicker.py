"""
<name>Row or Column Selection</name>
<tags>Subsetting</tags>
<icon>Subset.png</icon>
"""

from OWRpy import *
import OWGUI
import OWGUIEx
import redRGUI
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.signalClasses.RList import RList as redRRList
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.qtWidgets.radioButtons import radioButtons
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.separator import separator
from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.widgetBox import widgetBox
class rowcolPicker(OWRpy): 

    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self) #initialize the widget
        self.dataClass = None
        self.dataParent = None
        self.setRvariableNames(['rowcolSelector', 'rowcolSelectorNot'])
        self.SubsetByAttached = 0
        
        self.inputs.addInput('id0', 'Data Table', redRRDataFrame, self.setWidget)
        self.inputs.addInput('id1', 'Subsetting Vector', redRRList, self.setSubsettingVector)

        
        self.outputs.addOutput('id0', 'Data Table', redRRDataFrame)
        self.outputs.addOutput('id1', 'Not Data Table', redRRDataFrame)

        
        #set the gui
        area = widgetBox(self.controlArea,orientation='horizontal')       
        options = widgetBox(area, orientation = 'vertical')
        area.layout().setAlignment(options,Qt.AlignTop)
        self.alwaysSend = checkBox(options, buttons = ['Always send these selections'])
        self.sendSection = checkBox(options, label = "Send Where Selection Is:", buttons = ["True", "False"], setChecked = "True", toolTip = "Select True to send data from the Data slot where the selections that you made are True.\nSelect False to send data from the Not Data slot that are not the selections you made.")
        self.rowcolBox = radioButtons(options, label='Select On', buttons=['Column','Row'], setChecked= 'Column',
        callback=self.rowcolButtonSelected)
        
        self.invertButton = button(options, "Invert Selection", callback=self.invertSelection)

        self.subsetButton = button(options, "Subset on Selection", callback=self.subset)
        separator(options,height=15)

        self.subsetBox = groupBox(options,label='Subset by')
        self.subsetColumn = comboBox(self.subsetBox,label="Column:", orientation='vertical',items=['Select'])
        self.subOnAttachedButton = button(self.subsetBox, "Subset by column", callback=self.subOnAttached)
        self.subsetBox.setDisabled(True)
        
        separator(options,height=20)

        info = widgetBox(options)
        options.layout().setAlignment(info,Qt.AlignBottom)
        self.infoBox = widgetLabel(info)
        separator(info,height=15)
        self.selectionInfoBox = widgetLabel(info)
        
        self.attributes = listBox(area, label='Select',callback=self.onSelect)
        self.attributes.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def onSelect(self):
        count = self.attributes.selectionCount()
        self.selectionInfoBox.setText('# ' + self.rowcolBox.getChecked()  + 's selected: ' + str(count))
        
    def setWidget(self, data):
        if data:
            self.data = data.getData()
            self.dataParent = data
            self.rowcolButtonSelected()
            dims = data.getDims_data()
            self.infoBox.setText('# Rows: ' + str(dims[0]) +'\n# Columns: ' + str(dims[1]))
            if 'Always send these selections' in self.alwaysSend.getChecked():
                self.subset()
        else:
            self.data = ''
            self.dataParent = None
            self.attributes.clear()
    def invertSelection(self):
        self.attributes.invertSelection()
        self.onSelect()
    def rowcolButtonSelected(self): #recall the GUI setting the data if data is selected
        # print self.rowcolBox.getChecked()
        # if self.dataParent:
        if not self.dataParent: return
        if self.rowcolBox.getChecked() == 'Row': #if we are looking at rows
            r =  self.R('rownames('+self.data+')', wantType = 'list')
            if type(r) == list:
                self.attributes.update(r)

        elif self.rowcolBox.getChecked() == 'Column': # if we are looking in the columns
            c =  self.R('colnames('+self.data+')', wantType = 'list')
            if type(c) == list:
                self.attributes.update(c)

        else: #by exclusion we haven't picked anything yet
            self.status.setText('You must select either Row or Column to procede')
    def setSubsettingVector(self, data):
        if data == None: 
            self.subsetBox.setEnabled(False)
            self.ssv = ''
            self.subsetColumn.clear()
            return       
            
        self.subsetBox.setEnabled(True)

        self.ssv = data.getData()
        self.subsetColumn.clear()
        
        self.subsetColumn.addItems(self.R('names(as.list('+data.getData()+'))', wantType = 'list'))
        self.ssvdata = data
        
    def subOnAttached(self):
        if self.data == None or self.data == '': return
                
        col=str(self.subsetColumn.currentText())
        
        if self.rowcolBox.getChecked() == 'Row':
            if "True" in self.sendSection.getChecked():
                self.R(self.Rvariables['rowcolSelector']+'<-as.data.frame('+self.data+'[rownames('+self.data+')'+' %in% '+self.ssv+'[["'+col+'"]],])', wantType = 'NoConversion')
                newData = redRRDataFrame(data = self.Rvariables['rowcolSelector'])
                self.rSend('id0', newData)
            if "False" in self.sendSection.getChecked():
                self.R(self.Rvariables['rowcolSelectorNot']+'<-as.data.frame('+self.data+'[!rownames('+self.data+')'+' %in% '+self.ssv+'[["'+col+'"]],])', wantType = 'NoConversion')
                newDataNot = redRRDataFrame(data = self.Rvariables['rowcolSelectorNot'])
                self.rSend('id1', newDataNot)
        elif self.rowcolBox.getChecked() == 'Column':
            if "True" in self.sendSection.getChecked():
                self.R(self.Rvariables['rowcolSelector']+'<-as.data.frame('+self.data+'[,colnames('+self.data+')'+
            ' %in% '+self.ssv+'[[\''+col+'\']]])', wantType = 'NoConversion')
                newData = redRRDataFrame(data = self.Rvariables['rowcolSelector'])
                self.rSend('id0', newData)
            if "False" in self.sendSection.getChecked():
                self.R(self.Rvariables['rowcolSelectorNot']+'<-as.data.frame('+self.data+'[,!colnames('+self.data+')'+
            ' %in% '+self.ssv+'[[\''+col+'\']]])', wantType = 'NoConversion')
                newDataNot = redRRDataFrame(data = self.Rvariables['rowcolSelectorNot'])
                self.rSend('id1', newDataNot)
        self.SubsetByAttached = 1
    def subset(self): # now we need to make the R command that will handle the subsetting.
        if self.data == None or self.data == '': 
            self.status.setText("Connect data before processing")
            return
        
        selectedDFItems = []
        for name in self.attributes.selectedItems():
            selectedDFItems.append('"'+str(name.text())+'"') # get the text of the selected items
        
        if self.rowcolBox.getChecked() == 'Row':
            if "True" in self.sendSection.getChecked():
                self.R(self.Rvariables['rowcolSelector']+'<-as.data.frame('+self.data+'[rownames('+self.data+')'+' %in% c('+','.join(selectedDFItems)+')'+',])', wantType = 'NoConversion')
                newData = redRRDataFrame(data = self.Rvariables['rowcolSelector'])
                self.rSend('id0', newData)
            if "False" in self.sendSection.getChecked():
                self.R(self.Rvariables['rowcolSelectorNot']+'<-as.data.frame('+self.data+'[!rownames('+self.data+') %in% c('+','.join(selectedDFItems)+'),])', wantType = 'NoConversion')
                newDataNot = redRRDataFrame(data = self.Rvariables['rowcolSelectorNot'])
                self.rSend('id1', newDataNot)
        elif self.rowcolBox.getChecked() == 'Column':
            if "True" in self.sendSection.getChecked():
                self.R(self.Rvariables['rowcolSelector']+'<-as.data.frame('+self.data+'[,colnames('+self.data+')'+' %in% c('+','.join(selectedDFItems)+')'+'])', wantType = 'NoConversion')
                newData = redRRDataFrame(data = self.Rvariables['rowcolSelector'])
                self.rSend('id0', newData)
            if "False" in self.sendSection.getChecked():
                self.R(self.Rvariables['rowcolSelectorNot']+'<-as.data.frame('+self.data+'[,!colnames('+self.data+')'+' %in% c('+','.join(selectedDFItems)+')])', wantType = 'NoConversion')
                newDataNot = redRRDataFrame(data = self.Rvariables['rowcolSelectorNot'])
                self.rSend('id1', newDataNot)
        self.SubsetByAttached = 0
    # def getReportText(self, fileDir):
        # if self.SubsetByAttached:
            # text = 'Data was subset by '+str(self.rowcolBox.getChecked())+' '+str(self.subsetColumn.currentText())+'\n\n'
        # else:
            # text = 'Data was subset by the following selections:\n\n'
            # selectedDFItems = []
            # for name in self.attributes.selectedItems():
                # selectedDFItems.append('"'+str(name.text())+'"') # get the text of the selected items
                
            # for name in selectedDFItems:
                # text += '-'+str(name)+'\n\n'
                
        # text += '\n\n'
        # return text