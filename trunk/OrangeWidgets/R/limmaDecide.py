"""
<name>Limma Decide</name>
<description>Calculates differential expression of genes from an eSet object</description>
<icon>icons/readcel.png</icons>
<priority>2030</priority>
"""

import OWGUI
from OWRpy import *


class limmaDecide(OWRpy):
    settingsList = ['modelProcessed', 'vs', 'dmethod', 'adjmethods', 'foldchange', 'pval', 'data', 'sending', 'ebdata', 'eset']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        
        self.vs = self.variable_suffix
        self.rsession("require('affy')")
        self.rsession("require('gcrma')")
        self.rsession("require('limma')")
        self.rsession("require('panp')")
        self.dmethod = "separate"
        self.adjmethods = "BH"
        self.foldchange = "0"
        self.pval = "0.05"
        self.data = ''
        self.ebdata = ''
        
        self.eset = None
        self.sending = None
        self.modelProcessed = 0
        self.loadSettings()
        
        self.setRvariableNames(['gcm', 'eset_sub', 'geneissig', 'dfsg'])
        
        #self.sendMe()
        
        self.inputs = [("eBayes fit", orange.Variable, self.process), ('NormalizedAffybatch', RvarClasses.RDataFrame, self.processeset)]
        self.outputs = [("Gene Change Matrix", RvarClasses.RDataFrame), ("Expression Subset", RvarClasses.RDataFrame)]
        
        #GUI
        #want to have an options part, a data viewing part and a run part
        
        layk = QWidget(self)
        self.controlArea.layout().addWidget(layk)
        grid = QGridLayout()
        grid.setMargin(0)
        layk.setLayout(grid)
        
        optionsbox = OWGUI.widgetBox(self.controlArea, "Options")
        grid.addWidget(optionsbox, 0,0)
        OWGUI.comboBox(optionsbox, self, "dmethod", label = "Combine Method"+"  ", items = ["separate", "global", "hierarchical", "nestedF"], orientation=0)
        OWGUI.comboBox(optionsbox, self, "adjmethods", label = "P-value Adjust Methods", items = ["BH", "none", "fdr", "BY", "holm"], orientation=0)
        OWGUI.lineEdit(optionsbox, self, "pval", label = "Minimum p-value change:", orientation = 0)
        OWGUI.lineEdit(optionsbox, self, "foldchange", label = "Minimum fold change:", orientation = 0)
        
        computebox = OWGUI.widgetBox(self.controlArea, "Compute")
        grid.addWidget(computebox, 1,0)
        self.infoa = OWGUI.widgetLabel(computebox, "Data not yet connected")
        runbutton = OWGUI.button(computebox, self, "Run Analysis", callback = self.runAnalysis, width=200)
        if self.loadingSavedSession:
            self.runAnalysis()
        
    def process(self, dataset):
        if dataset and 'data' in dataset:
            if 'kill' in dataset and dataset['kill'] == True:
                self.rSend("Gene Change Matrix", {'kill':True})
                self.rSend("Expression Subset", {'kill':True})
                return
            self.data = dataset['data']
            self.ebdata = dataset
            self.infoa.setText("Data connected")
        else: 
            self.rSend("Gene Change Matrix", {'kill':True})
            self.rSend("Expression Subset", {'kill':True})
        
    def runAnalysis(self):
        self.Rvariables['gcm'] = 'gcm'+self.variable_suffix
        if not self.loadingSavedSession:
            #run the analysis using the parameters selected or input
            self.rsession(self.Rvariables['gcm']+'<-decideTests('+str(self.data)+', method="'+str(self.dmethod)+'", adjust.method="'+str(self.adjmethods)+'", p.value='+str(self.pval)+', lfc='+str(self.foldchange)+')')
            self.infoa.setText("Gene Matrix Processed and sent!")
            self.sending = {'data':self.Rvariables['gcm']}
        self.send("Gene Change Matrix", self.sending)
        
        self.rsession(self.Rvariables['gcm']+'[,2]!=0 ->'+self.Rvariables['geneissig'])
        self.rsession(self.Rvariables['gcm']+'[geneissig,] ->'+self.Rvariables['dfsg'])
        self.modelProcessed = 1
        
        self.sendesetsubset()

    def processeset(self, data):
        if data:
            self.eset = data['data'] #this is data from an expression matrix or data.frame
            self.olddata = data.copy()
            if self.sending != None and self.ebdata != '':
                self.sendesetsubset()
        else: return

    def sendesetsubset(self):
        if self.eset != None and self.modelProcessed == 1:
            self.rsession(self.Rvariables['eset_sub']+'<-'+self.eset+'[rownames(dfsg),]')
            self.newdata['data']=self.Rvariables['eset_sub']
            if 'classes' in self.ebdata:
                self.newdata['classes'] = self.ebdata['classes']
            self.send("Expression Subset", self.newdata)
        else:
            return 