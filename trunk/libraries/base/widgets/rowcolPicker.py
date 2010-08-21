"""
<name>Row or Column Selection</name>
<description>Subsets a data.frame object to pass to subsequent widgets.</description>
<tags>Subsetting</tags>
<author>Anup Parikh (anup@red-r.org) and Kyle R Covington (kyle@red-r.org)</author>
<RFunctions>base:rownames,base:colnames,base:summary</RFunctions>
<icon>Subset.png</icon>
"""

from OWRpy import *
import OWGUI
import OWGUIEx
import redRGUI
import libraries.base.signalClasses.RDataFrame as rdf
import libraries.base.signalClasses.RVector as rvec
class rowcolPicker(OWRpy): 

    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self) #initialize the widget
        self.dataClass = None
        self.dataParent = None
        self.setRvariableNames(['rowcolSelector', 'rowcolSelectorNot'])
        self.SubsetByAttached = 0
        
        self.inputs = [('Data Table', rdf.RDataFrame, self.setWidget), 
        ('Subsetting Vector', rdf.RDataFrame, self.setSubsettingVector)]
        
        self.outputs = [('Data Table', rdf.RDataFrame), 
        ('Not Data Table', rdf.RDataFrame)]
        
        #set the gui
        area = redRGUI.widgetBox(self.controlArea,orientation='horizontal')       
        options = redRGUI.widgetBox(area, orientation = 'vertical')
        area.layout().setAlignment(options,Qt.AlignTop)
        
        self.sendSection = redRGUI.checkBox(options, label = "Send Where Selection Is:", buttons = ["True", "False"], setChecked = "True", toolTip = "Select True to send data from the Data slot where the selections that you made are True.\nSelect False to send data from the Not Data slot that are not the selections you made.")
        self.rowcolBox = redRGUI.radioButtons(options, label='Select On', buttons=['Column','Row'], setChecked= 'Column',
        callback=self.rowcolButtonSelected)
        
        self.invertButton = redRGUI.button(options, "Invert Selection", callback=self.invertSelection)

        self.subsetButton = redRGUI.button(options, "Subset on Selection", callback=self.subset)
        redRGUI.separator(options,height=15)

        self.subsetBox = redRGUI.groupBox(options,label='Subset by')
        self.subsetColumn = redRGUI.comboBox(self.subsetBox,label="Column:", orientation='vertical',items=['Select'])
        self.subOnAttachedButton = redRGUI.button(self.subsetBox, "Subset by column", callback=self.subOnAttached)
        self.subsetBox.setDisabled(True)
        
        redRGUI.separator(options,height=20)

        info = redRGUI.widgetBox(options)
        options.layout().setAlignment(info,Qt.AlignBottom)
        self.infoBox = redRGUI.widgetLabel(info)
        redRGUI.separator(info,height=15)
        self.selectionInfoBox = redRGUI.widgetLabel(info)
        
        self.attributes = redRGUI.listBox(area, label='Select',callback=self.onSelect)
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

    def invertSelection(self):
        self.attributes.invertSelection()
        self.onSelect()
    def rowcolButtonSelected(self): #recall the GUI setting the data if data is selected
        # print self.rowcolBox.getChecked()
        # if self.dataParent:
        if not self.dataParent: return
        if self.rowcolBox.getChecked() == 'Row': #if we are looking at rows
            r =  self.R(self.dataParent.getRownames_call())
            if type(r) == list:
                self.attributes.update(r)

        elif self.rowcolBox.getChecked() == 'Column': # if we are looking in the columns
            c =  self.R(self.dataParent.getColumnnames_call())
            if type(c) == list:
                self.attributes.update(c)

        else: #by exclusion we haven't picked anything yet
            self.status.setText('You must select either Row or Column to procede')
    def setSubsettingVector(self, data):
        if data == None: return       
        self.subsetBox.setEnabled(True)

        self.ssv = data.getData()
        print self.ssv
        self.subsetColumn.clear()
        self.subsetColumn.addItems(data.getColumnnames_data())
        self.ssvdata = data
        
    def subOnAttached(self):
        if self.data == None or self.data == '': return
                
        col=str(self.subsetColumn.currentText())
        
        if self.rowcolBox.getChecked() == 'Row':
            if "True" in self.sendSection.getChecked():
                self.R(self.Rvariables['rowcolSelector']+'<-'+self.data+'[rownames('+self.data+')'+' %in% '+self.ssv+'[,"'+col+'"],]')
                newData = rdf.RDataFrame(data = self.Rvariables['rowcolSelector'])
                self.rSend('Data Table', newData)
            if "False" in self.sendSection.getChecked():
                self.R(self.Rvariables['rowcolSelectorNot']+'<-'+self.data+'[!rownames('+self.data+')'+' %in% '+self.ssv+'[,"'+col+'"],]')
                newDataNot = rdf.RDataFrame(data = self.Rvariables['rowcolSelectorNot'])
                self.rSend('Not Data Table', newDataNot)
        elif self.rowcolBox.getChecked() == 'Column':
            if "True" in self.sendSection.getChecked():
                self.R(self.Rvariables['rowcolSelector']+'<-'+self.data+'[,colnames('+self.data+')'+
            ' %in% '+self.ssv+'[,\''+col+'\']]')
                newData = rdf.RDataFrame(data = self.Rvariables['rowcolSelector'])
                self.rSend('Data Table', newData)
            if "False" in self.sendSection.getChecked():
                self.R(self.Rvariables['rowcolSelectorNot']+'<-'+self.data+'[,!colnames('+self.data+')'+
            ' %in% '+self.ssv+'[,\''+col+'\']]')
                newDataNot = rdf.RDataFrame(data = self.Rvariables['rowcolSelectorNot'])
                self.rSend('Not Data Table', newDataNot)
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
                self.R(self.Rvariables['rowcolSelector']+'<-as.data.frame('+self.data+'[rownames('+self.data+')'+' %in% c('+','.join(selectedDFItems)+')'+',])')
                newData = rdf.RDataFrame(data = self.Rvariables['rowcolSelector'])
                self.rSend('Data Table', newData)
            if "False" in self.sendSection.getChecked():
                self.R(self.Rvariables['rowcolSelectorNot']+'<-as.data.frame('+self.data+'[!rownames('+self.data+') %in% c('+','.join(selectedDFItems)+'),])')
                newDataNot = rdf.RDataFrame(data = self.Rvariables['rowcolSelectorNot'])
                self.rSend('Not Data Table', newDataNot)
        elif self.rowcolBox.getChecked() == 'Column':
            if "True" in self.sendSection.getChecked():
                self.R(self.Rvariables['rowcolSelector']+'<-as.data.frame('+self.data+'[,colnames('+self.data+')'+' %in% c('+','.join(selectedDFItems)+')'+'])')
                newData = rdf.RDataFrame(data = self.Rvariables['rowcolSelector'])
                self.rSend('Data Table', newData)
            if "False" in self.sendSection.getChecked():
                self.R(self.Rvariables['rowcolSelectorNot']+'<-as.data.frame('+self.data+'[,!colnames('+self.data+')'+' %in% c('+','.join(selectedDFItems)+')])')
                newDataNot = rdf.RDataFrame(data = self.Rvariables['rowcolSelectorNot'])
                self.rSend('Not Data Table', newDataNot)
        self.SubsetByAttached = 0
    def getReportText(self, fileDir):
        if self.SubsetByAttached:
            text = 'Data was subset by '+str(self.rowcolBox.getChecked())+' '+str(self.subsetColumn.currentText())+'\n\n'
        else:
            text = 'Data was subset by the following selections:\n\n'
            selectedDFItems = []
            for name in self.attributes.selectedItems():
                selectedDFItems.append('"'+str(name.text())+'"') # get the text of the selected items
                
            for name in selectedDFItems:
                text += '-'+str(name)+'\n\n'
                
        text += '\n\n'
        return text