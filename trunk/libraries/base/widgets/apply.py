"""
<name>Apply</name>
<author>Red-R Development Team</author>
<description>Applies math across a data table.  These functions could include max (maximum value), mean (the mean value), median (median value), etc.>description>
<RFunctions>base:apply</RFunctions>
<tags>Data Manipulation</tags>
<icon>rexecutor.png</icon>
<inputWidgets></inputWidgets>
<outputWidgets>plotting_plot, base_RDataTable, base_ListSelector, base_DataExplorer, base_rowcolPicker, base_rViewer</outputWidgets>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.signalClasses.RVector import RVector as redRRVector

from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.lineEdit import lineEdit as redRLineEdit
from libraries.base.qtWidgets.textEdit import textEdit as redRTextEdit
from libraries.base.qtWidgets.separator import separator
from libraries.base.qtWidgets.filterTable import filterTable as redRFilterTable
from libraries.base.qtWidgets.radioButtons import radioButtons
from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.checkBox import checkBox as redRCheckBox

class apply(OWRpy): 
    globalSettingsList = ['commitOnInput']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["apply"])
        self.data = {}
         
        self.RFunctionParam_X = ''
        self.inputs.addInput('id0', 'X', redRRDataFrame, self.processX)

        self.outputs.addOutput('id0', 'apply Output', redRRVector)

        
        area = widgetBox(self.controlArea,orientation='horizontal')       
        
        box = widgetBox(area)
        box.setMinimumWidth(200)
        area.layout().setAlignment(box,Qt.AlignLeft)
        
        self.functions =  listBox(box,  label = "Select Function",
        items=['mean','median','max','min','sum','log2', 'log10'],callback=self.functionSelect)
        self.functions.setSelectionMode(QAbstractItemView.SingleSelection)
        
        separator(box,height=10)
        self.functionText = redRTextEdit(box,label='Function:', orientation='vertical')
        self.parameters = redRLineEdit(box,label='Additional Parameters:', orientation='vertical')
        
        self.RFunctionParamMARGIN_radioButtons =  radioButtons(box,  
        label = "to:", buttons = ['Rows', 'Columns'],setChecked='Rows',
        orientation='horizontal')
        buttonBox = widgetBox(box,orientation='horizontal')
        self.commitOnInput = redRCheckBox(buttonBox, buttons = ['Commit on Input'],
        toolTips = ['Whenever this selection changes, send data forward.'])
        
        button(buttonBox, "Commit", align='right', callback = self.commitFunction)
        
        self.outputTable = redRFilterTable(area,sortable=True)

    def processX(self, data):
        if data:
            self.RFunctionParam_X=data.getData()
            self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_X=''
    def functionSelect(self):
        selection = self.functions.getCurrentSelection()
        f = selection[0].split('\n--')
        #print f
        self.functionText.setText(f[0])
        self.parameters.setText(', '.join(f[1:]))
    def commitFunction(self):
        func = str(self.functionText.toPlainText())
        paramText = str(self.parameters.text())
        if str(self.RFunctionParam_X) == '' or func =='': return
        
        params = []
        for x in paramText.split(','):
            if x.strip() !='':
                params.append(x.strip())
            
        saveAs = func + '\n--' + '\n--'.join(params)
        
        if not self.functions.findItems(saveAs,Qt.MatchExactly):
            self.functions.addItem(saveAs)
            self.saveGlobalSettings()

        injection = []
        
        if self.RFunctionParamMARGIN_radioButtons.getChecked() == 'Rows':
            string = 'MARGIN='+str(1)
        else:
            string = 'MARGIN = '+str(2)
        injection.append(string)
            
        string = 'FUN='+str(self.functionText.toPlainText())
        injection.append(string)
        
        injection.extend(params)
        
        inj = ','.join(injection)
        
        try:
            self.R(self.Rvariables['apply']+'<-apply(X='+str(self.RFunctionParam_X)+','+inj+')')
            self.outputTable.setRTable(self.Rvariables['apply'])
            newData = redRRVector(data = self.Rvariables['apply'])
            self.rSend("id0", newData)
        except: 
            self.R('%s <- NULL'%self.Rvariables['apply'],silent=True)
            self.outputTable.clear()
            self.rSend("id0", None)
        
        
    def getReportText(self, fileDir):
        return 'Data was manipulated using the apply feature performing the function %s along the %s of the data.\n\n' % (str(self.functionText.toPlainText()), self.RFunctionParamMARGIN_radioButtons.getChecked())
