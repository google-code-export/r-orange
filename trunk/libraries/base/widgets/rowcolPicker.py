"""
<name>Row or Column Selection</name>
<description>Subsets a data.frame object to pass to subsequent widgets.</description>
<tags>Subsetting</tags>
<author>Anup Parikh (anup@red-r.org) and Kyle R Covington (kyle@red-r.org)</author>
<RFunctions>base:rownames,base:colnames,base:summary</RFunctions>
<icon>subset2.png</icon>
"""

from OWRpy import *
import redRGUI
import libraries.base.signalClasses.RDataFrame as rdf
import libraries.base.signalClasses.RVector as rvec
class rowcolPicker(OWRpy): 
    globalSettingsList = ['sendOnSelect']

    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self) #initialize the widget
        self.dataClass = None
        self.dataParent = None
        self.setRvariableNames(['rowcolSelector', 'rowcolSelectorNot'])
        
        
        self.inputs = [('Data Table', rdf.RDataFrame, self.setWidget)]
        
        self.outputs = [('Data Table', rdf.RDataFrame), 
        ('Not Data Table', rdf.RDataFrame), 
        ('Reduced Vector', rvec.RVector),
        ('Not Reduced Vector', rvec.RVector)]
        
        #set the gui
        area = redRGUI.widgetBox(self.controlArea,orientation='horizontal')       
        options = redRGUI.widgetBox(area, orientation = 'vertical')
        area.layout().setAlignment(options,Qt.AlignTop)

        info = redRGUI.widgetBox(options)
        self.infoBox = redRGUI.widgetLabel(info)
        redRGUI.separator(info,height=4)
        self.selectionInfoBox = redRGUI.widgetLabel(info)
        redRGUI.separator(info,height=8)

        self.rowcolBox = redRGUI.radioButtons(options, label='Select On', buttons=['Column','Row'], setChecked= 'Column',
        orientation='horizontal', callback=self.rowcolButtonSelected)

        self.invertButton = redRGUI.button(options, "Invert Selection",toolTip='Invert the selection', 
        callback=self.invertSelection)

        self.subsetButton = redRGUI.button(options, "Subset on Selection",toolTip='Commit the subsetting', callback=self.subset)
        
        self.sendOnSelect = redRGUI.checkBox(options,buttons=['Send on select'], 
        toolTips=['Commit subsetting on select from the list.'])
        
        self.attributes = redRGUI.listBox(area, label='Select',callback=self.onSelect)
        self.attributes.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        
    def onSelect(self):
        count = self.attributes.selectionCount()
        self.selectionInfoBox.setText('# ' + self.rowcolBox.getChecked()  + 's selected: ' + str(count))
        if 'Send on select' in self.sendOnSelect.getChecked():
            self.subset()
    def setWidget(self, data):
        if data:
            self.data = data.getData()
            self.dataParent = data
            self.rowcolButtonSelected()
            dims = data.getDims_data()
            self.infoBox.setText('Input data size:\n# Rows: ' + str(dims[0]) +'\n# Columns: ' + str(dims[1]))
                
    def invertSelection(self):
        self.attributes.invertSelection()
        self.onSelect()
    def rowcolButtonSelected(self): #recall the GUI setting the data if data is selected
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
            