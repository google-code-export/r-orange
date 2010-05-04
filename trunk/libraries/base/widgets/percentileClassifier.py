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
        self.loadSettings()
        self.inputs = [('Data Frame', signals.RDataFrame, self.processData)]
        self.outputs = [('Data Frame', signals.RDataFrame)]
        
        ### GUI ###
        self.colNames_listBox = redRGUI.listBox(self.controlArea, label = 'Column Names:')
        self.colNames_listBox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.percentile_spinBox = redRGUI.spinBox(self.controlArea, label= 'Percentile Cutoff Selector:', min = 0, max = 100)
        self.percentile_lineEdit = redRGUI.lineEdit(self.controlArea, label = 'Percentile Cutoff:', toolTip = 'Input multiple cutoffs in the form; a, b, c.  Where a, b, and c are cutoffs.\nThis takes the place of the Percentile Cutoff Selector if not blank.')
        self.outputWindow = redRGUI.textEdit(self.controlArea, label = 'Output Summary')
        
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commit)
        
    def processData(self, data):
        if data:
            self.data = data['data']
            self.dataParent = data.copy()
            self.colNames_listBox.update(self.R('colnames('+self.data+')'))
            self.outputWindow.clear()
            self.commit()
        else:
            self.data = ''
            self.dataParent = {}
        
        
        
    def commit(self):
        # set a column where the classes are either greater than or less than the xth percentile of the selected column
        self.outputWindow.clear()
        if self.data == '': 
            self.outputWindow.insertHtml('No data to work with')
            return
        if self.dataParent == {}: 
            self.outputWindow.insertHtml('No data to work with')
            return
        items = self.colNames_listBox.selectedItems()
        if len(items) == 0: 
            self.outputWindow.insertHtml('No items selected in the Column Names box')
            return
        percentile = [str(self.percentile_spinBox.value())]
        if str(self.percentile_lineEdit.text()) not in ['', ' ']:
            lineText = str(self.percentile_lineEdit.text())
            lineText.replace(' ', '')
            percentile = lineText.split(',')
        self.R(self.Rvariables['percentileClassifier_df']+'<-'+self.data)
        self.outputWindow.insertHtml('<table class="reference" cellspacing="0" border="1" width="100%"><tr><th align="left" width="50%">New Column Name</th><th align="left" width="50%">Number above percentile</th></tr>')
        for percent in percentile:
            for item in items:
                
                column = str(item.text())
                length = self.R('length(na.omit('+self.data+'[,\''+column+'\']))')
                
                self.R(self.Rvariables['percentileClassifier_df'] + '$' + column+'_'+str(percent).strip(' ')+'percentile' + '<- !is.na(' + self.Rvariables['percentileClassifier_df'] +'$'+column+ ') & ' + self.Rvariables['percentileClassifier_df'] + '$'+column+' > sort('+self.Rvariables['percentileClassifier_df']+'$'+column+')['+str(percent).strip(' ')+'/100*'+str(length)+']')
                self.outputWindow.insertHtml('<tr><td width="50%">' + column+'_'+str(percent)+'percentile</td><td width="50%">'+str(self.R('sum(as.numeric('+self.Rvariables['percentileClassifier_df'] + '$' + column+'_'+str(percent).strip(' ')+'percentile))'))+'</td></tr>')
        self.outputWindow.insertHtml('</table>')
        newData = self.dataParent.copy()
        newData.data = self.Rvariables['percentileClassifier_df']
        self.rSend('Data Frame', newData)