"""
<name>Histogram</name>
<tags>Plotting</tags>
<icon>histogram2.png</icon>
"""
from OWRpy import * 
from libraries.base.signalClasses.RVariable import RVariable as redRRVariable
from libraries.base.signalClasses.RList import RList as redRRList
from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.commitButton import commitButton as redRCommitButton

class hist(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.RFunctionParam_x = ''
        self.column = ''
        self.needsColumns = 0
        self.inputs.addInput('id0', 'x', redRRList, self.processx)

        
        box = groupBox(self.controlArea, "Widget Box")
        #self.infoa = widgetLabel(box, "")
        self.column = comboBox(box, label='Data Element:')
        self.RFunctionParam_main = lineEdit(box, label = "Main Title")
        self.RFunctionParam_xlab = lineEdit(box, label = "X Label")
        self.bins = lineEdit(box, label = 'Bins:')
        self.plotArea = redRgraphicsView(self.controlArea,label='Histogram',displayLabel=False)
        self.commit = redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            #self.commitFunction()
            myclass = self.R('class('+self.RFunctionParam_x+')')
            if myclass in ['matrix', 'data.frame', 'list']:
                colnames = self.R('names('+self.RFunctionParam_x+')')
                if type(colnames) == type(''):
                    colnames = [colnames]
                    
                self.column.update(colnames)
                self.needsColumns = 1
                if self.commit.processOnInput():
                    self.commitFunction()
            
        else:
            self.RFunctionParam_x = ''
    def commitFunction(self):
        if self.RFunctionParam_x == '': return
        if self.needsColumns:
            ## check if numeric
            if self.R('class('+str(self.RFunctionParam_x)+'$'+str(self.column.currentText())+')') not in ['numeric']: 
                self.status.setText('Data not numeric')
                return
            injection = []
            if self.RFunctionParam_main.text() != '':
                injection.append('main = "'+str(self.RFunctionParam_main.text())+'"')
            if self.RFunctionParam_xlab.text() != '':
                injection.append('xlab = "'+str(self.RFunctionParam_xlab.text())+'"')
            if str(self.bins.text()) != '':
                injection.append('breaks = '+str(self.bins.text()))
            if injection != []:
                inj = ','.join(injection)
            else: inj = ''
        
        
            self.plotArea.plot('x=as.numeric('+str(self.RFunctionParam_x)+'$'+str(self.column.currentText())+')'+','+inj, function = 'hist')
            return
        else:
            if self.R('class('+str(self.RFunctionParam_x)+')') not in ['numeric']: 
                self.status.setText('Data not numeric')
                return
            try:
                self.plotArea.plot('x=as.numeric('+str(self.RFunctionParam_x)+','+inj, function = 'hist')
            except:
                self.status.setText('Please make sure that you used the right kind of data.')
    def getReportText(self, fileDir):
        if str(self.RFunctionParam_x) == '': return 'Nothing to plot from this widget'
        
        self.R('png(file="'+fileDir+'/plot'+str(self.widgetID)+'.png")', wantType = 'NoConversion')
            
        if self.needsColumns:
            injection = []
            if self.RFunctionParam_main.text() != '':
                injection.append('main = "'+str(self.RFunctionParam_main.text())+'"')
            if self.RFunctionParam_xlab.text() != '':
                injection.append('xlab = "'+str(self.RFunctionParam_xlab.text())+'"')
                
            if injection != []:
                inj = ','.join(injection)
            else: inj = ''
        
        
            self.R('hist(x='+str(self.RFunctionParam_x)+'[,"'+str(self.column.currentText())+'"]'+','+inj+')', wantType = 'NoConversion')
        else:
            try:
                self.R('hist(x='+str(self.RFunctionParam_x)+')', wantType = 'NoConversion')
            except:
                self.status.setText('Please make sure that you used the right kind of data.')
        self.R('dev.off()', wantType = 'NoConversion')
        text = 'The following plot was generated:\n\n'
        #text += '<img src="plot'+str(self.widgetID)+'.png" alt="Red-R R Plot" style="align:center"/></br>'
        text += '.. image:: '+fileDir+'/plot'+str(self.widgetID)+'.png\n    :scale: 50%%\n\n'
            
        return text
