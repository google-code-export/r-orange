"""
<name>Histogram</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
class hist(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.RFunctionParam_x = ''
        self.column = ''
        self.needsColumns = 0
        self.inputs = [("x", RvarClasses.RVariable, self.processx)]
        
        box = OWGUI.widgetBox(self.controlArea, "Widget Box")
        self.infoa = OWGUI.widgetLabel(box, "")
        self.columnPicker = OWGUI.comboBox(box, self, 'column', label='Data Column:')
        OWGUI.button(box, self, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data["data"]
            #self.commitFunction()
            myclass = self.R('class('+self.RFunctionParam_x+')')
            if myclass == 'matrix' or myclass == 'data.frame':
                self.columnPicker.addItems(self.R('colnames('+self.RFunctionParam_x+')'))
                self.needsColumns = 1
            else:
                self.commitFunction()
    def commitFunction(self):
        if self.x == '': return
        if self.needsColumns:
            self.Rplot('hist(x='+str(self.RFunctionParam_x)+'[,"'+str(self.columnPicker.currentText())+'"])', 3,3)
            return
        else:
            try:
                self.Rplot('hist(x='+str(self.RFunctionParam_x)+')', 3, 3)
            except:
                self.infoa.setText('Please make sure that you used the right kind of data.')