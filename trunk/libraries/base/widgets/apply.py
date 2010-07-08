"""
<name>Apply</name>
<author>Anup Parikh (anup@red-r.org) and Kyle R Covington (kyle@red-r.org)</author>
<description>Applies math across a data table.  These functions could include max (maximum value), mean (the mean value), median (median value), etc.>description>
<RFunctions>base:apply</RFunctions>
<tags>Data Manipulation</tags>
<icon>rexecutor.png</icon>
<inputWidgets></inputWidgets>
<outputWidgets>plotting_plot, base_RDataTable, base_ListSelector, base_DataExplorer, base_rowcolPicker, base_rViewer</outputWidgets>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses.RDataFrame as rdf
import libraries.base.signalClasses.RVector as rvec
class apply(OWRpy): 
        globalSettingsList = ['functions']
        def __init__(self, parent=None, signalManager=None):
            OWRpy.__init__(self, parent, signalManager, "Apply", wantMainArea = 0, resizingEnabled = 1)
            self.setRvariableNames(["apply"])
            self.data = {}
             
            self.RFunctionParam_X = ''
            self.inputs = [("X", rdf.RDataFrame, self.processX)]
            self.outputs = [("apply Output", rvec.RVector)]
            
            area = redRGUI.widgetBox(self.controlArea,orientation='horizontal')       
            
            box = redRGUI.widgetBox(area)
            box.setMinimumWidth(200)
            area.layout().setAlignment(box,Qt.AlignLeft)
            
            self.functions =  redRGUI.listBox(box,  label = "Select Function",
            items=['mean','median','max','min','sum','log2', 'log10'],callback=self.functionSelect)
            self.functions.setSelectionMode(QAbstractItemView.SingleSelection)
            # self.functions.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding ,QSizePolicy.Expanding ))                
            # box.layout().setStretchFactor(self.functions.hb,4)
            
            redRGUI.separator(box,height=10)
            self.functionText = redRGUI.textEdit(box,label='This function will be applied:')
            
            self.RFunctionParamMARGIN_radioButtons =  redRGUI.radioButtons(box,  
            label = "to:", buttons = ['Rows', 'Columns'],setChecked='Rows',
            orientation='horizontal')
            
            redRGUI.button(box, "Commit", align='right', callback = self.commitFunction)
            
            self.outputTable = redRGUI.Rtable(area,sortable=True)

        def processX(self, data):
            if data:
                self.RFunctionParam_X=data.getData()
                self.data = data
                self.commitFunction()
            else:
                self.RFunctionParam_X=''
        def functionSelect(self):
            selection = self.functions.getCurrentSelection()
            self.functionText.setText(selection[0])
        def commitFunction(self):
            func = str(self.functionText.toPlainText())
            if str(self.RFunctionParam_X) == '' or func =='': return

            if not self.functions.findItems(func,Qt.MatchExactly):
                self.functions.addItem(func)
                self.saveGlobalSettings()

            injection = []
            
            if self.RFunctionParamMARGIN_radioButtons.getChecked() == 'Rows':
                string = 'MARGIN='+str(1)
                injection.append(string)
            else:
                string = 'MARGIN = '+str(2)
                injection.append(string)
                
                
            string = 'FUN='+str(self.functionText.toPlainText())
            injection.append(string)

            
            inj = ','.join(injection)
            try:
                self.R(self.Rvariables['apply']+'<-apply(X='+str(self.RFunctionParam_X)+','+inj+')')
            except: 
                return

            
            self.outputTable.setRTable(self.Rvariables['apply'])
            
            newData = rvec.RVector(data = self.Rvariables['apply'])

            self.rSend("apply Output", newData)
