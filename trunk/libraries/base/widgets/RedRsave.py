"""
<name>RedRsave</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>base:save</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
from libraries.base.qtWidgets.lineEdit import lineEdit as redRlineEdit 
#from libraries.base.qtWidgets.radioBox import radioBox as redRradioBox 
from libraries.base.qtWidgets.comboBox import comboBox as redRcomboBox 
from libraries.base.qtWidgets.checkBox import checkBox as redRcheckBox 
from libraries.base.qtWidgets.textEdit import textEdit as redRtextEdit 
import libraries.base.signalClasses as signals

class RedRsave(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.RFunctionParam_list = {}
        self.inputs.addInput("list", "list", signals.RVariable.RVariable, self.processlist, multiple = True)
        
        self.RFunctionParamfile_lineEdit = redRlineEdit(self.controlArea, label = "file:", text = '')
        redRbutton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processlist(self, data, id):
        if data:
            self.RFunctionParam_list[id]=data.getData()
            
        else:
            self.RFunctionParam_list[id]=''
    def commitFunction(self):
        if str(self.RFunctionParam_list) == {}: return
        if str(self.RFunctionParamfile_lineEdit.text()) == '':
            import redREnviron
            res = QFileDialog.getSaveFileName(self, 'Save File Name', redREnviron.directoryNames['documentsDir'], 'R Data File (.RData)')
            if res.isEmpty(): return
            self.RFunctionParamfile_lineEdit.setText(str(res))
        injection = []
        #if str(self.RFunctionParamfile_lineEdit.text()) != '':
        string = 'file="'+str(self.RFunctionParamfile_lineEdit.text())+'"'
        injection.append(string)
        inj = ','.join(injection)
        index = 0
        items = []
        for i in [str(a) for (k, a) in self.RFunctionParam_list.items()]:
            self.R('temp%s<-%s' % (str(index), (i)))
            
            items.append('temp%s' % str(index))
            index += 1
        self.R('save('+str(','.join(items))+','+inj+')')
        for i in items:
            self.R('rm(%s)' % i)