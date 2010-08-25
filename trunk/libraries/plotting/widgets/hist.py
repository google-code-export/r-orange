"""
<name>Histogram</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Makes a histogram of data.  This data should be in the form of a single 'vector'.  Use of the Row of Column selectors or perhaps the list selector may be helpful in this.</description>
<RFunctions>graphics:hist</RFunctions>
<tags>Plotting</tags>
<icon>histogram2.png</icon>
"""
from OWRpy import * 
import OWGUI 
import libraries.base.signalClasses.RVariable as rvar
from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.button import button
class hist(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.RFunctionParam_x = ''
        self.column = ''
        self.needsColumns = 0
        self.inputs = [("x", rvar.RVariable, self.processx)]
        
        box = groupBox(self.controlArea, "Widget Box")
        #self.infoa = widgetLabel(box, "")
        self.column = comboBox(box, label='Data Column:')
        self.RFunctionParam_main = lineEdit(box, label = "Main Title")
        self.RFunctionParam_xlab = lineEdit(box, label = "X Label")
        button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
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
    def getReportText(self, fileDir):
        if str(self.RFunctionParam_x) == '': return 'Nothing to plot from this widget'
        
        self.R('png(file="'+fileDir+'/plot'+str(self.widgetID)+'.png")')
            
        if self.needsColumns:
            injection = []
            if self.RFunctionParam_main.text() != '':
                injection.append('main = "'+str(self.RFunctionParam_main.text())+'"')
            if self.RFunctionParam_xlab.text() != '':
                injection.append('xlab = "'+str(self.RFunctionParam_xlab.text())+'"')
                
            if injection != []:
                inj = ','.join(injection)
            else: inj = ''
        
        
            self.R('hist(x='+str(self.RFunctionParam_x)+'[,"'+str(self.column.currentText())+'"]'+','+inj+')')
        else:
            try:
                self.R('hist(x='+str(self.RFunctionParam_x)+')')
            except:
                self.status.setText('Please make sure that you used the right kind of data.')
        self.R('dev.off()')
        text = 'The following plot was generated:\n\n'
        #text += '<img src="plot'+str(self.widgetID)+'.png" alt="Red-R R Plot" style="align:center"/></br>'
        text += '.. image:: '+fileDir+'/plot'+str(self.widgetID)+'.png\n    :scale: 50%%\n\n'
            
        return text
