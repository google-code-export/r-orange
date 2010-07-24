"""
<name>Merge</name>
<description>Merges or subsets two datasets depending on options.</description>
<tags>Data Manipulation</tags>
<RFunctions>base:match,base:merge</RFunctions>
<icon>merge2.png</icon>
"""

from OWRpy import *
import redRGUI
import libraries.base.signalClasses.RDataFrame as rdf

class mergeR(OWRpy):
    settingsList = ['dataA','dataB','colAsel', 'colBsel']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        #self.setStateVariables(['dataA','dataB','colAsel', 'colBsel'])
        
        self.dataParentA = {}
        self.dataParentB = {}
        self.dataA = ''
        self.dataB = ''
        
        
        self.inputs = [("RExampleTable A", rdf.RDataFrame, self.processA), ("RExampleTable B", rdf.RDataFrame, self.processB)]
        self.outputs = [("Merged Examples All", rdf.RDataFrame),("Merged Examples A+B", rdf.RDataFrame), ("Merged Examples B+A", rdf.RDataFrame)]

        #default values        
        self.colAsel = None
        self.colBsel = None
        #self.forceMergeAll = 0 #checkbox value for forcing merger on all data, default is to remove instances from the rows or cols.
        print 'init merge and load settings'
        
        
        #set R variable names
        self.setRvariableNames(['merged_dataAB','merged_dataBA','merged_dataAll'])
                
        #GUI
        
        infoBox = redRGUI.groupBox(self.controlArea, "Info")
        self.infoa = redRGUI.widgetLabel(infoBox, "No Data Loaded")
        infoBox.hide()
        layk = QWidget(self)
        self.controlArea.layout().addWidget(layk)
        grid = QGridLayout()
        grid.setMargin(0)
        layk.setLayout(grid)
        
        pickA = redRGUI.groupBox(self.controlArea, "Select Columns to Merge From A")
        grid.addWidget(pickA, 0,0)
        self.colA = redRGUI.listBox(pickA, callback = self.setcolA)
        
        
        pickB = redRGUI.groupBox(self.controlArea, "Select Columns to Merge From B")
        grid.addWidget(pickB, 0,1)
        self.colB = redRGUI.listBox(pickB, callback = self.setcolB)
        

        self.mergeLikeThis = redRGUI.checkBox(self.bottomAreaRight, buttons = ['Always Merge Like This'], toolTips = ['Whenever this widget gets data it should try to merge as was done here'])
        redRGUI.button(self.bottomAreaRight, 'Commit', callback = self.run)
        
    def processA(self, data):
        #print 'processA'
        if data:
            self.dataA = str(data.getData())
            self.dataParentA = data
            colsA = self.R('colnames('+self.dataA+')') #collect the sample names to make the differential matrix
            
            if type(colsA) is str:
                colsA = [colsA]
            colsA.insert(0, 'Rownames')
            self.colA.update(colsA)

            if 'Always Merge Like This' in self.mergeLikeThis.getChecked():
                self.run()
            
            if self.dataA != '' and self.dataB != '':
                aRowLen = self.R('length('+self.dataA+'[,1])')
                aColLen = self.R('length('+self.dataB+'[1,])')
                bRowLen = self.R('length('+self.dataA+'[,1])')
                bColLen = self.R('length('+self.dataA+'[1,])')
                try:
                    if aRowLen == bRowLen:
                        self.colBindButton.setEnabled(True)
                    if aColLen == bColLen:
                        self.rowBindButton.setEnabled(True)
                except: # there must not be any row of col names so there can't be a comparison
                    pass
        else: return
            #self.sendNothing

    def processB(self, data):
        #print 'processB'
        if data:
            self.dataB = str(data.getData())
            self.dataParentB = data
            colsB = self.R('colnames('+self.dataB+')') #collect the sample names to make the differential matrix
            if type(colsB) is str:
                colsB = [colsB]
            colsB.insert(0, 'Rownames')
            self.colB.update(colsB)
            
                    
            #self.colB.setCurrentRow(self.colB.row(QListWidgetItem(self.colBsel)))
            if 'Always Merge Like This' in self.mergeLikeThis.getChecked():
                self.run()
            
            if self.dataA != '' and self.dataB != '':
                aRowLen = self.R('length('+self.dataA+'[,1])')
                aColLen = self.R('length('+self.dataB+'[1,])')
                bRowLen = self.R('length('+self.dataA+'[,1])')
                bColLen = self.R('length('+self.dataA+'[1,])')
                try:
                    if aRowLen == bRowLen:
                        self.colBindButton.setEnabled(True)
                    if aColLen == bColLen:
                        self.rowBindButton.setEnabled(True)
                except: # there must not be any row of col names so there can't be a comparison
                    pass
                    
        else: return
            #self.sendNothing
            
    
    def run(self):
        try:
            
            if self.dataA != '' and self.dataB != '':
                h = self.R('intersect(colnames('+self.dataA+'), colnames('+self.dataB+'))')
            else: h = None
            # make a temp variable that is the combination of the parent frame and the cm for the parent.

            self.R('tmpa<-cbind('+self.dataA+')')
            self.R('tmpb<-cbind('+self.dataB+')')
           
            if self.colAsel == None and self.colBsel == None and type(h) is str: 
                self.colA.setCurrentRow( self.R('which(colnames('+self.dataA+') == "' + h + '")-1'))
                self.colB.setCurrentRow( self.R('which(colnames('+self.dataB+') == "' + h + '")-1'))
                self.R(self.Rvariables['merged_dataAB']+'<-merge(tmpa, tmpb,all.x=T)')
                self.R(self.Rvariables['merged_dataBA']+'<-merge(tmpa, tmpb,all.y=T)')
                self.R(self.Rvariables['merged_dataAll']+'<-merge(tmpa, tmpb, all.x = TRUE, all.y = TRUE)')
                
            elif self.colAsel and self.colBsel:
                if self.colAsel == 'Rownames': cas = '0'
                else: cas = self.colAsel
                if self.colBsel == 'Rownames': cbs = '0'
                else: cbs = self.colBsel
                self.R(self.Rvariables['merged_dataAB']+'<-merge(tmpa, tmpb, by.x='+cas+', by.y='+cbs+',all.x=T)')
                self.R(self.Rvariables['merged_dataBA']+'<-merge(tmpa, tmpb,by.x='+cas+', by.y='+cbs+',all.y=T)')
                self.R(self.Rvariables['merged_dataAll']+'<-merge(tmpa, tmpb,by.x='+cas+', by.y='+cbs+', all.x = TRUE, all.y=TRUE)')

                
            
            self.sendMe()
        except: 
            print 'merge error'
            import sys, traceback
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60        

            self.sendMe(kill=True)
            return 
    def sendMe(self,kill=False):
        mergedCM = False
        if kill:
            self.rSend("Merged Examples A+B", None)
            self.rSend("Merged Examples B+A", None)
            self.rSend("Merged Examples All", None)
        elif self.R('exists("'+self.Rvariables['merged_dataAll']+'")'):
            # bind the cm's of the parent data together.
            if 'cm' in self.dataParentA.dictAttrs.keys() and 'cm' in self.dataParentB.dictAttrs.keys():
                self.R('cm_'+self.Rvariables['merged_dataAB'] + '<-c('+self.dataParentA.dictAttrs['cm']+','+self.dataParentB.dictAttrs['cm']+')')
                self.R('cm_'+self.Rvariables['merged_dataAll'] + '<-c('+self.dataParentA.dictAttrs['cm']+','+self.dataParentB.dictAttrs['cm']+')')
                self.R('cm_'+self.Rvariables['merged_dataBA'] + '<-c('+self.dataParentA.dictAttrs['cm']+','+self.dataParentB.dictAttrs['cm']+')')
                mergedCM = True
            newDataAB = rdf.RDataFrame(data = self.Rvariables['merged_dataAB'])
            newDataAB.dictAttrs = self.dataParentB.dictAttrs.copy()
            newDataAB.dictAttrs.update(self.dataParentA.dictAttrs) # A data takes presedence over B data
            
            
            newDataBA = rdf.RDataFrame(data = self.Rvariables['merged_dataBA'])
            newDataBA.dictAttrs = self.dataParentB.dictAttrs.copy()
            newDataBA.dictAttrs.update(self.dataParentA.dictAttrs) # A data takes presedence over B data
            
            
            newDataAll = rdf.RDataFrame(data = self.Rvariables['merged_dataAll'])
            newDataAll.dictAttrs = self.dataParentB.dictAttrs.copy()
            newDataAll.dictAttrs.update(self.dataParentA.dictAttrs) # A data takes presedence over B data
            
            if mergedCM:
                newDataAll.dictAttrs['cm'] = ('cm_'+self.Rvariables['merged_dataAll'], 'Merge', 'Class Managers combined from data entering Merge.', None)
                newDataAB.dictAttrs['cm'] = ('cm_'+self.Rvariables['merged_dataAB'], 'Merge', 'Class Managers combined from data entering Merge.', None)
                newDataBA.dictAttrs['cm'] = ('cm_'+self.Rvariables['merged_dataBA'], 'Merge', 'Class Managers combined from data entering Merge.', None)
            self.rSend("Merged Examples B+A", newDataBA)
            self.rSend("Merged Examples A+B", newDataAB)
            self.rSend("Merged Examples All", newDataAll)
    
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
    
