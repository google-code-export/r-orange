"""
<name>Percentile Classifier</name>
<author>Kyle R. Covington</author>
<description>Appends a column to a data frame with the classifications of rows based on the values of a column being greater than some percentile.</description>
<tags>Data Classification</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class percentileClassifier(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Percentile Classifier", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["percentileClassifier_df", "percentileClassifier", 'percentileClassifier_cm'])
        self.data = ''
        self.dataParent = {}
        self.inputs = [('Data Frame', RvarClasses.RDataFrame, self.processData)]
        self.outputs = [('Data Frame', RvarClasses.RDataFrame)]
        
        ### GUI ###
        self.percentile_lineEdit = redRGUI.lineEdit(self.controlArea, label= 'Percentile')
        self.colNames_combo = redRGUI.comboBox(self.controlArea, label = 'Column Names')
        
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commit)
        
    def processData(self, data):
        if data:
            self.data = data['data']
            self.dataParent = data.copy()
            self.colNames_combo.update(self.R('colnames('+self.data+')'))
        else:
            self.data = ''
            self.dataParent = {}
        
        
        
    def commit(self):
        # set a column where the classes are either greater than or less than the xth percentile of the selected column
        
        if self.data == '': return
        if self.dataParent == {}: return
        percentile = str(self.percentile_lineEdit.text())
        column = str(self.colNames_combo.currentText())
        length = self.R('length(na.omit('+self.data+'[,\''+column+'\']))')
        self.R(self.Rvariables['percentileClassifier_df']+'<-'+self.data+'[!is.na('+self.data+'[,\''+column+'\']),]')
        self.R(self.Rvariables['percentileClassifier_df'] + '$' + self.Rvariables['percentileClassifier'] + '<-' + self.Rvariables['percentileClassifier_df'] + '[,\''+column+'\'] > sort('+self.Rvariables['percentileClassifier_df']+'[,\''+column+'\'])['+str(percentile)+'/100*'+str(length)+']')
        self.dataParent['data'] = self.Rvariables['percentileClassifier_df']
        self.dataParent['parent'] = self.Rvariables['percentileClassifier_df']
        self.rSend('Data Frame', self.dataParent)