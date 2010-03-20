"""
<name>pamr.from.excel</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
import redRGUI 
class pamr_from_excel(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["pamr.from.excel"])
        self.RFunctionParam_sample_labels = "FALSE"
        self.RFunctionParam_batch_labels = "FALSE"
        self.RFunctionParam_file = ""
        self.RFunctionParam_ncols = ""
        self.loadSettings() 
        self.outputs = [("pamr.from.excel Output", RvarClasses.RVariable)]
        
        self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
        box = redRGUI.tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.RFunctionParamsample_labels_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "sample_labels:")
        self.RFunctionParambatch_labels_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "batch_labels:")
        redRGUI.button(self.standardTab, "Load File", callback = self.loadFile)
        self.RFunctionParamfile_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "file:")
        self.RFunctionParamncols_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "ncols:")
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        redRGUI.button(self.controlArea, "Report", callback = self.sendReport)
    def loadFile(self):
        file = self.R('(choose.files())')
        self.RFunctionParamfile_lineEdit.setText(str(file))
    def commitFunction(self):
        if str(self.RFunctionParamfile_lineEdit.text()) == '': return
        if str(self.RFunctionParamncols_lineEdit.text()) == '': return
        injection = []
        if str(self.RFunctionParamsample_labels_lineEdit.text()) != '':
            string = 'sample_labels='+str(self.RFunctionParamsample_labels_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParambatch_labels_lineEdit.text()) != '':
            string = 'batch_labels='+str(self.RFunctionParambatch_labels_lineEdit.text())
            injection.append(string)
        if str(self.RFunctionParamfile_lineEdit.text()) != '':
            string = 'file="'+str(self.RFunctionParamfile_lineEdit.text()).replace('\\','/')+'"'
            injection.append(string)
        if str(self.RFunctionParamncols_lineEdit.text()) != '':
            string = 'ncols='+str(self.RFunctionParamncols_lineEdit.text())
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['pamr.from.excel']+'<-pamr.from.excel('+inj+')')
        self.rSend("pamr.from.excel Output", {"data":self.Rvariables["pamr.from.excel"]})
    def compileReport(self):
        self.reportSettings('Function Settings', [('sample_labels',str(self.RFunctionParam_sample_labels))])
        self.reportSettings('Function Settings', [('batch_labels',str(self.RFunctionParam_batch_labels))])
        self.reportSettings('Function Settings', [('file',str(self.RFunctionParam_file))])
        self.reportSettings('Function Settings', [('ncols',str(self.RFunctionParam_ncols))])
        self.reportRaw(self.Rvariables["pamr.from.excel"])
    def sendReport(self):
        self.compileReport()
        self.showReport()
