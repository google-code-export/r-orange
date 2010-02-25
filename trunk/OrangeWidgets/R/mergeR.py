"""
<name>Merge Data</name>
<description>Merges or subsets two datasets depending on options.</description>
<tags>Data Manipulation</tags>
<RFunctions>base:match,base:merge</RFunctions>
<icon>icons/merge.png</icon>
<priority>2030</priority>
"""

from OWRpy import *
import redRGUI


class mergeR(OWRpy):
    settingsList = ['dataA','dataB','colAsel', 'colBsel']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Merge Data")
        #self.setStateVariables(['dataA','dataB','colAsel', 'colBsel'])
        
        self.dataParentA = {}
        self.dataParentB = {}
        
        
        self.inputs = [("RExampleTable A", RvarClasses.RDataFrame, self.processA), ("RExampleTable B", RvarClasses.RDataFrame, self.processB)]
        self.outputs = [("Merged Examples All", RvarClasses.RDataFrame),("Merged Examples A+B", RvarClasses.RDataFrame), ("Merged Examples B+A", RvarClasses.RDataFrame)]

        #default values        
        self.colAsel = None
        self.colBsel = None
        self.forceMergeAll = 0 #checkbox value for forcing merger on all data, default is to remove instances from the rows or cols.
        print 'init merge and load settings'
        self.loadSettings()
        
        #set R variable names
        self.setRvariableNames(['merged_dataAB','merged_dataBA','merged_dataAll', 'merged_dataAB_cm_', 'merged_dataAll_cm_', 'merged_dataBA_cm_'])
                
        #GUI
        layk = QWidget(self)
        self.controlArea.layout().addWidget(layk)
        grid = QGridLayout()
        grid.setMargin(0)
        layk.setLayout(grid)
        
        pickA = redRGUI.widgetBox(self.controlArea, "Select Columns to Merge From A")
        grid.addWidget(pickA, 0,0)
        self.colA = redRGUI.listBox(pickA, self, callback = self.setcolA)
        
        
        pickB = redRGUI.widgetBox(self.controlArea, "Select Columns to Merge From B")
        grid.addWidget(pickB, 0,1)
        self.colB = redRGUI.listBox(pickB, self, callback = self.setcolB)
        
        infoBox = redRGUI.widgetBox(self.controlArea, "Info")
        self.infoa = redRGUI.widgetLabel(infoBox, "No Data Loaded")
        
        #runbox = redRGUI.widgetBox(self.controlArea, "Run")
        #redRGUI.button(runbox, self, "Run", callback = self.run)
        
        # ## Other options
        otherBox = redRGUI.widgetBox(self.controlArea, "Binding")
        redRGUI.checkBox(otherBox, self, "forceMergeAll", "Force Merger")
        redRGUI.button(otherBox, self, "Bind By Columns", callback = self.colBind)
        redRGUI.button(otherBox, self, "Bind By Rows", callback = self.rowBind)

        
    def onLoadSavedSession(self):
        
        self.processSignals()
        try:

            self.colA.setCurrentRow( self.R('which(colnames('+self.dataA+') == "' + self.colAsel + '")-1'))
            self.colB.setCurrentRow( self.R('which(colnames('+self.dataB+') == "' + self.colBsel + '")-1'))
            self.sendMe()
        except:
            self.sendMe(kill=True)
    def processA(self, data):
        print 'processA'
        if data:
            self.dataA = str(data['data'])
            self.dataParentA = data.copy()
            colsA = self.R('colnames('+self.dataA+')') #collect the sample names to make the differential matrix
            if type(colsA) is str:
                colsA = [colsA]
            self.colA.clear()
            for v in colsA:
                self.colA.addItem(v)
                if v == self.colAsel:
                    self.colA.setCurrentRow((self.colA.count()-1))
            
            self.run()
        else: return
            #self.sendNothing

    def processB(self, data):
        print 'processB'
        if data:
            self.dataB = str(data['data'])
            self.dataParentB = data.copy()
            colsB = self.R('colnames('+self.dataB+')') #collect the sample names to make the differential matrix
            if type(colsB) is str:
                colsB = [colsB]
            self.colB.clear()
            for v in colsB:
                self.colB.addItem(v)
                if v == self.colBsel:
                    self.colB.setCurrentRow((self.colB.count()-1))
                    
            #self.colB.setCurrentRow(self.colB.row(QListWidgetItem(self.colBsel)))
            self.run()
        else: return
            #self.sendNothing
            
    def run(self):
        try:
            h = self.R('intersect(colnames('+self.dataA+'), colnames('+self.dataB+'))')
            
            # make a temp variable that is the combination of the parent frame and the cm for the parent.
            self.R('tmpa<-cbind('+self.dataA+','+self.dataParentA['cm']+')')
            self.R('tmpb<-cbind('+self.dataB+','+self.dataParentB['cm']+')')
            
            if self.colAsel == None and self.colBsel == None and type(h) is str: 
                self.colA.setCurrentRow( self.R('which(colnames('+self.dataA+') == "' + h + '")-1'))
                self.colB.setCurrentRow( self.R('which(colnames('+self.dataB+') == "' + h + '")-1'))
                self.R('tmpab<-merge(tmpa, tmpb,all.x=T)')
                self.R(self.Rvariables['merged_dataAB']+'<-tmpab[!(colnames(tmpab) %in% c(colnames('+self.dataParentA['cm']+','+self.dataParentB['cm']+'))),]')
                self.R(self.Rvariables['merged_dataAB_cm_']+'<-tmpab[(colnames(tmpab) %in% c(colnames('+self.dataParentA['cm']+','+self.dataParentB['cm']+'))),]')
                
                self.R('tmpba<-merge(tmpa, tmpb,all.y=T)')
                self.R(self.Rvariables['merged_dataBA']+'<-tmpba[!(colnames(tmpba) %in% c(colnames('+self.dataParentA['cm']+','+self.dataParentB['cm']+'))),]') 
                self.R(self.Rvariables['merged_dataBA_cm_']+'<-tmpba[(colnames(tmpba) %in% c(colnames('+self.dataParentA['cm']+','+self.dataParentB['cm']+'))),]')        

                self.R('tmpall<-merge(tmpa, tmpb)')
                self.R(self.Rvariables['merged_dataAll']+'<-tmpall[!(colnames(tmpall) %in% c(colnames('+self.dataParentA['cm']+','+self.dataParentB['cm']+'))),]')
                self.R(self.Rvariables['merged_dataAll_cm_']+'<-tmpall[(colnames(tmpall) %in% c(colnames('+self.dataParentA['cm']+','+self.dataParentB['cm']+'))),]')
                
                
            elif self.colAsel and self.colBsel:
            
                self.R('tmpab<-merge(tmpa, tmpb, by.x="'+self.colAsel+'", by.y="'+self.colBsel+'",all.x=T)')
                self.R(self.Rvariables['merged_dataAB']+'<-tmpab[!(colnames(tmpab) %in% c(colnames('+self.dataParentA['cm']+','+self.dataParentB['cm']+'))),]')
                self.R(self.Rvariables['merged_dataAB_cm_']+'<-tmpab[(colnames(tmpab) %in% c(colnames('+self.dataParentA['cm']+','+self.dataParentB['cm']+'))),]')
                
                self.R('tmpba<-merge(tmpa, tmpb,by.x="'+self.colAsel+'", by.y="'+self.colBsel+'",all.y=T)')
                self.R(self.Rvariables['merged_dataBA']+'<-tmpba[!(colnames(tmpba) %in% c(colnames('+self.dataParentA['cm']+','+self.dataParentB['cm']+'))),]') 
                self.R(self.Rvariables['merged_dataBA_cm_']+'<-tmpba[(colnames(tmpba) %in% c(colnames('+self.dataParentA['cm']+','+self.dataParentB['cm']+'))),]')        

                self.R('tmpall<-merge(tmpa, tmpb,by.x="'+self.colAsel+'", by.y="'+self.colBsel+'")')
                self.R(self.Rvariables['merged_dataAll']+'<-tmpall[!(colnames(tmpall) %in% c(colnames('+self.dataParentA['cm']+','+self.dataParentB['cm']+'))),]')
                self.R(self.Rvariables['merged_dataAll_cm_']+'<-tmpall[(colnames(tmpall) %in% c(colnames('+self.dataParentA['cm']+','+self.dataParentB['cm']+'))),]')
                
                
                
            
            self.sendMe()
        except: 
            print 'merge error'
            self.sendMe(kill=True)
            return 
    def sendMe(self,kill=False):
        if kill:
            self.rSend("Merged Examples A+B", None)
            self.rSend("Merged Examples B+A", None)
            self.rSend("Merged Examples All", None)
        elif self.R('exists("'+self.Rvariables['merged_dataAll']+'")'):
            self.rSend("Merged Examples A+B", {'data':self.Rvariables['merged_dataAB'], 'cm':self.Rvariables['merged_dataAB_cm_'], 'parent':self.Rvariables['merged_dataAB']})
            self.rSend("Merged Examples B+A", {'data':self.Rvariables['merged_dataBA'], 'cm':self.Rvariables['merged_dataBA_cm_'], 'parent':self.Rvariables['merged_dataBA']})
            self.rSend("Merged Examples All", {'data':self.Rvariables['merged_dataAll'], 'cm':self.Rvariables['merged_dataAll_cm_'], 'parent':self.Rvariables['merged_dataAll']})
    
    def setcolA(self):
        try:
            self.colAsel = str(self.colA.selectedItems()[0].text())
            self.run()
        except: return
    def setcolB(self):
        try:
            self.colBsel = str(self.colB.selectedItems()[0].text())
            self.run()
        except: return
    
    def rowBind(self):
        try:
            if self.forceMergeAll == 0:
                self.R('tmp<-colnames('+self.dataB+') %in% colnames('+self.dataA+')')
                self.R('tmp2<-'+self.dataB+'[,!tmp]')
                self.R(self.Rvariables['merged_dataAll']+'<-cbind('+self.dataA+', tmp2)')
                self.R('rm(tmp); rm(tmp2)')
            else:
                self.R(self.Rvariables['merged_dataAll']+'<-cbind('+self.dataA+', '+self.dataB+')')
            self.rSend("Merged Examples All", {'data':self.Rvariables['merged_dataAll']})
        except:
            self.infoa.setText("Merger Failed. Be sure data is connected")
    def colBind(self):
        try:
            if self.forceMergeAll == 0:
                self.R('tmp<-rownames('+self.dataB+') %in% rownames('+self.dataA+')')
                self.R('tmp2<-'+self.dataB+'[!tmp,]')
                self.R(self.Rvariables['merged_dataAll']+'<-rbind('+self.dataA+', tmp2)')
                self.R('rm(tmp); rm(tmp2)')
            else:
                self.R(self.Rvariables['merged_dataAll']+'<-rbind('+self.dataA+', '+self.dataB+')')
            self.rSend("Merged Examples All", {'data':self.Rvariables['merged_dataAll']})
        except:
            self.infoa.setText("Merger Failed. Be sure data is connected")