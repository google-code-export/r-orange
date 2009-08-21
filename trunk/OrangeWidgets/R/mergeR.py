"""
<name>Merge RExampleTables</name>
<description>Merges or subsets two RExampleTables depending on options.</description>
<icon>icons/rma.png</icons>
<priority>3010</priority>
"""

from OWRpy import *
import OWGUI


class mergeR(OWRpy):
    #settingsList = ['variable_suffix','colAsel', 'colBsel']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Merge Data")
        self.setStateVariables(['dataA','dataB','colAsel', 'colBsel'])
        
        self.inputs = [("RExampleTable A", RvarClasses.RDataFrame, self.processA), ("RExampleTable B", RvarClasses.RDataFrame, self.processB)]
        self.outputs = [("Merged Examples A+B", RvarClasses.RDataFrame), ("Merged Examples B+A", RvarClasses.RDataFrame)]

        #default values        
        self.colAsel = ''
        self.colBsel = ''
        self.loadSettings()
        
        #set R variable names
        self.setRvariableNames(['merged_dataAB','merged_dataBA'])
                
        #GUI
        layk = QWidget(self)
        self.controlArea.layout().addWidget(layk)
        grid = QGridLayout()
        grid.setMargin(0)
        layk.setLayout(grid)
        
        pickA = OWGUI.widgetBox(self.controlArea, "Select Columns to Merge From A")
        grid.addWidget(pickA, 0,0)
        self.colA = OWGUI.listBox(pickA, self, callback = self.setcolA)
        
        
        pickB = OWGUI.widgetBox(self.controlArea, "Select Columns to Merge From B")
        grid.addWidget(pickB, 0,1)
        self.colB = OWGUI.listBox(pickB, self, callback = self.setcolB)
        
        runbox = OWGUI.widgetBox(self.controlArea, "Run")
        OWGUI.button(runbox, self, "Run", callback = self.run)
        #print self.colAsel, self.colBsel
        if self.rsession('exists("' + self.Rvariables['loadSavedSession'] + '")'):
            self.loadSavedSession = True
            self.processA({'data': self.dataA})
            self.processB({'data': self.dataB})

        
        
    def processA(self, data):
        if data:
            self.dataA = str(data['data'])
            colsA = self.rsession('colnames('+self.dataA+')') #collect the sample names to make the differential matrix
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
        if data:
            self.dataB = str(data['data'])
            colsB = self.rsession('colnames('+self.dataB+')') #collect the sample names to make the differential matrix
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
        print self.loadSavedSession
        try:
            if self.colAsel == '' and self.colBsel == '': 
                h = self.rsession('intersect(colnames('+self.dataA+'), colnames('+self.dataB+'))')
                if type(h) is str: 
                    self.colA.setCurrentRow(self.rsession('which('+self.dataA+' == "' + h + '")'-1))
                    self.colB.setCurrentRow(self.rsession('which('+self.dataB+' == "' + h + '")'-1))
                    if not self.loadSavedSession:
                        self.rsession(self.Rvariables['merged_dataAB']+'<-merge('+self.dataA+', '+self.dataB+',all.x=T)')
                        self.rsession(self.Rvariables['merged_dataBA']+'<-merge('+self.dataA+', '+self.dataB+',all.y=T)')
                    self.rSend("Merged Examples A+B", {'data':self.Rvariables['merged_dataAB']})
                    self.rSend("Merged Examples B+A", {'data':self.Rvariables['merged_dataBA']})
                    
            elif self.colAsel != '' and self.colBsel != '':
                if not self.loadSavedSession:
                    self.rsession(self.Rvariables['merged_dataAB']+'<-merge('+self.dataA+', '+self.dataB+', by.x="'+self.colAsel+'", by.y="'+self.colBsel+'",all.x=T)')
                    self.rsession(self.Rvariables['merged_dataBA']+'<-merge('+self.dataA+', '+self.dataB+', by.x="'+self.colAsel+'", by.y="'+self.colBsel+'",all.y=T)')
                self.rSend("Merged Examples A+B", {'data':self.Rvariables['merged_dataAB']})
                self.rSend("Merged Examples B+A", {'data':self.Rvariables['merged_dataBA']})
        except: 
            return 
    
    def setcolA(self):
        try:
            self.colAsel = str(self.colA.selectedItems()[0].text())
            
        except: return
    def setcolB(self):
        try:
            self.colBsel = str(self.colB.selectedItems()[0].text())
            
        except: return