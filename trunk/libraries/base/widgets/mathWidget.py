## Math widget.  Performs math on a column of a data table (RDataFrame).  Math functions can be added as the user wishes but many functions should already be present.  Note that if the widget fails you will get a message indicating that your function is unknown.

"""
<name>Math</name>
<author>Written by Kyle R. Covington, inspired by Anup Parikh</author>
<description>Performs basic mathematical opperations on a table.  These include changing the class of a column.  Opperations such as log, exponent, addition, sumtraction, multiplication, and division are supported.</description>
<RFunctions></RFunctions>
<tags>Data Manipulation</tags>
"""
from OWRpy import * 
import redRGUI 
class mathWidget(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Math", wantMainArea = 0, resizingEnabled = 1)
        
        self.setRvariableNames(['math'])
        
        self.counter = 1
        self.functionsList = ['log2', 'log10', 'add', 'subtract', 'multiply', 'divide', 'match', 'as.numeric', 'as.character', 'exp']
        
        self.inputs = [('Data Frame', signals.RDataFrame, self.gotData)]
        self.outputs = [('Data Frame', signals.RDataFrame)]
        #GUI#
        
        mainArea = redRGUI.widgetBox(self.controlArea, orientation = 'horizontal')
        leftArea = redRGUI.groupBox(mainArea, label = 'Table View')
        rightArea = redRGUI.groupBox(mainArea, label = 'Math Box')
        
        self.table = redRGUI.Rtable(leftArea)
        
        self.functionLineEdit = redRGUI.lineEdit(rightArea, label = 'Function Search or Run', callback = self.functionDone)
        QObject.connect(self.functionLineEdit, SIGNAL('textChanged(const QString&)'), lambda s: self.textChanged(s))
        
        self.functionListBox = redRGUI.listBox(rightArea, items = self.functionsList, callback = self.funcionPressed)
        
        self.helpButton = redRGUI.button(rightArea, label = 'Help') #, toolTip = 'Press this then select a function from the list for help.')
        self.dialog = redRGUI.dialog(self)
        self.dialogTopArea = redRGUI.groupBox(self.dialog, label = 'Left Side')
        self.dialogTopLineEdit = redRGUI.lineEdit(self.dialogTopArea, label = 'Constant', toolTip = 'Must be a number')
        self.dialogTopListBox = redRGUI.listBox(self.dialogTopArea, label = 'Columns', toolTip = 'Select one of the columns', callback = self.dialogTopLineEdit.clear)
        
        self.dialogLabel = redRGUI.widgetLabel(self.dialog)
        
        self.dialogBottomArea = redRGUI.groupBox(self.dialog, label = 'Right Side')
        self.dialogBottomLineEdit = redRGUI.lineEdit(self.dialogBottomArea, label = 'Constant', toolTip = 'Must be a number')
        self.dialogBottomListBox = redRGUI.listBox(self.dialogBottomArea, label = 'Columns', toolTip = 'Select one of the columns', callback = self.dialogBottomLineEdit.clear)
        redRGUI.button(self.dialog, label = 'Done', callback = self.functionCommit)
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
                        
            self.dialogBottomListBox.update(self.R('colnames('+self.data+')', wantType = 'list'))
            self.dialogTopListBox.update(self.R('colnames('+self.data+')', wantType = 'list'))
            newData = signals.RDataFrame(data = self.data, parent = self.data)
            self.rSend('Data Frame', newData)
            self.dialog.hide()
        except:
            self.status.setText('An error occured in your function')