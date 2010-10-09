## Math widget.  Performs math on a column of a data table (RDataFrame).  Math functions can be added as the user wishes but many functions should already be present.  Note that if the widget fails you will get a message indicating that your function is unknown.

"""
<name>Math</name>
<tags>Data Manipulation</tags>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.dialog import dialog
from libraries.base.qtWidgets.Rtable import Rtable
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.widgetBox import widgetBox
class mathWidget(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        
        self.setRvariableNames(['math'])
        
        self.counter = 1
        self.functionsList = ['log2', 'log10', 'add', 'subtract', 'multiply', 'divide', 'match', 'as.numeric', 'as.character', 'exp', 'logicAND', 'logicOR']
        
        self.inputs.addInput('id0', 'Data Frame', redRRDataFrame, self.gotData)

        self.outputs.addOutput('id0', 'Data Frame', redRRDataFrame)

        #GUI#
        
        mainArea = widgetBox(self.controlArea, orientation = 'horizontal')
        leftArea = groupBox(mainArea, label = 'Table View')
        rightArea = groupBox(mainArea, label = 'Math Box')
        
        self.table = Rtable(leftArea)
        
        self.functionLineEdit = lineEdit(rightArea, label = 'Function Search or Run', callback = self.functionDone)
        QObject.connect(self.functionLineEdit, SIGNAL('textChanged(const QString&)'), lambda s: self.textChanged(s))
        
        self.functionListBox = listBox(rightArea, items = self.functionsList, callback = self.funcionPressed)
        
        #self.helpButton = button(rightArea, label = 'Help') #, toolTip = 'Press this then select a function from the list for help.')
        self.dialog = dialog(self)
        self.dialogTopArea = groupBox(self.dialog, label = 'Left Side')
        self.dialogTopLineEdit = lineEdit(self.dialogTopArea, label = 'Constant', toolTip = 'Must be a number')
        self.dialogTopListBox = listBox(self.dialogTopArea, label = 'Columns', toolTip = 'Select one of the columns', callback = self.dialogTopLineEdit.clear)
        
        self.dialogLabel = widgetLabel(self.dialog)
        
        self.dialogBottomArea = groupBox(self.dialog, label = 'Right Side')
        self.dialogBottomLineEdit = lineEdit(self.dialogBottomArea, label = 'Constant', toolTip = 'Must be a number')
        self.dialogBottomListBox = listBox(self.dialogBottomArea, label = 'Columns', toolTip = 'Select one of the columns', callback = self.dialogBottomLineEdit.clear)
        redRCommitButton(self.dialog, label = 'Done', callback = self.functionCommit)
        self.dialog.hide()
    def gotData(self, data):
        if data:
            self.R(self.Rvariables['math'] + '<-' + data.getData())
            self.data = self.Rvariables['math']
            self.table.setRTable(data.getData())
            self.dialogBottomListBox.update(self.R('colnames('+self.data+')', wantType = 'list'))
            self.dialogTopListBox.update(self.R('colnames('+self.data+')', wantType = 'list'))
        else:
            self.table.clear()
            
    def textChanged(self, s):
        print s
        self.functionListBox.scrollToItem(self.functionListBox.findItems(s, Qt.MatchStartsWith)[0])
        
    def functionDone(self):
        text = str(self.functionLineEdit.text())
        self.executeFunction(text)
        
    def funcionPressed(self):
        text = str(self.functionListBox.selectedItems()[0].text())
        self.executeFunction(text)
        
    def executeFunction(self, text):
        if text in ['log10', 'log2', 'as.numeric', 'as.character', 'exp']:
            self.dialogBottomArea.hide()
            self.dialog.show()
        else:
            self.dialogBottomArea.show()
            self.dialog.show()
        self.dialogLabel.setText(text)
    def functionCommit(self):
        try:
            if str(self.dialogTopLineEdit.text()) != '':
                topText = str(self.dialogTopLineEdit.text())
                try:
                    a = float(topText)
                except:
                    self.status.setText('Top Text Area Does Not Contain A Number')
                    return 
            else:
                topText = self.data+'$'+str(self.dialogTopListBox.selectedItems()[0].text())
                
            if self.dialogBottomArea.isVisible():
                if str(self.dialogBottomLineEdit.text()) != '':
                    bottomText = str(self.dialogBottomLineEdit.text())
                    try:
                        if str(self.dialogLabel.text()) not in ['match']:
                            a = float(bottomText)
                    except:
                        self.status.setText('Top Text Area Does Not Contain A Number')
                        return
                else:
                    bottomText = self.data+'$'+str(self.dialogBottomListBox.selectedItems()[0].text())
                    
            function = str(self.dialogLabel.text())
            
            if function in ['log10', 'log2', 'as.numeric', 'as.character', 'exp']:
                try:
                    self.R(self.data+'$'+function+str(self.counter)+'<-'+function+'('+topText+')')
                    self.table.setRTable(self.data)
                    self.counter += 1
                except:
                    self.status.setText('An error occured in your function')
                    
            elif function in ['match']:
                try:
                    self.R(self.data+'$'+function+str(self.counter)+'<-'+function+'('+topText+', '+bottomText+')')
                    self.table.setRTable(self.data)
                    self.counter += 1
                except:
                    self.status.setText('An error occured in your function')
            else:
                if function == 'add':
                    try:
                        self.R(self.data+'$'+'plus_'+str(self.counter)+'<-'+topText+' + '+bottomText)
                        self.table.setRTable(self.data)
                    except:
                        self.status.setText('An error occured in your function')
                elif function == 'subtract':
                    try:
                        self.R(self.data+'$'+'minus_'+str(self.counter)+'<-'+topText+' - '+bottomText)
                        self.table.setRTable(self.data)
                    except:
                        self.status.setText('An error occured in your function')
                elif function == 'multiply':
                    try:
                        self.R(self.data+'$'+'times_'+str(self.counter)+'<-as.numeric('+topText+') * as.numeric('+bottomText+')')
                        self.table.setRTable(self.data)
                    except:
                        self.status.setText('An error occured in your function')
                elif function == 'divide':
                    try:
                        self.R(self.data+'$'+'divide_'+str(self.counter)+'<-as.numeric('+topText+') / as.numeric('+bottomText+')')
                        self.table.setRTable(self.data)
                    except:
                        self.status.setText('An error occured in your function')
                elif function == 'logicAND':
                    try:
                        self.R(self.data+'$'+'logic_AND'+str(self.counter)+'<-'+topText+'&'+bottomText)
                    except:
                        self.status.setText('An error occured in your function')
                elif function == 'logicOR':
                    try:
                        self.R(self.data+'$'+'logic_OR'+str(self.counter)+'<-'+topText+'|'+bottomText)
                    except:
                        self.status.setText('An error occured in your function')
                self.counter += 1
            self.dialogBottomListBox.update(self.R('colnames('+self.data+')', wantType = 'list'))
            self.dialogTopListBox.update(self.R('colnames('+self.data+')', wantType = 'list'))
            newData = redRRDataFrame(data = self.data, parent = self.data)
            self.rSend("id0", newData)
            self.dialog.hide()
        except:
            self.status.setText('An error occured in your function')
            
    def getReportText(self, fileDir):
        text = 'Performed one or more mathematical opperations on the columns of the data.  See the Red-R .rrs file or the included notes for more information on what procedures were performed.\n\n'
        return text