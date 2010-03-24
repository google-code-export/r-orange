"""
<name>Row or Column Screener</name>
<description>Subsets a data.frame object to pass to subsequent widgets.</description>
<tags>Data Manipulation</tags>
<RFunctions>base:rownames,base:colnames,base:summary</RFunctions>
<icon>icons/subset.png</icon>
<priority>2010</priority>

"""

### this is a rewright of the rowSelector and colSelector to work better than the one orriginaly written.  This widget may have less functionality than the orriginal but should conform to RedR1.7 standards.

from OWRpy import *
import OWGUI
import redRGUI
import OWGUIEx

class rowcolSelector(OWRpy): # a simple widget that actually will become quite complex.  We want to do several things, give into about the variables that are selected (do a summary on the attributes and show them to the user) and to pass forward both a subsetted data.frame or a vector for classification for things evaluating TRUE to the subsetting
    settingsList = ['rowcolselect', 'newdata', 'rowactiveCriteria', 'rowselectionCriteria', 'cTableTexts', 'olddata', 'ssvdata', 'data', 'test', 'saveData']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1) #initialize the widget
        self.namesPresent = 0
        self.dataClass = None
        self.setRvariableNames(['rowcolSelector', 'rowcolselect_cm_'])
        
        self.inputs = [('Data Table', RvarClasses.RDataFrame, self.setWidget), ('Subsetting Vector', RvarClasses.RVector, self.setSubsettingVector)]
        self.outputs = [('Data Table', RvarClasses.RDataFrame), ('Reduced Vector', RvarClasses.RVector)]
        
        self.help.setHtml('<small>The Row Column Selection widget allows one to select subsets of Data Tables.  If complex selections are required simply link many of these widgets together.  It may be useful to also consider using the Merge Data Table widget or the Melt widget when using this widget to but the data into the proper shape for later analysis.  The sections of this widget are:<br>Select by row or column<br><nbsp>- Allows you to select either rows or columns that match a certain criteria.  For example if you pick to select rows you will select based on criteria that are in the columns.<br>Attributes<br><nbsp>- Attributes are the names of the attributes that have the criteria that you will be selecting on, for example if you want to pick all rows that have a value greater than 5 in the second column the second column would be your attribute.<br>Logical<br><nbsp>- This section discribes the logic that should be applied to the selection, for example should the attribute be less than, greater than, equal to, or in a selection list.  "NOT" is also available.<br><br>One can also select based on an attached subsetting vector.  This will look for matches in the subsetting vector to values that are in your selected attribute.  This can be useful when dealing with "lists" of things that can be coerced into vectors.<br><br>This widget will send either a Data Table or a Vector depending on the dimention of your selection.')
        #set the gui
        box = redRGUI.widgetBoxNoLabel(self.controlArea, orientation = 'horizontal')
        self.rowcolBox = redRGUI.radioButtons(box, label='Select by row or column', buttons=['Row', 'Column'], callback=self.rowcolButtonSelected)
        self.attributes = redRGUI.listBox(box, label='Attributes', callback = self.attributeSelected)
        
        selectionBox = redRGUI.widgetBoxNoLabel(box, orientation = 'horizontal')
        self.ISNOT = redRGUI.comboBox(selectionBox, items = ['IS', 'IS NOT'])
        self.selections = redRGUI.checkBox(selectionBox, buttons=['<', '>', '='])
        
        self.attsList = redRGUI.listBox(selectionBox)
        self.attsList.setSelectionMode(QAbstractItemView.MultiSelection)
        self.attsList.hide()
        self.attsHintEdit = OWGUIEx.lineEditHint(selectionBox, None, None, callback = self.callback)
        self.attsHintEdit.hide()
        self.attsLineEdit = redRGUI.lineEdit(selectionBox)
        self.attsLineEdit.hide()
        
        buttonsBox = redRGUI.widgetBoxNoLabel(selectionBox)
        self.subOnAttachedButton = redRGUI.button(buttonsBox, "Select on Attached", callback=self.subOnAttached)
        self.subOnAttachedButton.setEnabled(False)
        
        self.subsetButton = redRGUI.button(self.bottomAreaRight, "Subset", callback=self.subset)
        self.infoArea = redRGUI.textEdit(self.controlArea, '<center>Criteria not selected.  Please select a criteria to see its attributes.</center>')
        self.outputBox = redRGUI.textEdit(self.controlArea, '<center>No output generated yet.  Please make selections to generate output.</center>')
        
    def setWidget(self, data):
        if data:
            self.data = data['data']
            if data['parent']:
                
                self.parent = data['parent'] 
            else:
                self.parent = data['data']
            if data['cm']:
                self.cm = data['cm']
            else:
                self.R(self.data+'_cm<-data.frame(row.names = rownames('+self.data+'))')
                self.cm = self.data+'_cm'
            self.parentData = data.copy()
            r = self.R('rownames('+self.data+')')
            c = self.R('colnames('+self.data+')')
            self.R(self.Rvariables['rowcolselect_cm_']+'<-data.frame(row.names = rownames('+self.data+'))')
            if self.rowcolBox.getChecked() == 'Row': #if we are looking at rows
                c = self.R('colnames('+self.data+')')
                if c != 'NULL':
                    self.attributes.update(c)
                    self.namesPresent = 1
                else:
                    self.attributes.update([i for i in range(self.R('length('+self.data+'[1,])'))])
                    self.namesPresent = 0
            elif self.rowcolBox.getChecked() == 'Column': # if we are looking in the columns
                
                if type(r) == list:
                    self.attributes.update(r)
                    self.namesPresent = 1
                else:
                    self.attributes.update([i for i in range(self.R('length('+self.data+'[,1])'))])
                    self.namesPresent = 0
            else: #by exclusion we haven't picked anything yet
                self.attributes.clear()
                self.status.setText('You must select either Row or Column to procede')
    def rowcolButtonSelected(self): #recall the GUI setting the data if data is selected
        print self.rowcolBox.getChecked()
        if self.data: self.setWidget(self.parentData)
    def setSubsettingVector(self, data):
        if 'data' in data:
            self.subOnAttachedButton.setEnabled(True)
            self.ssv = data['data']
            self.ssvdata = data
        else:
            return
        
    def subOnAttached(self):
        tmpitem = self.rsession(self.ssv) #get the items to subset with
        if type(tmpitem) is str: #it's a string!!!!!!!
            items = []
            items.append(tmpitem)
        elif type(tmpitem) is list: #it's a list
            items = tmpitem
        elif type(tmpitem) is dict: #it's a dict
            items = []
            for key in tmpitem.keys():
                items.append(tmpitem['key'])
    def attributeSelected(self): # an item in the row or column section was clicked and you need to set the attList or give some infromation about the row or column for the user to make a decision.  In the case of continuous data we want to show the line edit for generating logic.  In the case of a set of text values or factors we want to show the factors so the user can select them.  We could also look for class infromation so that we could tell the user what she classified the data as.
        if self.data == None: return
        
        
        if self.rowcolBox.getChecked() == 'Row': #if we are selecting rows
            if self.namesPresent:
                name = '"'+str(self.attributes.selectedItems()[0].text())+'"'
            else:
                name = str(self.attributes.selectedItems()[0].text())
            self.attName = name
            self.R('t<-'+self.data+'[,'+name+']') # set a temp variable for the selections made.
            c = self.R('class(t)')
            self.classifyData(c)

        elif self.rowcolBox.getChecked() == 'Column': # if we are selecting columns
            print str(self.namesPresent)
            if self.namesPresent:
                name = '"'+str(self.attributes.selectedItems()[0].text())+'"'
            else:
                name = str(self.attributes.selectedItems()[0].text())
                
            self.R('t<-'+self.data+'['+name+',]')
            c = self.R('class(t(t)[,1])')
            self.classifyData(c)

        else: #by exclusion we haven't picked anything yet
            self.status.setText('You must select either Row or Column to procede')
    def callback(self):
        text = str(self.attsHintEdit.text())
        for i in range(0, self.attsList.count()):
            item = self.attsList.item(i)
            if str(item.text()) == text:
                self.attsList.setItemSelected(item, 1)
                
                
    def classifyData(self, c):
        if c == 'character':
            self.attsList.show()
            self.attsLineEdit.hide()
            self.attsHintEdit.show()
            self.attsHintEdit.setItems(self.R('as.vector(t)'))
            self.attsList.update(self.R('as.vector(t)'))
            self.infoArea.setHtml('Character attribute detected.  The attribute can be seen to the right of the logic box.  Multiple items can be selected for subsetting.')
            self.dataClass = 'character'
        elif c == 'factor':
            self.attsLineEdit.hide()
            self.attsHintEdit.show()
            self.attsHintEdit.setItems(self.R('levels(t)'))
            self.attsList.show()
            self.attsList.update(self.R('levels(t)'))
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
        if self.data == None: return
        self.R(self.cm+'$'+self.Rvariables['rowcolselect_cm_']+'<-rep(FALSE, length('+self.parentData['parent']+'[,1]))')
        if self.ISNOT.currentText() == 'IS': isNot = ''
        elif self.ISNOT.currentText() == 'IS NOT': isNot = '!' 
        
        
        if self.dataClass in ['character', 'factor']:#the data is in the attsList
            selectedDFItems = []
            for name in self.attsList.selectedItems():
                selectedDFItems.append('"'+str(name.text())+'"') # get the text of the selected items
            
            if self.rowcolBox.getChecked() == 'Row':
                self.Rvariables['rowcolSelector'] = self.parentData['data']
                
                self.R(self.cm+'$'+self.Rvariables['rowcolselect_cm_']+'[rownames('+self.parentData['data']+'),]<-'+isNot+'('+self.data+'[,'+self.attName+']'+' %in% c('+','.join(selectedDFItems)+'))') # assign the selections to the cm for this object
                self.parentData['data'] = self.Rvariables['rowcolSelector']+'['+self.cm+'$'+self.Rvariables['rowcolselect_cm_']+',]'
            elif self.rowcolBox.getChecked() == 'Column': # pick the columns that you want and send those forward as the new data
                self.R(self.Rvariables['rowcolSelector']+'<-'+self.data+'[,'+isNot+self.data+'['+self.attName+',]'+' %in% c('+','.join(selectedDFItems)+')'+']')
            
                
        elif self.dataClass == 'numeric': # the criteria is in the attsLineEdit
            logic = []
            if '<' in self.selections.getChecked():
                logic.append('<')
            elif '>' in self.selections.getChecked():
                logic.append('>')
            if '=' in self.selections.getChecked():
                logic.append('=')
                
                
            if self.rowcolBox.getChecked() == 'Row':
                RLogic = []
                for logical in logic:
                    RLogic.append(str(isNot+'('+self.data+'[,'+self.attName+']'+logical+self.attsLineEdit.text()+')'))
                #self.Rvariables['rowcolSelector'] = self.parentData['data']
                self.parentData['data'] = self.data+'['+self.cm+'$'+self.Rvariables['rowcolselect_cm_']+'== 1,]'
                self.R(self.cm+'$'+self.Rvariables['rowcolselect_cm_']+'[rownames('+self.parentData['data']+'),]<-'+'&'.join(RLogic)) # add criteria to the cm
                
            elif self.rowcolBox.getChecked() == 'Column':
                RLogic = []
                for logical in logic:
                    RLogic.append(isNot+'('+self.data+'['+self.attName+',]'+logical+self.attsLineEdit.text()+')')            
                self.R(self.Rvariables['rowcolSelector']+'<-'+self.data+'[,'+'&'.join(RLogic)+']')
                self.parentData['data'] = self.Rvariables['rowcolSelector']
                    
        # send the data
        
        self.parentData['cm'] = self.cm  
        self.parentData['parent'] = self.parent
        self.rSend('Data Table', self.parentData)
        
        
        self.R('txt<-capture.output('+self.parentData['data']+'[1:5,])')
        tmp = self.R('paste(txt, collapse ="\n")')
        self.outputBox.setHtml('A sample of your selection is shown.  Ignore any values with NA.<pre>'+tmp+'</pre>')
            