"""
<name>Box Plot</name>
<tags>Plotting</tags>
<icon>boxplot.png</icon>
"""
from OWRpy import * 
import OWGUI, redRGUI
from libraries.base.signalClasses.RList import RList as redRRList
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.commitButton import commitButton as redRCommitButton
class boxplot(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', 'x', redRRList, self.processx)

        
        self.commit = redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,processOnInput=True)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            if self.commit.processOnInput():
                self.commitFunction()
    def commitFunction(self):
        if self.x == '': 
            self.status.setText('Do data. Can not plot')
            return
        try:
            self.Rplot('boxplot(x=as.list('+str(self.RFunctionParam_x)+'), notch = TRUE'+str(self.commandLine.text())+')')
        except:
            QMessageBox.information(self,'R Error', "Plotting failed.  Try to format the data in a way that is acceptable for this widget.\nSee the documentation for help.", 
            QMessageBox.Ok + QMessageBox.Default)
            return
    def getReportText(self, fileDir):
        if self.x == '': return 'Nothing to plot from this widget.\n\n'
        
        self.R('png(file="'+fileDir+'/plot'+str(self.widgetID)+'.png")', wantType = 'NoConversion')
            
        self.R('boxplot(x=as.list('+str(self.RFunctionParam_x)+'), notch = TRUE'+str(self.commandLine.text())+')', wantType = 'NoConversion')
        self.R('dev.off()', wantType = 'NoConversion')
        text = 'The following plot was generated:\n\n'
        #text += '<img src="plot'+str(self.widgetID)+'.png" alt="Red-R R Plot" style="align:center"/></br>'
        text += '.. image:: '+fileDir+'/plot'+str(self.widgetID)+'.png\n    :scale: 50%%\n\n'
            
        return text