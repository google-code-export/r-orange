"""
<name>Diff Exp</name>
<description>Calculates differential expression of genes from an eSet object</description>
<tags>Microarray</tags>
<RFunctions>limma:lmFit</RFunctions>
<icon>icons/diffexp.png</icon>
<priority>70</priority>
"""

from OWRpy import *
import redRGUI

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
        
        boxVal = redRGUI.widgetBox(self.controlArea, "Set Classes")
        self.boxIndices[0] = boxVal
        layk = QWidget(self)
        boxVal.layout().addWidget(layk)
        grid = QGridLayout()
        grid.setMargin(0)
        layk.setLayout(grid)
        
        # set as valstack 0
        box = redRGUI.widgetBox(boxVal, "Process")
        grid.addWidget(box, 0,1)
        processButton = redRGUI.button(box, self, "Process eSet", callback = self.processEset, width=200)
        self.arrays = redRGUI.listBox(box, self, callback = self.printSelected)
        setAbutton = redRGUI.button(box, self, "Switch Class", callback = self.switchClass, width = 200)
        self.infoa = redRGUI.widgetLabel(box, "No arrays selected")
        self.infob = redRGUI.widgetLabel(box, "Setting Class A")
        
        selecteda = redRGUI.widgetBox(self.controlArea, "Selected Arrays")
        grid.addWidget(selecteda, 0,0)
        self.selectedArrays = redRGUI.listBox(selecteda, self)
        clearaButton = redRGUI.button(selecteda, self, "Clear",callback = self.clearA, width = 200)
        
        selectedb = redRGUI.widgetBox(self.controlArea, "Selected Arrays")
        grid.addWidget(selectedb, 0,2)
        self.selectedArraysB = redRGUI.listBox(selectedb, self)
        clearbButton = redRGUI.button(selectedb, self, "Clear", callback = self.clearB, width = 200)
        self.valuesStack.addWidget(boxVal)
        # end valstack 0
        
        # valstack 1: phenodataConnected
        
        boxVal = redRGUI.widgetBox(self.controlArea, "Set Classes")
        self.boxIndices[1] = boxVal
        layk2 = QWidget(self)
        boxVal.layout().addWidget(layk2)
        grid2 = QGridLayout()
        grid2.setMargin(0)
        layk2.setLayout(grid2)
        
        
        box = redRGUI.widgetBox(self, "Phenotype Variables")
        grid2.addWidget(box, 0, 0)
        self.phenoVarListBox = redRGUI.listBox(box, self, callback = self.phenoVarListBoxItemClicked)
        buttonsBox = redRGUI.widgetBox(self, "Commands")
        grid2.addWidget(buttonsBox, 0,1)
        self.plusButton = redRGUI.button(buttonsBox, self, "And", callback = self.plusButtonClicked)
        self.plusButton.setEnabled(False)
        self.colonButton = redRGUI.button(buttonsBox, self, "Interacting With", callback = self.colonButtonClicked)
        self.colonButton.setEnabled(False)
        self.starButton = redRGUI.button(buttonsBox, self, "Together and Interacting", callback = self.starButtonClicked)
        self.starButton.setEnabled(False)
        self.processEsetButton = redRGUI.button(buttonsBox, self, "Commit", callback = self.processEset)
        self.processEsetButton.setEnabled(False)
        
        self.modelText = redRGUI.widgetLabel(boxVal, "Model: ")
        self.valuesStack.addWidget(boxVal)
        
        self.valuesStack.setCurrentWidget(self.boxIndices[0])
        
        #self.Rreload() #Important to be at the end of the __init__
        # try:
            # varexists1 = self.R('exists("'+self.Rvariables['classes']+'")') #should trigger an exception if it doesn't exist
            # varexists2 = self.R('exists("'+self.Rvariables['results']+'")')
            # self.infod.setText(str(varexists))
            # if varexists1 and varexists2:
                # self.processEset(reload = True)
            # else:
                # return
        # except:
            # pass
        # if self.loadingSavedSession:
            # self.processEset()
    def onLoadSavedSession(self):
        if self.Rvariables['results'] in self.R('ls()'):
            self.Rreload()
            self.processEset(reload = 1)
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
        if not data: return
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
        self.data = '' #clear the data
        self.olddata = {'data':''} # clear the send signal
        for output in self.outputs:
            self.rSend(output[0], None, 0) #start the killing cascade.
        if data:
            self.data = data['data']
            self.olddata = data.copy()
            self.samplenames = self.rsession('colnames('+self.data+')') #collect the sample names to make the differential matrix

            if self.samplenames is str:
                self.samplenames = [self.samplenames]
            for v in self.samplenames:
                self.arrays.addItem(v)
            

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
    def processEset(self, reload = 0): #convert the listBox elements to R objects, perform differential expression and send the results of that to the next widget
        if not reload: # we really need to process this block
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
        self.rSend('eBayes fit', self.newdata)
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
        self.arrays.addItems(self.sampleA)
        self.arrays.addItems(self.sampleB)
        self.modelText.setText("Model: " + self.modelFormula)
        