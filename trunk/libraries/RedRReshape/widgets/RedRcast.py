"""
<name>Cast</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>reshape:cast</RFunctions>
<tags>Reshape</tags>
<icon></icon>
"""
from OWRpy import * 
from libraries.base.qtWidgets.lineEdit import lineEdit as redRlineEdit 
from libraries.base.qtWidgets.radioButtons import radioButtons as redRradioButtons 
from libraries.base.qtWidgets.comboBox import comboBox as redRcomboBox 
from libraries.base.qtWidgets.checkBox import checkBox as redRcheckBox 
from libraries.base.qtWidgets.textEdit import textEdit as redRtextEdit 
from libraries.base.qtWidgets.gridBox import gridBox
import libraries.base.signalClasses as signals

class RedRcast(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["cast"])
        self.data = {}
        self.require_librarys(["reshape", "gregmisc"])
        self.RFunctionParam_data = ''
        self.inputs.addInput("data", "Molten Data", signals.RDataFrame.RDataFrame, self.processdata)
        self.outputs.addOutput("cast Output","Reshaped Data (Data Table)", signals.RDataFrame.RDataFrame)
        self.outputs.addOutput('cast Output List', "Reshaped Data (Data List)", signals.RList.RList)
        
        box = gridBox(self.controlArea)
        
        self.useAllRemainingCheckbox = redRcheckBox(box.cell(0,0), label = 'Persistent Columns:', buttons = [('useAll', 'Make All Available Columns Static')], callback = self.useAllRemainingCheckboxChecked, setChecked = ['useAll'])
        self.RFunctionParamformula_listBox = redRListBox(box.cell(0,0), label = "Static Variables:", toolTip = "These are the variables that will not be changed in the new data")
        self.RFunctionParamformula_listBox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.RFunctionParamformula_listBox.hide()
        self.aggregatingColumns = redRListBox(box.cell(0,1), label = "Aggregating Variables:", toolTip = "These variables will be combined to make new columns with the values in the Value Column filling them")
        self.aggregationMethod = redRradioButtons(box.cell(0,2), label = 'Aggregation Method:', buttons = [(' | ', 'List'), ('+', 'Data Table')], setChecked = '+', orientation = 'horizontal')
        
        self.aggregatingColumns.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.RFunctionParamfun_aggregate_lineEdit = redRcomboBox(box.cell(0,2), label = "Aggregating Function:", items = ['NULL', 'mean', 'median', 'mode', 'range', 'sd', 'mean and sd', 'custom'])
        #self.valueColumn = redRcomboBox(box.cell(0,2), label = "Value Column:", toolTip = "Select the column that represents the values to be cast, these will generally be named values if the data comes from melt.")
        self.customFunction = redRlineEdit(box.cell(0,2), label = 'Custom Function:', toolTip = 'Sets a custom aggregation function.  This will take a single argument "a" and must be written as a single line, eg: mean(a)')
        self.margins = redRListBox(box.cell(0,2), label = 'Margins')
        self.margins.setSelectionMode(QAbstractItemView.ExtendedSelection)
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRtextEdit(self.controlArea, label = "R Output Window")
    def useAllRemainingCheckboxChecked(self):
        if 'useAll' in self.useAllRemainingCheckbox.getCheckedIds():
            self.RFunctionParamformula_listBox.setEnabled(False)
            self.RFunctionParamformula_listBox.hide()
        else:
            self.RFunctionParamformula_listBox.setEnabled(True)
            self.RFunctionParamformula_listBox.show()
    def processdata(self, data):
        
        if data:
            self.RFunctionParam_data=data.getData()
            #self.data = data
            names = self.R('names('+self.RFunctionParam_data+')')
            self.RFunctionParamformula_listBox.update(names)
            self.aggregatingColumns.update(names)
            #self.valueColumn.update(names)
            self.margins.update([('FALSE', 'Don\'t Use'), ('TRUE', 'Use All'), ('grand_col', 'Grand Column'), ('grand_row', 'Grand Row')] + [(n, n) for n in names])
            self.commitFunction()
        else:
            self.RFunctionParam_data=''
    def commitFunction(self):
        if str(self.RFunctionParam_data) == '': return
        injection = []
        ## build the formula
        if 'useAll' in self.useAllRemainingCheckbox.getCheckedIds():
            static = '...'
        else:
            static = ' + '.join([unicode(i) for i in self.RFunctionParamformula_listBox.selectedItems()])
        if len(self.aggregatingColumns.selectedItems()) == 0: 
            self.status.setText('You must select an item to aggregate over')
            return
        elif len(self.aggregatingColumns.selectedItems()) == 1:
            dtype = 0
            agg = self.aggregatingColumns.selectedItems().values()[0]
        else:
            if self.aggregationMethod.getCheckedId() == '+':
                dtype = 0
                agg = ' + '.join([unicode(i) for i in self.aggregatingColumns.selectedItems()])
            else:
                dtype = 1
                agg = ' | '.join([unicode(i) for i in self.aggregatingColumns.selectedItems()])
        string = ',formula=%s~%s' % (static, agg)
        injection.append(string)
        if 'TRUE' in self.margins.selectedItems():
            injection.append(', margins = TRUE')
        elif 'FALSE' in self.margins.selectedItems():
            injection.append(', margins = FALSE')
        elif len(self.margins.selectedItems()) == 0:
            pass
        else:
            injection.append(', margins = c("%s")' % unicode('","'.join(i for i in self.margins.selectedItems() if i not in ['TRUE', 'FALSE'])))
        if self.RFunctionParamfun_aggregate_lineEdit.currentText() not in ['mean and sd', 'custom']:
            string = ',fun.aggregate='+str(self.RFunctionParamfun_aggregate_lineEdit.currentText())+''
            injection.append(string)
        elif self.RFunctionParamfun_aggregate_lineEdit.currentText() == 'mean and sd':
            self.R('krcmsd<-function(a){return(list(Mean = mean(a),SD = sd(a), SEM = sd(a)/sqrt(length(a))))}', wantType = 'NoConversion')
            string = ',fun.aggregate=krcmsd'
            injection.append(string)
        else:
            self.R('tempfun<-function(a){return(%s)}' % self.customFunction.text(), wantType = 'NoConversion')
            injection.append(',fun.aggregate = tempfun')
        inj = ''.join(injection)
        ## rename the value column
        #self.R('rename.vars(%s, from = "%s", to = "value")' % (self.RFunctionParam_data, self.valueColumn.currentText()), wantType = 'NoConversion')
        self.R(self.Rvariables['cast']+'<-cast(data='+str(self.RFunctionParam_data)+inj+')', wantType = 'NoConversion')
        ## rename the parent variable back
        self.R('names(%s)<-make.names(names(%s))' % (self.Rvariables['cast'], self.Rvariables['cast']), wantType = 'NoConversion')
        #self.R('rename.vars(%s, from = "value", to = "%s")' % (self.RFunctionParam_data, self.valueColumn.currentText()), wantType = 'NoConversion')
        self.R('txt<-capture.output(head(%s))' % (self.Rvariables['cast'],), wantType = 'NoConversion')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertPlainText('This is your data:\n\n'+tmp)
        if dtype == 0: ## it's a data.frame
            newData = signals.RDataFrame.RDataFrame(self, data = 'as.data.frame('+self.Rvariables['cast']+')', parent = 'as.data.frame('+self.Rvariables['cast']+')')
            self.rSend('cast Output', newData)
            self.rSend('cast Output List', None)
        elif dtype == 1: ## it's a list
            newData = signals.RList.RList(self, data = self.Rvariables['cast'])
            self.rSend('cast Output List', newData)
            self.rSend('cast Output', None)