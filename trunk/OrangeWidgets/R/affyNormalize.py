"""
<name>Normalize</name>
<description>Processes an Affybatch to an eset using RMA</description>
<icon>icons/Normalize.png</icon>
<priority>1010</priority>
"""


from OWRpy import *
import OWGUI
import RAffyClasses

class affyNormalize(OWRpy):
    settingsList = ['norminfo', 'enableMethBox', 'data','normmeth', 'normoptions', 'bgcorrect', 'bgcorrectmeth', 'pmcorrect', 'summarymeth', 'norm', 'selectMethod']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Normalization")
        
        #OWRpy.__init__(self)
        #self.setStateVariables(['enableMethBox','data','normmeth', 'normoptions', 'bgcorrect', 'bgcorrectmeth', 'pmcorrect', 'summarymeth', 'norm', 'selectMethod'])
        #default values        
        self.normmeth = 'quantiles'
        self.normoptions = ''
        self.bgcorrect = 'FALSE'
        self.bgcorrectmeth = 'none'
        self.pmcorrect = 'pmonly'
        self.summarymeth = 'liwong'
        self.norm = ['quantiles']
        self.selectMethod = 3
        self.data = ''
        self.enableMethBox = False
        self.norminfo = ''
        self.loadSettings()
        
        
        
        
        #set R variable names
        self.setRvariableNames(['normalized_affybatch','folder'])
        
        #signals		
        self.inputs = [("Expression Matrix", RAffyClasses.RAffyBatch, self.process)]
        self.outputs = [("Normalized DataFrame", RvarClasses.RDataFrame),("Normalized AffyBatch", RAffyClasses.RAffyBatch)]

        
        #the GUI
        status = OWGUI.widgetBox(self.controlArea, "Status")
        self.infoa = OWGUI.widgetLabel(status, 'No data loaded.')
        normrad = OWGUI.widgetBox(self.controlArea, "Normalization Methods")
        self.selMethBox = OWGUI.radioButtonsInBox(normrad, self, 'selectMethod', ["RMA", "MAS5", "Custom"], callback=self.selectMethodChanged)
        self.selMethBox.setEnabled(self.enableMethBox)
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
        if self.loadingSavedSession:
            self.normalize()
        
        
    def normalize(self):
        self.infoa.setText('Processing')
        if not self.loadingSavedSession:
            if self.selectMethod == 0:
                self.rsession(self.Rvariables['normalized_affybatch']+'<-rma('+self.data+')',True) #makes the rma normalization
                self.norminfo = 'Normalized with RMA'
            if self.selectMethod == 1:
                self.rsession(self.Rvariables['normalized_affybatch']+'<-mas5('+self.data+')',True) #makes the mas5 normalization
                self.norminfo = 'Normalized with MAS5'
            if self.selectMethod == 2:
                self.rsession(self.Rvariables['normalized_affybatch']+'<-expresso('+self.data+', bg.correct='+self.bgcorrect+', bgcorrect.method="'+self.bgcorrectmeth+'", pmcorrect.method="'+self.pmcorrect+'", summary.method="'+self.summarymeth+'")',True)
                self.norminfo = 'Normalized by: Background Correction:'+self.bgcorrect+', Method:'+self.bgcorrectmeth+', Perfect Match Correct Method: '+self.pmcorrect+', Summary Method: '+self.summarymeth

        neset = {'data':'exprs('+self.Rvariables['normalized_affybatch']+')', 'eset':self.Rvariables['normalized_affybatch'], 'normmethod':'rma'}
        
        self.rSend("Normalized DataFrame", neset)
        self.rSend("Normalized AffyBatch", {'data':self.Rvariables['normalized_affybatch']})
        self.infoa.setText(self.norminfo)
        
    def collectOptions(self):
        if self.normmeth == None: self.normoptions = ""
        elif self.normmeth == "":
            self.normmeth = None
            self.collectOptions()
        else:
            self.normoptions = ',method='+self.normmeth
    
    def process(self, dataset):
        #required librarys
        self.require_librarys(['affy'])
        if self.loadingSavedSession:
            self.selectMethodChanged()
            self.selMethBox.setEnabled(True)
            self.normalize()
            return

        try: 
            print str(dataset['data'])
            self.data = str(dataset['data'])
            
            if self.rsession('length(exprs('+self.data+')[1,])') > 10:
                self.selectMethod = 2
                self.selectMethodChanged()
                
            else:
                self.selectMethod = 0
                self.selectMethodChanged()
                
            self.selMethBox.setEnabled(True)
            self.infoa.setText('Data Loaded')
                if dataset['kill'] == True:
                    self.rSend("Normalized DataFrame", {'kill':True, 'data':''})
                    self.rSend("Normalized AffyBatch", {'kill':True, 'data':''})
        except: 
            print 'error'

        
        self.bgcmethselector.addItems(self.rsession('bgcorrect.methods'))
        self.pmcorrectselector.addItems(self.rsession('pmcorrect.methods'))
        self.summethselector.addItems(self.rsession('express.summary.stat.methods'))
        
    
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
        
        #self.infoa.setText('Ready to Normalize')

            
