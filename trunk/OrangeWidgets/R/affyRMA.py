"""
<name>Normalize</name>
<description>Processes an Affybatch to an eset using RMA</description>
<icon>icons/rma.png</icons>
<priority>1010</priority>
"""


from OWRpy import *
import OWGUI
class affyRMA(OWRpy):
    settingsList = ['variable_suffix', 'normmeth', 'normoptions', 'bgcorrect', 'bgcorrectmeth', 'pmcorrect', 'summarymeth', 'norm', 'selectMethod']
    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager, "Normalization")
        OWRpy.__init__(self)
        
        #default values        
        self.normmeth = 'quantiles'
        self.normoptions = ''
        self.bgcorrect = 'FALSE'
        self.bgcorrectmeth = 'none'
        self.pmcorrect = 'pmonly'
        self.summarymeth = 'liwong'
        self.norm = ['quantiles']
        self.selectMethod = 3
        self.loadSettings()
        
        #required librarys
        self.require_librarys(['affy'])
        
        
        #set R variable names
        self.Rvariables = self.setRvariableNames(['normalized_affybatch','folder'])
        
        #signals		
        self.inputs = [("Affybatch Expression Matrix", orange.Variable, self.process)]
        self.outputs = [("Normalized eSet", orange.Variable)]

        
        #the GUI
        status = OWGUI.widgetBox(self.controlArea, "Status")
        self.infoa = OWGUI.widgetLabel(status, 'No data loaded.')
        normrad = OWGUI.widgetBox(self.controlArea, "Normalization Methods")
        self.selMethBox = OWGUI.radioButtonsInBox(normrad, self, 'selectMethod', ["RMA", "MAS5", "Custom"], callback=self.selectMethodChanged)
        self.selMethBox.setEnabled(False)
        info = OWGUI.widgetBox(self.controlArea, "Normalization Options")
        
        #drop list box
        
        #insert a block to check what type of object is connected.  If nothing connected set the items of the normalize methods objects to 
        self.normselector = OWGUI.comboBox(info, self, 'normmeth', label="Normalization Method  ", items=self.norm, orientation=0)
        self.normselector.setEnabled(False)
        self.bgcorrectselector = OWGUI.comboBox(info, self, 'bgcorrect', label="Background Correct Methods", items=['TRUE', 'FALSE'], orientation=0)
        self.bgcorrectselector.setEnabled(False)
        self.bgcmethselector = OWGUI.comboBox(info, self, 'bgcorrectmeth', label="Background Correct Methods", items=self.rsession('bgcorrect.methods'), orientation=0)
        self.bgcmethselector.setEnabled(False)
        self.pmcorrectselector = OWGUI.comboBox(info, self, 'pmcorrect', label="Perfect Match Correct Methods", items=self.rsession('pmcorrect.methods'), orientation=0)
        self.pmcorrectselector.setEnabled(False)
        self.summethselector = OWGUI.comboBox(info, self, 'summarymeth', label="Summary Methods", items=self.rsession('express.summary.stat.methods'), orientation=0)
        self.summethselector.setEnabled(False)
        
        
        #run = OWGUI.widgetBox(self.controlArea, "Run the Normalization")
        #self.infob = OWGUI.widgetLabel(run, 'Procedure not run yet')
        runbutton = OWGUI.button(info, self, "Run Normalization", callback = self.normalize, width=200)
        #OWGUI.button(run, self, 'test', callback = self.checkRCode, width=200)
        
    def normalize(self):
        self.infoa.setText('Processing')
        if self.selectMethod == 0:
            self.rsession(self.Rvariables['normalized_affybatch']+'<-rma('+self.data+')',True) #makes the rma normalization
        if self.selectMethod == 1:
            self.rsession(self.Rvariables['normalized_affybatch']+'<-mas5('+self.data+')',True) #makes the rma normalization
        if self.selectMethod == 2:
            self.rsession(self.Rvariables['normalized_affybatch']+'<-expresso('+self.data+', bg.correct='+self.bgcorrect+', bgcorrect.method="'+self.bgcorrectmeth+'", pmcorrect.method="'+self.pmcorrect+'", summary.method="'+self.summarymeth+'")',True)

        self.infoa.setText('Processed')
        neset = {'data':'exprs('+self.Rvariables['normalized_affybatch']+')', 'eset':self.Rvariables['normalized_affybatch'], 'normmethod':'rma'}
        
        self.send("Normalized eSet", neset)
    
    
    # def checkRCode(self):
        # self.infob.setText('normalized_affybatch'+self.state['vs']+'<-expresso('+self.state['data']+', bg.correct='+self.bgcorrect+', bgcorrect.method='+self.bgcorrectmeth+', pmcorrect.method='+self.pmcorrect+', summary.method='+self.summarymeth+')')
        
    def collectOptions(self):
        if self.normmeth == None: self.normoptions = ""
        elif self.normmeth == "":
            self.normmeth = None
            self.collectOptions()
        else:
            self.normoptions = ',method='+self.normmeth
    
    def process(self, dataset):
        
        try: 
            
            print str(dataset['eset'])
            self.data = str(dataset['eset'])
            
            if self.rsession('length(exprs('+self.data+')[1,])') > 10:
                self.selectMethod = 2
                self.selectMethodChanged()
                
            else:
                self.selectMethod = 0
                self.selectMethodChanged()
                
            self.selMethBox.setEnabled(True)
            self.infoa.setText('Data Loaded')
        except: 
            print 'error'
    
    
    
    def runCustom(self):
        self.infoa.setText('Processing')
        self.collectOptions()
        if self.state['data']:
            self.rsession('normalized_affybatch'+self.state['vs']+'<-expresso('+self.state['data']+', bg.correct='+self.bgcorrect+', bgcorrect.method="'+self.bgcorrectmeth+'", pmcorrect.method="'+self.pmcorrect+'", summary.method="'+self.summarymeth+'")')
            normset = 'normalized_affybatch'+self.state['vs']
            self.infob.setText('Normalization compleated.')
            self.send("Normalized eSet", normset)
        else: return
    
    def selectMethodChanged(self):
        if self.selectMethod == 0:
            self.bgcorrectselector.setEnabled(False)
            self.bgcmethselector.setEnabled(False)
            self.pmcorrectselector.setEnabled(False)
            self.summethselector.setEnabled(False)
            self.normselector.setEnabled(False)
        if self.selectMethod == 1:
            self.bgcorrectselector.setEnabled(False)
            self.bgcmethselector.setEnabled(False)
            self.pmcorrectselector.setEnabled(False)
            self.summethselector.setEnabled(False)
            self.normselector.setEnabled(False)
        if self.selectMethod == 2:
            self.bgcorrectselector.setCurrentIndex(self.bgcorrectselector.findText('FALSE'))
            self.bgcorrectselector.setEnabled(True)
            self.bgcorrectmeth = 'none'
            self.bgcmethselector.setCurrentIndex(self.bgcmethselector.findText('none'))
            self.bgcmethselector.setEnabled(True)
            self.pmcorrect = 'pmonly'
            self.pmcorrectselector.setCurrentIndex(self.pmcorrectselector.findText('pmonly'))
            self.pmcorrectselector.setEnabled(True)
            self.summarymeth = 'liwong'
            self.summethselector.setCurrentIndex(self.summethselector.findText('liwong'))
            self.summethselector.setEnabled(True)
            self.norm = ['quantiles']
            self.normselector.clear()
            self.normselector.addItems(self.rsession('normalize.methods('+self.data+')'))
            self.normselector.setCurrentIndex(self.normselector.findText('invariantset'))
            self.normselector.setEnabled(True)
        
        self.infoa.setText('Data has been connected')

            
