"""
<name>Differential Expression</name>
<description>Calculates differential expression of genes from an eSet object</description>
<tags>Microarray</tags>
<RFunctions>limma:lmFit</RFunctions>
<icon>icons/diffexp.png</icon>
<priority>70</priority>
"""

from OWRpy import *
import redRGUI

class diffExp(OWRpy):

    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        
        self.samplenames = []
        self.sampleA = []
        self.sampleB = []
        self.phenoData = ''
        self.modelFormula = ''
        self.data = ''
        self.newdata = {}
        self.olddata = {}
        self.require_librarys(['affy','gcrma','limma'])
        self.loadSettings()
        
        self.setRvariableNames(['results','classes','subset', 'diffExp_cm'])
        

        self.inputs = [("Expression Set", signals.RDataFrame, self.process), ("Phenotype Data", signals.RDataFrame, self.phenoProcess)]
        self.outputs = [("eBayes fit", signals.affy.RMArrayLM), ('eBayes data frame', signals.RDataFrame)]
        
        self.samplenames = None #names of the samples (as a python object) to be used for generating the differential expression matrix
        self.classA = True #a container to maintain which list to add the arrays to
        
        #GUI
        self.boxIndices = {}
        self.dontSaveList.append('boxIndices')
        self.valuesStack = QStackedWidget(self)
        self.controlArea.layout().addWidget(self.valuesStack)
        
        boxVal = redRGUI.widgetBox(self.controlArea)
        self.boxIndices[0] = boxVal
        layk = QWidget(self)
        boxVal.layout().addWidget(layk)
        grid = QGridLayout()
        grid.setMargin(0)
        layk.setLayout(grid)
        
        # set as valstack 0
        box = redRGUI.widgetBox(boxVal, sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        grid.addWidget(box, 0,1)
        processButton = redRGUI.button(self.bottomAreaRight, "Process eSet", callback = self.processEset, width=150)
        self.arrays = redRGUI.listBox(box, label = 'Available Samples', callback = self.printSelected)
        setAbutton = redRGUI.button(box, "Switch Class", callback = self.switchClass, width = 200)
        self.infoa = redRGUI.widgetLabel(box, "No arrays selected")
        self.infob = redRGUI.widgetLabel(box, "Setting Class A")
        
        selecteda = redRGUI.widgetBox(self.controlArea,sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        grid.addWidget(selecteda, 0,0)
        self.selectedArrays = redRGUI.listBox(selecteda, label = 'Class A Samples')
        clearaButton = redRGUI.button(selecteda, "Clear",callback = self.clearA, width = 200)
        
        selectedb = redRGUI.widgetBox(self.controlArea,sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        grid.addWidget(selectedb, 0,2)
        self.selectedArraysB = redRGUI.listBox(selectedb, label = 'Class B Samples')
        clearbButton = redRGUI.button(selectedb, "Clear", callback = self.clearB, width = 200)
        self.valuesStack.addWidget(boxVal)
        # end valstack 0
        
        # valstack 1: phenodataConnected
        
        boxVal = redRGUI.widgetBox(self.controlArea)
        self.boxIndices[1] = boxVal
        layk2 = QWidget(self)
        boxVal.layout().addWidget(layk2)
        grid2 = QGridLayout()
        grid2.setMargin(0)
        layk2.setLayout(grid2)
        
        
        box = redRGUI.widgetBox(boxVal)
        grid2.addWidget(box, 0, 0)
        self.functionBox = redRGUI.RFormulaEntry(box)
        self.functionBox.outcomeVariable.hide() #don't need to see the outcome variable
        self.valuesStack.addWidget(boxVal)
        
        self.valuesStack.setCurrentWidget(self.boxIndices[0])
        
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
        if not self.data == '' and self.R('intersect(rownames('+data['data']+'), colnames('+self.data+'))') == None:
            self.infoa.setText('No intersect between the phenoData and the expression data.\nPhenoData ignored.')
            return
        
        self.phenoData = data['data']
        colnames = self.R('colnames('+self.phenoData+')')
        self.functionBox.update(colnames)
        self.valuesStack.setCurrentWidget(self.boxIndices[1])

    def process(self, data):
        
        self.arrays.clear()
        self.selectedArrays.clear()
        self.selectedArraysB.clear()
        self.data = '' #clear the data
        if not data: return

        self.data = data['data']
        self.samplenames = self.R('colnames('+self.data+')',wantType='list') #collect the sample names to make the differential matrix

        for v in self.samplenames:
            self.arrays.addItem(v)
        
        if not self.phenoData == '' and self.R('intersect(rownames('+self.phenoData+'), colnames('+self.data+'))') == None:
            self.infoa.setText('No intersect between the phenoData and the expression data.\nPhenoData ignored.')
            self.valuesStack.setCurrentWidget(self.boxIndices[0])
            return

    def processEset(self, reload = 0): #convert the listBox elements to R objects, perform differential expression and send the results of that to the next widget
        if self.data == '': return
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
                
                self.R(self.Rvariables['subset']+'<-'+self.data+'[,c('+h+i[:len(i)-1]+')]')
                self.R(self.Rvariables['classes']+'<-as.numeric(colnames('+self.Rvariables['subset']+') %in% c('+i[:len(i)-1]+'))') #make the cla object in R to assign the classes based on the values of h

                
                self.R('cvect<-data.frame(type=1, class='+self.Rvariables['classes']+')') 
                self.R('design<-model.matrix(~class, cvect)')
            else: #someone attached phenoData so lets use that to make the design
                print self.functionBox.Formula()[1]
                print self.phenoData
                print self.data
                self.R('design<-model.matrix(~'+self.functionBox.Formula()[1]+', '+self.phenoData+'[colnames('+self.data+'),])')
                self.R(self.Rvariables['subset']+ '<-' +self.data)
                self.R(self.Rvariables['classes']+'<-as.data.frame(design)')
            self.R('fit<-lmFit('+self.Rvariables['subset']+', design)')
            self.R(self.Rvariables['results']+'<-eBayes(fit)')

        newdata = signals.RDataFrame(data = 'as.data.frame('+self.Rvariables['results']+')') 
        #newdata.setOptionalData('classes', self.Rvariables['classes'], 'Differential Expression', 'Created from either a design matrix or the user input in Differential Expression')
        self.rSend('eBayes data frame', newdata)
        
        self.newdata = signals.affy.RMArrayLM(data = self.Rvariables['results'])
        #self.newdata.setOptionalData('classes', self.Rvariables['classes'], 'Differential Expression', 'Created from either a design matrix or the user input in Differential Expression')
        self.rSend('eBayes fit', self.newdata)
        self.infoa.setText('Your data fit has been sent.  Use the diffSelector widget to select significant cutoffs')


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

    
    # def Rreload(self):
        # for v in self.sampleA:
            # self.selectedArrays.addItem(str(v))
        # for v in self.sampleB:
            # self.selectedArraysB.addItem(str(v))
        # self.arrays.addItems(self.sampleA)
        # self.arrays.addItems(self.sampleB)
        # self.modelText.setText("Model: " + self.modelFormula)
        