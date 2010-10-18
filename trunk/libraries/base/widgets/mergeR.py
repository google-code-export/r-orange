"""
<name>Merge</name>
<tags>Data Manipulation</tags>
<icon>merge2.png</icon>
"""

from OWRpy import *
import redRGUI
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame

from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.radioButtons import radioButtons
class mergeR(OWRpy):
    globalSettingsList = ['mergeLikeThis']

    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        
        # self.dataParentA = {}
        # self.dataParentB = {}
        self.dataA = ''
        self.dataB = ''
        
        
        self.inputs.addInput('id0', 'Dataset A', redRRDataFrame, self.processA)
        self.inputs.addInput('id1', 'Dataset B', redRRDataFrame, self.processB)

        self.outputs.addOutput('id0', 'Merged', redRRDataFrame)


        #default values        
        self.colAsel = None
        self.colBsel = None
        #self.forceMergeAll = 0 #checkbox value for forcing merger on all data, default is to remove instances from the rows or cols.
        
        #set R variable names
        self.setRvariableNames(['merged'])
                
        #GUI
        
        infoBox = groupBox(self.controlArea, "Info")
        self.infoa = widgetLabel(infoBox, "No Data Loaded")
        infoBox.hide()
        layk = QWidget(self)
        self.controlArea.layout().addWidget(layk)
        grid = QGridLayout()
        grid.setMargin(0)
        layk.setLayout(grid)
        
        pickA = groupBox(self.controlArea, "Select Columns to Merge From A")
        grid.addWidget(pickA, 0,0)
        self.colA = listBox(pickA, callback = self.setcolA)
        
        
        pickB = groupBox(self.controlArea, "Select Columns to Merge From B")
        grid.addWidget(pickB, 0,1)
        self.colB = listBox(pickB, callback = self.setcolB)
        

        self.sortOption = checkBox(self.bottomAreaLeft, buttons = ['Sort by Selected Column'], 
        toolTips = ['logical. Should the results be sorted on the by columns?'])
        self.bottomAreaLeft.layout().setAlignment(self.sortOption, Qt.AlignLeft)
        self.mergeOptions = radioButtons(self.bottomAreaCenter,buttons=['A+B','B+A','AB'],setChecked='A+B',
        orientation='horizontal')
        self.bottomAreaCenter.layout().setAlignment(self.mergeOptions, Qt.AlignCenter)
        self.mergeLikeThis = checkBox(self.bottomAreaRight, buttons = ['Merge on Connect'], 
        toolTips = ['Whenever this widget gets data it should try to merge as was done here'])
        redRCommitButton(self.bottomAreaRight, 'Commit', callback = self.run)
        
    def processA(self, data):
        #print 'processA'
        if not data:
            self.colA.clear()
            return 
        self.dataA = str(data.getData())
        self.dataParentA = data
        colsA = self.R('colnames('+self.dataA+')') #collect the sample names to make the differential matrix
        
        if type(colsA) is str:
            colsA = [colsA]
        colsA.insert(0, 'Rownames')
        self.colA.update(colsA)

        if 'Merge on Connect' in self.mergeLikeThis.getChecked():
            self.run()
        
    def processB(self, data):
        #print 'processB'
        if not data:
            self.colB.clear()
            return 
        self.dataB = str(data.getData())
        self.dataParentB = data
        colsB = self.R('colnames('+self.dataB+')') #collect the sample names to make the differential matrix
        if type(colsB) is str:
            colsB = [colsB]
        colsB.insert(0, 'Rownames')
        self.colB.update(colsB)
                
        if 'Merge on Connect' in self.mergeLikeThis.getChecked():
            self.run()
    
    def run(self):
        if self.dataA == '': return
        if self.dataB == '': return
        
        if len(self.colA.selectedItems()) == 0 or len(self.colB.selectedItems()) == 0:
            self.status.setText('Please make valid column selections')
            return
        if self.dataA != '' and self.dataB != '':
            h = self.R('intersect(colnames('+self.dataA+'), colnames('+self.dataB+'))')
        else: h = None
        
        # make a temp variable that is the combination of the parent frame and the cm for the parent.
        if self.mergeOptions.getChecked() =='A+B':
            options = 'all.x=T'
        elif self.mergeOptions.getChecked() =='B+A':
            options = 'all.y=T'
        else:
            options = '' #'all.y=T, all.x=T'
        if 'Sort by Selected Column' in self.sortOption.getChecked():
            options += ', sort=TRUE'
            
        if self.colAsel == None and self.colBsel == None and type(h) is str: 
            self.colA.setCurrentRow( self.R('which(colnames('+self.dataA+') == "' + h + '")-1'))
            self.colB.setCurrentRow( self.R('which(colnames('+self.dataB+') == "' + h + '")-1'))
            
            self.R(self.Rvariables['merged']+'<-merge('+self.dataA+', '+self.dataB+','+options+')')
            self.sendMe()
        elif self.colAsel and self.colBsel:
            if self.colAsel == 'Rownames': cas = '0'
            else: cas = self.colAsel
            if self.colBsel == 'Rownames': cbs = '0'
            else: cbs = self.colBsel
            
            self.R(self.Rvariables['merged']+'<-merge('+self.dataA+', '+self.dataB+', by.x='+cas+', by.y='+cbs+','+options+')', wantType = 'NoConversion')
            if self.colAsel == 'Rownames':
                self.R('rownames('+self.Rvariables['merged']+')<-rownames('+self.dataA+')', wantType = 'NoConversion')
            self.sendMe()

    def sendMe(self,kill=False):
            newDataAll = redRRDataFrame(data = self.Rvariables['merged'])
            newDataAll.dictAttrs = self.dataParentB.dictAttrs.copy()
            newDataAll.dictAttrs.update(self.dataParentA.dictAttrs)
            self.rSend("id0", newDataAll)
    
    def setcolA(self):
        try:
            self.colAsel = '\''+str(self.colA.selectedItems()[0].text())+'\''
            if self.colAsel == '\'Rownames\'':
                self.colAsel = '0'
        except: return
    def setcolB(self):
        try:
            self.colBsel = '\''+str(self.colB.selectedItems()[0].text())+'\''
            if self.colBsel == '\'Rownames\'':
                self.colBsel = '0'
        except: return
    def getReportText(self, fileDir):
        return 'Data from %s was merged with data from %s using the %s column in the first table and %s in the second.\n\n' % (self.dataA, self.dataB, self.colAsel, self.colBsel)
    
