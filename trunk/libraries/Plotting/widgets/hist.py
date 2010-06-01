"""
<name>Histogram</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Makes a histogram of data.  This data should be in the form of a single 'vector'.  Use of the Row of Column selectors or perhaps the list selector may be helpful in this.</description>
<RFunctions>graphics:hist</RFunctions>
<tags>Plotting</tags>
<icon>histogram.png</icon>
"""
from OWRpy import * 
import OWGUI 
class hist(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Histogram", wantMainArea = 0, resizingEnabled = 1)
        self.RFunctionParam_x = ''
        self.column = ''
        self.needsColumns = 0
        self.inputs = [("x", signals.RVariable, self.processx)]
        
        box = redRGUI.groupBox(self.controlArea, "Widget Box")
        #self.infoa = redRGUI.widgetLabel(box, "")
        self.column = redRGUI.comboBox(box, label='Data Column:')
        self.RFunctionParam_main = redRGUI.lineEdit(box, label = "Main Title")
        self.RFunctionParam_xlab = redRGUI.lineEdit(box, label = "X Label")
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            #self.commitFunction()
            myclass = self.R('class('+self.RFunctionParam_x+')')
            if myclass == 'matrix' or myclass == 'data.frame':
                colnames = self.R('colnames('+self.RFunctionParam_x+')')
                if type(colnames) == type(''):
                    colnames = [colnames]
                    
                self.column.update(colnames)
                self.needsColumns = 1
                self.commitFunction()
            
        else:
            self.RFunctionParam_x = ''
    def commitFunction(self):
        if self.RFunctionParam_x == '': return
        if self.needsColumns:
            injection = []
            if self.RFunctionParam_main.text() != '':
                injection.append('main = "'+str(self.RFunctionParam_main.text())+'"')
            if self.RFunctionParam_xlab.text() != '':
                injection.append('xlab = "'+str(self.RFunctionParam_xlab.text())+'"')
                
            if injection != []:
                inj = ','.join(injection)
            else: inj = ''
        
        
            self.Rplot('hist(x='+str(self.RFunctionParam_x)+'[,"'+str(self.column.currentText())+'"]'+','+inj+')', 3,3)
            return
        else:
            try:
                self.Rplot('hist(x='+str(self.RFunctionParam_x)+')', 3, 3)
            except:
                self.status.setText('Please make sure that you used the right kind of data.')
