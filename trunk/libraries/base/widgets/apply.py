"""
<name>Apply</name>
<tags>Data Manipulation</tags>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.signalClasses.RMatrix import RMatrix as redRRMatrix

from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.spinBox import spinBox as RedRSpinBox
from libraries.base.qtWidgets.lineEdit import lineEdit as redRLineEdit
from libraries.base.qtWidgets.textEdit import textEdit as redRTextEdit
from libraries.base.qtWidgets.separator import separator
from libraries.base.qtWidgets.filterTable import filterTable as redRFilterTable
from libraries.base.qtWidgets.radioButtons import radioButtons
from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.checkBox import checkBox as redRCheckBox

class apply(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["apply"])
        self.numDims = 2
        self.data=None
        self.inputs.addInput('id0', 'X', redRRMatrix, self.processX)

        self.outputs.addOutput('id0', 'apply Output', redRRDataFrame)

        
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
        
        self.demension =  radioButtons(box, label = "To:", buttons = ['Rows', 'Columns',''],
        setChecked='Rows', orientation='horizontal',callback= lambda: self.dimensionChange(1))
        self.indexSpinBox = RedRSpinBox(self.demension.box, label='Demension', displayLabel=False,
        min = 1, value = 1, callback= lambda: self.dimensionChange(2))
        buttonBox = widgetBox(box,orientation='horizontal')
        
        
        self.commit = redRCommitButton(buttonBox, "Commit", alignment=Qt.AlignLeft, 
        callback = self.commitFunction, processOnInput=True,processOnChange=True)
        
        self.outputTable = redRFilterTable(area,label='Results of Apply', sortable=True)

    def dimensionChange(self,type):
        if type == 1:
            if self.demension.getChecked() =='Rows':
                self.indexSpinBox.setValue(1)
            else:
                self.indexSpinBox.setValue(2)
        else:
            if self.indexSpinBox.value() == 1:
                self.demension.setChecked('Rows')
            elif self.indexSpinBox.value() == 2:
                self.demension.setChecked('Columns')
            else:
                self.demension.setChecked('')
            
    def processX(self, data):
        if data:
            self.data=data.getData()
            self.numDims = self.R('length(dim(%s))' % self.data, silent=True)
            self.indexSpinBox.setMaximum(self.numDims)
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.data=None
    def functionSelect(self):
        selection = self.functions.getCurrentSelection()
        f = selection[0].split('\n--')
        #print f
        self.functionText.setText(f[0])
        self.parameters.setText(', '.join(f[1:]))
        if self.commit.processOnChange():
            self.commitFunction()
    def commitFunction(self):
        func = str(self.functionText.toPlainText())
        paramText = str(self.parameters.text())
        if str(self.data) == None or func =='': return
        
        params = []
        for x in paramText.split(','):
            if x.strip() !='':
                params.append(x.strip())
            
        saveAs = func 
        if len(params):
            saveAs += '\n--' + '\n--'.join(params)
        
        if not self.functions.findItems(saveAs,Qt.MatchExactly):
            self.functions.addItem(saveAs)
            self.saveGlobalSettings()

        injection = []
        string = 'MARGIN = %s' % str(self.indexSpinBox.value())
        injection.append(string)
            
        string = 'FUN='+str(self.functionText.toPlainText())
        injection.append(string)
        
        injection.extend(params)
        
        inj = ','.join(injection)
        
        # try:
        self.R(self.Rvariables['apply']+'<- as.data.frame(apply(X='+str(self.data)+','+inj+'))', wantType = 'NoConversion')
        self.outputTable.setRTable(self.Rvariables['apply'])
        newData = redRRDataFrame(data = self.Rvariables['apply'])
        self.rSend("id0", newData)
        # except: 
            # self.R('%s <- NULL'%self.Rvariables['apply'],silent=True)
            # self.outputTable.clear()
            # self.rSend("id0", None)
        
        
    def getReportText(self, fileDir):
        return 'Data was manipulated using the apply feature performing the function %s along the %s of the data.\n\n' % (str(self.functionText.toPlainText()), self.demension.getChecked())
