"""
<name>Pathway Enrichment</name>
<description>Performs Pathway Analysis on a genelist or subset (must specify gene list as either a full list or a subset on connecting)</description>
<tags>Microarray</tags>
<RFunctions>sigPathway:runSigPathway</RFunctions>
<icon>icons/readcel.png</icon>
<priority>2030</priority>
"""

import os, glob
import redRGUI
import redRGUI
from OWRpy import *
import redREnviron

class runSigPathway(OWRpy):
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        
        
        self.setRvariableNames(['data', 'affy', 'pAnnots',  'sublist', 'wd', 'minNPS', 'maxNPS', 'phenotype', 'weightType', 'sigpath'])
        self.Rpannot = None
        self.clickedRow = None
        self.data = ''
        self.affy = ''
        self.pAnnots = ''
        
        self.sublist = ''
        self.wd = ''
        self.availablePaths = []
        self.phenotype = ''
        self.weightType = 'constant'
        self.newdata = {}
        self.dboptions = ''
        self.subtable = {}
        self.noFile() # run the file manager to get all the needed files.
        
        
        self.inputs = [("Expression Set", signals.RDataFrame, self.process), 
        ("Pathway Annotation List", signals.RDataFrame, self.processPathAnnot), 
        ('Phenotype Vector', signals.RVector, self.phenotypeConnected)]
        self.outputs = [("Pathway Analysis File", signals.RDataFrame), 
        ("Pathway Annotation List", signals.RDataFrame), 
        ("Pathway List", signals.RDataFrame)]
    
        #GUI
        mainArea = redRGUI.widgetBox(self.controlArea, orientation = 'horizontal')
        leftArea = redRGUI.widgetBox(mainArea, sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding))
        rightArea = redRGUI.widgetBox(mainArea)
        info = redRGUI.groupBox(leftArea, "Info")
        
        self.infob = redRGUI.widgetLabel(info, '')
 
        sigPathOptions = redRGUI.groupBox(leftArea, "Options", sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.minNPS = redRGUI.lineEdit(sigPathOptions, '20', 'Min Genes in Pathway:')
        self.maxNPS = redRGUI.lineEdit(sigPathOptions, '500', 'Max Genes in Pathway:')
        self.pAnnotlist = redRGUI.comboBox(sigPathOptions, label = "Pathway Annotation File:", items = self.availablePaths, callback = self.loadpAnnot) #Gets the availiable pathway annotation files.
        self.chiptype = redRGUI.lineEdit(sigPathOptions, '', label = "Chiptype", toolTip = 'If no chip type was detected you can input the chip type here.\nBe careful that you put the chip type in exactly as it would be specified in Read CEL Files.\nOtherwise you will likely get an error!!', callback = self.getChiptype)
        self.npath = redRGUI.lineEdit(sigPathOptions, '25', label = 'Number of Pathways')
        self.getNewAnnotButton = redRGUI.button(sigPathOptions, label = "New Annotation File", callback = self.noFile, width = 200)
        redRGUI.button(self.bottomAreaRight, 'Run', callback = self.runPath, width = 200)
        #redRGUI.button(sigPathOptions, 'Show Table', callback = self.tableShow, width = 200)
        self.usedb = redRGUI.checkBox(sigPathOptions, buttons = ['Use Annotation Database'])
        
        #split the canvas into two halves
        self.pathtable = redRGUI.groupBox(rightArea, "Pathway Info", sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.pathinfoA = redRGUI.widgetLabel(self.pathtable, "")
        self.table1 = redRGUI.table(self.pathtable) # change the table while processing
        self.table2 = redRGUI.table(self.pathtable) #change the table while processing
        
        
        
    def loadpAnnot(self):
        file = str(self.pAnnotlist.currentText())
        rrdir = redREnviron.RDir
        destpath = os.path.join(rrdir, 'R', 'doc', 'geneSets')
        if not os.path.isdir(destpath):
            os.mkdir(destpath)
        fileFull = os.path.abspath(os.path.join(destpath, file+'.RData'))
        #fileFull = fileFull.replace('\\', '//')
        self.R('load('+fileFull+')')
        self.pAnnots = 'G'
        self.infob.setText('Annotation file loaded')

    def process(self, data): #collect a preprocessed file for pathway analysis
        self.require_librarys(['sigPathway'])
        if data:
            try:
                self.removeWarning(id = 'NoData')
            except: pass
            self.olddata = data
            self.data = data['data']
            self.pAnnotlist.setEnabled(True)
            self.chiptype.clear()
            if signals.globalDataExists('chiptype'):
                self.chiptype.setEnabled(False)
                self.usedb.setChecked(['Use Annotation Database'])
                self.getChiptype()
            # if 'eset' in data:
                # self.affy = data['eset']
                # self.chiptype.setText(self.R('annotation('+self.affy+')'))
                # self.chiptype.setEnabled(False)
                # self.usedb.setChecked(['Use Annotation Database'])
                # self.getChiptype()
            # elif 'affy' in data:
                # self.affy = data['affy']
                # self.chiptype.setText(self.R('annotation('+self.affy+')'))
                # self.chiptype.setEnabled(False)
                # self.usedb.setChecked(['Use Annotation Database'])
                # self.getChiptype()
            # else:
                # self.infob.setText("No Chip Type Info Available. \n Please input.")
                # self.chiptype.setEnabled(True)
            if str(self.chiptype.text()) != '':
                self.infob.setText('Your chip type is '+str(self.chiptype.text()))
            if 'classes' in self.olddata:
                self.phenotype = self.olddata['classes']
            else: return
        else: 
            self.setWarning(id = 'NoData', text = 'No data was found in your connection')
    def processPathAnnot(self, data): #connect a processed annotation file if removed, re-enable the choose file function
        if data:
            self.pAnnots = data['data']
            self.pAnnotlist.setEnabled(False)
        else: 
            self.pAnnotlist.setEnabled(True)
            self.wdline.setEnabled(True)
            self.wdfilebutton.setEnabled(True)
    def getChiptype(self):
        if 'Use Annotation Database' in self.usedb.getChecked(): 
            try:
                self.require_librarys([str(self.chiptype.text() + '.db')]) # require the libraries, these are in the biocLite repository so if fails we need to run a special algorithm to get the packages
                self.dboptions = ',annotpkg = "'+str(self.chiptype.text())+'.db"'
                self.infob.setText("Chip type loaded")
            except:
                self.infob.setText('Chip type was not loaded successfully')
        else: return
    
    def noFile(self): # download all available files from "http://chip.org/~ppark/Supplements/PNAS05.html" and put them into the \R\doc\geneSets folder in the Red-R dir.
        print 'Entered noFile to get files'
        rrdir = redREnviron.RDir
        print rrdir
        
        destpath = os.path.join(rrdir, 'doc', 'geneSets')
        # if doesn't exist make the directory
        print destpath
        if not os.path.exists(destpath):
            os.makedirs(destpath)
        neededFiles = []
        for file in ['GenesetsU430v2', 'GenesetsU74av2', 'GenesetsU95av2', 'GenesetsU133a', 'GenesetsU133plus2']:
            if not os.path.isfile(os.path.abspath(os.path.join(destpath, file+'.RData'))):
                neededFiles.append(file)
                print 'Requiring ', file
            else:
                self.availablePaths.append(file)
                print 'Found ', file
        print neededFiles, len(neededFiles), len(neededFiles)>0
        if len(neededFiles) > 0:
            import urllib
            progressBar = QProgressDialog()
            progressBar.setCancelButtonText(QString())
            progressBar.setLabelText('Loading required annotation data')
            progressBar.setMaximum(5)
            progressBar.setValue(0)
            progressBar.setWindowTitle('Loading')
            pbv = 0
            opener = urllib.FancyURLopener()
            for geneSet in neededFiles:
                #try:
                opener.retrieve(url = 'http://chip.org/~ppark/Supplements/PNAS05/%s.RData' % geneSet, filename = os.path.abspath(os.path.join(destpath, geneSet+'.RData')))
                # except: 
                    # print 'Exception
                pbv += 1
                progressBar.setValue(pbv)

    def runPath(self, reload = 0):
        if self.data == '': return
        if not reload:
            self.getChiptype()
            try:
                self.R(self.Rvariables['sigpath']+'<-runSigPathway('+self.pAnnots+', minNPS='+str(self.minNPS.text())+', maxNPS = '+str(self.maxNPS.text())+', '+self.data+', phenotype = '+self.phenotype+', weightType = "'+self.weightType+'", npath = '+str(self.npath.text())+self.dboptions+')')
            except:
                self.pathinfoA.setText("Error occured in processing.  Change parameters and repeat.")
                return
            self.newdata = self.olddata.copy()
        self.newdata['data'] = self.Rvariables['sigpath']+'$df.pathways'
        self.newdata['sigPathObj'] = self.Rvariables['sigpath']
        self.send("Pathway Analysis File", self.newdata)

        headers = self.R('colnames('+self.newdata['data']+')')
        #self.headers = r('colnames('+self.dataframename+')')
        dataframe = self.R(self.newdata['data'])
        self.table1.setColumnCount(len(headers))
        self.table1.setRowCount(len(dataframe[headers[0]]))
        n=0
        for key in headers:
            m=0
            for item in dataframe[key]:
                newitem = QTableWidgetItem(str(item))
                self.table1.setItem(m,n,newitem)
                m += 1
            n += 1
        self.table1.setHorizontalHeaderLabels(headers)
        self.connect(self.table1, SIGNAL("itemClicked(QTableWidgetItem*)"), self.cellClicked)
        
    
    def tableShow(self):
        try:
            self.table1.show()
            #self.table.setMinimumSize(500, 500)
            self.connect(self.table, SIGNAL("itemClicked(QTableWidgetItem*)"), self.cellClicked)
        except: return
    
        
    def cellClicked(self, item):
        self.clickedRow = int(item.row())+1
        self.subtable = {'data':self.Rvariables['sigpath']+'$list.gPS[['+str(self.clickedRow)+']]', 'col':3, 'link':{'IHOP':'http://www.ihop-net.org/UniPub/iHOP/?search={4}', 'Entrez Gene': 'http://www.ncbi.nih.gov/gene/{3}'}}
        self.sendMe()
        try: self.table2
        except: pass
        else: self.table2.clear()
        #self.table2 = MyTable(self.subtable['data'])
        
        headers = self.R('colnames('+self.subtable['data']+')')
        #self.headers = r('colnames('+self.dataframename+')')
        dataframe = self.R(self.subtable['data'])
        self.table2.setColumnCount(len(headers))
        self.table2.setRowCount(len(dataframe[headers[0]]))
        n=0
        for key in headers:
            m=0
            for item in dataframe[key]:
                newitem = QTableWidgetItem(str(item))
                self.table2.setItem(m,n,newitem)
                m += 1
            n += 1
        self.table2.setHorizontalHeaderLabels(headers)
        self.connect(self.table2, SIGNAL("itemClicked(QTableWidgetItem*)"), self.geneClicked)
    
    def geneClicked(self, item):
        
        clickedGene = int(item.row())+1
        if 'GeneID' in self.R('colnames('+self.Rvariables['sigpath']+'$list.gPS[['+str(self.clickedRow)+']])'):
            genenumber = self.R(self.Rvariables['sigpath']+'$list.gPS[['+str(self.clickedRow)+']]['+str(clickedGene)+',3]')
            self.R('shell.exec("http://www.ncbi.nlm.nih.gov/gene/'+str(genenumber)+'")')
        
    def phenotypeConnected(self, data):
        if data:
            self.phenotype = data['data']
        else: return
    
    def sendMe(self, pafile = True, palist = True):
        if pafile:
            self.rSend("Pathway Analysis File", self.newdata)
        if palist:
            self.rSend("Pathway List", self.subtable)