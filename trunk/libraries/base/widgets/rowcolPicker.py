"""
<name>Row or Column Selection</name>
<description>Subsets a data.frame object to pass to subsequent widgets.  Very similar to the Row Col Selector but this widget doesn't look to row or column criteria.  Instead, this widget subsets on row or column name alone, while Row Col Selector does not.</description>
<tags>Subsetting</tags>
<RFunctions>base:rownames,base:colnames,base:summary</RFunctions>
<icon>Subset.png</icon>
<priority>2010</priority>

"""

### this is a rewright of the rowSelector and colSelector to work better than the one orriginaly written.  This widget may have less functionality than the orriginal but should conform to RedR1.7 standards.

from OWRpy import *
import OWGUI
import OWGUIEx
import redRGUI

class rowcolPicker(OWRpy): # a simple widget that actually will become quite complex.  We want to do several things, give into about the variables that are selected (do a summary on the attributes and show them to the user) and to pass forward both a subsetted data.frame or a vector for classification for things evaluating TRUE to the subsetting
    settingsList = ['rowcolselect', 'newdata', 'rowactiveCriteria', 'rowselectionCriteria', 'cTableTexts', 'olddata', 'ssvdata', 'data', 'test', 'saveData']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "RowColumnSelection", wantMainArea = 0, resizingEnabled = 1) #initialize the widget
        self.namesPresent = 0
        self.dataClass = None
        self.dataParent = None
        self.setRvariableNames(['rowcolSelector', 'rowcolSelectorNot'])
        
        
        self.inputs = [('Data Table', signals.RDataFrame, self.setWidget), ('Subsetting Vector', signals.RVector, self.setSubsettingVector)]
        self.outputs = [('Data Table', signals.RDataFrame), ('Not Data Table', signals.RDataFrame), ('Reduced Vector', signals.RVector)]
        
        #set the gui
        box = redRGUI.widgetBox(self.controlArea, orientation = 'horizontal')
        self.rowcolBox = redRGUI.radioButtons(box, 'The names come from:', ['Row', 'Column'], callback=self.rowcolButtonSelected)
        #self.ISNOT = redRGUI.comboBox(box, items = ['IS', 'IS NOT'])
        self.attributes = redRGUI.listBox(box, label='Attributes')
        self.attributes.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        selectionBox = redRGUI.widgetBox(box)
        self.attsHintEdit = OWGUIEx.lineEditHint(selectionBox, None, None, callback = self.callback)
        self.attsHintEdit.hide()    
        buttonsBox = redRGUI.widgetBox(selectionBox)
        self.subOnAttachedButton = redRGUI.button(buttonsBox, "Select on Attached", callback=self.subOnAttached)
        self.subOnAttachedButton.setEnabled(False)
        
        self.subsetButton = redRGUI.button(buttonsBox, "Subset", callback=self.subset)
        self.outputBox = redRGUI.textEdit(self.controlArea, '<center>No output generated yet.  Please make selections to generate output.</center>')
        
    def setWidget(self, data):
        if data:
            self.data = data.getData()
            self.dataParent = data
            
    def callback(self):
        text = str(self.attsHintEdit.text())
        for i in range(0, self.attributes.count()):
            item = self.attributes.item(i)
            if str(item.text()) == text:
                self.attributes.setItemSelected(item, 1)
                
    
    def rowcolButtonSelected(self): #recall the GUI setting the data if data is selected
        # print self.rowcolBox.getChecked()
        # if self.dataParent:
        if not self.dataParent: return
        if self.rowcolBox.getChecked() == 'Row': #if we are looking at rows
            r =  self.R(self.dataParent.getRownames_call())
            if type(r) == list:
                self.attributes.update(r)
                self.attsHintEdit.show()
                self.attsHintEdit.setItems(r)
                self.namesPresent = 1
            else:
                self.attributes.update([i for i in range(self.R('length('+self.data+'[1,])'))])
                self.attsHintEdit.show()
                self.attsHintEdit.setItems([i for i in range(self.R('length('+self.data+'[1,])'))])
                self.namesPresent = 0
        elif self.rowcolBox.getChecked() == 'Column': # if we are looking in the columns
            c =  self.R(self.dataParent.getColumnnames_call())
            if type(c) == list:
                self.attributes.update(c)
                self.attsHintEdit.show()
                self.attsHintEdit.setItems(c)
                self.namesPresent = 1
            else:
                self.attributes.update([i for i in range(self.R('length('+self.data+'[,1])'))])
                self.attsHintEdit.show()
                self.attsHintEdit.setItems([i for i in range(self.R('length('+self.data+'[,1])'))])
                self.namesPresent = 0
        else: #by exclusion we haven't picked anything yet
            self.status.setText('You must select either Row or Column to procede')
    def setSubsettingVector(self, data):
        if data == None: return
        self.subOnAttachedButton.setEnabled(True)
        self.ssv = data.getData()
        self.ssvdata = data
        
    def subOnAttached(self):
        if self.data == None or self.data == '': return
        
        
        if self.rowcolBox.getChecked() == 'Row':
            self.R(self.Rvariables['rowcolSelector']+'<-'+self.data+'[rownames('+self.data+')'+' %in% '+self.ssv+',]')
            self.R(self.Rvariables['rowcolSelectorNot']+'<-'+self.data+'[!rownames('+self.data+')'+' %in% '+self.ssv+',]')
        elif self.rowcolBox.getChecked() == 'Column':
            self.R(self.Rvariables['rowcolSelector']+'<-'+self.data+'[,colnames('+self.data+')'+' %in% '+self.ssv+']')
            self.R(self.Rvariables['rowcolSelectorNot']+'<-'+self.data+'[,!colnames('+self.data+')'+' %in% '+self.ssv+']')
                
        #self.makeCM(self.Rvariables['rowcolSelector_cm'], self.Rvariables['rowcolSelector'])
        newData = signals.RDataFrame(data = self.Rvariables['rowcolSelector'])
        self.rSend('Data Table', newData)
        newDataNot = signals.RDataFrame(data = self.Rvariables['rowcolSelectorNot'])
        self.rSend('Not Data Table', newDataNot)
        
        self.R('txt<-capture.output('+self.Rvariables['rowcolSelector']+'[1:5,])')
        tmp = self.R('paste(txt, collapse ="\n")')
        self.outputBox.setHtml('A sample of your selection is shown.  Ignore any values with NA.<pre>'+tmp+'</pre>')
        
    def attributeSelected(self, item): # an item in the row or column section was clicked and you need to set the attList or give some infromation about the row or column for the user to make a decision.  In the case of continuous data we want to show the line edit for generating logic.  In the case of a set of text values or factors we want to show the factors so the user can select them.  We could also look for class infromation so that we could tell the user what she classified the data as.
        if self.data == None: return
        
        
        if self.rowcolBox.getChecked() == 'Row': #if we are selecting row
            name = str(item.text())
            self.attName = name
            self.R('t<-'+self.dataParent.getItem_call(name)) # set a temp variable for the selections made.
            c = self.R('class(t)')
            self.classifyData(c)

        elif self.rowcolBox.getChecked() == 'Column': # if we are selecting columns
            name = item.text()    
            self.R('t<-'+self.dataParent.getRowData_call(name))
            c = self.R('class(t)')
            self.classifyData(c)

        else: #by exclusion we haven't picked anything yet
            self.status.setText('You must select either Row or Column to procede')
        
    def classifyData(self, c):
        if c == 'character':
            self.attsList.show()
            self.attsLineEdit.hide()
            self.attsList.clear()
            self.attsList.addItems(self.R('t'))
            self.infoArea.setHtml('Character attribute detected.  The attribute can be seen to the right of the logic box.  Multiple items can be selected for subsetting.')
            self.dataClass = 'character'
        elif c == 'factor':
            self.attsLineEdit.hide()
            self.attsList.show()
            self.attsList.clear()
            self.attsList.addItems(self.R('levels(t)'))
            self.R('txt<-capture.output(summary(t))')
            tmp = self.R('paste(txt, collapse ="\n")')
            self.infoArea.setHtml('A list of factors was detected.  These are often used for classification.  Multiple items can be selected for subsetting.<br><br>Summary:<br><pre>'+tmp+'</pre>')
            self.dataClass = 'factor'
        elif c == 'numeric':
            self.attsList.hide()
            self.attsLineEdit.show()
            self.attsLineEdit.clear()
            self.attsList.clear()
            self.R('txt<-capture.output(summary(t))')
            tmp = self.R('paste(txt, collapse ="\n")')
            self.infoArea.setHtml('Numeric data was detected.  You may use the line edit to the right of the logic box to select boundries for subsetting.<br><br>Summary:<br><pre>'+tmp+'</pre>')
            self.dataClass = 'numeric'
            
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
            newVector = signals.RVector(data = 'as.vector('+self.Rvariables['rowcolSelector']+')')
            self.rSend('Reduced Vector', newVector)
        if self.R('dim('+self.Rvariables['rowcolSelectorNot']+')')[1] == 1:
            self.R('colnames('+self.Rvariables['rowcolSelectorNot']+')<-c(setdiff(colnames('+self.data+'), colnames('+self.Rvariables['rowcolSelector']+')))')
            newVector = signals.RVector(data = 'as.vector('+self.Rvariables['rowcolSelectorNot']+')')
            self.rSend('Reduced Vector', newVector)
            
        
        newData = signals.RDataFrame(data = self.Rvariables['rowcolSelector'])
        self.rSend('Data Table', newData)

        newDataNot = signals.RDataFrame(data = self.Rvariables['rowcolSelectorNot'])
        self.rSend('Not Data Table', newDataNot)
                
        
        self.R('txt<-capture.output('+self.Rvariables['rowcolSelector']+'[1:5,])')
        tmp = self.R('paste(txt, collapse ="\n")')
        self.outputBox.setHtml('A sample of your selection is shown.  Ignore any values with NA.<pre>'+tmp+'</pre>')
            