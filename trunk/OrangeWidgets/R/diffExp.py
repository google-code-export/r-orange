"""
<name>Diff Exp</name>
<description>Calculates differential expression of genes from an eSet object</description>
<icon>icons/DiffExp.png</icon>
<priority>70</priority>
"""

from OWRpy import *
import OWGUI

class diffExp(OWRpy):
    settingsList = [ 'samplenames', 'sampleA', 'sampleB', 'phenoData', 'modelFormula', 'newdata']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        #self.setStateVariables(['samplenames', 'sampleA', 'sampleB'])        
        
        self.samplenames = []
        self.sampleA = []
        self.sampleB = []
        self.phenoData = ''
        self.modelFormula = ''
        self.processingComplete = 0
        self.newdata = {}
        self.olddata = {}
        self.loadSettings()
        
        self.setRvariableNames(['results','classes','subset'])
        

        self.inputs = [("Expression Set", RvarClasses.RDataFrame, self.process), ("Phenotype Data", RvarClasses.RDataFrame, self.phenoProcess)]
        self.outputs = [("eBayes fit", RvarClasses.RList)]
        
        self.samplenames = None #names of the samples (as a python object) to be used for generating the differential expression matrix
        self.classA = True #a container to maintain which list to add the arrays to
        
        #GUI
        self.boxIndices = {}
        self.valuesStack = QStackedWidget(self)
        self.controlArea.layout().addWidget(self.valuesStack)
        
        boxVal = OWGUI.widgetBox(self.controlArea, "Set Classes")
        self.boxIndices[0] = boxVal
        layk = QWidget(self)
        boxVal.layout().addWidget(layk)
        grid = QGridLayout()
        grid.setMargin(0)
        layk.setLayout(grid)
        
        # set as valstack 0
        box = OWGUI.widgetBox(boxVal, "Process")
        grid.addWidget(box, 0,1)
        processButton = OWGUI.button(box, self, "Process eSet", callback = self.processEset, width=200)
        self.arrays = OWGUI.listBox(box, self, callback = self.printSelected)
        setAbutton = OWGUI.button(box, self, "Switch Class", callback = self.switchClass, width = 200)
        self.infoa = OWGUI.widgetLabel(box, "No arrays selected")
        self.infob = OWGUI.widgetLabel(box, "Setting Class A")
        
        selecteda = OWGUI.widgetBox(self.controlArea, "Selected Arrays")
        grid.addWidget(selecteda, 0,0)
        self.selectedArrays = OWGUI.listBox(selecteda, self)
        clearaButton = OWGUI.button(selecteda, self, "Clear",callback = self.clearA, width = 200)
        
        selectedb = OWGUI.widgetBox(self.controlArea, "Selected Arrays")
        grid.addWidget(selectedb, 0,2)
        self.selectedArraysB = OWGUI.listBox(selectedb, self)
        clearbButton = OWGUI.button(selectedb, self, "Clear", callback = self.clearB, width = 200)
        self.valuesStack.addWidget(boxVal)
        # end valstack 0
        
        # valstack 1: phenodataConnected
        
        boxVal = OWGUI.widgetBox(self.controlArea, "Set Classes")
        self.boxIndices[1] = boxVal
        layk2 = QWidget(self)
        boxVal.layout().addWidget(layk2)
        grid2 = QGridLayout()
        grid2.setMargin(0)
        layk2.setLayout(grid2)
        
        
        box = OWGUI.widgetBox(self, "Phenotype Variables")
        grid2.addWidget(box, 0, 0)
        self.phenoVarListBox = OWGUI.listBox(box, self, callback = self.phenoVarListBoxItemClicked)
        buttonsBox = OWGUI.widgetBox(self, "Commands")
        grid2.addWidget(buttonsBox, 0,1)
        self.plusButton = OWGUI.button(buttonsBox, self, "And", callback = self.plusButtonClicked)
        self.plusButton.setEnabled(False)
        self.colonButton = OWGUI.button(buttonsBox, self, "Interacting With", callback = self.colonButtonClicked)
        self.colonButton.setEnabled(False)
        self.starButton = OWGUI.button(buttonsBox, self, "Together and Interacting", callback = self.starButtonClicked)
        self.starButton.setEnabled(False)
        self.processEsetButton = OWGUI.button(buttonsBox, self, "Commit", callback = self.processEset)
        self.processEsetButton.setEnabled(False)
        
        self.modelText = OWGUI.widgetLabel(boxVal, "Model: ")
        self.valuesStack.addWidget(boxVal)
        
        self.valuesStack.setCurrentWidget(self.boxIndices[0])
        
        #self.Rreload() #Important to be at the end of the __init__
        if self.loadingSavedSession:
            self.processEset()

    def clearA(self):
        self.selectedArrays.clear()
        self.sampleA = []
        
    def clearB(self):
        self.selectedArraysB.clear()
        self.sampleB = []
        
    def switchClass(self):
        if self.classA == True:
            self.classA = False
            self.infob.setText("Setting Class B")
        elif self.classA == False:
            self.classA = True
            self.infob.setText("Setting Class A")
        else: 
            self.classA = True
            self.infob.setText("Setting Class A")
    def phenoProcess(self, data):
        if 'data' in data: # make sure that there is data there 
            self.phenoData = data['data']
            colnames = self.rsession('colnames('+self.phenoData+')')
            for names in colnames:
                self.phenoVarListBox.addItem(names)
            self.valuesStack.setCurrentWidget(self.boxIndices[1])
        else:
            self.phenoData = ''
            self.valuesStack.setCurrentWidget(self.boxIndices[0])
    
    
    def process(self, data):
        self.require_librarys(['affy','gcrma','limma'])
        self.arrays.clear()
        self.selectedArrays.clear()
        self.selectedArraysB.clear()
        if data:
            try:
                if data['kill'] == True:
                    self.rSend("eBayes fit", {'kill':True})
                    self.data = ''
                    self.olddata = {}
                    return
            self.data = data['data']
            self.olddata = data.copy()
            self.samplenames = self.rsession('colnames('+self.data+')') #collect the sample names to make the differential matrix

            if self.samplenames is str:
                self.samplenames = [self.samplenames]
            for v in self.samplenames:
                self.arrays.addItem(v)
            
        else: 
            self.rSend("eBayes fit", {'kill':True})

    def phenoVarListBoxItemClicked(self):
        if self.processingComplete == 1:
            self.modelFormula = ''
            self.processingComplete = 0
        element = self.phenoVarListBox.selectedItems()[0].text()
        self.modelFormula += str(element)
        self.phenoVarListBox.setEnabled(False)
        self.plusButton.setEnabled(True)
        self.colonButton.setEnabled(True)
        self.starButton.setEnabled(True)
        self.processEsetButton.setEnabled(True)
        self.modelText.setText("Model: " + self.modelFormula)
    def plusButtonClicked(self):
        self.modelFormula += ' + '
        self.phenoVarListBox.setEnabled(True)
        self.plusButton.setEnabled(False)
        self.colonButton.setEnabled(False)
        self.starButton.setEnabled(False)
        self.processEsetButton.setEnabled(False)
        self.modelText.setText("Model: " + self.modelFormula)
    def colonButtonClicked(self):
        self.modelFormula += ' : '
        self.phenoVarListBox.setEnabled(True)
        self.plusButton.setEnabled(False)
        self.colonButton.setEnabled(False)
        self.starButton.setEnabled(False)
        self.processEsetButton.setEnabled(False)
        self.modelText.setText("Model: " + self.modelFormula)
    def starButtonClicked(self):
        self.modelFormula += ' * '
        self.phenoVarListBox.setEnabled(True)
        self.plusButton.setEnabled(False)
        self.colonButton.setEnabled(False)
        self.starButton.setEnabled(False)
        self.processEsetButton.setEnabled(False)
        self.modelText.setText("Model: " + self.modelFormula)
    def processEset(self): #convert the listBox elements to R objects, perform differential expression and send the results of that to the next widget
        if not self.loadingSavedSession: # we really need to process this block
            if self.phenoData == '':
                #first we need to construct the design
                h=''
                for j in xrange(self.selectedArrays.count()): #loop that makes r objects named holder_1,2,... that will be used to make the final vector
                    h += '"'+str(self.selectedArrays.item(int(j)).text())+'",'
                    self.sampleA.append(str(self.selectedArrays.item(int(j)).text()))
                i = ''
                for j in xrange(self.selectedArraysB.count()):
                    i += '"'+str(self.selectedArraysB.item(int(j)).text())+'",'
                    self.sampleB.append(str(self.selectedArraysB.item(int(j)).text()))
                #self.infoa.setText(h)
                
                self.rsession(self.Rvariables['subset']+'<-'+self.data+'[,c('+h+i[:len(i)-1]+')]')
                self.rsession(self.Rvariables['classes']+'<-as.numeric(colnames('+self.Rvariables['subset']+') %in% c('+i[:len(i)-1]+'))') #make the cla object in R to assign the classes based on the values of h

                
                self.rsession('cvect<-data.frame(type=1, class='+self.Rvariables['classes']+')') 
                self.rsession('design<-model.matrix(~class, cvect)')
            else: #someone attached phenoData so lets use that to make the design
                self.rsession('design<-model.matrix(~'+self.modelFormula+', '+self.phenoData+')')
                
            self.rsession('fit<-lmFit('+self.Rvariables['subset']+', design)')
            self.rsession(self.Rvariables['results']+'<-eBayes(fit)')
            self.newdata = self.olddata.copy()
            self.newdata['data']=self.Rvariables['results']
            self.newdata['classes'] = self.Rvariables['classes']
        self.send('eBayes fit', self.newdata)
        self.infoa.setText('Your data fit has been sent.  Use the diffSelector widget to select significant cutoffs')
        self.processingComplete = 1


    def printSelected(self):
        if self.classA == True:
            if self.arrays:
                self.selectedArrays.addItem(str(self.arrays.selectedItems()[0].text()))
                self.infoa.setText("An array was selected, and it's name is "+str(self.arrays.selectedItems()[0].text()))
                #self.arrays.selectedItems.clear()
            else: 
                self.infoa.setText("No arrays selected")
        elif self.classA == False:
            if self.arrays:
                self.selectedArraysB.addItem(str(self.arrays.selectedItems()[0].text()))
                self.infoa.setText("An array was selected, and it's name is "+str(self.arrays.selectedItems()[0].text()))
                #self.arrays.selectedItems.clear()
            else: 
                self.infoa.setText("No arrays selected")

    
    def Rreload(self):
        for v in self.sampleA:
            self.selectedArrays.addItem(str(v))
        for v in self.sampleB:
            self.selectedArraysB.addItem(str(v))
        self.modelText.setText("Model: " + self.modelFormula)
        