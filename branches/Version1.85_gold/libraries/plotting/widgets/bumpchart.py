"""
<name>bumpchart</name>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
class bumpchart(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_y = ''
        self.inputs.addInput('id0', 'y', signals.base.RDataFrame, self.processy)

        
        self.RFunctionParammar_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "mar:", text = 'c(2,8,5,8)')
        self.RFunctionParamlty_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "lty:", text = '1')
        self.RFunctionParamlabels_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "labels:", text = 'rownames(y)')
        self.RFunctionParamrank_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "rank:", text = 'TRUE')
        self.RFunctionParampch_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "pch:", text = '19')
        self.RFunctionParamtop_labels_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "top_labels:", text = 'colnames(y)')
        self.RFunctionParamcol_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "col:", text = 'par("fg")')
        self.RFunctionParamlwd_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = "lwd:", text = '1')
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
    def processy(self, data):
        if not self.require_librarys(["plotrix"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_y=data.getData()
            #self.data = data
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_y=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_y) == '': return
        injection = []
        if unicode(self.RFunctionParammar_lineEdit.text()) != '':
            string = 'mar='+unicode(self.RFunctionParammar_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamlty_lineEdit.text()) != '':
            string = 'lty='+unicode(self.RFunctionParamlty_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamlabels_lineEdit.text()) != '':
            string = 'labels='+unicode(self.RFunctionParamlabels_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamrank_lineEdit.text()) != '':
            string = 'rank='+unicode(self.RFunctionParamrank_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParampch_lineEdit.text()) != '':
            string = 'pch='+unicode(self.RFunctionParampch_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamtop_labels_lineEdit.text()) != '':
            string = 'top.labels='+unicode(self.RFunctionParamtop_labels_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamcol_lineEdit.text()) != '':
            string = 'col='+unicode(self.RFunctionParamcol_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamlwd_lineEdit.text()) != '':
            string = 'lwd='+unicode(self.RFunctionParamlwd_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        self.R('y<-'+unicode(self.RFunctionParam_y))
        self.R('bumpchart(y='+unicode(self.RFunctionParam_y)+','+inj+')')