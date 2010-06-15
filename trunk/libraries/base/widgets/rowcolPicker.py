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
        OWRpy.__init__(self, parent, signalManager, "RowColumnSelection", wantMainArea = 0, resizingEnabled = 1) #initialize the widget
        self.dataClass = None
        self.dataParent = None
        self.setRvariableNames(['rowcolSelector', 'rowcolSelectorNot'])
        
        
        self.inputs = [('Data Table', rdf.RDataFrame, self.setWidget), 
        ('Subsetting Vector', rdf.RDataFrame, self.setSubsettingVector)]
        
        self.outputs = [('Data Table', rdf.RDataFrame), 
        ('Not Data Table', rdf.RDataFrame), 
        ('Reduced Vector', rvec.RVector),
        ('Not Reduced Vector', rvec.RVector)]
        
        #set the gui
        area = redRGUI.widgetBox(self.controlArea,orientation='horizontal')       
        options = redRGUI.widgetBox(area, orientation = 'vertical')
        area.layout().setAlignment(options,Qt.AlignTop)

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
        
        # selectionBox = redRGUI.widgetBox(options)
        # self.attsHintEdit = OWGUIEx.lineEditHint(selectionBox, None, None, callback = self.callback)
        # self.attsHintEdit.hide()    
        # buttonsBox = redRGUI.widgetBox(selectionBox)
        # self.outputBox = redRGUI.textEdit(self.controlArea, '<center>No output generated yet.  Please make selections to generate output.</center>')
        
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
    # def callback(self):
        # text = str(self.attsHintEdit.text())
        # for i in range(0, self.attributes.count()):
            # item = self.attributes.item(i)
            # if str(item.text()) == text:
                # self.attributes.setItemSelected(item, 1)
                
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
                # self.attsHintEdit.show()
                # self.attsHintEdit.setItems(r)
            # else:
                # self.attributes.update([i for i in range(self.R('length('+self.data+'[1,])'))])
                # self.attsHintEdit.show()
                # self.attsHintEdit.setItems([i for i in range(self.R('length('+self.data+'[1,])'))])
        elif self.rowcolBox.getChecked() == 'Column': # if we are looking in the columns
            c =  self.R(self.dataParent.getColumnnames_call())
            if type(c) == list:
                self.attributes.update(c)
                # self.attsHintEdit.show()
                # self.attsHintEdit.setItems(c)
            # else:
                # self.attributes.update([i for i in range(self.R('length('+self.data+'[,1])'))])
                # self.attsHintEdit.show()
                # self.attsHintEdit.setItems([i for i in range(self.R('length('+self.data+'[,1])'))])
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
            self.R(self.Rvariables['rowcolSelector']+'<-'+self.data+'[rownames('+self.data+')'+' %in% '+self.ssv+'[,"'+col+'"],]')
            self.R(self.Rvariables['rowcolSelectorNot']+'<-'+self.data+'[!rownames('+self.data+')'+' %in% '+self.ssv+'[,"'+col+'"],]')
        elif self.rowcolBox.getChecked() == 'Column':
            self.R(self.Rvariables['rowcolSelector']+'<-'+self.data+'[,colnames('+self.data+')'+
            ' %in% '+self.ssv+'[,'+col+']]')
            self.R(self.Rvariables['rowcolSelectorNot']+'<-'+self.data+'[,!colnames('+self.data+')'+
            ' %in% '+self.ssv+'[,'+col+']]')
                
        print 'asdfasdf'
        newData = rdf.RDataFrame(data = self.Rvariables['rowcolSelector'])
        self.rSend('Data Table', newData)
        newDataNot = rdf.RDataFrame(data = self.Rvariables['rowcolSelectorNot'])
        self.rSend('Not Data Table', newDataNot)
        
        # self.R('txt<-capture.output('+self.Rvariables['rowcolSelector']+'[1:5,])')
        # tmp = self.R('paste(txt, collapse ="\n")')
        # self.outputBox.setHtml('A sample of your selection is shown.  Ignore any values with NA.<pre>'+tmp+'</pre>')
        

    def subset(self): # now we need to make the R command that will handle the subsetting.
        if self.data == None or self.data == '': return
        
        selectedDFItems = []
        for name in self.attributes.selectedItems():
            selectedDFItems.append('"'+str(name.text())+'"') # get the text of the selected items
        
        if self.rowcolBox.getChecked() == 'Row':
            self.R(self.Rvariables['rowcolSelector']+'<-as.data.frame('+self.data+'[rownames('+self.data+')'+' %in% c('+','.join(selectedDFItems)+')'+',])')
            self.R(self.Rvariables['rowcolSelectorNot']+'<-as.data.frame('+self.data+'[!rownames('+self.data+') %in% c('+','.join(selectedDFItems)+'),])')
        elif self.rowcolBox.getChecked() == 'Column':
            self.R(self.Rvariables['rowcolSelector']+'<-as.data.frame('+self.data+'[,colnames('+self.data+')'+' %in% c('+','.join(selectedDFItems)+')'+'])')
            self.R(self.Rvariables['rowcolSelectorNot']+'<-as.data.frame('+self.data+'[,!colnames('+self.data+')'+' %in% c('+','.join(selectedDFItems)+')])')
            
        if self.R('dim('+self.Rvariables['rowcolSelector']+')')[1] == 1:
            self.R('colnames('+self.Rvariables['rowcolSelector']+')<-c('+','.join(selectedDFItems)+')') # replace the colname if we are left with a 1 column data frame
            newVector = rvec.RVector(data = 'as.vector('+self.Rvariables['rowcolSelector']+')')
            self.rSend('Reduced Vector', newVector)
            
        if self.R('dim('+self.Rvariables['rowcolSelectorNot']+')')[1] == 1:
            self.R('colnames('+self.Rvariables['rowcolSelectorNot']+')<-c(setdiff(colnames('+self.data+'), colnames('+self.Rvariables['rowcolSelector']+')))')
            newVector = rvec.RVector(data = 'as.vector('+self.Rvariables['rowcolSelectorNot']+')')
            self.rSend('Not Reduced Vector', newVector)
            
        
        newData = rdf.RDataFrame(data = self.Rvariables['rowcolSelector'])
        self.rSend('Data Table', newData)

        newDataNot = rdf.RDataFrame(data = self.Rvariables['rowcolSelectorNot'])
        self.rSend('Not Data Table', newDataNot)
                
        
        # self.R('txt<-capture.output('+self.Rvariables['rowcolSelector']+'[1:5,])')
        # tmp = self.R('paste(txt, collapse ="\n")')
        # self.outputBox.setHtml('A sample of your selection is shown.  Ignore any values with NA.<pre>'+tmp+'</pre>')
            