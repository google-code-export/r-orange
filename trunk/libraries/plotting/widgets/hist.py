"""
<name>Histogram</name>
<tags>Plotting</tags>
<icon>histogram2.png</icon>
"""
from OWRpy import * 
import redRGUI, signals

class hist(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_x = ''
        self.column = ''
        self.needsColumns = 0
        self.inputs.addInput('id0', 'x', signals.base.RList, self.processx)

        
        box = redRGUI.base.groupBox(self.controlArea, "Widget Box")
        #self.infoa = widgetLabel(box, "")
        self.column = redRGUI.base.comboBox(box, label='Data Element:')
        self.RFunctionParam_main = redRGUI.base.lineEdit(box, label = "Main Title")
        self.RFunctionParam_xlab = redRGUI.base.lineEdit(box, label = "X Label")
        self.bins = redRGUI.base.lineEdit(box, label = 'Bins:')
        self.plotArea = redRGUI.base.graphicsView(self.controlArea,label='Histogram',displayLabel=False)
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=str(data.getData())
            #self.commitFunction()
            myclass = self.R('class('+self.RFunctionParam_x+')')
            if myclass in ['matrix', 'data.frame', 'list']:
                colnames = self.R('names(as.data.frame('+self.RFunctionParam_x+'))')
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
            if self.R('class('+unicode(self.RFunctionParam_x)+'$'+unicode(self.column.currentText())+')') not in ['numeric']: 
                self.status.setText('Data not numeric')
                return
            injection = []
            if self.RFunctionParam_main.text() != '':
                injection.append('main = "'+unicode(self.RFunctionParam_main.text())+'"')
            if self.RFunctionParam_xlab.text() != '':
                injection.append('xlab = "'+unicode(self.RFunctionParam_xlab.text())+'"')
            if unicode(self.bins.text()) != '':
                injection.append('breaks = '+unicode(self.bins.text()))
            if injection != []:
                inj = ','.join(injection)
            else: inj = ''
        
        
            self.plotArea.plot('x=as.numeric('+unicode(self.RFunctionParam_x)+'$'+unicode(self.column.currentText())+')'+','+inj, function = 'hist')
            return
        else:
            if self.R('class('+unicode(self.RFunctionParam_x)+')') not in ['numeric']: 
                self.status.setText('Data not numeric')
                return
            try:
                self.plotArea.plot('x=as.numeric('+unicode(self.RFunctionParam_x)+','+inj, function = 'hist')
            except:
                self.status.setText('Please make sure that you used the right kind of data.')